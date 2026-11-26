"""Whether the files the helper stored are still there, and where they went.

A photo counts as backed up only while its file is in the upload folder.
People sort, rename and delete files on their server, so the helper's
records are a starting point, never the answer. For each photo a phone asks
about, the helper looks at the path it recorded:

* a regular file there: the photo is backed up, whatever was done to the
  file's content since (a tag edited in place must not send a library again);
* nothing there (ENOENT or ENOTDIR): the photo is missing, unless the
  device's folder was renamed, or a file of the same name, size and date is
  somewhere else in the upload folder;
* any other error (a share that dropped, EIO, ESTALE, EACCES): the helper
  cannot tell, and the photo counts as there, so that a hiccup of a share
  never turns into a re-upload of everything.

A hidden folder, a recycle bin and the other folders a system keeps for
itself (storage.is_outside_name) are not the upload folder. Nothing is looked
for in them, and a record that points into one is answered missing whatever
is there: Windows keeps a deleted folder in `$RECYCLE.BIN` with every name,
size and date, and helper 1.0.2 took those files for the photos, moved. Only
a folder that the helper's own layout made is part of the upload folder
under such a name (storage.layout_names): helpers before 1.0.3 let a phone
have "Recycled" as its folder, and its photos are really there.

A photo that keeps leaving soon after it is stored is left out in the end
(store.LEAVE_OUT_AFTER): some program on the server takes new files away.
Such a program leaves the folders. When the folder that held a file is gone
as well, a person deleted it, and that never leads to leaving a photo out.
(A program that also removes the folders it emptied is taken for a person,
and its photos are sent again every time. The README says so.)

Only the answers to a phone are lenient like that. When the bytes of an
upload are in hand, `Verifier.state` must say PRESENT before the bytes are
thrown away (server.py), so nothing is dropped on a guess.
"""

from __future__ import annotations

import errno
import hashlib
import logging
import math
import os
import stat
import threading
import time
import unicodedata
from dataclasses import dataclass, field

from .storage import (
    StorageError,
    clean_folder_name,
    is_allowed_extension,
    is_outside_name,
    is_outside_path,
    layout_names,
    parse_created,
    path_component,
)
from .store import LEAVE_OUT_AFTER, Asset, Device, Store

log = logging.getLogger("phlix.presence")

PRESENT = "present"
MISSING = "missing"
UNKNOWN = "unknown"

_GONE = frozenset({errno.ENOENT, errno.ENOTDIR})

#: A folder that holds at least this many of the records in one request is
#: listed once; for fewer, each file is looked up on its own.
LIST_FROM = 8
#: A listing of a folder with more entries than this (a flat layout) is
#: used again for this many seconds, as long as the folder's modification
#: time stays what it was when the listing was made.
BIG_FOLDER = 10_000
BIG_FOLDER_SECONDS = 60.0

#: Seconds a check waits for the index of names to be ready.
INDEX_WAIT_SECONDS = 3.0
#: Seconds of looking at files and reading them, per check, to find moved files.
MATCH_SECONDS = 2.0
#: A moved file whose modification time is no longer the photo's date is
#: compared by content, up to this size.
HASH_LIMIT = 64 * 1024 * 1024
#: Shares that keep times to two seconds (FAT, some SMB servers).
MTIME_SLACK = 2.0

#: Records compared when a device's folder is missing and the folders next
#: to it are tried, how many of them must be found, and limits on the trying.
SAMPLE = 20
SAMPLE_SHARE = 0.75
MAX_SIBLINGS = 50
MAX_MISSES = 3

UNKNOWN_WARNING_SECONDS = 3600.0


def fold(name: str) -> str:
    """A file name as the index compares it: NFC, and case folded."""
    return unicodedata.normalize("NFC", name).casefold()


def state_of(path: str) -> tuple[str, OSError | None]:
    """PRESENT for a regular file at `path`, MISSING, or UNKNOWN with the error."""
    try:
        info = os.stat(path)
    except OSError as error:
        return (MISSING if error.errno in _GONE else UNKNOWN), error
    except ValueError:
        return MISSING, None
    return (PRESENT if stat.S_ISREG(info.st_mode) else MISSING), None


