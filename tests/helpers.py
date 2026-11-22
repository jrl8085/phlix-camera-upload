"""Shared pieces for the tests: a helper running on a spare port, and a
stand-in for Plex Media Server."""

from __future__ import annotations

import contextlib
import hashlib
import http.client
import http.server
import json
import os
import shutil
import ssl
import tempfile
import threading
import urllib.parse

from phlix_upload import config as config_module
from phlix_upload.__main__ import build_app
from phlix_upload.server import Server

OWNER_TOKEN = "owner-token-0123456789"
SHARED_TOKEN = "shared-token-0123456789"
MACHINE_ID = "0123456789abcdef0123456789abcdef01234567"


class FakePlex:
    """Answers the way a real server was seen to (November 2026): the owner
    gets 200 everywhere, a shared user 403 on owner-only paths, a bad or
    missing token 401."""

    def __init__(self, open_access: bool = False, identity_as_xml: bool = False):
        self.open_access = open_access
        self.identity_as_xml = identity_as_xml
        self.requests: list[tuple[str, str | None]] = []
        fake = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                token = self.headers.get("X-Plex-Token")
                path = urllib.parse.urlsplit(self.path).path
                fake.requests.append((path, token))
                if path == "/identity":
                    if fake.identity_as_xml:
                        body = (f'<?xml version="1.0"?><MediaContainer size="0" claimed="1" '
                                f'machineIdentifier="{MACHINE_ID}" version="1.41.2.9200"></MediaContainer>')
                        return self._answer(200, body.encode(), "text/xml")
                    body = json.dumps({"MediaContainer": {"machineIdentifier": MACHINE_ID,
                                                          "version": "1.41.2.9200"}})
                    return self._answer(200, body.encode())
                if path == "/redirect":
                    self.send_response(302)
                    self.send_header("Location", "http://127.0.0.1:9/elsewhere")
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return None
                if fake.open_access:
                    return self._answer(200, b"{}")
                if token == OWNER_TOKEN:
                    return self._answer(200, b"{}")
                if token == SHARED_TOKEN:
                    owner_only = path in ("/accounts", "/butler", "/myplex/account")
                    return self._answer(403 if owner_only else 200, b"{}")
                return self._answer(401, b"")

            def _answer(self, status, body, content_type="application/json"):
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        self.url = f"http://127.0.0.1:{self._server.server_address[1]}"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def close(self):
        self._server.shutdown()
        self._server.server_close()


class Running:
    """A helper serving on 127.0.0.1, with a client that speaks its API."""

    def __init__(self, app, server, root: str, tls: bool):
        self.app = app
        self.server = server
        self.root = root
        self.tls = tls
        self.port = server.server_address[1]
        self.upload_dir = app.config.upload_dir

    def connection(self, timeout: float = 20):
        if self.tls:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return http.client.HTTPSConnection("127.0.0.1", self.port, timeout=timeout, context=context)
        return http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)

    def request(self, method: str, path: str, body: bytes | dict | None = None,
                token: str | None = None, headers: dict[str, str] | None = None):
        """Returns (status, parsed JSON or raw bytes, response headers)."""
        all_headers = dict(headers or {})
        if isinstance(body, dict):
            body = json.dumps(body).encode()
            all_headers.setdefault("Content-Type", "application/json")
        if token:
            all_headers["Authorization"] = f"Bearer {token}"
        connection = self.connection()
        try:
            connection.request(method, path, body=body, headers=all_headers)
            response = connection.getresponse()
            raw = response.read()
            response_headers = {name.lower(): value for name, value in response.getheaders()}
        finally:
            connection.close()
        if response_headers.get("content-type", "").startswith("application/json"):
            return response.status, json.loads(raw), response_headers
        return response.status, raw, response_headers

    def pair(self, device_id: str = "device-0001", name: str = "iPhone", folder: str | None = None,
             code: str | None = None) -> str:
        body = {"method": "code", "code": code or self.app.pairing_code, "deviceId": device_id,
                "deviceName": name}
        if folder:
            body["folderName"] = folder
        status, payload, _ = self.request("POST", "/api/v1/pair", body)
        assert status == 200, (status, payload)
        return payload["deviceToken"]

    def upload(self, token: str, key: str, data: bytes, filename: str = "IMG_0001.HEIC",
               created: str | None = "2026-11-21T22:15:03-06:00", sha256: str | None = None,
               kind: str = "photo", headers: dict[str, str] | None = None):
        all_headers = {"X-Phlix-Filename": urllib.parse.quote(filename), "X-Phlix-Kind": kind,
                       "Content-Type": "application/octet-stream"}
        if created:
            all_headers["X-Phlix-Created"] = created
        all_headers["X-Phlix-SHA256"] = hashlib.sha256(data).hexdigest() if sha256 is None else sha256
        if all_headers["X-Phlix-SHA256"] == "":
            del all_headers["X-Phlix-SHA256"]
        all_headers.update(headers or {})
        return self.request("PUT", f"/api/v1/assets/{key}", data, token=token, headers=all_headers)

    def files(self) -> list[str]:
        """Every stored file, relative to the upload folder, sorted."""
        found = []
        for root, directories, names in os.walk(self.upload_dir):
            directories[:] = [name for name in directories if not name.startswith(".")]
            for name in names:
                found.append(os.path.relpath(os.path.join(root, name), self.upload_dir))
        return sorted(found)


@contextlib.contextmanager
def running(tls: bool = False, **environment):
    """Start a helper in a temporary folder; stop and delete it afterwards."""
    root = tempfile.mkdtemp(prefix="phlix-upload-test-")
    env = {
        "UPLOAD_DIR": os.path.join(root, "photos"),
        "CONFIG_DIR": os.path.join(root, "config"),
        "PORT": "7459",
        "TLS": "on" if tls else "off",
        "MIN_FREE_GB": "0",
        # Nothing answers here, so a test that says nothing about Plex gets a
        # helper that has not found one (and does not go looking on the host).
        "PLEX_URL": "http://127.0.0.1:9",
    }
    env.update({name: str(value) for name, value in environment.items()})
    config = config_module.load(env)
    app, context = build_app(config)
    server = Server(("127.0.0.1", 0), app, ssl_context=context)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    try:
        yield Running(app, server, root, tls)
    finally:
        server.shutdown()
        server.server_close()
        app.store.close()
        shutil.rmtree(root, ignore_errors=True)


def key(number: int) -> str:
    """A well-formed asset key."""
    return hashlib.sha256(f"asset-{number}".encode()).hexdigest()[:32]
