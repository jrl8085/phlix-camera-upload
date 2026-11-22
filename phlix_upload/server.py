"""The HTTP API the Phlix app talks to.

    GET  /api/v1/hello          who is this (no sign-in)
    POST /api/v1/pair           pair a phone, by Plex ownership or by code
    GET  /api/v1/status         free space and this phone's totals
    POST /api/v1/assets/check   which of these photos are already here
    PUT  /api/v1/assets/<key>   upload one photo or video
    POST /api/v1/unpair         forget this phone
    GET  /api/v1/health         the status page's facts, as JSON
    GET  /                      a small status page for people
    GET  /healthz               "ok", for Docker's health check

Every call except hello, pair, health, the status page and healthz needs the token
the phone was given when it paired: `Authorization: Bearer <token>`.

The helper only ever receives files. Nothing here reads a stored photo back,
so a pairing token can add to the upload folder and do nothing else.
"""

from __future__ import annotations

import hashlib
import http.server
import json
import logging
import os
import re
import socket
import ssl
import threading
import time
import urllib.parse

from . import API_VERSION, SERVICE_NAME, __version__
from . import plex as plex_module
from .config import Config
from .pairing import AttemptLimiter, codes_match
from .plex import PlexLink
from .statuspage import render_status_page
from .storage import (
    Storage,
    StorageError,
    clean_filename,
    clean_folder_name,
    is_allowed_extension,
    parse_created,
    storage_error_from,
)
from .store import Device, Store

log = logging.getLogger("phlix.server")

MAX_JSON_BYTES = 512 * 1024
MAX_CHECK_ITEMS = 2000
MAX_CONNECTIONS = 96
#: Connections one address may hold at once, so that a single misbehaving
#: device cannot take every place. A phone uses five at most; the number
#: leaves room for several phones that share an address (a second router, a
#: reverse proxy, or Docker Desktop, which shows every phone as one address).
MAX_CONNECTIONS_PER_ADDRESS = 24
#: Seconds a new connection has to finish its TLS handshake, and then to
#: send its first request.
_HANDSHAKE_SECONDS = 10
_FIRST_REQUEST_SECONDS = 20
#: Seconds a connection that has made a request may stay silent, between
#: requests or in the middle of an upload.
_IDLE_SECONDS = 75
#: How much of a refused upload is read and thrown away so that the phone
#: receives the refusal instead of a broken connection. A sender that is not
#: paired gets far less patience than a paired phone.
_DRAIN_BYTES = 32 * 1024 * 1024
_DRAIN_SECONDS = 15.0
_STRANGER_DRAIN_BYTES = 1024 * 1024
_STRANGER_DRAIN_SECONDS = 2.0
_CHUNK = 1024 * 1024

_DEVICE_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")
_ASSET_KEY = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_KINDS = ("photo", "video", "other")


