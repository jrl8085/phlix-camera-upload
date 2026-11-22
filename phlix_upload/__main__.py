"""Start the helper, or run one of its small admin commands.

    python -m phlix_upload                 run the server (what the container does)
    python -m phlix_upload doctor          check the install and say how to fix what is wrong
    python -m phlix_upload code            print the pairing code
    python -m phlix_upload new-code        replace the pairing code
    python -m phlix_upload devices         list paired devices
    python -m phlix_upload unpair NAME     forget a device (by folder, name or id)
    python -m phlix_upload version

In Docker, run a command with for example
`docker exec phlix-camera-upload python -m phlix_upload code`.
"""

from __future__ import annotations

import datetime as _dt
import json
import logging
import os
import signal
import socket
import sqlite3
import ssl
import sys
import threading
import urllib.error
import urllib.request

from . import __version__
from . import config as config_module
from .pairing import AttemptLimiter, new_code
from .plex import PlexLink
from .server import App, Server
from .storage import Storage
from .store import Store
from .tlsutil import TLSError, ensure_certificate, fingerprint, server_context

log = logging.getLogger("phlix")


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)-7s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )


def _chown_tree(path: str, uid: int, gid: int) -> None:
    for root, directories, files in os.walk(path):
        for name in [root] + [os.path.join(root, entry) for entry in directories + files]:
            try:
                os.chown(name, uid, gid, follow_symlinks=False)
            except OSError:
                pass


def drop_privileges(config: config_module.Config) -> None:
    """Stop being root, so uploaded files belong to a normal user.

    PUID and PGID say which user. Without them the helper becomes whoever owns
    the upload folder, which is nearly always the right answer: the files it
    writes then look like the ones already there.
    """
    if os.name != "posix" or os.geteuid() != 0:
        return
    uid, gid = config.puid, config.pgid
    if uid is None or gid is None:
        try:
            owner = os.stat(config.upload_dir)
        except OSError:
            owner = None
        if uid is None:
            uid = owner.st_uid if owner else 0
        if gid is None:
            gid = owner.st_gid if owner else 0
    if uid == 0:
        log.warning("Running as root, so uploaded files will belong to root. Set PUID and PGID to the "
                    "user that owns your photo folders.")
        return
    os.makedirs(config.config_dir, exist_ok=True)
    _chown_tree(config.config_dir, uid, gid)
    try:
        os.setgroups([])
        os.setgid(gid)
        os.setuid(uid)
    except OSError as error:
        log.warning("Could not switch to user %s:%s (%s). Staying root.", uid, gid, error)
        return
    log.info("Running as user %s, group %s", uid, gid)


def unmounted_folders(config: config_module.Config, environ=None) -> list[str]:
    """Folders that should be volumes but are not, when running in the image.

    A container started without `-v ...:/photos` would accept every upload and
    lose them all when it is next recreated; without `/config` every phone
    would have to pair again after each update. Better not to start. The
    image sets PHLIX_CONTAINER=1; ALLOW_UNMOUNTED=1 switches the check off.
    """
    env = os.environ if environ is None else environ
    if env.get("PHLIX_CONTAINER") != "1" or env.get("ALLOW_UNMOUNTED") == "1":
        return []
    return [path for path in (config.upload_dir, config.config_dir) if not os.path.ismount(path)]


def resolve_pairing_code(config: config_module.Config, store: Store) -> str:
    """The code in force: the owner's own, else the one made on first start."""
    if config.pairing_code:
        return config.pairing_code
    code = store.get_meta("pairing_code")
    if not code:
        code = new_code()
        store.set_meta("pairing_code", code)
    return code


def _local_addresses() -> list[str]:
    """This machine's addresses, for the banner. Best effort."""
    found: list[str] = []
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # No packet is sent: connecting a UDP socket only picks a route.
            probe.connect(("192.0.2.1", 9))
            found.append(probe.getsockname()[0])
        finally:
            probe.close()
    except OSError:
        pass
    return found