def folder_state(path: str) -> str:
    try:
        info = os.stat(path)
    except OSError as error:
        return MISSING if error.errno in _GONE else UNKNOWN
    return PRESENT if stat.S_ISDIR(info.st_mode) else MISSING


def device_prefix(template: str, folder: str) -> tuple[str, str] | None:
    """(the folder that holds device folders, this device's folder name), or
    None when the layout puts a date before the device (then no device has
    one folder to follow) or has no `{device}` folder of its own."""
    literal: list[str] = []
    for part in (piece for piece in template.split("/") if piece):
        if part == "{device}":
            return "/".join(literal), path_component(folder)
        if "{" in part:
            return None
        literal.append(path_component(part))
    return None


def _join(parent: str, name: str) -> str:
    return f"{parent}/{name}" if parent else name


def _expected_mtime(asset: Asset) -> float | None:
    """The modification time the helper gave the file: the photo's own date."""
    created = parse_created(asset.created)
    if created is None:
        return None
    try:
        return created.timestamp()
    except (OverflowError, ValueError, OSError):
        return None


def _sha256_until(path: str, deadline: float, clock) -> str | None:
    """The file's SHA-256, or None if it cannot be read before `deadline`."""
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
                if clock() >= deadline:
                    return None
    except OSError:
        return None
    return digest.hexdigest()


@dataclass
class Looked:
    """What one look at the disk found for a set of records."""
    states: dict[str, str] = field(default_factory=dict)
    #: Records whose file is there under a name spelt another way (NFD on
    #: disk, say): key -> the path as it is on disk.
    respelt: dict[str, str] = field(default_factory=dict)
    errors: list[OSError] = field(default_factory=list)
    #: Folders of missing files that are themselves gone, or are not part of
    #: the upload folder: a person deleted them.
    gone_folders: set[str] = field(default_factory=set)


@dataclass
class _Listing:
    exact: dict[str, bool]
    by_nfc: dict[str, str]
    expires: float
    #: The folder's modification time, read before it was listed.
    mtime_ns: int


@dataclass
class _Dir:
    mtime_ns: int
    #: Listed so soon after a change that a second change in the same tick of
    #: the clock could have been missed: list it again next time.
    racy: bool
    files: tuple[str, ...]
    subdirs: tuple[str, ...]