class App:
    """Everything a request needs, shared by all request threads."""

    def __init__(self, config: Config, store: Store, storage: Storage, plex: PlexLink,
                 pairing_code: str, tls_fingerprint: str | None = None,
                 limiter: AttemptLimiter | None = None):
        self.config = config
        self.store = store
        self.storage = storage
        self.plex = plex
        self.pairing_code = pairing_code
        self.tls_fingerprint = tls_fingerprint
        self.limiter = limiter or AttemptLimiter()
        #: Held while a finished upload is placed and recorded, so two uploads
        #: of the same file cannot both be stored.
        self.place_lock = threading.Lock()
        self._space_lock = threading.Lock()
        #: Bytes of uploads that were let in and have not reached the disk yet.
        self._promised = 0
        self._seen_lock = threading.Lock()
        self._seen: dict[str, float] = {}

    @property
    def code_pairing(self) -> bool:
        return self.config.pairing in ("auto", "code")

    @property
    def plex_pairing(self) -> bool:
        return self.config.pairing in ("auto", "plex")

    def reserve_space(self, length: int) -> bool:
        """Let an upload of `length` bytes in, if the disk has room for it.

        Room means: after this upload, and every other upload that is still
        arriving, the disk keeps MIN_FREE_GB free. Without the second part,
        several uploads sent at once would each see the same free space and
        together fill the disk past the floor.
        """
        with self._space_lock:
            free, _ = self.storage.disk_usage()
            if free - self._promised - length < self.config.min_free_bytes:
                return False
            self._promised += length
            return True

    def release_space(self, count: int) -> None:
        """Bytes that have been written, or that will not arrive after all."""
        if count <= 0:
            return
        with self._space_lock:
            self._promised = max(0, self._promised - count)

    def note_seen(self, device_id: str) -> None:
        """Record that a device called, at most once a minute per device."""
        now = time.monotonic()
        with self._seen_lock:
            if now - self._seen.get(device_id, -1e9) < 60:
                return
            self._seen[device_id] = now
        self.store.touch_device(device_id)


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 64

    def __init__(self, address, app: App, ssl_context: ssl.SSLContext | None = None):
        self.app = app
        self.ssl_context = ssl_context
        self._active = 0
        self._active_by_address: dict[str, int] = {}
        self._active_lock = threading.Lock()
        super().__init__(address, Handler)

    def process_request(self, request, client_address):
        address = client_address[0]
        with self._active_lock:
            held = self._active_by_address.get(address, 0)
            refuse = self._active >= MAX_CONNECTIONS or held >= MAX_CONNECTIONS_PER_ADDRESS
            if not refuse:
                self._active += 1
                self._active_by_address[address] = held + 1
        if refuse:
            self.shutdown_request(request)
            return
        super().process_request(request, client_address)

    def process_request_thread(self, request, client_address):
        address = client_address[0]
        try:
            super().process_request_thread(request, client_address)
        finally:
            with self._active_lock:
                self._active -= 1
                left = self._active_by_address.get(address, 1) - 1
                if left > 0:
                    self._active_by_address[address] = left
                else:
                    self._active_by_address.pop(address, None)

    def finish_request(self, request, client_address):
        if self.ssl_context is None:
            super().finish_request(request, client_address)
            return
        # The TLS handshake happens here, on the request's own thread, so a
        # client that opens a connection and says nothing cannot hold up
        # everyone else.
        request.settimeout(_HANDSHAKE_SECONDS)
        try:
            secure = self.ssl_context.wrap_socket(request, server_side=True)
        except (ssl.SSLError, OSError):
            return
        try:
            self.RequestHandlerClass(secure, client_address, self)
        finally:
            try:
                secure.close()
            except OSError:
                pass

    def handle_error(self, request, client_address):
        # A phone that walks out of Wi-Fi range mid-upload is not an error
        # worth a stack trace.
        log.debug("Connection from %s ended abruptly", client_address[0], exc_info=True)


