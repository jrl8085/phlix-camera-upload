"""The helper's link to the Plex Media Server it sits next to.

Two questions are asked of Plex, and nothing else:

1. "Which server are you?" (`/identity`, which needs no sign-in), so the app
   can tell that this helper belongs to the server it is connected to.
2. "Does this token belong to your owner?", when a phone pairs without a
   pairing code.

The helper never stores a Plex token. The one a phone sends when it pairs is
a short-lived one Plex issued for the purpose; it is used for the check and
then forgotten.
"""

from __future__ import annotations

import json
import logging
import re
import ssl
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from . import __version__

log = logging.getLogger("phlix.plex")

#: Seen on the owner's requests only. A user the server is merely shared with
#: is answered 403 here, although Plex lets them read `/:/prefs` (checked
#: against a real server, November 2026).
OWNER_ONLY_PATHS = ("/accounts", "/butler")

OWNER = "owner"
NOT_OWNER = "not_owner"
TOKEN_REJECTED = "token_rejected"
OPEN_ACCESS = "open_access"
UNREACHABLE = "unreachable"

_TIMEOUT = 4.0
_FOUND_TTL = 300.0
_MISSING_TTL = 30.0


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect could carry the token to another host, so none is followed."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        return None


def _opener() -> urllib.request.OpenerDirector:
    # Plex's own certificate is issued for a plex.direct name, never for the
    # address used here, so it cannot be checked by name. This hop stays on
    # the server's own machine or home network.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=context),
        _NoRedirects(),
    )


def _default_gateway() -> str | None:
    """The Docker host as seen from a container on the default bridge."""
    try:
        with open("/proc/net/route", encoding="ascii") as handle:
            for line in handle.readlines()[1:]:
                fields = line.split()
                if len(fields) >= 3 and fields[1] == "00000000":
                    raw = int(fields[2], 16)
                    return ".".join(str((raw >> shift) & 0xFF) for shift in (0, 8, 16, 24))
    except (OSError, ValueError):
        pass
    return None


def default_candidates() -> list[str]:
    """Where Plex usually is when nobody said: the Docker host, or a container named plex."""
    hosts = ["host.docker.internal"]
    gateway = _default_gateway()
    if gateway:
        hosts.append(gateway)
    hosts += ["127.0.0.1", "plex"]
    return [f"http://{host}:32400" for host in hosts]


def _other_scheme(url: str) -> str:
    if url.startswith("https://"):
        return "http://" + url[len("https://"):]
    return re.sub(r"^http://", "https://", url)


def _with_other_scheme(urls: list[str]) -> list[str]:
    """Each address as written, then the same one over the other of http and https."""
    result: list[str] = []
    for url in urls:
        for candidate in (url, _other_scheme(url)):
            if candidate not in result:
                result.append(candidate)
    return result


@dataclass(frozen=True)
class PlexIdentity:
    base_url: str
    machine_identifier: str
    version: str


def parse_identity(body: bytes) -> tuple[str, str] | None:
    """(machineIdentifier, version) from `/identity`, in JSON or XML."""
    text = body.decode("utf-8", "replace")
    try:
        container = json.loads(text).get("MediaContainer", {})
        machine = container.get("machineIdentifier")
        if isinstance(machine, str) and machine:
            return machine, str(container.get("version", ""))
    except (ValueError, AttributeError):
        pass
    # Older servers answer in XML whatever is asked for. Only the
    # MediaContainer tag is read: the XML declaration has a version of its own.
    tag = re.search(r"<MediaContainer\b([^>]*)>", text)
    if tag:
        machine_match = re.search(r'\bmachineIdentifier="([^"]+)"', tag.group(1))
        if machine_match:
            version_match = re.search(r'\bversion="([^"]*)"', tag.group(1))
            return machine_match.group(1), version_match.group(1) if version_match else ""
    return None