class NameIndex:
    """The file names in the whole upload folder, to find files that were
    moved. Built in the background the first time a check meets a missing
    file, and brought up to date at most once a minute by listing again only
    the folders that changed. Hidden folders, system folders (recycle bins
    among them) and symbolic links are left out."""

    REFRESH_SECONDS = 60.0
    MAX_NAMES = 500_000

    def __init__(self, root: str, wanted):
        self.root = root
        self._wanted = wanted
        self._lock = threading.Lock()
        self._names: dict[str, list[tuple[str, str]]] = {}
        self._dirs: dict[str, _Dir] = {}
        self._count = 0
        self._scanned_at: float | None = None
        self._running = False
        self._idle = threading.Event()
        self._idle.set()
        self.clock = time.monotonic
        self.scans = 0
        self.listings = 0
        self._said_full = False

    def refresh(self, wait: float) -> None:
        """Start a scan if the last one began a minute ago or more (or never
        ran). Only for the first index, wait up to `wait` seconds: once there
        is one, it answers at once while a newer one is made, and a file it
        does not know yet is found when the phone asks again."""
        with self._lock:
            first = self._scanned_at is None
            due = first or self.clock() - self._scanned_at >= self.REFRESH_SECONDS
            if due and not self._running:
                self._running = True
                self._idle.clear()
                threading.Thread(target=self._scan_safely, args=(self.clock(),), name="phlix-name-index",
                                 daemon=True).start()
        if first:
            self._idle.wait(wait)

    def lookup(self, name: str) -> list[str]:
        """Paths, relative to the upload folder, of files with this name."""
        with self._lock:
            return [_join(parent, actual) for parent, actual in self._names.get(fold(name), ())]

    def _scan_safely(self, started: float) -> None:
        try:
            self._scan()
            with self._lock:
                self._scanned_at = started
        except Exception:  # noqa: BLE001 - a failed scan only means fewer moved files are found
            log.debug("Could not index the upload folder", exc_info=True)
        finally:
            with self._lock:
                self._running = False
            self._idle.set()

    def _scan(self) -> None:
        self.scans += 1
        seen: set[str] = set()
        stack = [""]
        while stack:
            relative = stack.pop()
            path = os.path.join(self.root, relative) if relative else self.root
            try:
                info = os.stat(path)
            except OSError:
                continue
            seen.add(relative)
            old = self._dirs.get(relative)
            if old is not None and old.mtime_ns == info.st_mtime_ns and not old.racy:
                stack.extend(_join(relative, name) for name in old.subdirs)
                continue
            listed_at = time.time()
            listed = self._list(path)
            if listed is None:
                # Could not be read this time: keep what was known, and try again next time.
                if old is not None:
                    old.racy = True
                    stack.extend(_join(relative, name) for name in old.subdirs)
                continue
            files, subdirs = listed
            kept = self._replace(relative, old.files if old else (), files)
            self._dirs[relative] = _Dir(info.st_mtime_ns, abs(listed_at - info.st_mtime) < MTIME_SLACK,
                                        kept, subdirs)
            stack.extend(_join(relative, name) for name in subdirs)
        for relative in [known for known in self._dirs if known not in seen]:
            self._replace(relative, self._dirs.pop(relative).files, ())

    def _list(self, path: str) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
        self.listings += 1
        files: list[str] = []
        subdirs: list[str] = []
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    name = entry.name
                    if is_outside_name(name):
                        continue
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            subdirs.append(name)
                        elif entry.is_file(follow_symlinks=False) and self._wanted(name):
                            files.append(name)
                    except OSError:
                        continue
        except OSError:
            return None
        return tuple(files), tuple(subdirs)

    def _replace(self, relative: str, old: tuple[str, ...], new: tuple[str, ...]) -> tuple[str, ...]:
        """Swap a folder's names in the index. Returns the names kept."""
        with self._lock:
            for name in old:
                entries = self._names.get(fold(name))
                if entries and (relative, name) in entries:
                    entries.remove((relative, name))
                    self._count -= 1
                    if not entries:
                        del self._names[fold(name)]
            room = max(0, self.MAX_NAMES - self._count)
            kept = new[:room]
            for name in kept:
                self._names.setdefault(fold(name), []).append((relative, name))
            self._count += len(kept)
            full = len(kept) < len(new)
        if full and not self._said_full:
            self._said_full = True
            log.warning("The upload folder holds more than %s files. A moved file beyond that many is not "
                        "looked for, and its photo is uploaded again.", f"{self.MAX_NAMES:,}")
        return kept


