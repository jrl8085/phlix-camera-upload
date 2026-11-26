"""Since 1.0.2 a photo counts as backed up only while its file is in the
upload folder. Each test is something a person does to the files on the
server, and what the phone is told afterwards."""

import errno
import hashlib
import json
import os
import shutil
import socket
import sqlite3
import tempfile
import threading
import time
import unicodedata
import unittest
import urllib.parse
from unittest import mock

from phlix_upload import __main__ as main_module
from phlix_upload import config as config_module
from phlix_upload import presence, storage
from phlix_upload.store import Store, hash_token

from .helpers import key, running

CREATED = "2026-11-21T22:15:03-06:00"
MONTH = "2026/2026-11"


def put(helper, token, number, data=None, name=None, created=CREATED):
    """Upload photo `number`; returns (status, body)."""
    data = f"photo number {number}".encode() if data is None else data
    status, body, _ = helper.upload(token, key(number), data, filename=name or f"IMG_{number:04d}.HEIC",
                                    created=created)
    return status, body


def check(helper, token, numbers, hashes=None):
    """The check's answer, with keys turned back into photo numbers."""
    items = []
    for number in numbers:
        if hashes and number in hashes:
            items.append({"key": key(number), "sha256": hashes[number]})
        else:
            items.append(key(number))
    status, body, _ = helper.request("POST", "/api/v1/assets/check", {"items": items}, token=token)
    assert status == 200, (status, body)
    back = {key(number): number for number in numbers}
    return {field: [back[value] for value in values] for field, values in body.items()}


def disk(helper, relpath=""):
    return os.path.join(helper.upload_dir, relpath)


def path_of(number, folder="iPhone"):
    return f"{folder}/{MONTH}/IMG_{number:04d}.HEIC"


def asset_count(helper, token):
    return helper.request("GET", "/api/v1/status", token=token)[1]["device"]["assetCount"]


def pair(helper, device_id="device-0001", folder="iPhone", switch=None):
    body = {"method": "code", "code": helper.app.pairing_code, "deviceId": device_id, "deviceName": "iPhone",
            "folderName": folder}
    if switch is not None:
        body["switchFolder"] = switch
    status, payload, _ = helper.request("POST", "/api/v1/pair", body)
    assert status == 200, (status, payload)
    return payload["deviceToken"], payload["folder"]


def failing_stat(paths, code=errno.EIO):
    """os.stat fails with `code` for these paths, as a share having trouble does."""
    real = os.stat
    wanted = {os.fspath(path) for path in paths}

    def fake(path, *arguments, **keywords):
        if isinstance(path, (str, bytes, os.PathLike)) and os.fspath(path) in wanted:
            raise OSError(code, os.strerror(code), path)
        return real(path, *arguments, **keywords)

    return mock.patch.object(os, "stat", fake)


def wait_for(condition, seconds=5.0):
    """Whether `condition()` came true within `seconds`. The health check
    answers first and looks at the disk afterwards."""
    deadline = time.monotonic() + seconds
    while not condition() and time.monotonic() < deadline:
        time.sleep(0.01)
    return condition()


def count_stats(path):
    """Counts the looks (os.stat) at `path` while the block runs: `looks[0]`."""
    real = os.stat
    looks = [0]

    def spy(target, *arguments, **keywords):
        if isinstance(target, (str, bytes, os.PathLike)) and os.fspath(target) == path:
            looks[0] += 1
        return real(target, *arguments, **keywords)

    return mock.patch.object(os, "stat", spy), looks


