"""What the helper remembers: paired devices and the files it has stored.

One SQLite file in the config folder. SQLite keeps it consistent if the
container is stopped mid-write, and looking up a photo stays fast with
hundreds of thousands of rows.
"""

from __future__ import annotations

import contextlib
import hashlib
import hmac
import os
import secrets
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass

#: 2 (helper 1.0.2): a record whose file was not found is flagged instead of
#: trusted, counts how often its photo came back, and every folder a device
#: ever had is remembered. Helper 1.0.1 still opens a file of schema 2.
SCHEMA_VERSION = 2

# The assets table as a new file gets it. A file made by 1.0.1 gets the two
# new columns from `_migrate`.
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
    missing_at INTEGER,
    returns   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (device_id, key)
);
CREATE INDEX IF NOT EXISTS assets_by_sha ON assets (sha256);
CREATE INDEX IF NOT EXISTS assets_by_path ON assets (relpath);
CREATE TABLE IF NOT EXISTS device_folders (
    device_id TEXT NOT NULL,
    folder    TEXT NOT NULL,
    since     INTEGER NOT NULL,
    PRIMARY KEY (device_id, folder)
);
"""

#: A photo whose file left the upload folder this often, and was sent again
#: each time, is not asked for again: something on the server takes it away.
LEAVE_OUT_AFTER = 3
#: Only a file that went within this many seconds of being stored counts
#: towards that. One that stayed longer was deleted by a person, and the
#: count starts again.
LEAVE_OUT_WINDOW = 7 * 86400


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
    kind: str | None = None
    #: The photo's own date as the phone sent it; the file's modification time.
    created: str | None = None
    stored_at: int = 0
    #: When the file was last looked for and not found, or None.
    missing_at: int | None = None
    #: How many times the photo was received again after its file had gone.
    returns: int = 0


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
        self._depth = 0
        with self._lock:
            self._db.executescript(_SCHEMA)
            self._migrate()
            if self.get_meta("server_id") is None:
                self.set_meta("server_id", str(uuid.uuid4()))
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    def _migrate(self) -> None:
        """Bring a file made by an older helper up to this schema.

        Done on every open: a 1.0.1 helper started on this file in between
        adds devices without noting their folders.
        """
        with self.transaction():
            columns = {row["name"] for row in self._db.execute("PRAGMA table_info(assets)")}
            if "missing_at" not in columns:
                self._db.execute("ALTER TABLE assets ADD COLUMN missing_at INTEGER")
            if "returns" not in columns:
                self._db.execute("ALTER TABLE assets ADD COLUMN returns INTEGER NOT NULL DEFAULT 0")
            self._db.execute("INSERT OR IGNORE INTO device_folders (device_id, folder, since) "
                             "SELECT id, folder, paired_at FROM devices")
            if self.get_meta("returns_restarted") is None:
                # Once, when a 1.0.3 helper first opens the file. Helper 1.0.2
                # counted a folder that a person deleted like a file that a
                # program took away, and left photos out for it. Those counts
                # cannot be told apart now, so every count starts again.
                self._db.execute("UPDATE assets SET returns = 0 WHERE returns > 0")
                self.set_meta("returns_restarted", "1.0.3")
            version = self.get_meta("schema_version")
            if version is None or int(version) < SCHEMA_VERSION:
                self.set_meta("schema_version", str(SCHEMA_VERSION))

    def close(self) -> None:
        with self._lock:
            self._db.close()

    @contextlib.contextmanager
    def transaction(self):
        """Make the writes inside one transaction: one sync to disk instead of
        one for each row, which a NAS feels. The store stays locked until it
        ends, so another thread's writes cannot slip into it."""
        with self._lock:
            if self._depth:
                self._depth += 1
                try:
                    yield
                finally:
                    self._depth -= 1
                return
            self._db.execute("BEGIN IMMEDIATE")
            self._depth = 1
            try:
                yield
            except BaseException:
                self._depth = 0
                self._db.execute("ROLLBACK")
                raise
            self._depth = 0
            self._db.execute("COMMIT")

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

    def pair_device(self, device_id: str, name: str, wanted_folder: str, via: str,
                    switch_folder: bool = False) -> tuple[Device, str]:
        """Add a device, or give a returning one a new token.

        A device that pairs again keeps the folder it already has: its photos
        stay together whatever it calls itself this time. Only with
        `switch_folder` (the person typed another name) do its new photos go
        into a folder of the name it asked for; what is already on the server
        stays where it is. A new device gets the folder it asked for. Either
        way a number is added when another device has, or had, that folder.
        Returns the device and its new bearer token.
        """
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        with self.transaction():
            existing = self._db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
            if existing:
                folder = existing["folder"]
                # A name that differs only in case is the same folder on many shares.
                if switch_folder and wanted_folder.casefold() != folder.casefold():
                    folder = self._free_folder(wanted_folder, device_id)
                self._db.execute(
                    "UPDATE devices SET name = ?, folder = ?, token_hash = ?, paired_at = ?, paired_via = ?, "
                    "last_seen = ? WHERE id = ?",
                    (name, folder, hash_token(token), now, via, now, device_id),
                )
                # Only a person pairs a phone. One who connects again after
                # deleting files on the server wants them sent again, so no
                # photo of this device stays left out.
                self._db.execute("UPDATE assets SET returns = 0 WHERE device_id = ? AND returns > 0",
                                 (device_id,))
            else:
                folder = self._free_folder(wanted_folder, device_id)
                self._db.execute(
                    "INSERT INTO devices (id, name, folder, token_hash, paired_at, paired_via, last_seen) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (device_id, name, folder, hash_token(token), now, via, now),
                )
            self._db.execute("INSERT OR IGNORE INTO device_folders (device_id, folder, since) VALUES (?, ?, ?)",
                             (device_id, folder, now))
            row = self._db.execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        return self._device(row), token

    def _free_folder(self, wanted: str, device_id: str) -> str:
        """`wanted`, or `wanted 2`, `wanted 3`...: a name that no other device
        has or had. A folder this device had before is its own again, spelt
        as it was."""
        for row in self._db.execute("SELECT folder FROM device_folders WHERE device_id = ?", (device_id,)):
            if row["folder"].casefold() == wanted.casefold():
                return row["folder"]
        taken = self.folders_of_others(device_id)
        if wanted.casefold() not in taken:
            return wanted
        number = 2
        while f"{wanted} {number}".casefold() in taken:
            number += 1
        return f"{wanted} {number}"

    def folders_of_others(self, device_id: str) -> set[str]:
        """Every folder that another device has or had, case folded."""
        with self._lock:
            rows = self._db.execute(
                "SELECT folder FROM devices WHERE id != ? UNION SELECT folder FROM device_folders WHERE device_id != ?",
                (device_id, device_id),
            ).fetchall()
        return {row["folder"].casefold() for row in rows}

    def all_folders(self) -> list[tuple[str, str]]:
        """(device id, folder) for every folder a device has or had."""
        with self._lock:
            rows = self._db.execute(
                "SELECT id AS device_id, folder FROM devices UNION SELECT device_id, folder FROM device_folders"
            ).fetchall()
        return [(row["device_id"], row["folder"]) for row in rows]

    def relocate(self, device_id: str, old_prefix: str, new_prefix: str, folder: str) -> int:
        """A device's folder was renamed on the server: from now on it is
        `folder`, and every record under `old_prefix`, of any device, points
        under `new_prefix`. Returns the number of records changed."""
        old, new = old_prefix + "/", new_prefix + "/"
        with self.transaction():
            self._db.execute("UPDATE devices SET folder = ? WHERE id = ?", (folder, device_id))
            self._db.execute("INSERT OR IGNORE INTO device_folders (device_id, folder, since) VALUES (?, ?, ?)",
                             (device_id, folder, int(time.time())))
            # A prefix compared character by character: % and _ are allowed in
            # folder names, and LIKE would take them for wildcards. The range
            # lets the index on relpath find the rows ("0" follows "/").
            cursor = self._db.execute(
                "UPDATE assets SET relpath = ? || substr(relpath, ?) "
                "WHERE relpath >= ? AND relpath < ? AND substr(relpath, 1, ?) = ?",
                (new, len(old) + 1, old, old_prefix + "0", len(old), old),
            )
        return cursor.rowcount

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
            relpath=row["relpath"], size=row["size"], kind=row["kind"], created=row["created"],
            stored_at=row["stored_at"], missing_at=row["missing_at"], returns=row["returns"],
        )

    def asset(self, device_id: str, key: str) -> Asset | None:
        with self._lock:
            row = self._db.execute(
                "SELECT * FROM assets WHERE device_id = ? AND key = ?", (device_id, key)
            ).fetchone()
        return self._asset(row) if row else None

    def records(self, device_id: str, keys: list[str]) -> dict[str, Asset]:
        """This device's records of `keys`, by key. A key it never sent is not there."""
        found: dict[str, Asset] = {}
        with self._lock:
            for start in range(0, len(keys), 500):
                chunk = keys[start:start + 500]
                marks = ",".join("?" * len(chunk))
                rows = self._db.execute(
                    f"SELECT * FROM assets WHERE device_id = ? AND key IN ({marks})", (device_id, *chunk)
                ).fetchall()
                found.update((row["key"], self._asset(row)) for row in rows)
        return found

    def known_keys(self, device_id: str, keys: list[str]) -> set[str]:
        """Which of `keys` this device has a record of. Whether the files are
        still there is for the check in presence.py to say."""
        return set(self.records(device_id, keys))

    def assets_with_sha(self, sha256: str) -> list[Asset]:
        """Every record of a file with this content, from any device; the ones
        whose file was there when last looked for come first."""
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM assets WHERE sha256 = ? ORDER BY missing_at IS NOT NULL, stored_at", (sha256,)
            ).fetchall()
        return [self._asset(row) for row in rows]

    def sha_at_path(self, relpath: str) -> str | None:
        """The content hash recorded for the file at `relpath`, if any. A
        record whose file was found missing proves nothing about what is there."""
        with self._lock:
            row = self._db.execute(
                "SELECT sha256 FROM assets WHERE relpath = ? AND missing_at IS NULL LIMIT 1", (relpath,)
            ).fetchone()
        return row["sha256"] if row else None

    def held_by_other(self, relpath: str, device_id: str, key: str, sha256: str) -> bool:
        """Whether a record of other content than `sha256` points at `relpath`,
        other than this device's own record of `key`. Its file may be gone,
        but a new file there would make that photo count as backed up."""
        with self._lock:
            row = self._db.execute(
                "SELECT 1 FROM assets WHERE relpath = ? AND sha256 != ? AND NOT (device_id = ? AND key = ?) "
                "LIMIT 1",
                (relpath, sha256, device_id, key),
            ).fetchone()
        return row is not None

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
                     kind: str | None, created: str | None, returned: bool = False) -> None:
        """Note where a received photo is now. `returned`: its earlier file
        had gone from the upload folder soon after it was stored, so the
        photo came back once more. Otherwise the count starts again."""
        with self._lock:
            self._db.execute(
                "INSERT INTO assets (device_id, key, sha256, relpath, size, kind, created, stored_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(device_id, key) DO UPDATE SET sha256 = excluded.sha256, relpath = excluded.relpath, "
                "size = excluded.size, kind = excluded.kind, created = excluded.created, "
                "stored_at = excluded.stored_at, missing_at = NULL, "
                "returns = CASE WHEN ? THEN assets.returns + 1 ELSE 0 END",
                (device_id, key, sha256, relpath, size, kind, created, int(time.time()), int(returned)),
            )

    def record_twin(self, device_id: str, key: str, sha256: str, twin: Asset) -> bool:
        """Note that a photo this device never sent is the file of `twin`.
        Only if the device still has no record of it: an upload that was
        recorded in the meantime wins. Returns whether it was noted."""
        with self._lock:
            cursor = self._db.execute(
                "INSERT INTO assets (device_id, key, sha256, relpath, size, kind, created, stored_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(device_id, key) DO NOTHING",
                (device_id, key, sha256, twin.relpath, twin.size, twin.kind, twin.created, int(time.time())),
            )
        return cursor.rowcount > 0

    # The three writes of a check compare the record with the one the check
    # read, so that an upload or a move recorded while the check looked at
    # the disk is never undone by it.

    def flag_missing(self, asset: Asset, when: int, restart: bool = False) -> bool:
        """Note that the file of `asset` was not found. With `restart`, its
        count of returns starts again as well: the folder that held the file
        is gone, and that is a person's doing. Returns False if the record
        changed since it was read."""
        with self._lock:
            cursor = self._db.execute(
                "UPDATE assets SET missing_at = COALESCE(missing_at, ?), "
                "returns = CASE WHEN ? THEN 0 ELSE returns END WHERE device_id = ? AND key = ? "
                "AND relpath = ? AND stored_at = ? AND returns = ?",
                (when, int(restart), asset.device_id, asset.key, asset.relpath, asset.stored_at, asset.returns),
            )
        return cursor.rowcount > 0

    def clear_missing(self, asset: Asset) -> bool:
        """The file of `asset` is back where it was."""
        with self._lock:
            cursor = self._db.execute(
                "UPDATE assets SET missing_at = NULL WHERE device_id = ? AND key = ? AND relpath = ?",
                (asset.device_id, asset.key, asset.relpath),
            )
        return cursor.rowcount > 0

    def repoint(self, asset: Asset, relpath: str, sha256: str | None = None, size: int | None = None) -> bool:
        """The photo of `asset` was found at `relpath`. Only if the record still
        holds the path it had when it was read. Returns whether it changed."""
        with self._lock:
            cursor = self._db.execute(
                "UPDATE assets SET relpath = ?, sha256 = COALESCE(?, sha256), size = COALESCE(?, size), "
                "missing_at = NULL WHERE device_id = ? AND key = ? AND relpath = ?",
                (relpath, sha256, size, asset.device_id, asset.key, asset.relpath),
            )
        return cursor.rowcount > 0

    def reset_returns(self, device_id: str, prefix: str) -> int:
        """Start the count of returns again for this device's records under
        `prefix` (which ends with a slash): its whole folder was deleted, by
        a person who starts over. Returns the number of records changed."""
        with self._lock:
            cursor = self._db.execute(
                "UPDATE assets SET returns = 0 WHERE device_id = ? AND returns > 0 AND substr(relpath, 1, ?) = ?",
                (device_id, len(prefix), prefix),
            )
        return cursor.rowcount

    def restart_returns_under(self, prefix: str) -> int:
        """Start the count of returns again for every record, of any device,
        under `prefix` (which ends with a slash): that folder was deleted, by
        a person. Returns the number of records changed."""
        with self._lock:
            # The range lets the index on relpath find the rows, as in `relocate`.
            cursor = self._db.execute(
                "UPDATE assets SET returns = 0 WHERE returns > 0 AND relpath >= ? AND relpath < ? "
                "AND substr(relpath, 1, ?) = ?",
                (prefix, prefix[:-1] + "0", len(prefix), prefix),
            )
        return cursor.rowcount

    def sample_under(self, device_id: str, prefix: str, limit: int) -> list[Asset]:
        """Up to `limit` of this device's records under `prefix` (which ends
        with a slash), picked at random, those last found missing last."""
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM assets WHERE device_id = ? AND substr(relpath, 1, ?) = ? "
                "ORDER BY missing_at IS NOT NULL, random() LIMIT ?",
                (device_id, len(prefix), prefix, limit),
            ).fetchall()
        return [self._asset(row) for row in rows]

    def present_count(self) -> int:
        """How many records point at a file that was there when last looked for."""
        with self._lock:
            row = self._db.execute("SELECT COUNT(*) AS n FROM assets WHERE missing_at IS NULL").fetchone()
        return int(row["n"])

    def device_totals(self, device_id: str) -> tuple[int, int]:
        """(number of assets, total bytes) of a device whose files were in
        the upload folder when last looked for."""
        with self._lock:
            row = self._db.execute(
                "SELECT COUNT(*) AS n, COALESCE(SUM(size), 0) AS bytes FROM assets "
                "WHERE device_id = ? AND missing_at IS NULL",
                (device_id,),
            ).fetchone()
        return int(row["n"]), int(row["bytes"])

    def totals(self) -> tuple[int, int]:
        """(number of files stored, their total bytes), of the files that
        were in the upload folder when last looked for.

        A file two phones both hold is recorded once for each of them and
        stored once, so it is counted once here.
        """
        with self._lock:
            row = self._db.execute(
                "SELECT COUNT(*) AS n, COALESCE(SUM(size), 0) AS bytes "
                "FROM (SELECT relpath, MAX(size) AS size FROM assets WHERE missing_at IS NULL GROUP BY relpath)"
            ).fetchone()
        return int(row["n"]), int(row["bytes"])