class Verifier:
    """Answers "which of these photos are in the upload folder now", keeps
    the records true, and follows a device's folder that was renamed."""

    def __init__(self, config, store: Store, storage, place_lock: threading.Lock):
        self.config = config
        self.store = store
        self.storage = storage
        self.place_lock = place_lock
        self.index = NameIndex(storage.upload_dir,
                               lambda name: is_allowed_extension(name, config.extra_extensions))
        self.clock = time.monotonic
        self._listings: dict[str, _Listing] = {}
        #: Folders found to hold more than BIG_FOLDER entries. Only for these
        #: is the modification time read before they are listed.
        self._big: set[str] = set()
        self._listings_lock = threading.Lock()
        self._misses: dict[tuple[str, str], int] = {}
        self._warned_at: float | None = None
        self._warn_lock = threading.Lock()

    # -- one path ---------------------------------------------------------------

    def state(self, relpath: str) -> str:
        """PRESENT, MISSING or UNKNOWN for one recorded path. A path into a
        recycle bin or another folder that is not part of the upload folder
        is MISSING whatever is there: helper 1.0.2 may have recorded one."""
        if self._outside(relpath.rpartition("/")[0]):
            return MISSING
        try:
            path = self.storage.absolute(relpath)
        except StorageError:
            return MISSING
        return state_of(path)[0]

    def _outside(self, folder: str) -> bool:
        """Whether a recorded folder is or lies in a folder that is not part
        of the upload folder. Which names the layout itself writes is asked
        only for a path that has a system folder's name in it, so nearly
        never."""
        if not is_outside_path(folder):
            return False
        own = layout_names(self.config.path_template, [name for _, name in self.store.all_folders()])
        return is_outside_path(folder, own)

    def stored_twin(self, sha256: str, skip: Asset | None = None) -> Asset | None:
        """A record of this exact content whose file is surely there now."""
        for asset in self.store.assets_with_sha(sha256):
            if skip is not None and (asset.device_id, asset.key) == (skip.device_id, skip.key):
                continue
            if self.state(asset.relpath) == PRESENT:
                return asset
        return None

    # -- many records -----------------------------------------------------------

    def look(self, records) -> Looked:
        """The state of each record's file. A folder with LIST_FROM or more
        of the records is listed once; each name it lacks is still looked up
        on its own, which finds a name spelt in another case on a share that
        ignores case. A record that points into a folder that is not part of
        the upload folder is MISSING without a look. `gone_folders` gets the
        folders of missing files that are gone themselves, with one look at
        each, and none at a folder that was listed: that one is there."""
        looked = Looked()
        by_folder: dict[str, list[Asset]] = {}
        for record in records:
            by_folder.setdefault(record.relpath.rpartition("/")[0], []).append(record)
        for folder, group in by_folder.items():
            if self._outside(folder):
                # In a recycle bin, say: a person deleted the photo.
                looked.states.update((record.key, MISSING) for record in group)
                looked.gone_folders.add(folder)
                continue
            listing = self._listing(folder, looked) if len(group) >= LIST_FROM else None
            for record in group:
                name = record.relpath.rpartition("/")[2]
                if isinstance(listing, str):
                    looked.states[record.key] = listing
                    continue
                if listing is not None and name in listing.exact:
                    looked.states[record.key] = PRESENT if listing.exact[name] else MISSING
                    continue
                if listing is not None:
                    actual = listing.by_nfc.get(unicodedata.normalize("NFC", name))
                    if actual is not None and listing.exact.get(actual):
                        looked.states[record.key] = PRESENT
                        looked.respelt[record.key] = _join(folder, actual)
                        continue
                try:
                    path = self.storage.absolute(record.relpath)
                except StorageError:
                    looked.states[record.key] = MISSING
                    continue
                state, error = state_of(path)
                looked.states[record.key] = state
                if state == UNKNOWN and error is not None:
                    looked.errors.append(error)
            # The upload folder itself is not a folder a person deletes to
            # start over: only folders inside it are asked about. A folder
            # that was listed has answered already: there, gone, or unknown.
            if listing is None and folder and any(
                    looked.states[record.key] == MISSING for record in group):
                try:
                    if folder_state(self.storage.absolute(folder)) == MISSING:
                        looked.gone_folders.add(folder)
                except StorageError:
                    pass
        return looked

    def _listing(self, folder: str, looked: Looked):
        """The names in `folder`, MISSING if it is gone, or UNKNOWN."""
        try:
            path = self.storage.absolute(folder) if folder else self.storage.upload_dir
        except StorageError:
            return MISSING
        now = self.clock()
        with self._listings_lock:
            kept = self._listings.get(path)
            big = path in self._big
        # Read before the folder is listed, so that a change made while it is
        # listed shows as a newer time at the next look. Only for a folder
        # whose listing is kept or will be: a look that costs every other
        # folder nothing.
        info = None
        if kept is not None or big:
            try:
                info = os.stat(path)
            except OSError:
                # Gone, or out of sight: listing it below says which.
                info = None
        if kept is not None:
            # A kept listing answers only for the folder as it was listed.
            # One file deleted from it, or the whole folder, changes the time.
            if info is not None and kept.expires > now and kept.mtime_ns == info.st_mtime_ns:
                return kept
            with self._listings_lock:
                if self._listings.get(path) is kept:
                    del self._listings[path]
        exact: dict[str, bool] = {}
        listed_at = time.time()
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        exact[entry.name] = entry.is_file()
                    except OSError:
                        exact[entry.name] = False
        except OSError as error:
            if error.errno in _GONE:
                with self._listings_lock:
                    self._big.discard(path)
                if folder:
                    looked.gone_folders.add(folder)
                return MISSING
            looked.errors.append(error)
            return UNKNOWN
        by_nfc = {unicodedata.normalize("NFC", name): name for name in exact}
        if len(exact) <= BIG_FOLDER or info is None:
            # Not kept. A folder found big only now had no time read before
            # it was listed: it is noted, and its next listing is kept.
            with self._listings_lock:
                if len(exact) > BIG_FOLDER:
                    self._big.add(path)
                else:
                    self._big.discard(path)
            return _Listing(exact, by_nfc, now, 0)
        # A folder that changed moments before it was listed may change again
        # within the same tick of a coarse clock (FAT, some shares), and its
        # time would not show it: such a listing is kept no longer than a tick.
        racy = abs(listed_at - info.st_mtime) < MTIME_SLACK
        listing = _Listing(exact, by_nfc, now + (MTIME_SLACK if racy else BIG_FOLDER_SECONDS), info.st_mtime_ns)
        with self._listings_lock:
            self._listings[path] = listing
        return listing

    def check(self, device: Device, keys: list[str], hashes: dict[str, str]) -> tuple[set[str], set[str]]:
        """(known, left out) among `keys`. Known: the photo's file is in the
        upload folder now, as far as the helper can tell. Left out: missing
        again after it came back LEAVE_OUT_AFTER times, each time soon after
        it was stored. Never left out: a photo whose folder is gone as well.
        A person deleted that folder, so the photo is only missing, and its
        count of returns starts again."""
        records = self.store.records(device.id, keys)
        looked = self.look(records.values())
        if MISSING in looked.states.values():
            # A renamed device folder first: one change of every record, where
            # looking for each file on its own would cost a look at each.
            with self.place_lock:
                followed, restarted = self._follow(device)
            if followed.folder != device.folder:
                records = self.store.records(device.id, keys)
                looked = self.look(records.values())
            elif restarted:
                # The whole folder is gone, and its photos start their count of
                # returns again. The writes below compare with these records,
                # so take them as they are now; one that changed otherwise
                # meanwhile stays as read, and its own path decides at the end.
                fresh = self.store.records(device.id, list(records))
                for key, record in records.items():
                    now_record = fresh.get(key)
                    if now_record is not None and (now_record.relpath, now_record.stored_at) == (
                            record.relpath, record.stored_at):
                        records[key] = now_record
        self._warn(looked.errors)

        found = dict(looked.respelt)
        missing = [records[key] for key, state in looked.states.items() if state == MISSING]
        if missing:
            found.update(self._find_moved(missing))
        twins: dict[str, Asset] = {}
        for key, sha in hashes.items():
            if looked.states.get(key) in (PRESENT, UNKNOWN) or key in found:
                continue
            twin = self.stored_twin(sha)
            if twin is not None:
                twins[key] = twin

        known: set[str] = set()
        left_out: set[str] = set()
        changed: list[str] = []
        now = int(time.time())
        # Nearly always every file is where it was: then nothing is written,
        # and the check does not wait for an upload being put in place.
        quiet = not found and not twins and all(
            state == UNKNOWN or (state == PRESENT and records[key].missing_at is None)
            for key, state in looked.states.items())
        if quiet:
            return set(records), left_out
        with self.place_lock, self.store.transaction():
            for key, record in records.items():
                state = looked.states[key]
                if key in found:
                    target = found[key]
                    if target == record.relpath or self.store.repoint(record, target):
                        known.add(key)
                    else:
                        changed.append(key)
                elif state == PRESENT:
                    known.add(key)
                    if record.missing_at is not None:
                        self.store.clear_missing(record)
                elif state == UNKNOWN:
                    known.add(key)
                elif key in twins:
                    twin = twins[key]
                    if self.store.repoint(record, twin.relpath, hashes[key], twin.size):
                        known.add(key)
                    else:
                        changed.append(key)
                else:
                    # The count starts again in the same write that compares
                    # it with the record as read, so that an upload recorded
                    # meanwhile is still noticed.
                    restart = record.relpath.rpartition("/")[0] in looked.gone_folders
                    if not self.store.flag_missing(record, now, restart=restart):
                        changed.append(key)
                    elif record.returns >= LEAVE_OUT_AFTER and not restart:
                        left_out.add(key)
            for key, twin in twins.items():
                if key in records:
                    continue
                if self.store.record_twin(device.id, key, hashes[key], twin):
                    known.add(key)
                else:
                    changed.append(key)
            # The other photos that were in a deleted folder, of any device,
            # start their count again too. The phone asks about its photos in
            # several requests, and the first photos sent again make the
            # folder again before the others are asked about. After the
            # writes above, which compare the count as it was read.
            for folder in looked.gone_folders:
                self.store.restart_returns_under(folder + "/")
        # A record that changed while the check looked: an upload or a move
        # was recorded meanwhile. Its own path decides.
        for key in changed:
            asset = self.store.asset(device.id, key)
            if asset is not None and self.state(asset.relpath) != MISSING:
                known.add(key)
        return known, left_out

    def _find_moved(self, missing: list[Asset]) -> dict[str, str]:
        """Where missing files went, within MATCH_SECONDS of looking at files:
        the same content recorded elsewhere, else a file of the same name
        (in NFC, ignoring case) anywhere in the upload folder with the same
        size, and the photo's date as its modification time or, up to
        HASH_LIMIT, the same content. What is not found in time is answered
        missing; the phone asks again before it sends the photo."""
        found: dict[str, str] = {}
        spent = 0.0
        started = self.clock()
        for record in missing:
            if self.clock() - started >= MATCH_SECONDS:
                break
            twin = self.stored_twin(record.sha256, skip=record)
            if twin is not None:
                found[record.key] = twin.relpath
        spent += self.clock() - started
        rest = [record for record in missing if record.key not in found]
        if not rest or spent >= MATCH_SECONDS:
            return found
        self.index.refresh(INDEX_WAIT_SECONDS)
        deadline = self.clock() + MATCH_SECONDS - spent
        for record in rest:
            if self.clock() >= deadline:
                break
            expected = _expected_mtime(record)
            for candidate in self.index.lookup(record.relpath.rpartition("/")[2]):
                if candidate == record.relpath:
                    continue
                if self._same_file(candidate, record, expected, deadline):
                    found[record.key] = candidate
                    break
                if self.clock() >= deadline:
                    break
        return found

    def _same_file(self, relpath: str, record: Asset, expected: float | None, deadline: float) -> bool:
        try:
            path = self.storage.absolute(relpath)
            info = os.stat(path, follow_symlinks=False)
        except (StorageError, OSError, ValueError):
            return False
        if not stat.S_ISREG(info.st_mode) or info.st_size != record.size:
            return False
        if expected is not None and abs(info.st_mtime - expected) <= MTIME_SLACK:
            return True
        if info.st_size > HASH_LIMIT:
            return False
        return _sha256_until(path, deadline, self.clock) == record.sha256

    def _warn(self, errors: list[OSError]) -> None:
        if not errors:
            return
        with self._warn_lock:
            now = self.clock()
            if self._warned_at is not None and now - self._warned_at < UNKNOWN_WARNING_SECONDS:
                return
            self._warned_at = now
        reason = errno.errorcode.get(errors[0].errno or 0, type(errors[0]).__name__)
        log.warning("Could not tell whether %s stored files are still in the upload folder (%s). They count as "
                    "backed up for now. Is a share or disk having trouble? (This is said at most once an hour.)",
                    len(errors), reason)

    # -- a renamed device folder ------------------------------------------------

    def follow_folder(self, device: Device) -> Device:
        """If the device's folder is gone and a folder next to it holds its
        files, the device moves there. Call with `place_lock` held, before
        anything could make the old folder again. Returns the device as the
        store has it now."""
        return self._follow(device)[0]

    def before_folder_is_made(self, folder: str) -> None:
        """Call with `place_lock` held, before an upload makes `folder`
        (relative to the upload folder). If it is gone, a person deleted it,
        perhaps while the phone was still sending. The upload makes it
        again, and the next check would find the folder there and take its
        other photos for files that a program took away. So the count of
        returns starts again here, for every record under the highest folder
        that is gone: a year's folder takes its months with it. A folder
        that was never there has no records, and nothing changes."""
        if not folder:
            return
        try:
            if folder_state(self.storage.absolute(folder)) != MISSING:
                return
            top = folder
            while "/" in top:
                parent = top.rpartition("/")[0]
                if folder_state(self.storage.absolute(parent)) != MISSING:
                    break
                top = parent
        except StorageError:
            return
        self.store.restart_returns_under(top + "/")

    def _follow(self, device: Device) -> tuple[Device, bool]:
        """follow_folder, and whether the count of returns of the device's
        photos started again because its whole folder is gone."""
        current = self.store.device(device.id) or device
        layout = device_prefix(self.config.path_template, current.folder)
        if layout is None:
            return current, False
        parent, own = layout
        old_prefix = _join(parent, own)
        try:
            if folder_state(self.storage.absolute(old_prefix)) != MISSING:
                return current, False
        except StorageError:
            return current, False
        sample = self.store.sample_under(current.id, old_prefix + "/", SAMPLE)
        if not sample:
            return current, False
        need = max(1, math.ceil(len(sample) * SAMPLE_SHARE))
        for name in self._siblings(parent, current):
            new_prefix = _join(parent, name)
            hits = 0
            for done, asset in enumerate(sample, 1):
                rest = asset.relpath[len(old_prefix) + 1:]
                if self._is_file_of_size(_join(new_prefix, rest), asset.size):
                    hits += 1
                if hits >= need or hits + len(sample) - done < need:
                    break
            if hits >= need:
                moved = self.store.relocate(current.id, old_prefix, new_prefix, name)
                self._misses = {seen: count for seen, count in self._misses.items() if seen[0] != current.id}
                log.info('The folder "%s" was renamed to "%s". The helper follows it: %s records now point '
                         'there, and new photos from "%s" go there too.', old_prefix, new_prefix, moved,
                         current.name)
                return self.store.device(current.id) or current, False
            self._misses[(current.id, name)] = self._misses.get((current.id, name), 0) + 1
        # The whole folder is gone and no folder next to it holds its files: a
        # person started over (a program that takes new files away leaves the
        # folders). The photos sent again start their count of returns anew.
        return current, self.store.reset_returns(current.id, old_prefix + "/") > 0

    def _siblings(self, parent: str, device: Device) -> list[str]:
        """Folders next to the device's own that it could have been renamed
        to, the most recently changed first. Never another device's folder,
        present or past, and never a recycle bin or another folder that is
        not part of the upload folder."""
        taken = self.store.folders_of_others(device.id)
        found: list[tuple[float, str]] = []
        try:
            path = self.storage.absolute(parent) if parent else self.storage.upload_dir
            with os.scandir(path) as entries:
                for entry in entries:
                    name = entry.name
                    if is_outside_name(name) or name.casefold() in taken:
                        continue
                    if self._misses.get((device.id, name), 0) >= MAX_MISSES:
                        continue
                    # The helper writes a device's folder name cleaned; a name it
                    # would write differently cannot be followed.
                    if clean_folder_name(name) != name:
                        continue
                    try:
                        if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
                            continue
                        found.append((entry.stat(follow_symlinks=False).st_ctime, name))
                    except OSError:
                        continue
        except (OSError, StorageError):
            return []
        found.sort(reverse=True)
        return [name for _, name in found[:MAX_SIBLINGS]]

    def _is_file_of_size(self, relpath: str, size: int) -> bool:
        try:
            info = os.stat(self.storage.absolute(relpath))
        except (StorageError, OSError, ValueError):
            return False
        return stat.S_ISREG(info.st_mode) and info.st_size == size

    # -- whose path it is -------------------------------------------------------

    def path_is_own(self, device: Device, relpath: str, sha256: str) -> bool:
        """Whether a device may be told where this file is: it is in one of
        the device's own folders, or in no device's folder and its upload
        stored it. Where another phone keeps a photo is that phone's business."""
        theirs = False
        for device_id, folder in self.store.all_folders():
            layout = device_prefix(self.config.path_template, folder)
            if layout is None:
                return self.store.first_device_at(relpath, sha256) == device.id
            if relpath.startswith(_join(*layout) + "/"):
                if device_id == device.id:
                    return True
                theirs = True
        return not theirs and self.store.first_device_at(relpath, sha256) == device.id
