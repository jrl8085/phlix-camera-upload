"""Where uploaded files go on disk.

Everything a phone sends (a file name, a folder name, a date) is cleaned here
before it becomes part of a path, so nothing a phone says can make the helper
write outside the upload folder.
"""

from __future__ import annotations

import datetime as _dt
import errno
import hashlib
import os
import re
import secrets
import shutil
import threading
import time
import unicodedata

#: File types a phone's camera roll can hold. Anything else is refused, so a
#: stolen pairing token cannot be used to drop scripts or programs on a share.
MEDIA_EXTENSIONS = frozenset({
    # photos
    "jpg", "jpeg", "heic", "heif", "png", "gif", "tif", "tiff", "bmp", "webp", "avif", "jxl",
    # raw photos
    "dng", "cr2", "cr3", "nef", "arw", "raf", "orf", "rw2", "srw", "pef", "raw",
    # videos
    "mov", "mp4", "m4v", "avi", "3gp", "3g2", "mts", "m2ts", "mkv", "webm",
})

_WINDOWS_RESERVED = frozenset(
    ["CON", "PRN", "AUX", "NUL"] + [f"COM{n}" for n in range(1, 10)] + [f"LPT{n}" for n in range(1, 10)]
)
# Characters a Windows or SMB share refuses, plus the path separators.
_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]')
_MAX_NAME_BYTES = 150

#: Folders that a NAS or Windows keeps for itself inside any shared folder or
#: drive: recycle bins, snapshots, indexes. What is in one of them is not in
#: the upload folder: Windows keeps the name, size and date of every file of
#: a deleted folder in `$RECYCLE.BIN`, and such a file must never be taken
#: for a photo that is backed up.
SYSTEM_FOLDERS = frozenset({
    "lost+found", "@eaDir", "#recycle", "#snapshot", "@Recycle", "@Recently-Snapshot",
    "$RECYCLE.BIN", "RECYCLER", "RECYCLED", "System Volume Information",
})
_SYSTEM_FOLDERS_FOLDED = frozenset(name.casefold() for name in SYSTEM_FOLDERS)


class StorageError(Exception):
    """A file could not be stored. `code` is the API error code to answer with."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _clean_component(text: str, fallback: str, max_bytes: int = _MAX_NAME_BYTES) -> str:
    """One safe path component: no separators, no leading dot, not too long."""
    text = unicodedata.normalize("NFC", text)
    text = _FORBIDDEN.sub("_", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    if not text or text.upper().split(".")[0] in _WINDOWS_RESERVED:
        text = fallback
    while len(text.encode("utf-8")) > max_bytes:
        text = text[:-1]
    return text.strip(" .") or fallback


def is_outside_name(name: str) -> bool:
    """Whether a folder of this name is never part of the upload folder: a
    hidden one (the name starts with a dot), or one of SYSTEM_FOLDERS in any
    case, because Windows and most shares ignore case. This is the one place
    that says so; the search for moved files, the following of a renamed
    folder, the answers about recorded paths and the check at start all ask
    here."""
    return name.startswith(".") or name.casefold() in _SYSTEM_FOLDERS_FOLDED


def is_outside_path(folder: str, own: tuple[frozenset[str], ...] = ()) -> bool:
    """Whether `folder`, relative to the upload folder, is or lies in a
    folder that is never part of it. `own` (see `layout_names`) holds, for
    each depth, the names the helper's own layout writes there. Such a folder
    is part of the upload folder whatever it is called: helpers before 1.0.3
    let a phone have "Recycled" as its folder, and the photos in it are
    really there."""
    for depth, part in enumerate(piece for piece in folder.split("/") if piece):
        if is_outside_name(part) and not (depth < len(own) and part in own[depth]):
            return True
    return False


def clean_folder_name(name: str, fallback: str = "iPhone") -> str:
    """A device's folder name as it will appear in the upload folder. Never
    the name of a system folder: photos stored there would not count as
    being in the upload folder."""
    cleaned = _clean_component(name, fallback, max_bytes=80)
    return fallback if is_outside_name(cleaned) else cleaned


def path_component(text: str) -> str:
    """One folder of a stored file's path, as `relative_folder` writes it."""
    return _clean_component(text, "_")


def extension_of(filename: str) -> str:
    return os.path.splitext(filename)[1].lstrip(".").lower()


def clean_filename(name: str, fallback_stem: str) -> str:
    """A safe file name that keeps the original name and extension.

    `fallback_stem` names the file when nothing usable is left of `name`.
    """
    # Only the last component counts, whichever separator the sender used.
    name = name.replace("\\", "/").rsplit("/", 1)[-1]
    stem, extension = os.path.splitext(name)
    extension = re.sub(r"[^A-Za-z0-9]", "", extension)[:10]
    stem = _clean_component(stem, fallback_stem, max_bytes=_MAX_NAME_BYTES - len(extension) - 1)
    return f"{stem}.{extension}" if extension else stem


