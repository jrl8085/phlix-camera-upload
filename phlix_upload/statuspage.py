"""The page a person sees when they open the helper in a browser.

It answers "is it running, and can it do its job?" and nothing more: no
pairing code, no device names, no file names. Anyone on the home network can
open this page, so it shows nothing they could use.
"""

from __future__ import annotations

import html

from . import __version__
from .storage import GONE, GONE_MESSAGE


def _human(size: int) -> str:
    value = float(size)
    for unit in ("bytes", "KB", "MB", "GB", "TB", "PB"):
        if value < 1024 or unit == "PB":
            return f"{value:.0f} {unit}" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} bytes"


def _row(label: str, value: str, state: str = "") -> str:
    mark = {"ok": "ok", "bad": "bad", "warn": "warn"}.get(state, "")
    return (f'<tr><th scope="row">{html.escape(label)}</th>'
            f'<td class="{mark}">{html.escape(value)}</td></tr>')


def _plex_row(app, identity) -> str:
    if identity is None and not app.code_pairing:
        return _row("Plex Media Server", "Not found. This helper pairs through Plex only, so no phone can "
                    "pair until it is: set PLEX_URL.", "bad")
    if identity is None:
        return _row("Plex Media Server", "Not found. Pairing needs the pairing code; set PLEX_URL to pair "
                    "without it.", "warn")
    if app.plex.asks_for_sign_in is False:
        return _row("Plex Media Server", "Found, but it lets this helper in without signing in, so it cannot "
                    "confirm who owns the server. Pairing needs the pairing code.", "warn")
    return _row("Plex Media Server", f"Found (version {identity.version})" if identity.version else "Found", "ok")


def _upload_folder_row(trouble: str | None) -> str:
    if trouble is None:
        return _row("Upload folder", "Ready", "ok")
    if trouble == GONE:
        # Permissions are not the matter, so the page does not send anyone to them.
        return _row("Upload folder", GONE_MESSAGE, "bad")
    return _row("Upload folder", "The helper cannot write here. Check the folder's permissions, or set PUID "
                "and PGID.", "bad")


def render_status_page(app) -> str:
    config = app.config
    free, total = app.storage.disk_usage()
    trouble = app.storage.write_trouble()
    low = free < config.min_free_bytes
    identity = app.plex.identity()
    devices = len(app.store.devices())
    files, size = app.store.totals()

    rows = [
        _row("Helper", f"Running, version {__version__}", "ok"),
        _upload_folder_row(trouble),
        _row("Free space", f"{_human(free)} of {_human(total)}" + (" (too little: uploads are paused)" if low else ""),
             "bad" if low else "ok"),
        _plex_row(app, identity),
        _row("Paired devices", str(devices)),
        _row("Files stored", f"{files:,} ({_human(size)})"),
    ]
    if config.pairing in ("auto", "code"):
        pairing = ("To pair a phone that does not own the Plex server, type the pairing code into Phlix. "
                   "The code is printed in this container's log each time it starts.")
    else:
        pairing = "This helper pairs only with the owner of the Plex server."

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{html.escape(config.name)}</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin: 0; padding: 32px 20px; background: #0f0f10; color: #f2f2f3;
         font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  main {{ max-width: 640px; margin: 0 auto; }}
  h1 {{ font-size: 24px; margin: 0 0 4px; }}
  p {{ color: #a9a9b2; margin: 0 0 24px; }}
  table {{ width: 100%; border-collapse: collapse; background: #1a1a1d; border-radius: 12px; overflow: hidden; }}
  th, td {{ text-align: left; padding: 12px 16px; border-bottom: 1px solid #2a2a2f; vertical-align: top; }}
  tr:last-child th, tr:last-child td {{ border-bottom: 0; }}
  th {{ font-weight: 500; color: #a9a9b2; width: 38%; }}
  td.ok::before {{ content: "\\2713  "; color: #5fd08a; }}
  td.bad {{ color: #ff8a80; }}
  td.bad::before {{ content: "\\2717  "; }}
  td.warn {{ color: #e5a00d; }}
  .next {{ margin-top: 24px; }}
  a {{ color: #e5a00d; }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(config.name)}</h1>
  <p>Receives photos and videos from the Phlix app and puts them where Plex can find them.</p>
  <table>
    {"".join(rows)}
  </table>
  <p class="next">Open Phlix on your iPhone or iPad while it is on this network, then go to
  Settings &rsaquo; Camera Upload. {html.escape(pairing)}
  Setup guide: <a href="https://phlixapp.com/camera-upload/" rel="noreferrer">phlixapp.com/camera-upload</a></p>
</main>
</body>
</html>
"""
