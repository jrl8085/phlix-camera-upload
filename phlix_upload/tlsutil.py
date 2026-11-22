"""The helper's TLS certificate.

Photos and the pairing token travel over the home network encrypted. A home
server has no public name a certificate authority could vouch for, so the
helper makes its own certificate on first start and the app remembers its
fingerprint when it pairs. From then on the app only talks to a server that
shows that exact certificate.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import ssl
import subprocess

log = logging.getLogger("phlix.tls")


class TLSError(Exception):
    """The certificate could not be made or loaded."""


def ensure_certificate(tls_dir: str, name: str = "Phlix Camera Upload") -> tuple[str, str]:
    """Paths of the certificate and key in `tls_dir`, creating them once."""
    cert_path = os.path.join(tls_dir, "cert.pem")
    key_path = os.path.join(tls_dir, "key.pem")
    if os.path.isfile(cert_path) and os.path.isfile(key_path):
        return cert_path, key_path

    os.makedirs(tls_dir, mode=0o700, exist_ok=True)
    # Written under temporary names and renamed, so a start interrupted here
    # never leaves a certificate without its key.
    new_cert, new_key = cert_path + ".new", key_path + ".new"
    command = [
        "openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1",
        "-sha256", "-nodes", "-days", "7300",
        "-subj", f"/CN={_subject(name)}",
        "-keyout", new_key, "-out", new_cert,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    except FileNotFoundError:
        raise TLSError("openssl is not installed, so no certificate can be made. Set TLS=off or "
                       "give TLS_CERT and TLS_KEY.") from None
    except subprocess.TimeoutExpired:
        raise TLSError("openssl took too long to make a certificate") from None
    if result.returncode != 0 or not os.path.isfile(new_cert) or not os.path.isfile(new_key):
        raise TLSError(f"openssl could not make a certificate: {result.stderr.strip()[:300]}")
    os.chmod(new_key, 0o600)
    os.replace(new_key, key_path)
    os.replace(new_cert, cert_path)
    log.info("Made a new TLS certificate in %s", tls_dir)
    return cert_path, key_path


def _subject(name: str) -> str:
    cleaned = "".join(ch for ch in name if ch.isalnum() or ch in " -_.").strip()
    return cleaned[:60] or "Phlix Camera Upload"


def fingerprint(cert_path: str) -> str:
    """SHA-256 of the certificate as the app sees it (the DER bytes), in hex."""
    with open(cert_path, encoding="ascii") as handle:
        pem = handle.read()
    begin, end = "-----BEGIN CERTIFICATE-----", "-----END CERTIFICATE-----"
    start = pem.find(begin)
    stop = pem.find(end, start)
    if start < 0 or stop < 0:
        raise TLSError(f"{cert_path} holds no certificate")
    der = base64.b64decode("".join(pem[start + len(begin):stop].split()))
    return hashlib.sha256(der).hexdigest()


def server_context(cert_path: str, key_path: str) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    try:
        context.load_cert_chain(cert_path, key_path)
    except (ssl.SSLError, OSError) as error:
        raise TLSError(f"The certificate in {cert_path} could not be loaded: {error}") from error
    # The server only speaks HTTP/1.1.
    context.set_alpn_protocols(["http/1.1"])
    return context