def is_allowed_extension(filename: str, extra: frozenset[str] = frozenset()) -> bool:
    extension = extension_of(filename)
    return bool(extension) and (extension in MEDIA_EXTENSIONS or extension in extra)


def parse_created(text: str | None) -> _dt.datetime | None:
    """The photo's own date, as the phone sent it.

    The phone sends its local time with its UTC offset, for example
    `2026-11-21T22:15:03-06:00`. The folder is named from the local date, so a
    photo taken at 11 pm on the 31st lands in that month, whatever time zone
    the server is in.
    """
    if not text:
        return None
    try:
        parsed = _dt.datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if not 1900 <= parsed.year <= 2200:
        return None
    return parsed


def relative_folder(template: str, device_folder: str, created: _dt.datetime | None) -> str:
    """The folder, relative to the upload folder, for a file from this device."""
    when = created or _dt.datetime.now()
    values = {
        "device": device_folder,
        "year": f"{when.year:04d}",
        "month": f"{when.month:02d}",
        "day": f"{when.day:02d}",
    }
    parts = []
    for part in (piece for piece in template.split("/") if piece):
        # One pass: what a value brings with it is never read as a token. A
        # device whose folder is named "{year}" keeps that name.
        filled = re.sub(r"\{(device|year|month|day)\}", lambda match: values[match.group(1)], part)
        parts.append(path_component(filled))
    return "/".join(part for part in parts if part)