class _Abort(Exception):
    """Raised after an error response was sent, to unwind the handler."""


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = f"PhlixCameraUpload/{__version__}"
    sys_version = ""
    #: Seconds a new connection has to send its first request. Once it has,
    #: `_route` gives it `_IDLE_SECONDS` of silence at a time.
    timeout = _FIRST_REQUEST_SECONDS

    server: Server

    @property
    def app(self) -> App:
        return self.server.app

    # -- plumbing -----------------------------------------------------------

    def log_message(self, format, *args):  # noqa: A002 - the base class's name
        log.debug("%s %s", self.client_address[0], format % args)

    def version_string(self):
        return self.server_version

    def send_error(self, code, message=None, explain=None):
        # The base class calls this for requests it cannot parse.
        self.close_connection = True
        self._send_json(code, {"error": {"code": "bad_request", "message": message or "Bad request"}}, close=True)

    def _send(self, status: int, body: bytes, content_type: str, close: bool = False,
              headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        if close or self.close_connection:
            self.send_header("Connection", "close")
            self.close_connection = True
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, status: int, payload: dict, close: bool = False,
                   headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8", close=close, headers=headers)

    def _fail(self, status: int, code: str, message: str, close: bool = False,
              headers: dict[str, str] | None = None, **extra) -> _Abort:
        """Send an error and return the exception that unwinds the handler."""
        error = {"code": code, "message": message}
        error.update(extra)
        self._send_json(status, {"error": error}, close=close, headers=headers)
        return _Abort()

    def _content_length(self) -> int | None:
        value = self.headers.get("Content-Length")
        if value is None:
            return None
        try:
            length = int(value)
        except ValueError:
            return None
        return length if length >= 0 else None

    def _read_json(self) -> dict:
        if "chunked" in (self.headers.get("Transfer-Encoding") or "").lower():
            raise self._fail(411, "length_required", "Send a Content-Length", close=True)
        length = self._content_length()
        if length is None:
            raise self._fail(411, "length_required", "Send a Content-Length", close=True)
        if length > MAX_JSON_BYTES:
            raise self._fail(413, "too_large", "The request is too large", close=True)
        raw = self.rfile.read(length)
        if len(raw) != length:
            self.close_connection = True
            raise _Abort()
        try:
            payload = json.loads(raw.decode("utf-8"))
            # Text that cannot be written back as UTF-8 (half of a surrogate
            # pair) would fail much later, somewhere less convenient.
            json.dumps(payload, ensure_ascii=False).encode("utf-8")
        except (ValueError, UnicodeError, RecursionError):
            raise self._fail(400, "bad_request", "The request is not valid JSON") from None
        if not isinstance(payload, dict):
            raise self._fail(400, "bad_request", "The request must be a JSON object")
        return payload

    def _discard_body(self) -> None:
        """Skip the body of a request the route does not read."""
        length = self._content_length() or 0
        if length > MAX_JSON_BYTES or "chunked" in (self.headers.get("Transfer-Encoding") or "").lower():
            self.close_connection = True
            return
        if length:
            self.rfile.read(length)

    def _device(self) -> Device | None:
        header = self.headers.get("Authorization") or ""
        if not header.startswith("Bearer "):
            return None
        token = header[len("Bearer "):].strip()
        if not 20 <= len(token) <= 200:
            return None
        device = self.app.store.device_for_token(token)
        if device is not None:
            self.app.note_seen(device.id)
        return device

    def _require_device(self) -> Device:
        device = self._device()
        if device is None:
            raise self._fail(401, "unauthorized", "This phone is not paired with the helper. Pair it again.")
        return device

    # -- routing ------------------------------------------------------------

    def _route(self) -> None:
        path = urllib.parse.urlsplit(self.path).path
        method = self.command
        try:
            self.connection.settimeout(_IDLE_SECONDS)
        except OSError:
            pass
        if method in ("GET", "HEAD") and (self._content_length() or self.headers.get("Transfer-Encoding")):
            # These routes read no body. One that came anyway would be taken
            # for the start of the next request, so the connection ends here.
            self.close_connection = True
        try:
            if path.startswith("/api/v1/assets/") and path != "/api/v1/assets/check":
                if method != "PUT":
                    self._discard_body()
                    raise self._fail(405, "method_not_allowed", "Use PUT to upload", headers={"Allow": "PUT"})
                self._upload(path[len("/api/v1/assets/"):])
                return
            routes = {
                ("GET", "/api/v1/hello"): self._hello,
                ("GET", "/api/v1/health"): self._health,
                ("POST", "/api/v1/pair"): self._pair,
                ("GET", "/api/v1/status"): self._status,
                ("POST", "/api/v1/assets/check"): self._check,
                ("POST", "/api/v1/unpair"): self._unpair,
                ("GET", "/"): self._status_page,
                ("HEAD", "/"): self._status_page,
                ("GET", "/healthz"): self._healthz,
                ("HEAD", "/healthz"): self._healthz,
            }
            handler = routes.get((method, path))
            if handler is None:
                self._discard_body()
                known = any(route_path == path for _, route_path in routes)
                if known:
                    raise self._fail(405, "method_not_allowed", "That method is not allowed here")
                raise self._fail(404, "not_found", "There is nothing at this address")
            handler()
        except _Abort:
            return
        except (ConnectionError, TimeoutError, ssl.SSLError):
            self.close_connection = True
        except Exception as error:  # noqa: BLE001 - a request must never take the server down
            # One line, so that someone sending nonsense on purpose cannot
            # fill the log; the full trace is there at LOG_LEVEL=debug.
            log.error("Unexpected error handling %s %s from %s: %s: %s", method, path,
                      self.client_address[0], type(error).__name__, error)
            log.debug("The error in full", exc_info=True)
            self.close_connection = True
            try:
                self._send_json(500, {"error": {"code": "server_error", "message": "The helper hit an error"}},
                                close=True)
            except OSError:
                pass

    do_GET = _route
    do_HEAD = _route
    do_POST = _route
    do_PUT = _route
    do_DELETE = _route

    # -- handlers -----------------------------------------------------------

    def _healthz(self) -> None:
        self._send(200, b"ok\n", "text/plain; charset=utf-8")

    def _status_page(self) -> None:
        self._send(200, render_status_page(self.app).encode("utf-8"), "text/html; charset=utf-8",
                   headers={"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'",
                            "Referrer-Policy": "no-referrer"})

    def _plex_summary(self) -> dict | None:
        identity = self.app.plex.identity()
        if identity is None:
            return None
        return {"machineIdentifier": identity.machine_identifier}

    def _hello(self) -> None:
        app = self.app
        plex = self._plex_summary()
        self._send_json(200, {
            "service": SERVICE_NAME,
            "apiVersion": API_VERSION,
            "version": __version__,
            "serverId": app.store.server_id,
            "name": app.config.name,
            "pairing": {"plex": app.plex_pairing and plex is not None and app.plex.can_confirm_owner,
                        "code": app.code_pairing},
            "plex": plex,
            "tls": {"sha256": app.tls_fingerprint} if app.tls_fingerprint else None,
        })

    def _health(self) -> None:
        self._send_json(200, health_report(self.app))

    def _pair(self) -> None:
        app = self.app
        address = self.client_address[0]
        body = self._read_json()

        method = body.get("method")
        wait = app.limiter.retry_after(address, by_code=method != "plex")
        if wait:
            raise self._fail(429, "too_many_attempts", "Too many wrong tries. Wait a little and try again.",
                             headers={"Retry-After": str(wait)}, retryAfter=wait)

        device_id = body.get("deviceId")
        device_name = body.get("deviceName")
        if not isinstance(device_id, str) or not _DEVICE_ID.match(device_id):
            raise self._fail(400, "bad_request", "deviceId is missing or malformed")
        if not isinstance(device_name, str) or not device_name.strip():
            raise self._fail(400, "bad_request", "deviceName is missing")
        folder_name = body.get("folderName")
        if not isinstance(folder_name, str) or not folder_name.strip():
            folder_name = device_name
        display_name = clean_folder_name(device_name)
        folder = clean_folder_name(folder_name)

        if method == "code":
            if not app.code_pairing:
                raise self._fail(409, "pairing_method_off", "This helper does not pair with a code")
            code = body.get("code")
            if not isinstance(code, str) or not codes_match(app.pairing_code, code):
                app.limiter.record_failure(address)
                log.warning("Wrong pairing code from %s", address)
                raise self._fail(403, "code_wrong", "That pairing code is not right")
        elif method == "plex":
            if not app.plex_pairing:
                raise self._fail(409, "pairing_method_off", "This helper only pairs with its pairing code")
            token = body.get("plexToken")
            if not isinstance(token, str) or not 10 <= len(token) <= 400:
                raise self._fail(400, "bad_request", "plexToken is missing or malformed")
            self._check_plex_owner(token, address)
        else:
            raise self._fail(400, "bad_request", 'method must be "plex" or "code"')

        was_paired = any(known.id == device_id for known in app.store.devices())
        device, token = app.store.pair_device(device_id, display_name, folder, via=method)
        app.limiter.record_success(address)
        log.info('Paired "%s" (%s) from %s; its files go to "%s"', device.name, method, address, device.folder)
        if was_paired:
            # Normal for a phone that was restored or set up again. Worth a
            # line all the same: the token it had before has stopped working.
            log.warning('"%s" was already paired and has paired again from %s. Its earlier pairing no '
                        'longer works.', device.name, address)
        self._send_json(200, {
            "deviceToken": token,
            "deviceId": device.id,
            "folder": device.folder,
            "serverId": app.store.server_id,
            "name": app.config.name,
        })

    def _check_plex_owner(self, token: str, address: str) -> None:
        app = self.app
        verdict = app.plex.verify_owner(token)
        if verdict == plex_module.OWNER:
            return
        if verdict == plex_module.UNREACHABLE:
            raise self._fail(503, "plex_unreachable",
                             "The helper cannot reach Plex Media Server. Use the pairing code instead.")
        if verdict == plex_module.OPEN_ACCESS:
            raise self._fail(409, "plex_open_access",
                             "Plex lets this helper in without signing in, so it cannot confirm who owns "
                             "the server. Use the pairing code instead.")
        app.limiter.record_failure(address, by_code=False)
        if verdict == plex_module.TOKEN_REJECTED:
            log.warning("Plex rejected the token offered by %s", address)
            raise self._fail(401, "plex_token_rejected", "Plex did not accept this sign-in")
        log.warning("%s offered a Plex sign-in that does not own this server", address)
        raise self._fail(403, "plex_not_owner",
                         "This Plex account does not own the server. Ask the owner for the pairing code.")

    def _status(self) -> None:
        app = self.app
        device = self._require_device()
        free, total = app.storage.disk_usage()
        count, size = app.store.device_totals(device.id)
        self._send_json(200, {
            "serverId": app.store.server_id,
            "name": app.config.name,
            "version": __version__,
            "apiVersion": API_VERSION,
            "device": {"id": device.id, "name": device.name, "folder": device.folder,
                       "assetCount": count, "bytes": size},
            "storage": {"freeBytes": free, "totalBytes": total, "minFreeBytes": app.config.min_free_bytes,
                        "writable": app.storage.is_writable()},
            "limits": {"maxUploadBytes": app.config.max_upload_bytes, "maxCheckItems": MAX_CHECK_ITEMS},
            "plex": self._plex_summary(),
        })

    def _unpair(self) -> None:
        self._discard_body()
        device = self._require_device()
        self.app.store.remove_device(device.id)
        log.info('Unpaired "%s" at its own request', device.name)
        self._send_json(200, {"unpaired": True})

    def _check(self) -> None:
        app = self.app
        body = self._read_json()
        device = self._require_device()
        items = body.get("items")
        if not isinstance(items, list) or len(items) > MAX_CHECK_ITEMS:
            raise self._fail(400, "bad_request", f"items must be a list of at most {MAX_CHECK_ITEMS}")
        keys: list[str] = []
        hashes: dict[str, str] = {}
        for item in items:
            key = item.get("key") if isinstance(item, dict) else item
            if not isinstance(key, str) or not _ASSET_KEY.match(key):
                raise self._fail(400, "bad_request", "An item has a missing or malformed key")
            keys.append(key)
            sha = item.get("sha256") if isinstance(item, dict) else None
            if isinstance(sha, str) and _SHA256.match(sha.lower()):
                hashes[key] = sha.lower()

        known = app.store.known_keys(device.id, keys)
        # A photo another phone already sent (a shared library, say) is known
        # by its content: note it for this phone too, and skip the upload.
        for key, sha in hashes.items():
            if key in known:
                continue
            with app.place_lock:
                twin = self._stored_twin(sha)
                if twin is not None:
                    app.store.record_asset(device.id, key, sha, twin.relpath, twin.size, None, None)
                    known.add(key)
        self._send_json(200, {"known": [key for key in keys if key in known]})

    def _stored_twin(self, sha256: str):
        """A record of this exact content whose file is still on disk."""
        for asset in self.app.store.assets_with_sha(sha256):
            if self.app.storage.exists(asset.relpath):
                return asset
        return None

    # -- upload -------------------------------------------------------------

    def _refuse_upload(self, status: int, code: str, message: str, length: int | None) -> _Abort:
        """Refuse an upload whose body has not been read.

        The answer is sent at once and the connection is closed, after some of
        the body has been read and thrown away: closing with unread data makes
        the phone see a broken connection instead of the reason.
        """
        abort = self._fail(status, code, message, close=True)
        self._drain(length, stranger=status == 401)
        return abort

    def _drain(self, length: int | None, stranger: bool = False) -> None:
        budget = _STRANGER_DRAIN_BYTES if stranger else _DRAIN_BYTES
        remaining = budget if length is None else min(length, budget)
        deadline = time.monotonic() + (_STRANGER_DRAIN_SECONDS if stranger else _DRAIN_SECONDS)
        try:
            self.connection.settimeout(2)
            while remaining > 0 and time.monotonic() < deadline:
                chunk = self.rfile.read(min(remaining, 256 * 1024))
                if not chunk:
                    break
                remaining -= len(chunk)
        except (OSError, ssl.SSLError):
            pass

    def _upload(self, raw_key: str) -> None:
        app = self.app
        length = self._content_length()
        if "chunked" in (self.headers.get("Transfer-Encoding") or "").lower() or length is None:
            raise self._fail(411, "length_required", "Send a Content-Length", close=True)

        device = self._device()
        if device is None:
            raise self._refuse_upload(401, "unauthorized",
                                      "This phone is not paired with the helper. Pair it again.", length)
        key = urllib.parse.unquote(raw_key)
        if not _ASSET_KEY.match(key):
            raise self._refuse_upload(400, "bad_request", "The asset key is malformed", length)
        if length == 0:
            raise self._fail(400, "bad_request", "The upload is empty")
        if length > app.config.max_upload_bytes:
            raise self._refuse_upload(413, "too_large", "This file is larger than the helper accepts", length)

        filename = clean_filename(urllib.parse.unquote(self.headers.get("X-Phlix-Filename") or ""),
                                  fallback_stem=f"upload-{key[:12]}")
        if not is_allowed_extension(filename, app.config.extra_extensions):
            raise self._refuse_upload(415, "unsupported_type", "The helper does not store this kind of file",
                                      length)
        expected = (self.headers.get("X-Phlix-SHA256") or "").strip().lower()
        if expected and not _SHA256.match(expected):
            raise self._refuse_upload(400, "bad_request", "X-Phlix-SHA256 is malformed", length)
        created_text = (self.headers.get("X-Phlix-Created") or "").strip()[:40]
        created = parse_created(created_text)
        kind = (self.headers.get("X-Phlix-Kind") or "").strip().lower()
        kind = kind if kind in _KINDS else "other"

        if not app.reserve_space(length):
            log.warning('Refused an upload from "%s": the disk is too full', device.name)
            raise self._refuse_upload(507, "insufficient_storage", "The server's disk is too full", length)
        promised = [length]
        try:
            temp_path, sha256 = self._receive(length, promised)
        finally:
            app.release_space(promised[0])
        if expected and expected != sha256:
            _remove(temp_path)
            log.warning('An upload from "%s" arrived damaged and was discarded', device.name)
            raise self._fail(422, "checksum_mismatch", "The file was damaged on the way. Send it again.")

        try:
            with app.place_lock:
                relpath, stored, own = self._place(device, key, temp_path, filename, created, created_text,
                                                   sha256, length, kind)
        except StorageError as error:
            _remove(temp_path)
            status = 507 if error.code in ("insufficient_storage", "not_writable") else 500
            log.error('Could not store an upload from "%s": %s', device.name, error)
            raise self._fail(status, error.code, str(error)) from None

        if stored:
            log.info('Stored %s (%s) from "%s"', relpath, _human(length), device.name)
        self._send_json(201 if stored else 200, {
            "status": "stored" if stored else "duplicate",
            # Where another phone keeps the same photo is that phone's business.
            "path": relpath if own else "",
            "bytes": length,
        })

    def _receive(self, length: int, promised: list[int]) -> tuple[str, str]:
        """Read the upload into a temporary file. Returns (path, sha256).

        `promised` holds the bytes of this upload still counted against the
        disk's free space; it goes down as they are written.
        """
        app = self.app
        digest = hashlib.sha256()
        remaining = length
        try:
            temp_path = app.storage.new_temp_path()
            handle = open(temp_path, "wb")
        except OSError as error:
            log.error("Cannot write to the upload folder: %s", error)
            raise self._refuse_upload(507, "not_writable",
                                      "The helper is not allowed to write to the upload folder", length) from None
        try:
            with handle:
                while remaining > 0:
                    chunk = self.rfile.read(min(remaining, _CHUNK))
                    if not chunk:
                        raise ConnectionError("the phone stopped sending")
                    handle.write(chunk)
                    digest.update(chunk)
                    remaining -= len(chunk)
                    promised[0] -= len(chunk)
                    app.release_space(len(chunk))
                handle.flush()
                # The phone marks the photo as safely uploaded on our answer,
                # so the bytes must be on disk before we give it.
                os.fsync(handle.fileno())
        except (ConnectionError, TimeoutError, ssl.SSLError, socket.timeout):
            _remove(temp_path)
            self.close_connection = True
            raise _Abort() from None
        except OSError as error:
            _remove(temp_path)
            storage_error = storage_error_from(error)
            log.error("Could not write an upload: %s", storage_error)
            status = 507 if storage_error.code in ("insufficient_storage", "not_writable") else 500
            raise self._refuse_upload(status, storage_error.code, str(storage_error), remaining) from None
        return temp_path, digest.hexdigest()

    def _place(self, device: Device, key: str, temp_path: str, filename: str, created, created_text: str,
               sha256: str, size: int, kind: str) -> tuple[str, bool, bool]:
        """Decide where a received file belongs. Called with `place_lock` held.

        Returns the file's path, whether it was stored now, and whether the
        path is this device's own to know.
        """
        app = self.app
        # The same phone sending the same photo again: the answer to its first
        # upload was lost on the way. Keep the first copy.
        earlier = app.store.asset(device.id, key)
        if earlier is not None and app.storage.exists(earlier.relpath):
            _remove(temp_path)
            # Its record may point at a file that another phone stored.
            return earlier.relpath, False, self._stored_by(device, earlier.relpath, earlier.sha256)
        # The same content from another phone, or under another key.
        twin = self._stored_twin(sha256)
        if twin is not None:
            _remove(temp_path)
            app.store.record_asset(device.id, key, sha256, twin.relpath, size, kind, created_text or None)
            return twin.relpath, False, self._stored_by(device, twin.relpath, sha256)
        relpath, stored = app.storage.place(temp_path, device.folder, filename, created, sha256, size,
                                            app.store.sha_at_path)
        app.store.record_asset(device.id, key, sha256, relpath, size, kind, created_text or None)
        return relpath, stored, True

    def _stored_by(self, device: Device, relpath: str, sha256: str) -> bool:
        """Whether the file at `relpath` was put there by this device's own upload."""
        return self.app.store.first_device_at(relpath, sha256) == device.id


def health_report(app: App) -> dict:
    """Whether the helper can do its job, as the status page and the
    `doctor` command show it. Nothing here is secret: no code, no token, no
    device or file name."""
    config = app.config
    free, total = app.storage.disk_usage()
    writable = app.storage.is_writable()
    identity = app.plex.identity()
    files, size = app.store.totals()
    enough_space = free >= config.min_free_bytes
    return {
        "ok": writable and enough_space,
        "version": __version__,
        "uploadFolder": {"writable": writable, "freeBytes": free, "totalBytes": total,
                         "minFreeBytes": config.min_free_bytes, "enoughSpace": enough_space},
        "plex": {"found": identity is not None,
                 "version": identity.version if identity else None,
                 "asksForSignIn": app.plex.asks_for_sign_in},
        "pairing": {"plex": app.plex_pairing and app.plex.can_confirm_owner, "code": app.code_pairing},
        "tls": config.tls,
        "devices": len(app.store.devices()),
        "files": {"count": files, "bytes": size},
    }


def _remove(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


def _human(size: int) -> str:
    value = float(size)
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} bytes"
