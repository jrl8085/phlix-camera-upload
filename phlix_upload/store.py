"""What the helper remembers: paired devices and the files it has stored.

One SQLite file in the config folder. SQLite keeps it consistent if the
container is stopped mid-write, and looking up a photo stays fast with
hundreds of thousands of rows.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS devices (
    id         TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    folder     TEXT NOT NULL UNIQUE,
    token_hash TEXT NOT NULL,
    paired_at  INTEGER NOT NULL,
    paired_via TEXT NOT NULL,
    last_seen  INTEGER
);
CREATE TABLE IF NOT EXISTS assets (
    device_id TEXT NOT NULL,
    key       TEXT NOT NULL,
    sha256    TEXT NOT NULL,
    relpath   TEXT NOT NULL,
    size      INTEGER NOT NULL,
    kind      TEXT,
    created   TEXT,
    stored_at INTEGER NOT NULL,
    PRIMARY KEY (device_id, key)
);
CREATE INDEX IF NOT EXISTS assets_by_sha ON assets (sha256);
CREATE INDEX IF NOT EXISTS assets_by_path ON assets (relpath);
"""


@dataclass(frozen=True)
class Device:
    id: str
    name: str
    folder: str
    paired_at: int
    paired_via: str
    last_seen: int | None
    #: False once the device was unpaired. Its row stays, so that its folder
    #: is still its own if it ever pairs again.
    paired: bool = True


@dataclass(frozen=True)
class Asset:
    device_id: str
    key: str
    sha256: str
    relpath: str
    size: int