def layout_names(template: str, device_folders) -> tuple[frozenset[str], ...]:
    """For each folder of the layout, counted from the upload folder, the
    names the helper itself writes there for devices with these folders. A
    folder named for a date has none: a date is never a system folder's name."""
    names: list[frozenset[str]] = []
    for part in (piece for piece in template.split("/") if piece):
        if re.search(r"\{(year|month|day)\}", part):
            names.append(frozenset())
        elif "{device}" in part:
            names.append(frozenset(relative_folder(part, folder, None) for folder in device_folders))
        else:
            names.append(frozenset({relative_folder(part, "", None)}))
    return tuple(names)


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Storage:
    """The upload folder: free space, temporary files, and final placement."""

    def __init__(self, upload_dir: str, temp_dir: str, path_template: str):
        self.upload_dir = os.path.abspath(upload_dir)
        self.temp_dir = os.path.abspath(temp_dir)
        self.path_template = path_template
        self._keep_lock = threading.Lock()

    # -- state --------------------------------------------------------------

    def prepare(self) -> None:
        """Create the temporary folder and clear out abandoned uploads."""
        os.makedirs(self.temp_dir, exist_ok=True)
        self.sweep_temp(max_age_seconds=0)

    def sweep_temp(self, max_age_seconds: float = 24 * 3600) -> int:
        """Delete unfinished uploads older than `max_age_seconds`."""
        removed = 0
        cutoff = time.time() - max_age_seconds
        try:
            names = os.listdir(self.temp_dir)
        except OSError:
            return 0
        for name in names:
            path = os.path.join(self.temp_dir, name)
            try:
                if name.endswith(".part") and os.path.getmtime(path) <= cutoff:
                    os.unlink(path)
                    removed += 1
            except OSError:
                continue
        return removed

    def write_trouble(self) -> str | None:
        """None when the helper can write to the upload folder, else GONE or
        NOT_WRITABLE (see `trouble_of`)."""
        probe = os.path.join(self.temp_dir, f".probe-{secrets.token_hex(6)}")
        try:
            os.makedirs(self.temp_dir, exist_ok=True)
            with open(probe, "wb"):
                pass
            os.unlink(probe)
            return None
        except OSError as error:
            return trouble_of(error)

    def is_writable(self) -> bool:
        return self.write_trouble() is None

    def keep_temp_dir(self) -> None:
        """Make the temporary folder again if it is gone. It tells the next
        start that the upload folder is the right one, and a person who
        deletes everything in the upload folder deletes it too. Best effort:
        a folder that cannot be made is found by the next upload. Nearly
        always the folder is there, and then the disk is only read, because
        Docker's health check asks for this every 30 seconds.

        Only the hidden folder is made, never the upload folder itself: where
        that is gone (a disk that is not mounted), a folder made in its place
        would tell the next start that the wrong disk is the right one. And
        while one call waits for a share that does not answer, the next ones
        return at once, so that one thread at most ever waits there."""
        if not self._keep_lock.acquire(blocking=False):
            return
        try:
            if not os.path.isdir(self.temp_dir):
                os.mkdir(self.temp_dir)
        except OSError:
            pass
        finally:
            self._keep_lock.release()

    def disk_usage(self) -> tuple[int, int]:
        """(free bytes, total bytes) of the disk holding the upload folder."""
        try:
            usage = shutil.disk_usage(self.upload_dir)
        except OSError:
            return 0, 0
        return usage.free, usage.total

    # -- writing ------------------------------------------------------------

    def new_temp_path(self) -> str:
        os.makedirs(self.temp_dir, exist_ok=True)
        return os.path.join(self.temp_dir, f"{secrets.token_hex(16)}.part")

    def absolute(self, relpath: str) -> str:
        """The absolute path of `relpath`, refusing anything outside the folder."""
        path = os.path.abspath(os.path.join(self.upload_dir, relpath))
        if os.path.commonpath([path, self.upload_dir]) != self.upload_dir:
            raise StorageError("bad_request", "The path leaves the upload folder")
        return path

    def exists(self, relpath: str) -> bool:
        try:
            return os.path.isfile(self.absolute(relpath))
        except StorageError:
            return False

    def place(self, temp_path: str, device_folder: str, filename: str, created: _dt.datetime | None,
              sha256: str, size: int, sha_at_path, held=None) -> tuple[str, bool]:
        """Move a finished upload into its folder.

        `sha_at_path(relpath)` answers the recorded hash of a file the helper
        stored earlier, or None. `held(relpath)`, if given, says that a record
        of another photo still points at that name, even if its file is gone:
        the name is not used. Returns `(relpath, stored)`: `stored` is False
        when an identical file was already at that name, in which case the
        temporary file is deleted and the existing one is kept.
        """
        folder = relative_folder(self.path_template, device_folder, created)
        directory = self.absolute(folder)
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as error:
            raise storage_error_from(error) from error

        stem, extension = os.path.splitext(filename)
        for attempt in range(1, 1000):
            name = filename if attempt == 1 else f"{stem} ({attempt}){extension}"
            relpath = f"{folder}/{name}" if folder else name
            final = os.path.join(directory, name)
            if held is not None and held(relpath):
                continue
            try:
                # Creating the name with O_EXCL reserves it: two uploads that
                # want the same name cannot both get it, and nothing already
                # there is ever overwritten.
                descriptor = os.open(final, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
            except FileExistsError:
                if self._same_content(final, relpath, sha256, size, sha_at_path):
                    _unlink_quietly(temp_path)
                    return relpath, False
                continue
            except OSError as error:
                raise storage_error_from(error) from error
            os.close(descriptor)
            try:
                _move_into_place(temp_path, final)
            except OSError as error:
                _unlink_quietly(final)
                raise storage_error_from(error) from error
            if created is not None:
                # Plex dates a photo that carries no date of its own (a
                # screenshot, say) by the file's modification time.
                stamp = created.timestamp()
                try:
                    os.utime(final, (stamp, stamp))
                except (OSError, OverflowError, ValueError):
                    pass
            _sync_directory(directory)
            return relpath, True
        raise StorageError("server_error", "Too many files share this name")

    def _same_content(self, final: str, relpath: str, sha256: str, size: int, sha_at_path) -> bool:
        try:
            if os.path.getsize(final) != size:
                return False
        except OSError:
            return False
        recorded = sha_at_path(relpath)
        if recorded is not None:
            return recorded == sha256
        try:
            return file_sha256(final) == sha256
        except OSError:
            return False


#: Why the helper cannot write to the upload folder.
GONE = "gone"
NOT_WRITABLE = "not_writable"
#: What the helper says when the reason is GONE.
GONE_MESSAGE = ("The upload folder is gone, or it was replaced while the helper was running. "
                "Restart the helper.")


def trouble_of(error: OSError) -> str:
    """GONE when a failed write says that the upload folder itself is no
    longer there, else NOT_WRITABLE.

    Making the temporary folder makes a missing upload folder as well, so it
    fails with ENOENT only when nothing can be made where the upload folder
    was. That is so when the folder was removed and made again under a
    running container: the container still holds the removed one, until it is
    restarted. Another owner or other permissions would not help, so the
    helper must not advise them.
    """
    return GONE if error.errno == errno.ENOENT else NOT_WRITABLE


def storage_error_from(error: OSError) -> StorageError:
    """The API error for a failed write: a full disk, no permission, or other."""
    if error.errno in (errno.ENOSPC, errno.EDQUOT):
        return StorageError("insufficient_storage", "The server's disk is full")
    if error.errno in (errno.EACCES, errno.EPERM, errno.EROFS):
        return StorageError("not_writable", "The helper is not allowed to write to the upload folder")
    return StorageError("server_error", f"The file could not be stored ({errno.errorcode.get(error.errno, 'error')})")


def _move_into_place(temp_path: str, final: str) -> None:
    """Rename the finished upload over the name reserved for it.

    A rename is atomic. Pooled filesystems (mergerfs, unionfs) can refuse one
    between two of their disks; then the file is copied and synced instead.
    """
    try:
        os.replace(temp_path, final)
        return
    except OSError as error:
        if error.errno != errno.EXDEV:
            raise
    with open(temp_path, "rb") as source, open(final, "wb") as target:
        shutil.copyfileobj(source, target, 1024 * 1024)
        target.flush()
        os.fsync(target.fileno())
    _unlink_quietly(temp_path)


def _unlink_quietly(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass


def _sync_directory(directory: str) -> None:
    """Ask the disk to keep the new directory entry. Not every filesystem can."""
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)