class DeletedFilesTests(unittest.TestCase):
    def test_a_deleted_file_is_no_longer_backed_up_and_is_stored_again(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            put(helper, token, 2)
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1, 2]), {"known": [2]})
            self.assertEqual(asset_count(helper, token), 1)
            status, body = put(helper, token, 1)
            self.assertEqual((status, body["status"], body["path"]), (201, "stored", path_of(1)))
            self.assertEqual(check(helper, token, [1, 2]), {"known": [1, 2]})
            self.assertEqual(asset_count(helper, token), 2)

    def test_a_deleted_device_folder_is_sent_again_in_full(self):
        # The owner's case: the folder deleted on the server, the phone connected again.
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            shutil.rmtree(disk(helper, "iPhone"))
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": []})
            self.assertEqual(asset_count(helper, token), 0)
            for number in range(1, 4):
                self.assertEqual(put(helper, token, number)[1]["path"], path_of(number))
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2, 3]})
            self.assertEqual(helper.files(), [path_of(number) for number in range(1, 4)])

    def test_a_file_edited_in_place_still_counts(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            with open(disk(helper, path_of(1)), "wb") as handle:
                handle.write(b"the same photo with new tags, and longer")
            self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_a_file_back_where_it_was_counts_again(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            aside = os.path.join(helper.root, "aside.HEIC")
            os.rename(disk(helper, path_of(1)), aside)
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertIsNotNone(helper.app.store.asset("device-0001", key(1)).missing_at)
            os.rename(aside, disk(helper, path_of(1)))
            # The phone sends it before it asks again: the copy there is kept.
            status, body = put(helper, token, 1)
            self.assertEqual((status, body["status"]), (200, "duplicate"))
            self.assertIsNone(helper.app.store.asset("device-0001", key(1)).missing_at)
            self.assertEqual(asset_count(helper, token), 1)
            self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 0)

    def test_the_answer_says_left_out_only_when_something_is(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            _, body, _ = helper.request("POST", "/api/v1/assets/check", {"items": [key(1), key(2)]}, token=token)
            self.assertEqual(body, {"known": [key(1)]})

    def test_a_photo_that_keeps_disappearing_is_left_out_after_three_returns(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            for returned in range(1, 4):
                os.unlink(disk(helper, path_of(1)))
                self.assertEqual(check(helper, token, [1]), {"known": []})
                self.assertEqual(put(helper, token, 1)[0], 201)
                self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, returned)
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1, 2]), {"known": [], "leftOut": [1]})
            # Sent anyway, it is still taken.
            self.assertEqual(put(helper, token, 1)[0], 201)
            self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_a_device_folder_deleted_again_and_again_never_leaves_photos_out(self):
        # A person who starts over deletes the whole folder; a program that
        # takes new files away leaves the folders.
        with running() as helper:
            token = helper.pair()
            for number in range(1, 3):
                put(helper, token, number)
            for _ in range(4):
                shutil.rmtree(disk(helper, "iPhone"))
                self.assertEqual(check(helper, token, [1, 2]), {"known": []})
                self.assertEqual(asset_count(helper, token), 0)
                for number in range(1, 3):
                    self.assertEqual(put(helper, token, number)[0], 201)
            self.assertEqual(check(helper, token, [1, 2]), {"known": [1, 2]})
            # Counted since the folder was last deleted.
            self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 1)

    def test_a_year_folder_deleted_again_and_again_never_leaves_photos_out(self):
        # A person who tests deletes a folder inside the device's folder, and
        # does it again. Deleting a folder is never what a program does that
        # takes new files away, so no photo is left out for it. (With nine
        # photos the month's folder is listed; with two, each file is looked up.)
        for count in (2, 9):
            with self.subTest(photos=count), running() as helper:
                token = helper.pair()
                store = helper.app.store
                numbers = list(range(1, count + 1))
                for number in numbers:
                    put(helper, token, number)
                for _ in range(4):
                    shutil.rmtree(disk(helper, "iPhone/2026"))
                    self.assertEqual(check(helper, token, numbers), {"known": []})
                    self.assertEqual(store.asset("device-0001", key(1)).returns, 0)
                    self.assertIsNotNone(store.asset("device-0001", key(1)).missing_at)
                    for number in numbers:
                        self.assertEqual(put(helper, token, number)[0], 201)
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                # Counted since the folder was last deleted.
                self.assertEqual(store.asset("device-0001", key(2)).returns, 1)
                # Single files taken away, the folder left in place: counted as before.
                for returned in range(2, 4):
                    os.unlink(disk(helper, path_of(1)))
                    self.assertEqual(check(helper, token, numbers), {"known": numbers[1:]})
                    self.assertEqual(put(helper, token, 1)[0], 201)
                    self.assertEqual(store.asset("device-0001", key(1)).returns, returned)
                os.unlink(disk(helper, path_of(1)))
                self.assertEqual(check(helper, token, numbers), {"known": numbers[1:], "leftOut": [1]})

    def test_a_deleted_folder_lets_a_left_out_photo_be_sent_again(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            for _ in range(3):
                os.unlink(disk(helper, path_of(1)))
                check(helper, token, [1])
                put(helper, token, 1)
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1]), {"known": [], "leftOut": [1]})
            # The month's folder goes too: now a person did it.
            os.rmdir(disk(helper, f"iPhone/{MONTH}"))
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 0)
            self.assertEqual(put(helper, token, 1)[0], 201)
            self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_a_deleted_folder_restarts_the_count_of_photos_asked_about_later(self):
        # The phone asks about its photos in several requests. The photos of
        # the first request, sent again, make the folder again before the
        # others are asked about.
        with running() as helper:
            token = helper.pair()
            other = helper.pair("device-0002", folder="Alex")
            store = helper.app.store
            for number in range(1, 3):
                put(helper, token, number)
            # The same photo on a second phone: its record points at the first one's file.
            self.assertEqual(put(helper, other, 5, b"photo number 2")[1]["status"], "duplicate")
            with store.transaction():
                store._db.execute("UPDATE assets SET returns = 2 WHERE device_id = 'device-0002'")
            put(helper, token, 3, created="2025-06-01T10:00:00+02:00")
            for time_deleted in range(1, 5):
                shutil.rmtree(disk(helper, f"iPhone/{MONTH}"))
                os.unlink(disk(helper, "iPhone/2025/2025-06/IMG_0003.HEIC"))
                self.assertEqual(check(helper, token, [1]), {"known": []})
                self.assertEqual(store.asset("device-0002", key(5)).returns, 0)
                self.assertEqual(put(helper, token, 1)[0], 201)
                # Asked about only now, with their folder there again. The
                # photo in a folder that was never deleted went away by
                # itself each time, and is left out the fourth time as before.
                self.assertEqual(check(helper, token, [2, 3]),
                                 {"known": []} if time_deleted < 4 else {"known": [], "leftOut": [3]})
                self.assertEqual(check(helper, other, [5]), {"known": []})
                self.assertEqual(put(helper, token, 2)[0], 201)
                self.assertEqual(put(helper, other, 5, b"photo number 2")[0], 200)
                if time_deleted < 4:
                    self.assertEqual(put(helper, token, 3, created="2025-06-01T10:00:00+02:00")[0], 201)
            self.assertEqual(store.asset("device-0001", key(2)).returns, 1)
            self.assertEqual(store.asset("device-0001", key(3)).returns, 3)
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2], "leftOut": [3]})

    def test_an_upload_that_makes_a_deleted_folder_again_restarts_the_count(self):
        # The folder is deleted while the phone is still sending. A photo just
        # taken arrives before the phone asks about the others, and its upload
        # makes the folder again: the check then finds the folder in place.
        with running() as helper:
            token = helper.pair()
            store = helper.app.store
            put(helper, token, 1)
            put(helper, token, 2)
            # Photo 2 was sorted into the year's folder, and photo 3 keeps the device's folder there.
            os.rename(disk(helper, path_of(2)), disk(helper, "iPhone/2026/IMG_0002.HEIC"))
            put(helper, token, 3, created="2025-06-01T10:00:00+02:00")
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2, 3]})
            self.assertEqual(store.asset("device-0001", key(2)).relpath, "iPhone/2026/IMG_0002.HEIC")
            for time_deleted in range(4):
                shutil.rmtree(disk(helper, "iPhone/2026"))
                self.assertEqual(put(helper, token, 10 + time_deleted)[0], 201)
                self.assertTrue(os.path.isdir(disk(helper, f"iPhone/{MONTH}")))
                self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [3]})
                self.assertEqual(put(helper, token, 1)[0], 201)
                self.assertEqual(put(helper, token, 2)[0], 201)
                os.rename(disk(helper, path_of(2)), disk(helper, "iPhone/2026/IMG_0002.HEIC"))
                self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2, 3]})
            # Counted since the folder was last deleted.
            self.assertEqual(store.asset("device-0001", key(1)).returns, 1)
            self.assertEqual(store.asset("device-0001", key(2)).returns, 1)
            # A month's folder that is made for the first time changes no count.
            with store.transaction():
                store._db.execute("UPDATE assets SET returns = 3 WHERE key = ?", (key(1),))
            self.assertEqual(put(helper, token, 30, created="2026-12-01T10:00:00+02:00")[0], 201)
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [2, 3], "leftOut": [1]})

    def test_a_file_where_a_deleted_folder_was_is_a_deleted_folder(self):
        # Nothing can be in a folder whose name is a file's now, or that lies
        # under a file: the folder is gone for sure, not out of sight.
        for place in (f"iPhone/{MONTH}", "iPhone/2026"):
            with self.subTest(file=place), running() as helper:
                token = helper.pair()
                put(helper, token, 1)
                with helper.app.store.transaction():
                    helper.app.store._db.execute("UPDATE assets SET returns = 3")
                shutil.rmtree(disk(helper, "iPhone/2026"))
                os.makedirs(os.path.dirname(disk(helper, place)), exist_ok=True)
                with open(disk(helper, place), "wb"):
                    pass
                self.assertEqual(presence.folder_state(disk(helper, f"iPhone/{MONTH}")), presence.MISSING)
                self.assertEqual(check(helper, token, [1]), {"known": []})
                self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 0)

    def test_a_folder_that_cannot_be_looked_at_changes_no_count(self):
        # Only a folder that is surely gone says that a person deleted it.
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            for _ in range(3):
                os.unlink(disk(helper, path_of(1)))
                check(helper, token, [1])
                put(helper, token, 1)
            folder = disk(helper, f"iPhone/{MONTH}")
            shutil.rmtree(folder)
            with failing_stat([folder]):
                self.assertEqual(check(helper, token, [1]), {"known": [], "leftOut": [1]})
            self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 3)

    def test_connecting_again_after_deleting_the_folder_sends_every_photo_again(self):
        # The owner's test, done again and again: the folder deleted on the
        # server, the phone connected again with a new folder name.
        with running() as helper:
            token = helper.pair()
            folder = "iPhone"
            for number in range(1, 3):
                put(helper, token, number)
            for round_number in range(2, 7):
                shutil.rmtree(disk(helper, folder))
                token, folder = pair(helper, folder=f"Phlix {round_number}", switch=True)
                self.assertEqual(check(helper, token, [1, 2]), {"known": []})
                for number in range(1, 3):
                    self.assertEqual(put(helper, token, number)[1]["path"], path_of(number, folder))
            self.assertEqual(check(helper, token, [1, 2]), {"known": [1, 2]})

    def test_pairing_again_lets_a_left_out_photo_be_sent_again(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            for _ in range(3):
                os.unlink(disk(helper, path_of(1)))
                check(helper, token, [1])
                put(helper, token, 1)
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1]), {"known": [], "leftOut": [1]})
            # Only a person pairs a phone again.
            token, _ = pair(helper)
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(put(helper, token, 1)[0], 201)
            self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_a_file_that_stayed_a_while_starts_the_count_again(self):
        with running() as helper:
            token = helper.pair()
            store = helper.app.store
            put(helper, token, 1)
            for _ in range(2):
                os.unlink(disk(helper, path_of(1)))
                check(helper, token, [1])
                put(helper, token, 1)
            self.assertEqual(store.asset("device-0001", key(1)).returns, 2)
            # This time it stays eight days before it is deleted: a person did that.
            with store.transaction():
                store._db.execute("UPDATE assets SET stored_at = stored_at - ?", (8 * 86400,))
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(put(helper, token, 1)[0], 201)
            self.assertEqual(store.asset("device-0001", key(1)).returns, 0)
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1]), {"known": []})

    def test_a_new_photo_never_takes_the_name_of_a_deleted_one(self):
        # Otherwise the record of the deleted photo would point at the new
        # file, and that photo would count as backed up for good.
        with running() as helper:
            token = helper.pair()
            first = f"iPhone/{MONTH}/DSC_0001.JPG"
            put(helper, token, 1, name="DSC_0001.JPG")
            os.unlink(disk(helper, first))
            status, body = put(helper, token, 2, name="DSC_0001.JPG")
            self.assertEqual((status, body["path"]), (201, f"iPhone/{MONTH}/DSC_0001 (2).JPG"))
            self.assertEqual(check(helper, token, [1, 2]), {"known": [2]})
            # The deleted photo sent again gets its own name back.
            self.assertEqual(put(helper, token, 1, name="DSC_0001.JPG")[1]["path"], first)
            self.assertEqual(check(helper, token, [1, 2]), {"known": [1, 2]})

    def test_a_file_put_back_counts_again_when_the_phone_asks(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            aside = os.path.join(helper.root, "aside.HEIC")
            os.rename(disk(helper, path_of(1)), aside)
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(asset_count(helper, token), 0)
            os.rename(aside, disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertIsNone(helper.app.store.asset("device-0001", key(1)).missing_at)
            self.assertEqual(asset_count(helper, token), 1)


class ShareTroubleTests(unittest.TestCase):
    def test_a_file_that_cannot_be_looked_at_counts_as_there_with_one_warning(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            put(helper, token, 2)
            os.unlink(disk(helper, path_of(2)))
            with failing_stat([disk(helper, path_of(1))]):
                with self.assertLogs("phlix.presence", level="WARNING") as logs:
                    self.assertEqual(check(helper, token, [1, 2]), {"known": [1]})
                self.assertIn("EIO", "\n".join(logs.output))
                with self.assertNoLogs("phlix.presence", level="WARNING"):
                    self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertIsNone(helper.app.store.asset("device-0001", key(1)).missing_at)

    def test_a_folder_that_cannot_be_listed_counts_as_there(self):
        with running() as helper:
            token = helper.pair()
            numbers = list(range(1, 9))
            for number in numbers:
                put(helper, token, number)
            folder = disk(helper, f"iPhone/{MONTH}")
            real = os.scandir

            def broken(path=".", *arguments):
                if os.fspath(path) == folder:
                    raise OSError(errno.EIO, "Input/output error", path)
                return real(path, *arguments)

            with mock.patch.object(os, "scandir", broken), self.assertLogs("phlix.presence", level="WARNING"):
                self.assertEqual(check(helper, token, numbers), {"known": numbers})

    def test_with_the_bytes_in_hand_an_unseen_file_does_not_count(self):
        # A guess may answer a check; it never throws away an upload.
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            with failing_stat([disk(helper, path_of(1))]):
                status, body = put(helper, token, 1)
            self.assertEqual((status, body["status"]), (201, "stored"))
            self.assertEqual(body["path"], f"iPhone/{MONTH}/IMG_0001 (2).HEIC")
            # Not seen is not gone: it does not count as coming back.
            self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 0)

    def test_a_twin_whose_file_is_gone_is_not_used(self):
        data = b"a photo both phones hold"
        sha = hashlib.sha256(data).hexdigest()
        with running() as helper:
            first, _ = pair(helper, "device-0001", "Anna")
            second, _ = pair(helper, "device-0002", "Alex")
            put(helper, first, 1, data)
            os.unlink(disk(helper, path_of(1, "Anna")))
            self.assertEqual(check(helper, second, [2], {2: sha}), {"known": []})
            status, body = put(helper, second, 2, data, name="IMG_0001.HEIC")
            self.assertEqual((status, body["path"]), (201, path_of(1, "Alex")))

    def test_a_twin_that_cannot_be_looked_at_is_not_used(self):
        data = b"a photo both phones hold"
        sha = hashlib.sha256(data).hexdigest()
        with running() as helper:
            first, _ = pair(helper, "device-0001", "Anna")
            second, _ = pair(helper, "device-0002", "Alex")
            put(helper, first, 1, data)
            with failing_stat([disk(helper, path_of(1, "Anna"))]):
                self.assertEqual(check(helper, second, [2], {2: sha}), {"known": []})
                status, body = put(helper, second, 2, data, name="IMG_0001.HEIC")
            self.assertEqual((status, body["path"]), (201, path_of(1, "Alex")))


class HowTheDiskIsReadTests(unittest.TestCase):
    def _count_listings(self, helper, token, numbers):
        folder = disk(helper, f"iPhone/{MONTH}")
        listed = []
        real = os.scandir

        def spy(path=".", *arguments):
            if os.fspath(path) == folder:
                listed.append(path)
            return real(path, *arguments)

        with mock.patch.object(os, "scandir", spy):
            self.assertEqual(check(helper, token, numbers), {"known": numbers})
        return len(listed)

    def test_a_folder_with_many_of_the_photos_is_listed_once(self):
        with running() as helper:
            token = helper.pair()
            for number in range(1, 9):
                put(helper, token, number)
            self.assertEqual(self._count_listings(helper, token, list(range(1, 9))), 1)
            self.assertEqual(self._count_listings(helper, token, list(range(1, 8))), 0)

    def test_a_folder_is_looked_at_once_at_most_whatever_it_holds(self):
        # On a slow share every look is a round trip. A folder that is listed
        # needs no other look, and one whose files are looked up one by one
        # is asked about once when a file is missing, not once for each file.
        month = f"iPhone/{MONTH}"
        for count, looks_when_gone in ((5, 1), (9, 0)):
            with self.subTest(photos=count), running() as helper:
                token = helper.pair()
                numbers = list(range(1, count + 1))
                for number in numbers:
                    put(helper, token, number)
                # Keeps the device's folder in place, and the search for moved files out of the count.
                put(helper, token, 50, created="2025-06-01T10:00:00+02:00")
                helper.app.verifier.index.refresh = lambda wait: None
                counting, looks = count_stats(disk(helper, month))
                with counting:
                    self.assertEqual(check(helper, token, numbers), {"known": numbers})
                    self.assertEqual(looks[0], 0)
                    # Files taken away, the folder left in place.
                    os.unlink(disk(helper, path_of(1)))
                    os.unlink(disk(helper, path_of(2)))
                    self.assertEqual(check(helper, token, numbers), {"known": numbers[2:]})
                    self.assertEqual(looks[0], 0 if count >= presence.LIST_FROM else 1)
                    looks[0] = 0
                    shutil.rmtree(disk(helper, "iPhone/2026"))
                    self.assertEqual(check(helper, token, numbers), {"known": []})
                    self.assertEqual(looks[0], looks_when_gone)
                self.assertEqual(helper.app.store.asset("device-0001", key(1)).returns, 0)

    def test_a_name_spelt_another_way_on_disk_is_still_found(self):
        # A Mac writes "e" and the accent as two characters (NFD); the helper writes one.
        nfc = unicodedata.normalize("NFC", "Café")
        nfd = unicodedata.normalize("NFD", nfc)
        for count in (1, 8):
            with self.subTest(photos=count), running() as helper:
                token = helper.pair()
                numbers = list(range(1, count + 1))
                for number in numbers:
                    put(helper, token, number, name=f"{nfc} {number}.HEIC")
                for number in numbers:
                    stored = disk(helper, f"iPhone/{MONTH}/{nfc} {number}.HEIC")
                    with open(stored, "rb") as handle:
                        data = handle.read()
                    os.unlink(stored)
                    respelt = disk(helper, f"iPhone/{MONTH}/{nfd} {number}.HEIC")
                    with open(respelt, "wb") as handle:
                        handle.write(data)
                    stamp = storage.parse_created(CREATED).timestamp()
                    os.utime(respelt, (stamp, stamp))
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                for number in numbers:
                    relpath = helper.app.store.asset("device-0001", key(number)).relpath
                    self.assertTrue(os.path.isfile(disk(helper, relpath)), relpath)

    def test_two_thousand_missing_files_are_noted_in_one_go(self):
        with running() as helper:
            token = helper.pair()
            store = helper.app.store
            numbers = list(range(2000))
            with store.transaction():
                for number in numbers:
                    store.record_asset("device-0001", key(number), hashlib.sha256(b"%d" % number).hexdigest(),
                                       path_of(number), 10, "photo", CREATED)
            os.makedirs(disk(helper, f"iPhone/{MONTH}"))
            statements = []
            store._db.set_trace_callback(statements.append)
            started = time.monotonic()
            self.assertEqual(check(helper, token, numbers), {"known": []})
            elapsed = time.monotonic() - started
            store._db.set_trace_callback(None)
            self.assertEqual(store.device_totals("device-0001"), (0, 0))
            # One transaction, not one sync to disk for each record: on a NAS
            # that is the difference between a moment and minutes.
            self.assertLess(elapsed, 2.5)
            inside, alone, transactions = False, 0, 0
            for statement in statements:
                word = statement.split(None, 1)[0].upper()
                if word == "BEGIN":
                    inside, transactions = True, transactions + 1
                elif word in ("COMMIT", "ROLLBACK"):
                    inside = False
                elif word in ("INSERT", "UPDATE", "DELETE") and " assets " in statement and not inside:
                    alone += 1
            self.assertEqual((alone, transactions), (0, 1))


class MovedFilesTests(unittest.TestCase):
    def test_a_file_sorted_into_another_folder_is_found_there(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.makedirs(disk(helper, "Sorted/Trip"))
            os.rename(disk(helper, path_of(1)), disk(helper, "Sorted/Trip/IMG_0001.HEIC"))
            self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertEqual(helper.app.store.asset("device-0001", key(1)).relpath, "Sorted/Trip/IMG_0001.HEIC")
            self.assertEqual(asset_count(helper, token), 1)
            status, body = put(helper, token, 1)
            self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", "Sorted/Trip/IMG_0001.HEIC"))
            self.assertEqual(helper.files(), ["Sorted/Trip/IMG_0001.HEIC"])

    def test_a_moved_file_whose_date_changed_is_found_by_its_content(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.makedirs(disk(helper, "Sorted"))
            moved = disk(helper, "Sorted/img_0001.heic")
            os.rename(disk(helper, path_of(1)), moved)
            os.utime(moved, None)
            self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_a_moved_file_of_another_size_or_too_large_to_read_is_not_taken(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            put(helper, token, 2)
            os.makedirs(disk(helper, "Sorted"))
            for number in (1, 2):
                os.rename(disk(helper, path_of(number)), disk(helper, f"Sorted/IMG_{number:04d}.HEIC"))
            with open(disk(helper, "Sorted/IMG_0001.HEIC"), "ab") as handle:
                handle.write(b" edited")
            os.utime(disk(helper, "Sorted/IMG_0002.HEIC"), None)
            with mock.patch.object(presence, "HASH_LIMIT", 4):
                self.assertEqual(check(helper, token, [1, 2]), {"known": []})
            # With its date kept, a large file needs no reading.
            stamp = storage.parse_created(CREATED).timestamp()
            os.utime(disk(helper, "Sorted/IMG_0002.HEIC"), (stamp, stamp))
            helper.app.verifier.index.clock = lambda: time.monotonic() + 3600
            with mock.patch.object(presence, "HASH_LIMIT", 4):
                self.assertEqual(check(helper, token, [1, 2]), {"known": [2]})

    def test_a_renamed_file_is_sent_again_and_both_copies_stay(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.rename(disk(helper, path_of(1)), disk(helper, f"iPhone/{MONTH}/Beach.HEIC"))
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(put(helper, token, 1)[1]["path"], path_of(1))
            self.assertEqual(helper.files(), [f"iPhone/{MONTH}/Beach.HEIC", path_of(1)])

    def test_a_file_moved_out_of_the_upload_folder_is_sent_again(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.rename(disk(helper, path_of(1)), os.path.join(helper.root, "IMG_0001.HEIC"))
            self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(put(helper, token, 1)[0], 201)

    def test_a_device_folder_moved_into_another_folder_is_found_there(self):
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            os.makedirs(disk(helper, "Archive"))
            os.rename(disk(helper, "iPhone"), disk(helper, "Archive/iPhone"))
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2, 3]})
            self.assertEqual(helper.app.store.asset("device-0001", key(2)).relpath, "Archive/" + path_of(2))
            # Not renamed next to where it was, so new photos go to the folder's own name.
            self.assertEqual(put(helper, token, 4)[1]["path"], path_of(4))

    def test_the_index_is_brought_up_to_date_at_most_once_a_minute(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            put(helper, token, 2)
            os.makedirs(disk(helper, "A"))
            os.rename(disk(helper, path_of(1)), disk(helper, "A/IMG_0001.HEIC"))
            hour_ago = time.time() - 3600
            for root, folders, _ in os.walk(helper.upload_dir):
                for name in folders:
                    os.utime(os.path.join(root, name), (hour_ago, hour_ago))
            os.utime(helper.upload_dir, (hour_ago, hour_ago))
            now = [1000.0]
            index = helper.app.verifier.index
            index.clock = lambda: now[0]
            self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertEqual(index.scans, 1)
            listed = index.listings
            os.makedirs(disk(helper, "B"))
            os.rename(disk(helper, path_of(2)), disk(helper, "B/IMG_0002.HEIC"))
            # Less than a minute later the index is as it was.
            now[0] += 30
            self.assertEqual(check(helper, token, [2]), {"known": []})
            self.assertEqual(index.scans, 1)
            now[0] += 31
            # The check starts the new scan and answers with the index there is.
            gate = threading.Event()
            real = index._scan
            index._scan = lambda: (gate.wait(5), real())
            self.assertEqual(check(helper, token, [2]), {"known": []})
            gate.set()
            self.assertTrue(index._idle.wait(5))
            self.assertEqual(index.scans, 2)
            self.assertEqual(check(helper, token, [2]), {"known": [2]})
            self.assertEqual(index.scans, 2)
            # Listed again: the upload folder, the month the photo left, and B. Not A, iPhone or 2026.
            self.assertEqual(index.listings - listed, 3)

    def test_a_check_waits_for_the_index_only_so_long(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.makedirs(disk(helper, "Sorted"))
            os.rename(disk(helper, path_of(1)), disk(helper, "Sorted/IMG_0001.HEIC"))
            index = helper.app.verifier.index
            real = index._scan
            index._scan = lambda: (time.sleep(1.5), real())
            with mock.patch.object(presence, "INDEX_WAIT_SECONDS", 0.3):
                started = time.monotonic()
                self.assertEqual(check(helper, token, [1]), {"known": []})
                self.assertLess(time.monotonic() - started, 1.2)
                index._idle.wait(5)
                self.assertEqual(check(helper, token, [1]), {"known": [1]})
            # Once there is an index, a check never waits for a newer one.
            os.makedirs(disk(helper, "Other"))
            os.rename(disk(helper, "Sorted/IMG_0001.HEIC"), disk(helper, "Other/IMG_0001.HEIC"))
            index.clock = lambda: time.monotonic() + 3600
            with mock.patch.object(presence, "INDEX_WAIT_SECONDS", 5.0):
                started = time.monotonic()
                self.assertEqual(check(helper, token, [1]), {"known": []})
                self.assertLess(time.monotonic() - started, 1.2)
            self.assertTrue(index._idle.wait(5))
            self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_hidden_and_system_folders_and_links_are_not_searched(self):
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            for number, folder in ((1, ".hidden"), (2, "@eaDir")):
                os.makedirs(disk(helper, folder))
                os.rename(disk(helper, path_of(number)), disk(helper, f"{folder}/IMG_{number:04d}.HEIC"))
            outside = os.path.join(helper.root, "outside")
            os.makedirs(outside)
            os.rename(disk(helper, path_of(3)), os.path.join(outside, "IMG_0003.HEIC"))
            os.symlink(outside, disk(helper, "Linked"))
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": []})

    def test_a_recycle_bin_is_not_the_upload_folder(self):
        # With a whole Windows drive as the upload folder, a deleted folder
        # stays in $RECYCLE.BIN with every name, size and date kept.
        bins = ["$RECYCLE.BIN/S-1-5-21/$R8KQ2ZD", "Sorted/$Recycle.Bin", "System Volume Information",
                "system volume information/deep", "Recycler", "RECYCLED/DC1", "#Recycle"]
        with running() as helper:
            token = helper.pair()
            numbers = list(range(1, len(bins) + 2))
            for number in numbers:
                put(helper, token, number)
            for number, folder in enumerate(bins, 1):
                if not os.path.isdir(disk(helper, folder)):
                    os.makedirs(disk(helper, folder))
                os.rename(disk(helper, path_of(number)), disk(helper, f"{folder}/IMG_{number:04d}.HEIC"))
            # One file sorted into a folder of the person's own, to show that the others were looked for.
            os.makedirs(disk(helper, "Sorted/Trip"))
            os.rename(disk(helper, path_of(numbers[-1])), disk(helper, f"Sorted/Trip/IMG_{numbers[-1]:04d}.HEIC"))
            self.assertEqual(check(helper, token, numbers), {"known": [numbers[-1]]})
            index = helper.app.verifier.index
            self.assertEqual(index.lookup("IMG_0001.HEIC"), [])
            self.assertEqual(index.lookup("IMG_0003.HEIC"), [])
            self.assertEqual(index.lookup(f"IMG_{numbers[-1]:04d}.HEIC"), [f"Sorted/Trip/IMG_{numbers[-1]:04d}.HEIC"])
            self.assertEqual(put(helper, token, 1)[1]["path"], path_of(1))

    def test_a_record_that_points_into_a_recycle_bin_is_answered_missing(self):
        # What helper 1.0.2 may have left: the device's folder was deleted on
        # Windows, and every record was pointed at the file in the recycle bin.
        binned = "$RECYCLE.BIN/S-1-5-21/$R8KQ2ZD"
        data = b"a photo both phones hold"
        for count in (2, 9):
            with self.subTest(photos=count), running() as helper:
                token = helper.pair()
                other = helper.pair("device-0002", folder="Alex")
                store = helper.app.store
                numbers = list(range(1, count + 1))
                put(helper, token, 1, data)
                for number in numbers[1:]:
                    put(helper, token, number)
                os.makedirs(disk(helper, "$RECYCLE.BIN/S-1-5-21"))
                os.rename(disk(helper, "iPhone"), disk(helper, binned))
                for number in numbers:
                    self.assertTrue(store.repoint(store.asset("device-0001", key(number)),
                                                  path_of(number, binned)))
                # One of them was left out before its folder was deleted.
                with store.transaction():
                    store._db.execute("UPDATE assets SET returns = 3 WHERE key = ?", (key(2),))
                self.assertTrue(os.path.isfile(disk(helper, path_of(1, binned))))
                self.assertEqual(asset_count(helper, token), count)
                self.assertEqual(helper.app.verifier.state(path_of(1, binned)), presence.MISSING)
                # A photo in the recycle bin is no twin: neither for a check nor for an upload.
                sha = hashlib.sha256(data).hexdigest()
                self.assertEqual(check(helper, other, [50], {50: sha}), {"known": []})
                status, body = put(helper, other, 50, data)
                self.assertEqual((status, body["status"], body["path"]), (201, "stored", path_of(50, "Alex")))
                shutil.rmtree(disk(helper, "Alex"))
                self.assertEqual(check(helper, token, numbers), {"known": []})
                self.assertEqual(asset_count(helper, token), 0)
                self.assertEqual(store.asset("device-0001", key(2)).returns, 0)
                # Sent again, each photo gets a real path, and what is in the recycle bin stays there.
                for number in numbers:
                    status, body = put(helper, token, number, data if number == 1 else None)
                    self.assertEqual((status, body["status"], body["path"]), (201, "stored", path_of(number)))
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(store.asset("device-0001", key(1)).relpath, path_of(1))
                self.assertTrue(os.path.isfile(disk(helper, path_of(1, binned))))

    def test_a_record_that_points_into_a_recycle_bin_further_down_is_answered_missing(self):
        # A NAS keeps a recycle bin in each shared folder, and a share may be a folder of the upload folder.
        binned = "Sorted/#recycle"
        for count in (2, 9):
            with self.subTest(photos=count), running() as helper:
                token = helper.pair()
                store = helper.app.store
                numbers = list(range(1, count + 1))
                for number in numbers:
                    put(helper, token, number)
                os.makedirs(disk(helper, "Sorted"))
                os.rename(disk(helper, "iPhone"), disk(helper, binned))
                for number in numbers:
                    self.assertTrue(store.repoint(store.asset("device-0001", key(number)), path_of(number, binned)))
                self.assertTrue(os.path.isfile(disk(helper, path_of(1, binned))))
                self.assertEqual(helper.app.verifier.state(path_of(1, binned)), presence.MISSING)
                self.assertEqual(check(helper, token, numbers), {"known": []})
                self.assertEqual(asset_count(helper, token), 0)
                self.assertEqual(put(helper, token, 1)[1]["path"], path_of(1))

    def test_a_phone_that_already_has_a_system_folders_name_keeps_its_photos(self):
        # Helpers before 1.0.3 gave a phone the folder it asked for, whatever
        # the name. The photos in it are really there, and must not be sent
        # again on every run.
        with running() as helper:
            token = helper.pair()
            other = helper.pair("device-0002", folder="Alex")
            store = helper.app.store
            with store.transaction():
                store._db.execute("UPDATE devices SET folder = 'Recycled' WHERE id = 'device-0001'")
                store._db.execute("UPDATE device_folders SET folder = 'Recycled' WHERE device_id = 'device-0001'")
            data = b"a photo both phones hold"
            for status, answer in ((201, "stored"), (200, "duplicate")):
                self.assertEqual(put(helper, token, 1, data)[1], {"status": answer, "path": path_of(1, "Recycled"),
                                                                  "bytes": len(data)})
                self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertEqual(helper.app.verifier.state(path_of(1, "Recycled")), presence.PRESENT)
            self.assertEqual(asset_count(helper, token), 1)
            # The other phone's same photo is that file.
            self.assertEqual(check(helper, other, [50], {50: hashlib.sha256(data).hexdigest()}), {"known": [50]})
            # A deleted file there is missing as anywhere, and the folder's name restarts no count.
            with store.transaction():
                store._db.execute("UPDATE assets SET returns = 3 WHERE device_id = 'device-0001'")
            os.unlink(disk(helper, path_of(1, "Recycled")))
            self.assertEqual(check(helper, token, [1]), {"known": [], "leftOut": [1]})
            # Only the folder the layout made has that right. A recycle bin
            # in it, or the same name in another place or another case, has not.
            put(helper, token, 2)
            for folder in ("Recycled/$RECYCLE.BIN", "Sorted/Recycled", "RECYCLED"):
                os.makedirs(disk(helper, folder), exist_ok=True)
                moved = f"{folder}/IMG_0002.HEIC"
                os.rename(disk(helper, store.asset("device-0001", key(2)).relpath), disk(helper, moved))
                self.assertTrue(store.repoint(store.asset("device-0001", key(2)), moved))
                self.assertEqual(helper.app.verifier.state(moved), presence.MISSING, folder)
                self.assertEqual(check(helper, token, [2]), {"known": []}, folder)

    def test_a_layout_that_names_a_system_folder_still_counts_its_photos(self):
        for template, path in (("Recycled/{device}/{year}", "Recycled/iPhone/2026/IMG_0001.HEIC"),
                               ("{device}/Recycled/{year}", "iPhone/Recycled/2026/IMG_0001.HEIC"),
                               ("{year}/lost+found/{device}", "2026/lost+found/iPhone/IMG_0001.HEIC")):
            with self.subTest(template=template), running(PATH_TEMPLATE=template) as helper:
                token = helper.pair()
                for status, answer in ((201, "stored"), (200, "duplicate")):
                    self.assertEqual(put(helper, token, 1)[1]["status"], answer)
                    self.assertEqual(put(helper, token, 1)[1]["path"], path)
                    self.assertEqual(check(helper, token, [1]), {"known": [1]})

    def test_a_device_folder_is_never_followed_into_a_system_folder(self):
        outside = ["$Recycle.Bin", "system volume information", "Recycler", "RECYCLED", "#Recycle", "@eadir",
                   "Lost+Found", ".hidden"]
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            os.rename(disk(helper, "iPhone"), disk(helper, outside[0]))
            for name in outside[1:] + ["Holiday"]:
                os.makedirs(disk(helper, name))
            device = helper.app.store.device("device-0001")
            self.assertEqual(helper.app.verifier._siblings("", device), ["Holiday"])
            # The folder that holds every file of the device is the recycle bin: not followed, not searched.
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": []})
            self.assertEqual(helper.request("GET", "/api/v1/status", token=token)[1]["device"]["folder"], "iPhone")
            self.assertEqual(put(helper, token, 1)[1]["path"], path_of(1))

    def test_a_phone_is_never_given_a_system_folder_as_its_own(self):
        with running() as helper:
            for number, name in enumerate(("$RECYCLE.BIN", "recycled", "System Volume Information", "@eaDir")):
                _, folder = pair(helper, f"device-000{number}", folder=name)
                self.assertEqual(folder, "iPhone" if number == 0 else f"iPhone {number + 1}")

    def test_the_index_holds_at_most_so_many_names(self):
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            os.makedirs(disk(helper, "Sorted"))
            for number in range(1, 4):
                os.rename(disk(helper, path_of(number)), disk(helper, f"Sorted/IMG_{number:04d}.HEIC"))
            index = helper.app.verifier.index
            with mock.patch.object(type(index), "MAX_NAMES", 2), \
                    self.assertLogs("phlix.presence", level="WARNING") as logs:
                self.assertEqual(len(check(helper, token, [1, 2, 3])["known"]), 2)
            self.assertIn("more than 2 files", "\n".join(logs.output))

    def test_a_very_large_folder_is_listed_once_a_minute_at_most(self):
        with running(PATH_TEMPLATE="{device}") as helper:
            token = helper.pair()
            numbers = list(range(1, 13))
            for number in numbers:
                put(helper, token, number)
            folder = disk(helper, "iPhone")
            # A folder that changed a moment ago is listed again sooner.
            hour_ago = time.time() - 3600
            os.utime(folder, (hour_ago, hour_ago))
            listed = []
            real = os.scandir

            def spy(path=".", *arguments):
                if os.fspath(path) == folder:
                    listed.append(path)
                return real(path, *arguments)

            with mock.patch.object(presence, "BIG_FOLDER", 10), mock.patch.object(os, "scandir", spy):
                # The first listing finds the folder that large. From the second
                # on, its time is read first and the listing is kept.
                for _ in range(4):
                    self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(len(listed), 2)
                helper.app.verifier.clock = lambda: time.monotonic() + 61
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(len(listed), 3)

    def test_a_kept_listing_is_dropped_when_its_folder_changes(self):
        with running(PATH_TEMPLATE="{device}") as helper:
            token = helper.pair()
            numbers = list(range(1, 13))
            for number in numbers:
                put(helper, token, number)
            folder = disk(helper, "iPhone")
            # Not changed a moment ago, so its listing is kept for the full minute.
            hour_ago = time.time() - 3600
            os.utime(folder, (hour_ago, hour_ago))
            # The search for moved files lists folders too, and is not what is counted here.
            helper.app.verifier.index.refresh = lambda wait: None
            listed = []
            real = os.scandir

            def spy(path=".", *arguments):
                if path == folder:
                    listed.append(path)
                return real(path, *arguments)

            with mock.patch.object(presence, "BIG_FOLDER", 10), mock.patch.object(os, "scandir", spy):
                # Listed once to find it that large, and once more to keep the listing.
                for _ in range(3):
                    self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(len(listed), 2)
                self.assertIn(folder, helper.app.verifier._listings)
                # One file deleted: the folder's time changes, and the kept listing is not believed.
                os.unlink(disk(helper, "iPhone/IMG_0003.HEIC"))
                self.assertEqual(check(helper, token, numbers), {"known": [n for n in numbers if n != 3]})
                self.assertEqual(len(listed), 3)
                self.assertEqual(put(helper, token, 3)[0], 201)
                os.utime(folder, (hour_ago, hour_ago))
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(len(listed), 4)
                # A folder that cannot be looked at: listing it again says what is the matter.
                with failing_stat([folder]):
                    self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(len(listed), 5)
                # A listing is kept again, so that the last step means something.
                os.utime(folder, (hour_ago, hour_ago))
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertEqual(len(listed), 6)
                self.assertIn(folder, helper.app.verifier._listings)
                # The whole folder deleted: answered at once, not a minute later.
                shutil.rmtree(folder)
                self.assertEqual(check(helper, token, numbers), {"known": []})
                self.assertEqual(asset_count(helper, token), 0)

    def test_a_listing_of_a_folder_that_just_changed_is_kept_only_a_moment(self):
        # A share that keeps times to two seconds would not show a second change.
        with running(PATH_TEMPLATE="{device}") as helper:
            token = helper.pair()
            numbers = list(range(1, 13))
            for number in numbers:
                put(helper, token, number)
            folder = disk(helper, "iPhone")
            verifier = helper.app.verifier
            with mock.patch.object(presence, "BIG_FOLDER", 10):
                # The first listing only finds the folder that large.
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                self.assertNotIn(folder, verifier._listings)
                os.utime(folder)
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                kept = verifier._listings[folder]
                self.assertLessEqual(kept.expires - verifier.clock(), presence.MTIME_SLACK)
                hour_ago = time.time() - 3600
                os.utime(folder, (hour_ago, hour_ago))
                self.assertEqual(check(helper, token, numbers), {"known": numbers})
                kept = verifier._listings[folder]
                self.assertGreater(kept.expires - verifier.clock(), presence.BIG_FOLDER_SECONDS - 5)

    def test_looking_for_moved_files_stops_when_its_time_is_up(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.makedirs(disk(helper, "Sorted"))
            os.rename(disk(helper, path_of(1)), disk(helper, "Sorted/IMG_0001.HEIC"))
            with mock.patch.object(presence, "MATCH_SECONDS", 0.0):
                self.assertEqual(check(helper, token, [1]), {"known": []})
            self.assertEqual(check(helper, token, [1]), {"known": [1]})


class RenamedDeviceFolderTests(unittest.TestCase):
    def test_a_renamed_device_folder_is_followed(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            put(helper, token, 2, created="2025-06-01T10:00:00+02:00")
            for number in range(3, 7):
                put(helper, token, number)
            os.rename(disk(helper, "iPhone"), disk(helper, "Jason's iPhone"))
            self.assertEqual(check(helper, token, list(range(1, 7))), {"known": list(range(1, 7))})
            # One change of the records, not a search for each file.
            self.assertEqual(helper.app.verifier.index.scans, 0)
            device = helper.request("GET", "/api/v1/status", token=token)[1]["device"]
            self.assertEqual((device["folder"], device["assetCount"]), ("Jason's iPhone", 6))
            self.assertEqual(helper.app.store.asset("device-0001", key(2)).relpath,
                             "Jason's iPhone/2025/2025-06/IMG_0002.HEIC")
            self.assertEqual(put(helper, token, 7)[1]["path"], path_of(7, "Jason's iPhone"))
            self.assertFalse(os.path.exists(disk(helper, "iPhone")))

    def test_a_folder_renamed_to_a_name_the_helper_would_write_otherwise_is_not_followed(self):
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            # The helper would write "Kitchen": following would put new photos elsewhere.
            os.rename(disk(helper, "iPhone"), disk(helper, "Kitchen."))
            # The files are found one by one instead.
            self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2, 3]})
            self.assertEqual(helper.request("GET", "/api/v1/status", token=token)[1]["device"]["folder"], "iPhone")
            self.assertEqual(put(helper, token, 4)[1]["path"], path_of(4))

    def test_an_upload_arriving_during_a_folder_rename_lands_in_the_renamed_folder(self):
        # Otherwise the upload makes the old folder again, and the old folder
        # then holds none of the photos: the whole library would be sent again.
        with running() as helper:
            token = helper.pair()
            for number in range(1, 5):
                put(helper, token, number)
            data = os.urandom(200_000)
            head = (f"PUT /api/v1/assets/{key(9)} HTTP/1.1\r\nHost: helper\r\nAuthorization: Bearer {token}\r\n"
                    f"Content-Length: {len(data)}\r\nX-Phlix-Filename: IMG_0009.HEIC\r\nX-Phlix-Kind: photo\r\n"
                    f"X-Phlix-Created: {CREATED}\r\nX-Phlix-SHA256: {hashlib.sha256(data).hexdigest()}\r\n\r\n")
            with socket.create_connection(("127.0.0.1", helper.port), timeout=20) as connection:
                connection.sendall(head.encode() + data[:100_000])
                time.sleep(0.3)
                os.rename(disk(helper, "iPhone"), disk(helper, "Renamed"))
                connection.sendall(data[100_000:])
                answer = b""
                while b"\r\n\r\n" not in answer:
                    answer += connection.recv(65536)
                header, _, body = answer.partition(b"\r\n\r\n")
                length = int([line.split(b":")[1] for line in header.split(b"\r\n")
                              if line.lower().startswith(b"content-length")][0])
                while len(body) < length:
                    body += connection.recv(65536)
            self.assertEqual(json.loads(body)["path"], path_of(9, "Renamed"))
            self.assertFalse(os.path.exists(disk(helper, "iPhone")))
            self.assertEqual(check(helper, token, [1, 2, 3, 4, 9]), {"known": [1, 2, 3, 4, 9]})

    def test_only_a_device_with_photos_in_its_folder_looks_for_it(self):
        with running() as helper:
            first, _ = pair(helper, "device-0001", "Anna")
            for number in range(1, 4):
                put(helper, first, number)
            second, _ = pair(helper, "device-0002", "Alex")
            # The new phone holds one of those photos: it has a record, in Anna's folder.
            put(helper, second, 4, data=b"photo number 1", name="IMG_0001.HEIC")
            shutil.copytree(disk(helper, "Anna"), disk(helper, "Copy"))
            looked = []
            real = helper.app.verifier._siblings
            helper.app.verifier._siblings = lambda parent, device: looked.append(device.id) or real(parent, device)
            self.assertEqual(put(helper, second, 5)[1]["path"], path_of(5, "Alex"))
            self.assertEqual(helper.request("GET", "/api/v1/status", token=second)[1]["device"]["folder"], "Alex")
            self.assertEqual(looked, [])

    def test_another_devices_folder_is_never_taken_or_told(self):
        with running() as helper:
            first, _ = pair(helper, "device-0001", "Anna")
            pair(helper, "device-0002", "Alex")
            for number in range(1, 4):
                put(helper, first, number)
            shutil.copytree(disk(helper, "Anna"), disk(helper, "Alex"))
            shutil.rmtree(disk(helper, "Anna"))
            # Found in the other phone's folder by name, size and date...
            self.assertEqual(check(helper, first, [1, 2, 3]), {"known": [1, 2, 3]})
            # ...but that folder does not become this phone's, and its path is not told.
            self.assertEqual(helper.request("GET", "/api/v1/status", token=first)[1]["device"]["folder"], "Anna")
            status, body = put(helper, first, 1)
            self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", ""))
            self.assertEqual(put(helper, first, 4)[1]["path"], path_of(4, "Anna"))

    def test_a_folder_that_does_not_hold_the_photos_is_tried_three_times(self):
        with running() as helper:
            token = helper.pair()
            for number in range(1, 4):
                put(helper, token, number)
            shutil.rmtree(disk(helper, "iPhone"))
            os.makedirs(disk(helper, "Other/2026"))
            tried = []
            real = helper.app.verifier._is_file_of_size
            helper.app.verifier._is_file_of_size = lambda relpath, size: tried.append(relpath) or real(relpath, size)
            counts = []
            for _ in range(5):
                before = len(tried)
                self.assertEqual(check(helper, token, [1, 2, 3]), {"known": []})
                counts.append(len(tried) - before)
            self.assertEqual(counts, [1, 1, 1, 0, 0])

    def test_the_most_recently_changed_folders_are_tried_first(self):
        for decoy_last, followed in ((True, "iPhone"), (False, "Renamed")):
            with self.subTest(decoy_last=decoy_last), running() as helper:
                token = helper.pair()
                for number in range(1, 4):
                    put(helper, token, number)
                if not decoy_last:
                    os.makedirs(disk(helper, "Decoy"))
                    time.sleep(0.05)
                os.rename(disk(helper, "iPhone"), disk(helper, "Renamed"))
                if decoy_last:
                    time.sleep(0.05)
                    os.makedirs(disk(helper, "Decoy"))
                with mock.patch.object(presence, "MAX_SIBLINGS", 1):
                    self.assertEqual(check(helper, token, [1, 2, 3]), {"known": [1, 2, 3]})
                self.assertEqual(helper.request("GET", "/api/v1/status", token=token)[1]["device"]["folder"],
                                 followed)

    def test_folder_names_with_wildcard_characters_are_rewritten_exactly(self):
        with running() as helper:
            first, _ = pair(helper, "device-0001", "a_b")
            second, _ = pair(helper, "device-0002", "aXb")
            for number in (1, 2):
                put(helper, first, number)
            put(helper, second, 3)
            # The second phone holds the first phone's photo 1 too: its record points into a_b.
            put(helper, second, 4, data=b"photo number 1", name="IMG_0001.HEIC")
            os.rename(disk(helper, "a_b"), disk(helper, "a_c"))
            self.assertEqual(check(helper, first, [1, 2]), {"known": [1, 2]})
            store = helper.app.store
            self.assertEqual(store.asset("device-0002", key(3)).relpath, path_of(3, "aXb"))
            self.assertEqual(store.asset("device-0002", key(4)).relpath, path_of(1, "a_c"))
            self.assertEqual(check(helper, second, [3, 4]), {"known": [3, 4]})


class RacesTests(unittest.TestCase):
    def test_an_upload_during_a_check_is_not_undone(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            os.unlink(disk(helper, path_of(1)))
            verifier = helper.app.verifier
            real = verifier.look
            sent = []

            def look_then_upload(records):
                looked = real(records)
                if not sent:
                    # The phone's upload of the same photo arrives while the check looks.
                    sent.append(put(helper, token, 1)[0])
                return looked

            verifier.look = look_then_upload
            self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertEqual(sent, [201])
            self.assertIsNone(helper.app.store.asset("device-0001", key(1)).missing_at)
            self.assertEqual(asset_count(helper, token), 1)


    def test_a_check_of_files_that_are_all_there_does_not_wait_for_an_upload(self):
        with running() as helper:
            token = helper.pair()
            put(helper, token, 1)
            # As if an upload were being put in place right now.
            with helper.app.place_lock:
                self.assertEqual(check(helper, token, [1, 2]), {"known": [1]})


class PairingAgainTests(unittest.TestCase):
    def test_another_folder_name_takes_new_photos_and_leaves_the_old_ones(self):
        with running() as helper:
            token, _ = pair(helper, folder="iPhone")
            put(helper, token, 1)
            token, folder = pair(helper, folder="Jason", switch=True)
            self.assertEqual(folder, "Jason")
            self.assertEqual(check(helper, token, [1]), {"known": [1]})
            self.assertEqual(put(helper, token, 2)[1]["path"], path_of(2, "Jason"))
            self.assertTrue(os.path.isfile(disk(helper, path_of(1))))
            # A deleted old photo goes to the new folder.
            os.unlink(disk(helper, path_of(1)))
            self.assertEqual(check(helper, token, [1, 2]), {"known": [2]})
            self.assertEqual(put(helper, token, 1)[1]["path"], path_of(1, "Jason"))
            # The old name stays this phone's.
            self.assertEqual(pair(helper, "device-0002", folder="iPhone")[1], "iPhone 2")

    def test_the_same_name_or_no_request_keeps_the_folder(self):
        with running() as helper:
            pair(helper, folder="iPhone")
            self.assertEqual(pair(helper, folder="IPHONE", switch=True)[1], "iPhone")
            self.assertEqual(pair(helper, folder="Jason")[1], "iPhone")
            self.assertEqual(pair(helper, folder="Jason", switch="yes")[1], "iPhone")

    def test_a_phone_can_go_back_to_a_folder_it_had(self):
        with running() as helper:
            pair(helper, folder="iPhone")
            self.assertEqual(pair(helper, folder="Jason", switch=True)[1], "Jason")
            self.assertEqual(pair(helper, folder="iphone", switch=True)[1], "iPhone")

    def test_hello_and_status_name_what_this_helper_does(self):
        with running() as helper:
            token = helper.pair()
            features = ["verified-check", "switch-folder", "left-out"]
            self.assertEqual(helper.request("GET", "/api/v1/hello")[1]["features"], features)
            self.assertEqual(helper.request("GET", "/api/v1/status", token=token)[1]["features"], features)


class PathPrivacyTests(unittest.TestCase):
    def test_a_photo_found_in_another_phones_folder_is_not_located_for_it(self):
        data = b"a photo both phones hold"
        with running() as helper:
            first, _ = pair(helper, "device-0001", "Anna")
            second, _ = pair(helper, "device-0002", "Alex")
            put(helper, first, 1, data)
            os.unlink(disk(helper, path_of(1, "Anna")))
            self.assertEqual(put(helper, second, 2, data, name="IMG_0001.HEIC")[1]["path"], path_of(1, "Alex"))
            # The first phone sends it again: it is the second phone's file now.
            status, body = put(helper, first, 1, data)
            self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", ""))
            self.assertEqual(put(helper, second, 2, data, name="IMG_0001.HEIC")[1]["path"], path_of(1, "Alex"))


# The schema of helper 1.0.1, as it made its database.
V1_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, folder TEXT NOT NULL UNIQUE, token_hash TEXT NOT NULL,
    paired_at INTEGER NOT NULL, paired_via TEXT NOT NULL, last_seen INTEGER);
CREATE TABLE IF NOT EXISTS assets (
    device_id TEXT NOT NULL, key TEXT NOT NULL, sha256 TEXT NOT NULL, relpath TEXT NOT NULL,
    size INTEGER NOT NULL, kind TEXT, created TEXT, stored_at INTEGER NOT NULL,
    PRIMARY KEY (device_id, key));
CREATE INDEX IF NOT EXISTS assets_by_sha ON assets (sha256);
CREATE INDEX IF NOT EXISTS assets_by_path ON assets (relpath);
"""


class StartGuardTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="phlix-guard-test-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.photos = os.path.join(self.root, "photos")
        self.env = {"UPLOAD_DIR": self.photos, "CONFIG_DIR": os.path.join(self.root, "config"),
                    "PORT": "17498", "BIND": "127.0.0.1", "TLS": "off", "MIN_FREE_GB": "0",
                    "PLEX_URL": "http://127.0.0.1:9"}
        self.config = config_module.load(self.env)

    def _stored_before(self, count=3):
        store = Store(self.config.database_path)
        store.pair_device("device-0001", "iPhone", "iPhone", "code")
        for number in range(count):
            store.record_asset("device-0001", key(number), "a" * 64, path_of(number), 10, "photo", CREATED)
        store.close()

    def _starts(self):
        app, _ = main_module.build_app(self.config)
        app.store.close()
        return True

    def test_an_empty_upload_folder_stops_a_helper_that_stored_photos_there(self):
        self._stored_before()
        # The last ones: a new or another Windows drive, which holds these from the first day.
        for contents in ((), (".DS_Store", "@eaDir", "lost+found", "#recycle"),
                         ("$RECYCLE.BIN", "System Volume Information"), ("$Recycle.Bin", "RECYCLER", "Recycled")):
            shutil.rmtree(self.photos, ignore_errors=True)
            os.makedirs(self.photos, exist_ok=True)
            for name in contents:
                os.makedirs(os.path.join(self.photos, name), exist_ok=True)
            with self.assertRaises(main_module.StartRefused, msg=contents):
                main_module.build_app(self.config)
        # (Were it to start after all, it must not serve for ever here.)
        with mock.patch.dict(os.environ, self.env, clear=True), \
                mock.patch.object(main_module, "Server", side_effect=OSError("it started")), \
                self.assertLogs("phlix", level="ERROR") as logs:
            self.assertEqual(main_module.serve(), 1)
        text = "\n".join(logs.output)
        self.assertIn("the upload folder %s is empty, and the helper stored 3 files there before" % self.photos,
                      text)
        self.assertIn("make a folder named .phlix-upload-tmp in it", text)
        self.assertNotIn("Traceback", text)

    def test_a_missing_upload_folder_is_not_made_in_its_place(self):
        self._stored_before()
        with self.assertRaises(main_module.StartRefused):
            main_module.build_app(self.config)
        self.assertFalse(os.path.exists(self.photos))

    def test_the_hidden_folder_lets_it_start(self):
        self._stored_before()
        os.makedirs(os.path.join(self.photos, ".phlix-upload-tmp"))
        self.assertTrue(self._starts())

    def test_a_folder_with_photos_or_a_fresh_helper_starts(self):
        os.makedirs(self.photos)
        self.assertTrue(self._starts())
        self._stored_before()
        os.makedirs(os.path.join(self.photos, "iPhone"))
        shutil.rmtree(os.path.join(self.photos, ".phlix-upload-tmp"))
        self.assertTrue(self._starts())

    def test_a_running_helper_makes_the_hidden_folder_again(self):
        # On Windows the hidden folder is in plain sight, and a person who
        # deletes everything deletes it too. Docker's health check brings it
        # back, so that the helper still starts the next time.
        with running(UPLOAD_DIR=self.photos, CONFIG_DIR=self.config.config_dir) as helper:
            token = helper.pair()
            put(helper, token, 1)
            for name in os.listdir(self.photos):
                shutil.rmtree(os.path.join(self.photos, name))
            self.assertEqual(main_module.emptied_upload_folder(self.config, helper.app.store), 1)
            # The health check answers whether or not the folder could be made.
            tried = threading.Event()

            def refused(path, *arguments, **keywords):
                tried.set()
                raise PermissionError(errno.EACCES, "Permission denied", path)

            with mock.patch.object(os, "mkdir", refused):
                self.assertEqual(helper.request("GET", "/healthz")[:2], (200, b"ok\n"))
                self.assertTrue(tried.wait(5))
            self.assertEqual(os.listdir(self.photos), [])
            self.assertEqual(helper.request("GET", "/healthz")[:2], (200, b"ok\n"))
            self.assertTrue(wait_for(lambda: os.listdir(self.photos) == [".phlix-upload-tmp"]))
            self.assertEqual(main_module.emptied_upload_folder(self.config, helper.app.store), 0)
        self.assertTrue(self._starts())

    def test_the_health_check_never_makes_the_upload_folder_itself(self):
        # The upload folder is gone: a disk that is not mounted, say. A folder
        # made in its place would let the next start run on the wrong disk.
        with running(UPLOAD_DIR=self.photos, CONFIG_DIR=self.config.config_dir) as helper:
            token = helper.pair()
            put(helper, token, 1)
            shutil.rmtree(self.photos)
            looked = threading.Event()
            real = os.path.isdir

            def spy(path):
                found = real(path)
                if os.fspath(path) == helper.app.storage.temp_dir:
                    looked.set()
                return found

            with mock.patch.object(os.path, "isdir", spy):
                self.assertEqual(helper.request("GET", "/healthz")[:2], (200, b"ok\n"))
                self.assertTrue(looked.wait(5))
            helper.app.storage.keep_temp_dir()
            self.assertFalse(os.path.exists(self.photos))
            self.assertEqual(main_module.emptied_upload_folder(self.config, helper.app.store), 1)
        with self.assertRaises(main_module.StartRefused):
            main_module.build_app(self.config)

    def test_files_already_found_missing_do_not_stop_it(self):
        self._stored_before()
        store = Store(self.config.database_path)
        for number in range(3):
            store.flag_missing(store.asset("device-0001", key(number)), int(time.time()))
        store.close()
        os.makedirs(self.photos)
        self.assertTrue(self._starts())

    def test_a_database_of_helper_1_0_1_is_upgraded_and_starts(self):
        os.makedirs(os.path.join(self.photos, ".phlix-upload-tmp"))
        os.makedirs(os.path.join(self.photos, "iPhone", "2026", "2026-11"))
        with open(os.path.join(self.photos, path_of(1)), "wb") as handle:
            handle.write(b"photo number 1")
        token = "t" * 43
        os.makedirs(self.config.config_dir)
        database = sqlite3.connect(self.config.database_path)
        database.executescript(V1_SCHEMA)
        database.execute("INSERT INTO meta VALUES ('schema_version', '1'), ('server_id', 'old-server-id')")
        database.execute("INSERT INTO devices VALUES ('device-0001', 'iPhone', 'iPhone', ?, 1, 'code', 1)",
                         (hash_token(token),))
        database.execute("INSERT INTO assets VALUES ('device-0001', ?, ?, ?, 14, 'photo', ?, 1)",
                         (key(1), hashlib.sha256(b"photo number 1").hexdigest(), path_of(1), CREATED))
        database.commit()
        database.close()
        with running(UPLOAD_DIR=self.photos, CONFIG_DIR=self.config.config_dir) as helper:
            self.assertEqual(helper.request("GET", "/api/v1/hello")[1]["serverId"], "old-server-id")
            self.assertEqual(check(helper, token, [1, 2]), {"known": [1]})
            self.assertEqual(helper.app.store.get_meta("schema_version"), "2")
            self.assertEqual(helper.app.store.all_folders(), [("device-0001", "iPhone")])
        # ...and helper 1.0.1 can still open what 1.0.2 left.
        database = sqlite3.connect(self.config.database_path)
        database.executescript(V1_SCHEMA)
        database.execute("INSERT INTO assets (device_id, key, sha256, relpath, size, kind, created, stored_at) "
                         "VALUES ('device-0001', ?, ?, 'iPhone/x.HEIC', 1, 'photo', NULL, 2)", (key(2), "b" * 64))
        rows = database.execute("SELECT key FROM assets WHERE device_id = 'device-0001'").fetchall()
        database.close()
        self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