def build_app(config: config_module.Config) -> tuple[App, object | None]:
    """Assemble the server's parts. Returns the app and its TLS context."""
    os.makedirs(config.config_dir, exist_ok=True)
    store = Store(config.database_path)
    storage = Storage(config.upload_dir, config.temp_dir, config.path_template)
    try:
        os.makedirs(config.upload_dir, exist_ok=True)
        storage.prepare()
    except OSError as error:
        log.error("Cannot use the upload folder %s: %s", config.upload_dir, error)

    context = None
    cert_fingerprint = None
    if config.tls:
        if config.tls_cert:
            cert_path, key_path = config.tls_cert, config.tls_key
        else:
            cert_path, key_path = ensure_certificate(config.tls_dir, config.name)
        context = server_context(cert_path, key_path)
        cert_fingerprint = fingerprint(cert_path)

    plex = PlexLink(config.plex_urls, server_id=store.server_id)
    app = App(config, store, storage, plex, resolve_pairing_code(config, store),
              tls_fingerprint=cert_fingerprint, limiter=AttemptLimiter())
    return app, context


def _banner(app: App) -> None:
    config = app.config
    scheme = "https" if config.tls else "http"
    free, _ = app.storage.disk_usage()
    log.info("Phlix Camera Upload %s", __version__)
    log.info("Upload folder: %s (%s, %.1f GB free)", config.upload_dir,
             "ready" if app.storage.is_writable() else "NOT WRITABLE", free / 1024 ** 3)
    for address in _local_addresses():
        log.info("Listening on %s://%s:%s (inside a container this is the container's own address)",
                 scheme, address, config.port)
    if not config.tls:
        log.warning("TLS is off: photos travel unencrypted unless a reverse proxy adds HTTPS.")
    if app.code_pairing:
        log.info("Pairing code: %s", app.pairing_code)
    if app.plex_pairing:
        log.info("The owner of the Plex server can pair from Phlix without the code.")


def serve() -> int:
    try:
        config = config_module.load()
    except config_module.ConfigError as error:
        print(f"Phlix Camera Upload cannot start: {error}", file=sys.stderr)
        return 2
    _setup_logging(config.log_level)
    missing = unmounted_folders(config)
    if missing:
        for path in missing:
            log.error("Nothing is mounted at %s.", path)
        log.error("Start the container with your photo folder at %s and a folder for the helper's own data "
                  "at %s, for example:  -v /path/to/photos/Camera\\ Uploads:%s  -v /path/to/appdata:%s",
                  config.upload_dir, config.config_dir, config.upload_dir, config.config_dir)
        return 1
    drop_privileges(config)
    os.umask(config.umask)
    try:
        app, context = build_app(config)
    except sqlite3.Error as error:
        # Nearly always: the user the helper runs as may not write there.
        log.error("Phlix Camera Upload cannot start: it cannot use its own data folder %s (%s). "
                  "The helper runs as user %s, group %s, and that user must be able to write to the "
                  "folder. Change the folder's owner, or set PUID and PGID. On a system with SELinux, "
                  "the folder also needs the label for containers: see Troubleshooting in the README.",
                  config.config_dir, error, os.geteuid(), os.getegid())
        return 1
    except (TLSError, OSError) as error:
        log.error("Phlix Camera Upload cannot start: %s", error)
        return 1

    try:
        server = Server((config.bind, config.port), app, ssl_context=context)
    except OSError as error:
        log.error("Cannot listen on port %s: %s", config.port, error)
        return 1
    _banner(app)

    def find_plex() -> None:
        if app.plex.identity(wait=True) is None and app.plex_pairing:
            places = ", ".join(app.plex.candidates()[:4])
            if app.code_pairing:
                log.warning("No Plex Media Server found at %s. Phones can still pair with the pairing code. "
                            "To pair without it, set PLEX_URL to your server's address.", places)
            else:
                log.warning("No Plex Media Server found at %s. With PAIRING=plex no phone can pair until "
                            "it is found: set PLEX_URL to your server's address.", places)

    threading.Thread(target=find_plex, name="plex-find", daemon=True).start()

    def stop(signum, frame):  # noqa: ARG001 - signal handler signature
        log.info("Stopping")
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        server.server_close()
        app.store.close()
    return 0


