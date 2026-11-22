"""Settings, read once from environment variables.

Every setting has a default that suits the documented Docker setup, so a
container started with nothing but its two volumes works.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from . import DEFAULT_PORT

#: Folder layout under the upload folder. `{device}` is the folder name the
#: phone chose when it paired; the date parts come from each photo's own date.
DEFAULT_PATH_TEMPLATE = "{device}/{year}/{year}-{month}"

_TEMPLATE_TOKENS = ("device", "year", "month", "day")
_GIB = 1024 ** 3


class ConfigError(ValueError):
    """A setting has a value the helper cannot use."""


@dataclass(frozen=True)
class Config:
    port: int = DEFAULT_PORT
    bind: str = "0.0.0.0"
    upload_dir: str = "/photos"
    config_dir: str = "/config"
    name: str = "Phlix Camera Upload"
    #: Plex addresses to try, in order. Empty means "work it out".
    plex_urls: tuple[str, ...] = ()
    #: `auto` offers both ways to pair; `code` or `plex` offers only that one.
    pairing: str = "auto"
    #: A pairing code chosen by the owner. Empty means the helper makes one.
    pairing_code: str = ""
    path_template: str = DEFAULT_PATH_TEMPLATE
    min_free_bytes: int = 2 * _GIB
    max_upload_bytes: int = 50 * _GIB
    tls: bool = True
    tls_cert: str = ""
    tls_key: str = ""
    puid: int | None = None
    pgid: int | None = None
    umask: int = 0o022
    extra_extensions: frozenset[str] = field(default_factory=frozenset)
    log_level: str = "INFO"

    @property
    def database_path(self) -> str:
        return os.path.join(self.config_dir, "phlix-camera-upload.db")

    @property
    def tls_dir(self) -> str:
        return os.path.join(self.config_dir, "tls")

    @property
    def temp_dir(self) -> str:
        # Inside the upload folder so that moving a finished file into place
        # is a rename on one filesystem. The leading dot hides it from Plex.
        return os.path.join(self.upload_dir, ".phlix-upload-tmp")


def _flag(value: str, name: str) -> bool:
    lowered = value.strip().lower()
    if lowered in ("1", "true", "yes", "on"):
        return True
    if lowered in ("0", "false", "no", "off"):
        return False
    raise ConfigError(f"{name} must be on or off, not {value!r}")


def _number(value: str, name: str, minimum: float, maximum: float) -> float:
    try:
        number = float(value)
    except ValueError:
        raise ConfigError(f"{name} must be a number, not {value!r}") from None
    if not minimum <= number <= maximum:
        raise ConfigError(f"{name} must be between {minimum:g} and {maximum:g}, not {value!r}")
    return number


def _optional_id(value: str, name: str) -> int | None:
    if not value.strip():
        return None
    return int(_number(value, name, 0, 2 ** 31 - 1))


def validate_path_template(template: str) -> str:
    """Return the template with its slashes tidied, or raise ConfigError."""
    cleaned = "/".join(part.strip() for part in template.replace("\\", "/").split("/") if part.strip())
    for part in cleaned.split("/") if cleaned else []:
        if part in (".", "..") or part.startswith("."):
            raise ConfigError("PATH_TEMPLATE folders must not be '.', '..' or start with a dot")
    for token in re.findall(r"\{([^{}]*)\}", cleaned):
        if token not in _TEMPLATE_TOKENS:
            allowed = ", ".join("{" + name + "}" for name in _TEMPLATE_TOKENS)
            raise ConfigError(f"PATH_TEMPLATE has an unknown part {{{token}}}. Use {allowed}")
    if "{" in re.sub(r"\{[^{}]*\}", "", cleaned) or "}" in re.sub(r"\{[^{}]*\}", "", cleaned):
        raise ConfigError("PATH_TEMPLATE has an unmatched brace")
    return cleaned


def load(environ: dict[str, str] | None = None) -> Config:
    """Build the settings from `environ` (the process environment by default)."""
    env = os.environ if environ is None else environ

    def get(name: str, default: str = "") -> str:
        return env.get(name, default).strip()

    pairing = get("PAIRING", "auto").lower()
    if pairing not in ("auto", "code", "plex"):
        raise ConfigError(f"PAIRING must be auto, code or plex, not {pairing!r}")

    pairing_code = get("PAIRING_CODE")
    if pairing_code and len(normalise_code(pairing_code)) < 6:
        raise ConfigError("PAIRING_CODE must have at least 6 letters or digits")

    plex_urls = tuple(
        url.rstrip("/") for url in (part.strip() for part in get("PLEX_URL").split(",")) if url
    )
    for url in plex_urls:
        if not re.match(r"^https?://[^/\s]+$", url):
            raise ConfigError(f"PLEX_URL must look like http://192.168.1.10:32400, not {url!r}")

    umask_text = get("UMASK", "022")
    try:
        umask = int(umask_text, 8)
    except ValueError:
        raise ConfigError(f"UMASK must be octal digits such as 022, not {umask_text!r}") from None
    if not 0 <= umask <= 0o777:
        raise ConfigError(f"UMASK must be between 000 and 777, not {umask_text!r}")

    extensions = frozenset(
        part.strip().lower().lstrip(".") for part in get("EXTRA_EXTENSIONS").split(",") if part.strip()
    )
    for extension in extensions:
        if not re.match(r"^[a-z0-9]{1,10}$", extension):
            raise ConfigError(f"EXTRA_EXTENSIONS entries must be letters and digits, not {extension!r}")

    log_level = get("LOG_LEVEL", "INFO").upper()
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
        raise ConfigError(f"LOG_LEVEL must be debug, info, warning or error, not {log_level!r}")

    tls_cert, tls_key = get("TLS_CERT"), get("TLS_KEY")
    if bool(tls_cert) != bool(tls_key):
        raise ConfigError("Set both TLS_CERT and TLS_KEY, or neither")

    return Config(
        port=int(_number(get("PORT", str(DEFAULT_PORT)), "PORT", 1, 65535)),
        bind=get("BIND", "0.0.0.0") or "0.0.0.0",
        upload_dir=os.path.abspath(get("UPLOAD_DIR", "/photos") or "/photos"),
        config_dir=os.path.abspath(get("CONFIG_DIR", "/config") or "/config"),
        name=(get("NAME", "Phlix Camera Upload") or "Phlix Camera Upload")[:60],
        plex_urls=plex_urls,
        pairing=pairing,
        pairing_code=pairing_code,
        path_template=validate_path_template(get("PATH_TEMPLATE", DEFAULT_PATH_TEMPLATE)),
        min_free_bytes=int(_number(get("MIN_FREE_GB", "2"), "MIN_FREE_GB", 0, 1_000_000) * _GIB),
        max_upload_bytes=int(_number(get("MAX_UPLOAD_GB", "50"), "MAX_UPLOAD_GB", 0.001, 1_000_000) * _GIB),
        tls=_flag(get("TLS", "on"), "TLS"),
        tls_cert=tls_cert,
        tls_key=tls_key,
        puid=_optional_id(get("PUID"), "PUID"),
        pgid=_optional_id(get("PGID"), "PGID"),
        umask=umask,
        extra_extensions=extensions,
        log_level=log_level,
    )


def normalise_code(code: str) -> str:
    """A pairing code as it is compared: letters and digits only, upper case."""
    return re.sub(r"[^A-Z0-9]", "", code.upper())