class PlexLink:
    """Finds the Plex server and answers the two questions above."""

    def __init__(self, configured_urls: tuple[str, ...] = (), server_id: str = ""):
        self._configured = list(configured_urls)
        self._server_id = server_id
        self._opener = _opener()
        self._lock = threading.Lock()
        self._identity: PlexIdentity | None = None
        self._asks_for_sign_in: bool | None = None
        self._checked_at = 0.0
        self._refreshing = False

    # -- http ---------------------------------------------------------------

    def _get(self, base_url: str, path: str, token: str | None) -> tuple[int, bytes]:
        """(status, body). Status 0 means the server did not answer."""
        request = urllib.request.Request(base_url + path, method="GET")
        request.add_header("Accept", "application/json")
        request.add_header("X-Plex-Product", "Phlix Camera Upload")
        request.add_header("X-Plex-Version", __version__)
        if self._server_id:
            request.add_header("X-Plex-Client-Identifier", self._server_id)
        if token is not None:
            request.add_header("X-Plex-Token", token)
        try:
            with self._opener.open(request, timeout=_TIMEOUT) as response:
                return response.status, response.read(1024 * 1024)
        except urllib.error.HTTPError as error:
            status = error.code
            error.close()
            return status, b""
        except (urllib.error.URLError, OSError, ValueError):
            return 0, b""

    # -- which server -------------------------------------------------------

    def candidates(self) -> list[str]:
        """Where to look for Plex, in order.

        An address from PLEX_URL is tried as it was written, then the other
        way. Addresses the helper thinks of by itself are tried over https
        first: a phone's Plex sign-in is shown to this server when the phone
        pairs, and should not cross a network in the clear when it need not.
        The certificate is not checked either way (Plex's is made out to a
        plex.direct name, not to an address), so https here keeps the
        sign-in from being read on the way, and no more than that.
        """
        if self._configured:
            return _with_other_scheme(self._configured)
        return _with_other_scheme([_other_scheme(url) for url in default_candidates()])

    def _probe(self) -> PlexIdentity | None:
        for base_url in self.candidates():
            status, body = self._get(base_url, "/identity", None)
            if status != 200:
                continue
            parsed = parse_identity(body)
            if parsed:
                return PlexIdentity(base_url=base_url, machine_identifier=parsed[0], version=parsed[1])
        return None

    def identity(self, wait: bool = False) -> PlexIdentity | None:
        """The Plex server found, or None.

        The answer is cached. A stale one is refreshed in the background so
        that `/api/v1/hello` never waits on Plex; pass `wait=True` where the
        fresh answer matters more than the delay (pairing).
        """
        with self._lock:
            age = time.monotonic() - self._checked_at
            fresh = self._checked_at > 0 and age < (_FOUND_TTL if self._identity else _MISSING_TTL)
            if fresh:
                return self._identity
            if not wait:
                if not self._refreshing:
                    self._refreshing = True
                    threading.Thread(target=self._refresh, name="plex-refresh", daemon=True).start()
                return self._identity
        return self._refresh()

    def _refresh(self) -> PlexIdentity | None:
        found = self._probe()
        asks = None
        if found:
            status, _ = self._get(found.base_url, OWNER_ONLY_PATHS[0], None)
            asks = True if status == 401 else False if status == 200 else None
        with self._lock:
            previous = self._identity
            self._identity = found
            self._asks_for_sign_in = asks
            self._checked_at = time.monotonic()
            self._refreshing = False
        if found and (previous is None or previous.base_url != found.base_url):
            log.info("Found Plex Media Server %s at %s", found.version or "", found.base_url)
        elif previous and not found:
            log.warning("Plex Media Server at %s no longer answers", previous.base_url)
        return found

    @property
    def asks_for_sign_in(self) -> bool | None:
        """Whether Plex refuses this helper's requests when they carry no token.

        False means Plex is set to trust this address ("List of IP addresses
        and networks that are allowed without auth"), so it cannot tell the
        owner from anyone else and pairing through Plex is not offered. None
        means not known yet.
        """
        with self._lock:
            return self._asks_for_sign_in

    @property
    def can_confirm_owner(self) -> bool:
        """Whether a phone can pair by Plex ownership right now."""
        with self._lock:
            return self._identity is not None and self._asks_for_sign_in is not False

    # -- is this the owner --------------------------------------------------

    def verify_owner(self, token: str) -> str:
        """Whether `token` belongs to the owner of the Plex server found.

        Returns one of OWNER, NOT_OWNER, TOKEN_REJECTED, OPEN_ACCESS or
        UNREACHABLE.
        """
        identity = self.identity(wait=True)
        if identity is None:
            return UNREACHABLE
        base_url = identity.base_url

        # Control: without a token the same request must be refused. A server
        # set to trust this address ("List of IP addresses and networks that
        # are allowed without auth") answers 200 to anybody, and then a 200
        # proves nothing about the token.
        control, _ = self._get(base_url, OWNER_ONLY_PATHS[0], None)
        if control == 0:
            return UNREACHABLE
        if control == 200:
            log.warning(
                "Plex answers %s without a token for this address, so it cannot confirm who owns "
                "the server. Pair with the pairing code instead.", OWNER_ONLY_PATHS[0],
            )
            return OPEN_ACCESS

        statuses = [self._get(base_url, path, token)[0] for path in OWNER_ONLY_PATHS]
        if statuses[0] == 0:
            return UNREACHABLE
        if statuses[0] == 401:
            return TOKEN_REJECTED
        if statuses[0] != 200 or any(status in (401, 403) for status in statuses[1:]):
            return NOT_OWNER
        return OWNER