def _ask_running_helper(config: config_module.Config) -> dict | None:
    """The running helper's own health report, or None if it does not answer."""
    scheme = "https" if config.tls else "http"
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    # Its own certificate, asked for over the loopback address.
    context.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                         urllib.request.HTTPSHandler(context=context))
    # The helper answers on every address unless BIND names one.
    host = "127.0.0.1" if config.bind in ("", "0.0.0.0") else config.bind
    try:
        with opener.open(f"{scheme}://{host}:{config.port}/api/v1/health", timeout=5) as response:
            return json.loads(response.read(64 * 1024))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _gb(size: int) -> str:
    return f"{size / 1024 ** 3:.1f} GB"


def _size(size: int) -> str:
    value = float(size)
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} bytes"


def doctor(config: config_module.Config, out=None) -> int:
    """Check the install and print, for each problem, how to fix it.

    Returns 0 when nothing needs fixing. Run it in the container with
    `docker exec phlix-camera-upload python -m phlix_upload doctor`.
    """
    out = out or sys.stdout
    problems = 0

    def ok(text: str) -> None:
        print(f"OK       {text}", file=out)

    def note(text: str) -> None:
        print(f"NOTE     {text}", file=out)

    def problem(text: str, fix: str) -> None:
        nonlocal problems
        problems += 1
        print(f"PROBLEM  {text}\n         Fix: {fix}", file=out)

    print(f"Phlix Camera Upload {__version__}", file=out)

    for path in unmounted_folders(config):
        problem(f"Nothing is mounted at {path}.",
                f"Add a volume for {path} to the Compose file, then run: docker compose up -d")

    report = _ask_running_helper(config)
    if report is None:
        problem(f"The helper is not answering on port {config.port}.",
                "Start it with: docker compose up -d   If it stops again, read why with: "
                "docker logs phlix-camera-upload")
    else:
        ok(f"The helper is running on port {config.port}" + ("" if config.tls else " (TLS is off)"))
        folder = report.get("uploadFolder", {})
        try:
            owner = os.stat(config.upload_dir)
            owner_text = f" It belongs to user {owner.st_uid}, group {owner.st_gid}."
        except OSError:
            owner_text = ""
        if folder.get("writable"):
            ok(f"The upload folder {config.upload_dir} can be written to.")
        else:
            problem(f"The helper cannot write to the upload folder {config.upload_dir}.{owner_text}",
                    "Set PUID and PGID in the Compose file to the user and group that own your photo "
                    "folders (the command `ls -ldn` on the folder shows them), then run: docker compose up -d")
        free, minimum = int(folder.get("freeBytes", 0)), int(folder.get("minFreeBytes", 0))
        if folder.get("enoughSpace"):
            ok(f"{_gb(free)} free on the upload disk.")
        else:
            problem(f"Only {_gb(free)} free on the upload disk; uploads pause below {_gb(minimum)}.",
                    "Free some space, or lower MIN_FREE_GB in the Compose file.")
        plex = report.get("plex", {})
        if config.pairing == "code":
            note("This helper is set to pair with the pairing code only (PAIRING=code).")
        elif not plex.get("found") and config.pairing == "plex":
            problem("No Plex Media Server found, and this helper pairs through Plex only (PAIRING=plex), "
                    "so no phone can pair.",
                    "Set PLEX_URL to your server's address, for example PLEX_URL=http://192.168.1.10:32400, "
                    "or set PAIRING to auto.")
        elif not plex.get("found"):
            note("No Plex Media Server found. Phones pair with the pairing code. To let the server's "
                 "owner pair without it, set PLEX_URL, for example PLEX_URL=http://192.168.1.10:32400")
        elif plex.get("asksForSignIn") is False:
            note("Plex lets this helper in without signing in, so it cannot confirm who owns the "
                 "server. Phones pair with the pairing code.")
        else:
            ok("Plex Media Server found: its owner can pair from Phlix without a code.")
        if _helper_runs_as_root():
            note("The helper runs as root, because root owns the upload folder, so the files it stores "
                 "belong to root. On Docker Desktop for Mac or Windows that is normal. Anywhere else, set "
                 "PUID and PGID in the Compose file to the user and group that own your photo folders, "
                 "then run: docker compose up -d")
        files = report.get("files", {})
        ok(f"{report.get('devices', 0)} paired, {files.get('count', 0)} files stored "
           f"({_size(int(files.get('bytes', 0)))}).")
        if not config.tls:
            note("TLS is off. Phlix only connects over HTTPS, so a reverse proxy must add it.")

    if config.pairing in ("auto", "code"):
        note("Pairing code: run `python -m phlix_upload code` the same way to see it.")
    print("Nothing needs fixing." if problems == 0 else f"{problems} to fix.", file=out)
    return 0 if problems == 0 else 1