def hash_token(token: str) -> str:
    """Tokens are stored hashed, so a copy of the database pairs nothing."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class Store:
    """Thread-safe access to the helper's database."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.RLock()
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        # One connection shared by every request thread, guarded by a lock.
        # `timeout` covers the admin commands, which open the same file from
        # another process.
        self._db = sqlite3.connect(path, check_same_thread=False, timeout=30, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        with self._lock:
            self._db.executescript(_SCHEMA)
            if self.get_meta("schema_version") is None:
                self.set_meta("schema_version", str(SCHEMA_VERSION))
            if self.get_meta("server_id") is None:
                self.set_meta("server_id", str(uuid.uuid4()))
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    def close(self) -> None:
        with self._lock:
            self._db.close()

    # -- meta ---------------------------------------------------------------

    def get_meta(self, key: str) -> str | None:
        with self._lock:
            row = self._db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    @property
    def server_id(self) -> str:
        value = self.get_meta("server_id")
        assert value is not None
        return value

    # -- devices ------------------------------------------------------------

    @staticmethod
    def _device(row: sqlite3.Row) -> Device:
        return Device(
            id=row["id"], name=row["name"], folder=row["folder"], paired_at=row["paired_at"],
            paired_via=row["paired_via"], last_seen=row["last_seen"], paired=bool(row["token_hash"]),
        )

    def devices(self, include_unpaired: bool = False) -> list[Device]:
        """Paired devices, oldest first; with `include_unpaired`, former ones too."""
        with self._lock:
            rows = self._db.execute("SELECT * FROM devices ORDER BY paired_at, id").fetchall()
        devices = [self._device(row) for row in rows]
        return devices if include_unpaired else [device for device in devices if device.paired]

    def device(self, device_id: str) -> Device | None:
        with self._lock:
            row = self._db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        return self._device(row) if row else None

    def device_for_token(self, token: str) -> Device | None:
        """The device a bearer token belongs to, or None."""
        candidate = hash_token(token)
        with self._lock:
            rows = self._db.execute("SELECT * FROM devices WHERE token_hash != ''").fetchall()
        # Compared in constant time against every device, so the answer's
        # timing says nothing about how close a guess was.
        match = None
        for row in rows:
            if hmac.compare_digest(row["token_hash"], candidate):
                match = row
        return self._device(match) if match else None

    def pair_device(self, device_id: str, name: str, wanted_folder: str, via: str) -> tuple[Device, str]:
        """Add a device, or give a returning one a new token.

        A device that pairs again keeps the folder it already has: its photos
        stay together whatever it calls itself this time. A new device gets
        the folder it asked for, with a number added if another device has it.
        Returns the device and its new bearer token.
        """
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        with self._lock:
            existing = self._db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
            if existing:
                self._db.execute(
                    "UPDATE devices SET name = ?, token_hash = ?, paired_at = ?, paired_via = ?, last_seen = ? "
                    "WHERE id = ?",
                    (name, hash_token(token), now, via, now, device_id),
                )
            else:
                folder = self._free_folder(wanted_folder)
                self._db.execute(
                    "INSERT INTO devices (id, name, folder, token_hash, paired_at, paired_via, last_seen) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (device_id, name, folder, hash_token(token), now, via, now),
                )
            row = self._db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        return self._device(row), token

    def _free_folder(self, wanted: str) -> str:
        taken = {row["folder"].casefold() for row in self._db.execute("SELECT folder FROM devices")}
        if wanted.casefold() not in taken:
            return wanted
        number = 2
        while f"{wanted} {number}".casefold() in taken:
            number += 1
        return f"{wanted} {number}"

    def remove_device(self, device_id: str) -> bool:
        """Unpair a device: its token stops working at once.

        Its files, their records and its folder name all stay, so nothing is
        uploaded twice and nobody else is given its folder if it pairs again.
        Returns False if no paired device has that id.
        """
        with self._lock:
            cursor = self._db.execute(
                "UPDATE devices SET token_hash = '' WHERE id = ? AND token_hash != ''", (device_id,)
            )
        return cursor.rowcount > 0

    def touch_device(self, device_id: str) -> None:
        with self._lock:
            self._db.execute("UPDATE devices SET last_seen = ? WHERE id = ?", (int(time.time()), device_id))

    # -- assets -------------------------------------------------------------

    @staticmethod
    def _asset(row: sqlite3.Row) -> Asset:
        return Asset(
            device_id=row["device_id"], key=row["key"], sha256=row["sha256"],
            relpath=row["relpath"], size=row["size"],
        )

    def asset(self, device_id: str, key: str) -> Asset | None:
        with self._lock:
            row = self._db.execute(
                "SELECT * FROM assets WHERE device_id = ? AND key = ?", (device_id, key)
            ).fetchone()
        return self._asset(row) if row else None

    def known_keys(self, device_id: str, keys: list[str]) -> set[str]:
        """Which of `keys` this device has already uploaded."""
        known: set[str] = set()
        with self._lock:
            for start in range(0, len(keys), 500):
                chunk = keys[start:start + 500]
                marks = ",".join("?" * len(chunk))
                rows = self._db.execute(
                    f"SELECT key FROM assets WHERE device_id = ? AND key IN ({marks})", (device_id, *chunk)
                ).fetchall()
                known.update(row["key"] for row in rows)
        return known

    def assets_with_sha(self, sha256: str) -> list[Asset]:
        """Every record of a file with this content, from any device."""
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM assets WHERE sha256 = ? ORDER BY stored_at", (sha256,)
            ).fetchall()
        return [self._asset(row) for row in rows]

    def sha_at_path(self, relpath: str) -> str | None:
        """The content hash recorded for the file at `relpath`, if any."""
        with self._lock:
            row = self._db.execute("SELECT sha256 FROM assets WHERE relpath = ? LIMIT 1", (relpath,)).fetchone()
        return row["sha256"] if row else None

    def first_device_at(self, relpath: str, sha256: str) -> str | None:
        """The device whose upload put this content at `relpath`.

        Every later record of the same file, from that device or another,
        points at the same path; the first one is the upload that wrote it.
        """
        with self._lock:
            row = self._db.execute(
                "SELECT device_id FROM assets WHERE relpath = ? AND sha256 = ? ORDER BY rowid LIMIT 1",
                (relpath, sha256),
            ).fetchone()
        return row["device_id"] if row else None

    def record_asset(self, device_id: str, key: str, sha256: str, relpath: str, size: int,
                     kind: str | None, created: str | None) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO assets (device_id, key, sha256, relpath, size, kind, created, stored_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(device_id, key) DO UPDATE SET sha256 = excluded.sha256, relpath = excluded.relpath, "
                "size = excluded.size, kind = excluded.kind, created = excluded.created, "
                "stored_at = excluded.stored_at",
                (device_id, key, sha256, relpath, size, kind, created, int(time.time())),
            )

    def device_totals(self, device_id: str) -> tuple[int, int]:
        """(number of assets, total bytes) recorded for a device."""
        with self._lock:
            row = self._db.execute(
                "SELECT COUNT(*) AS n, COALESCE(SUM(size), 0) AS bytes FROM assets WHERE device_id = ?",
                (device_id,),
            ).fetchone()
        return int(row["n"]), int(row["bytes"])

    def totals(self) -> tuple[int, int]:
        """(number of files stored, their total bytes).

        A file two phones both hold is recorded once for each of them and
        stored once, so it is counted once here.
        """
        with self._lock:
            row = self._db.execute(
                "SELECT COUNT(*) AS n, COALESCE(SUM(size), 0) AS bytes "
                "FROM (SELECT relpath, MAX(size) AS size FROM assets GROUP BY relpath)"
            ).fetchone()
        return int(row["n"]), int(row["bytes"])