def _helper_runs_as_root(proc: str = "/proc") -> bool:
    """Whether the helper serving in this container is root.

    `doctor` is a second process, started by `docker exec`, and is always
    root itself. In the image the helper is process 1, and Linux says who a
    process runs as in its status file. Anywhere this cannot be read, the
    answer is no.
    """
    try:
        with open(os.path.join(proc, "1", "cmdline"), "rb") as handle:
            if b"phlix_upload" not in handle.read():
                return False
        with open(os.path.join(proc, "1", "status"), encoding="ascii", errors="replace") as handle:
            for line in handle:
                if line.startswith("Uid:"):
                    # Real, effective, saved and file-system user ids.
                    return line.split()[2] == "0"
    except (OSError, IndexError):
        pass
    return False


def _admin_store() -> tuple[config_module.Config, Store]:
    config = config_module.load()
    if not os.path.exists(config.database_path):
        print(f"No helper data in {config.config_dir} yet. Start the helper once first.", file=sys.stderr)
        raise SystemExit(1)
    return config, Store(config.database_path)


def _when(timestamp: int | None) -> str:
    if not timestamp:
        return "never"
    return _dt.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    command = arguments[0] if arguments else "serve"

    if command == "serve":
        return serve()
    if command in ("version", "--version", "-V"):
        print(__version__)
        return 0
    if command in ("help", "--help", "-h"):
        print(__doc__)
        return 0
    if command == "doctor":
        try:
            return doctor(config_module.load())
        except config_module.ConfigError as error:
            print(f"PROBLEM  A setting is wrong: {error}\n         Fix: correct it in the Compose file, "
                  "then run: docker compose up -d", file=sys.stderr)
            return 2
    try:
        config, store = _admin_store()
    except config_module.ConfigError as error:
        print(f"Phlix Camera Upload: {error}", file=sys.stderr)
        return 2
    try:
        return _admin(command, arguments, config, store)
    finally:
        store.close()


def _admin(command: str, arguments: list[str], config: config_module.Config, store: Store) -> int:
    if command == "code":
        print(resolve_pairing_code(config, store))
        return 0
    if command == "new-code":
        if config.pairing_code:
            print("The pairing code is set with PAIRING_CODE. Change it there.", file=sys.stderr)
            return 1
        code = new_code()
        store.set_meta("pairing_code", code)
        print(f"{code}\nRestart the helper to use it. Phones already paired stay paired.")
        return 0
    if command == "devices":
        devices = store.devices(include_unpaired=True)
        if not any(device.paired for device in devices):
            print("No devices are paired.")
        for device in devices:
            count, _ = store.device_totals(device.id)
            state = f"paired {_when(device.paired_at)} by {device.paired_via}" if device.paired else "unpaired"
            print(f'{device.folder}\t{count} files\t{state}'
                  f'\tlast seen {_when(device.last_seen)}\tid {device.id}')
        return 0
    if command == "unpair":
        if len(arguments) < 2:
            print("Say which device: its folder, name or id (see the devices command).", file=sys.stderr)
            return 2
        wanted = " ".join(arguments[1:]).casefold()
        matches = [device for device in store.devices()
                   if wanted in (device.id.casefold(), device.folder.casefold(), device.name.casefold())]
        if len(matches) != 1:
            print("No device matches that." if not matches else "More than one device matches. Use its id.",
                  file=sys.stderr)
            return 1
        store.remove_device(matches[0].id)
        print(f'Unpaired "{matches[0].folder}". Its files are untouched.')
        return 0

    print(f"Unknown command {command!r}. Try: python -m phlix_upload help", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
