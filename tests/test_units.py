"""Settings, file naming, pairing codes and the database, without a server."""

import datetime as dt
import errno
import os
import shutil
import tempfile
import unittest
from unittest import mock

from phlix_upload import __main__ as main_module
from phlix_upload import config as config_module
from phlix_upload import plex, storage
from phlix_upload.pairing import CODE_ALPHABET, AttemptLimiter, codes_match, new_code
from phlix_upload.plex import parse_identity
from phlix_upload.store import Store


class ConfigTests(unittest.TestCase):
    def test_defaults_suit_the_documented_container(self):
        config = config_module.load({})
        self.assertEqual(config.port, 7459)
        self.assertEqual(config.upload_dir, "/photos")
        self.assertEqual(config.config_dir, "/config")
        self.assertTrue(config.tls)
        self.assertEqual(config.pairing, "auto")
        self.assertEqual(config.path_template, "{device}/{year}/{year}-{month}")
        self.assertEqual(config.min_free_bytes, 2 * 1024 ** 3)
        self.assertEqual(config.umask, 0o022)
        self.assertEqual(config.temp_dir, "/photos/.phlix-upload-tmp")

    def test_values_are_read(self):
        config = config_module.load({
            "PORT": "8443", "TLS": "off", "PAIRING": "code", "PAIRING_CODE": "sun-flower-42",
            "PLEX_URL": "http://192.168.1.10:32400/, https://plex.lan:32400", "MIN_FREE_GB": "0.5",
            "PUID": "99", "PGID": "100", "UMASK": "002", "EXTRA_EXTENSIONS": ".insp, LRV",
            "PATH_TEMPLATE": "/{year}/{month}/", "NAME": "Tower",
        })
        self.assertEqual(config.port, 8443)
        self.assertFalse(config.tls)
        self.assertEqual(config.plex_urls, ("http://192.168.1.10:32400", "https://plex.lan:32400"))
        self.assertEqual(config.min_free_bytes, 512 * 1024 ** 2)
        self.assertEqual((config.puid, config.pgid, config.umask), (99, 100, 0o002))
        self.assertEqual(config.extra_extensions, frozenset({"insp", "lrv"}))
        self.assertEqual(config.path_template, "{year}/{month}")
        self.assertEqual(config.name, "Tower")

    def test_mistakes_are_named(self):
        for environment, word in [
            ({"PORT": "seventy"}, "PORT"),
            ({"PORT": "70000"}, "PORT"),
            ({"TLS": "maybe"}, "TLS"),
            ({"PAIRING": "open"}, "PAIRING"),
            ({"PAIRING_CODE": "abc"}, "PAIRING_CODE"),
            ({"PLEX_URL": "192.168.1.10:32400"}, "PLEX_URL"),
            ({"PLEX_URL": "http://192.168.1.10:32400/web"}, "PLEX_URL"),
            ({"UMASK": "abc"}, "UMASK"),
            ({"PATH_TEMPLATE": "{device}/../{year}"}, "PATH_TEMPLATE"),
            ({"PATH_TEMPLATE": "{album}"}, "PATH_TEMPLATE"),
            ({"PATH_TEMPLATE": ".hidden/{year}"}, "PATH_TEMPLATE"),
            ({"PATH_TEMPLATE": "{year"}, "PATH_TEMPLATE"),
            ({"TLS_CERT": "/config/cert.pem"}, "TLS_CERT"),
            ({"EXTRA_EXTENSIONS": "sh;rm"}, "EXTRA_EXTENSIONS"),
        ]:
            with self.subTest(environment=environment):
                with self.assertRaises(config_module.ConfigError) as raised:
                    config_module.load(environment)
                self.assertIn(word, str(raised.exception))

    def test_an_empty_template_puts_everything_in_one_folder(self):
        # A lone slash asks for no folders at all: every file goes straight
        # into the upload folder.
        self.assertEqual(config_module.load({"PATH_TEMPLATE": "/"}).path_template, "")

    def test_an_empty_setting_means_its_default(self):
        # Template screens (Unraid, Portainer) pass every setting they know,
        # filled in or not.
        names = ["PORT", "BIND", "UPLOAD_DIR", "CONFIG_DIR", "NAME", "PLEX_URL", "PAIRING", "PAIRING_CODE",
                 "PATH_TEMPLATE", "MIN_FREE_GB", "MAX_UPLOAD_GB", "TLS", "TLS_CERT", "TLS_KEY", "PUID", "PGID",
                 "UMASK", "EXTRA_EXTENSIONS", "LOG_LEVEL"]
        self.assertEqual(config_module.load({name: "" for name in names}), config_module.load({}))
        self.assertEqual(config_module.load({name: "   " for name in names}), config_module.load({}))


class MountGuardTests(unittest.TestCase):
    def test_outside_the_image_nothing_is_demanded(self):
        from phlix_upload.__main__ import unmounted_folders
        config = config_module.load({"UPLOAD_DIR": "/tmp/not-a-mount", "CONFIG_DIR": "/tmp/also-not"})
        self.assertEqual(unmounted_folders(config, {}), [])

    def test_in_the_image_both_folders_must_be_volumes(self):
        from phlix_upload.__main__ import unmounted_folders
        root = tempfile.mkdtemp(prefix="phlix-mount-")
        self.addCleanup(shutil.rmtree, root, True)
        config = config_module.load({"UPLOAD_DIR": os.path.join(root, "photos"), "CONFIG_DIR": "/"})
        # "/" is a mount point; a plain folder is not.
        self.assertEqual(unmounted_folders(config, {"PHLIX_CONTAINER": "1"}), [os.path.join(root, "photos")])
        self.assertEqual(unmounted_folders(config, {"PHLIX_CONTAINER": "1", "ALLOW_UNMOUNTED": "1"}), [])


class NamingTests(unittest.TestCase):
    def test_a_camera_name_is_kept(self):
        self.assertEqual(storage.clean_filename("IMG_1234.HEIC", "x"), "IMG_1234.HEIC")

    def test_a_name_cannot_leave_its_folder(self):
        for hostile in ["../../etc/passwd.jpg", "..\\..\\windows\\system32\\evil.jpg", "/etc/cron.d/job.jpg",
                        "a/b/c.jpg", "....//....//x.jpg"]:
            with self.subTest(name=hostile):
                cleaned = storage.clean_filename(hostile, "fallback")
                self.assertNotIn("/", cleaned)
                self.assertNotIn("\\", cleaned)
                self.assertFalse(cleaned.startswith("."))
                self.assertNotEqual(cleaned, "..")

    def test_hidden_and_reserved_names_are_replaced(self):
        self.assertEqual(storage.clean_filename(".htaccess", "upload-1"), "htaccess")
        # Nothing but dots before "jpg" leaves a name with no extension,
        # which the server then refuses as not being a photo or video.
        self.assertEqual(storage.clean_filename("...jpg", "upload-1"), "jpg")
        self.assertFalse(storage.is_allowed_extension(storage.clean_filename("...jpg", "upload-1")))
        self.assertEqual(storage.clean_filename("CON.jpg", "upload-1"), "upload-1.jpg")
        self.assertEqual(storage.clean_filename("", "upload-1"), "upload-1")
        self.assertEqual(storage.clean_filename("   .   ", "upload-1"), "upload-1")

    def test_characters_a_share_refuses_are_replaced(self):
        self.assertEqual(storage.clean_filename('a<b>c:d"e|f?g*h.png', "x"), "a_b_c_d_e_f_g_h.png")
        self.assertEqual(storage.clean_filename("line\nbreak\x00.jpg", "x"), "line_break_.jpg")

    def test_a_long_name_is_cut_but_keeps_its_extension(self):
        cleaned = storage.clean_filename("é" * 400 + ".jpeg", "x")
        self.assertLessEqual(len(cleaned.encode()), 150)
        self.assertTrue(cleaned.endswith(".jpeg"))

    def test_an_extension_is_letters_and_digits_only(self):
        self.assertEqual(storage.clean_filename("photo.j$p;g", "x"), "photo.jpg")
        self.assertTrue(storage.is_allowed_extension("IMG_1.HEIC"))
        self.assertTrue(storage.is_allowed_extension("clip.MOV"))
        self.assertFalse(storage.is_allowed_extension("run.sh"))
        self.assertFalse(storage.is_allowed_extension("page.php.jpg.exe"))
        self.assertFalse(storage.is_allowed_extension("noextension"))
        self.assertTrue(storage.is_allowed_extension("pano.insp", frozenset({"insp"})))

    def test_folder_names(self):
        self.assertEqual(storage.clean_folder_name("Anna’s iPhone"), "Anna’s iPhone")
        self.assertEqual(storage.clean_folder_name("../../etc"), ".._.._etc".strip("."))
        self.assertEqual(storage.clean_folder_name("   "), "iPhone")
        self.assertEqual(storage.clean_folder_name(".."), "iPhone")
        self.assertNotIn("/", storage.clean_folder_name("a/b"))

    def test_folders_that_are_never_part_of_the_upload_folder(self):
        for name in (".hidden", ".phlix-upload-tmp", "lost+found", "@eaDir", "#recycle", "#snapshot", "@Recycle",
                     "@Recently-Snapshot", "$RECYCLE.BIN", "$Recycle.Bin", "$recycle.bin", "RECYCLER", "Recycler",
                     "RECYCLED", "recycled", "System Volume Information", "SYSTEM VOLUME INFORMATION", "@EADIR"):
            self.assertTrue(storage.is_outside_name(name), name)
        for name in ("iPhone", "2026", "Recycled photos", "$RECYCLE", "Recycle Bin", "eaDir", "My.Photos"):
            self.assertFalse(storage.is_outside_name(name), name)
        self.assertTrue(storage.is_outside_path("$RECYCLE.BIN/S-1-5-21/$R8KQ2ZD/2026/2026-11"))
        self.assertTrue(storage.is_outside_path("Sorted/system volume information"))
        self.assertTrue(storage.is_outside_path("iPhone/.trash/2026"))
        self.assertFalse(storage.is_outside_path("iPhone/2026/2026-11"))
        self.assertFalse(storage.is_outside_path(""))
        # No phone gets such a folder as its own: its photos would never count as backed up.
        for name in ("$RECYCLE.BIN", "recycled", "System Volume Information", "@eaDir", "lost+found"):
            self.assertEqual(storage.clean_folder_name(name), "iPhone", name)

    def test_a_folder_the_layout_itself_names_is_part_of_the_upload_folder(self):
        # Helpers before 1.0.3 let a phone have such a folder, and a layout name one.
        own = storage.layout_names("{device}/{year}/{year}-{month}", ["Recycled", "iPhone"])
        self.assertEqual(own, (frozenset({"Recycled", "iPhone"}), frozenset(), frozenset()))
        self.assertFalse(storage.is_outside_path("Recycled/2026/2026-11", own))
        # Only at its own depth, spelt as the helper wrote it, and not what lies in it.
        for folder in ("RECYCLED/2026/2026-11", "Sorted/Recycled", "Recycled/$RECYCLE.BIN/2026", "Recycled/.trash",
                       "$RECYCLE.BIN/S-1-5-21/$R8KQ2ZD/2026/2026-11", "iPhone/Recycled"):
            self.assertTrue(storage.is_outside_path(folder, own), folder)
        own = storage.layout_names("lost+found/{year}/Phone {device}/@eaDir", ["one", "two"])
        self.assertEqual(own, (frozenset({"lost+found"}), frozenset(), frozenset({"Phone one", "Phone two"}),
                               frozenset({"@eaDir"})))
        self.assertFalse(storage.is_outside_path("lost+found/2026/Phone one/@eaDir", own))
        self.assertTrue(storage.is_outside_path("lost+found/2026/@eaDir", own))
        self.assertEqual(storage.layout_names("", ["iPhone"]), ())
        # What it names is what `relative_folder` writes.
        when = storage.parse_created("2026-11-21T22:15:03-06:00")
        for template in ("{device}/{year}", "Photos: {device}./x", "{year}/{device}"):
            written = storage.relative_folder(template, "a?b", when).split("/")
            names = storage.layout_names(template, ["a?b"])
            self.assertEqual(len(written), len(names))
            for part, allowed in zip(written, names):
                self.assertTrue(not allowed or part in allowed, (template, part))

    def test_the_folder_follows_the_photos_own_local_date(self):
        late = storage.parse_created("2026-12-31T23:10:05-06:00")
        self.assertEqual(storage.relative_folder("{device}/{year}/{year}-{month}", "iPhone", late),
                         "iPhone/2026/2026-12")
        self.assertEqual(storage.relative_folder("{year}/{month}/{day}", "iPhone", late), "2026/12/31")
        self.assertEqual(storage.relative_folder("", "iPhone", late), "")
        self.assertEqual(storage.relative_folder("{device}", "iPhone", None), "iPhone")
        # A device's name is never read as part of the pattern.
        self.assertEqual(storage.relative_folder("{device}/{year}", "{year}", late), "{year}/2026")
        self.assertEqual(storage.relative_folder("{year}/{device}", "{month}{day}", late), "2026/{month}{day}")

    def test_dates_that_are_not_dates(self):
        self.assertIsNone(storage.parse_created(None))
        self.assertIsNone(storage.parse_created(""))
        self.assertIsNone(storage.parse_created("yesterday"))
        self.assertIsNone(storage.parse_created("0001-01-01T00:00:00+00:00"))
        self.assertEqual(storage.parse_created("2026-11-21T10:00:00Z").utcoffset(), dt.timedelta(0))


class PlacementTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="phlix-storage-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.storage = storage.Storage(self.root, os.path.join(self.root, ".tmp"), "{device}/{year}/{year}-{month}")
        self.storage.prepare()
        self.created = storage.parse_created("2026-11-21T22:15:03-06:00")

    def _temp(self, data: bytes) -> str:
        path = self.storage.new_temp_path()
        with open(path, "wb") as handle:
            handle.write(data)
        return path

    def _place(self, data: bytes, name: str = "IMG_1.HEIC", recorded=None):
        return self.storage.place(self._temp(data), "iPhone", name, self.created,
                                  storage.hashlib.sha256(data).hexdigest(), len(data),
                                  lambda relpath: (recorded or {}).get(relpath))

    def test_a_file_lands_in_its_month_with_the_photos_date(self):
        relpath, stored = self._place(b"photo")
        self.assertEqual((relpath, stored), ("iPhone/2026/2026-11/IMG_1.HEIC", True))
        final = os.path.join(self.root, relpath)
        with open(final, "rb") as handle:
            self.assertEqual(handle.read(), b"photo")
        self.assertAlmostEqual(os.path.getmtime(final), self.created.timestamp(), delta=1)
        self.assertEqual(os.listdir(self.storage.temp_dir), [])

    def test_a_different_photo_with_the_same_name_gets_a_number(self):
        self._place(b"first")
        relpath, stored = self._place(b"second")
        self.assertEqual((relpath, stored), ("iPhone/2026/2026-11/IMG_1 (2).HEIC", True))
        relpath, stored = self._place(b"third!")
        self.assertEqual(relpath, "iPhone/2026/2026-11/IMG_1 (3).HEIC")

    def test_the_same_photo_again_is_not_stored_twice(self):
        self._place(b"same")
        relpath, stored = self._place(b"same")
        self.assertEqual((relpath, stored), ("iPhone/2026/2026-11/IMG_1.HEIC", False))
        self.assertEqual(os.listdir(os.path.join(self.root, "iPhone/2026/2026-11")), ["IMG_1.HEIC"])
        self.assertEqual(os.listdir(self.storage.temp_dir), [])

    def test_a_recorded_hash_settles_it_without_reading_the_file(self):
        self._place(b"aaaa")
        # Same size, and the record says the content differs: a new name.
        relpath, stored = self._place(b"bbbb", recorded={"iPhone/2026/2026-11/IMG_1.HEIC": "0" * 64})
        self.assertEqual((relpath, stored), ("iPhone/2026/2026-11/IMG_1 (2).HEIC", True))

    def test_nothing_resolves_outside_the_upload_folder(self):
        with self.assertRaises(storage.StorageError):
            self.storage.absolute("../outside.jpg")
        with self.assertRaises(storage.StorageError):
            self.storage.absolute("/etc/passwd")
        self.assertFalse(self.storage.exists("../outside.jpg"))

    def test_abandoned_uploads_are_swept(self):
        stale = self._temp(b"half")
        self.assertEqual(self.storage.sweep_temp(max_age_seconds=3600), 0)
        self.assertTrue(os.path.exists(stale))
        self.assertEqual(self.storage.sweep_temp(max_age_seconds=0), 1)
        self.assertFalse(os.path.exists(stale))

    def test_why_the_upload_folder_cannot_be_written(self):
        self.assertIsNone(self.storage.write_trouble())
        for code, trouble in ((errno.ENOENT, storage.GONE), (errno.EACCES, storage.NOT_WRITABLE),
                              (errno.EROFS, storage.NOT_WRITABLE), (errno.EIO, storage.NOT_WRITABLE)):
            with mock.patch.object(os, "makedirs", side_effect=OSError(code, os.strerror(code))):
                self.assertEqual(self.storage.write_trouble(), trouble, errno.errorcode[code])
                self.assertFalse(self.storage.is_writable())
                # Asked to keep the temporary folder there, it never raises.
                self.storage.keep_temp_dir()
        shutil.rmtree(self.storage.temp_dir)
        with mock.patch.object(os, "mkdir", side_effect=OSError(errno.EACCES, os.strerror(errno.EACCES))):
            self.storage.keep_temp_dir()
        self.assertFalse(os.path.exists(self.storage.temp_dir))
        self.storage.keep_temp_dir()
        self.assertTrue(os.path.isdir(self.storage.temp_dir))
        # Only the hidden folder is made, never an upload folder that is gone.
        shutil.rmtree(self.storage.upload_dir)
        self.storage.keep_temp_dir()
        self.assertFalse(os.path.exists(self.storage.upload_dir))

    def test_free_space_and_writability(self):
        free, total = self.storage.disk_usage()
        self.assertGreater(total, 0)
        self.assertGreaterEqual(total, free)
        self.assertTrue(self.storage.is_writable())


class PairingCodeTests(unittest.TestCase):
    def test_a_new_code_is_easy_to_read_and_type(self):
        code = new_code()
        self.assertRegex(code, r"^[A-Z2-9]{4}-[A-Z2-9]{4}$")
        self.assertTrue(set(code.replace("-", "")) <= set(CODE_ALPHABET))
        for confusable in "ILOU01":
            self.assertNotIn(confusable, CODE_ALPHABET)
        self.assertNotEqual(new_code(), new_code())

    def test_codes_match_however_they_are_typed(self):
        self.assertTrue(codes_match("K7QM-3XPD", "k7qm3xpd"))
        self.assertTrue(codes_match("K7QM-3XPD", " K7QM 3XPD "))
        self.assertFalse(codes_match("K7QM-3XPD", "K7QM-3XPE"))
        self.assertFalse(codes_match("K7QM-3XPD", ""))
        self.assertFalse(codes_match("", ""))
        self.assertFalse(codes_match("K7QM-3XPD", "K7QM-3XP"))
        self.assertFalse(codes_match("K7QM-3XPD", "K7QM-3XPDD"))
        # Anything that is not a letter or digit is ignored, like the dash.
        self.assertTrue(codes_match("K7QM-3XPD", "K7QM_3XPD!"))

    def test_wrong_tries_from_one_address_are_slowed(self):
        now = [1000.0]
        limiter = AttemptLimiter(per_address=3, address_window=60, overall=100, overall_window=600,
                                 clock=lambda: now[0])
        for _ in range(3):
            self.assertEqual(limiter.retry_after("10.0.0.5"), 0)
            limiter.record_failure("10.0.0.5")
        self.assertGreater(limiter.retry_after("10.0.0.5"), 0)
        self.assertLessEqual(limiter.retry_after("10.0.0.5"), 61)
        self.assertEqual(limiter.retry_after("10.0.0.6"), 0)
        now[0] += 61
        self.assertEqual(limiter.retry_after("10.0.0.5"), 0)

    def test_many_addresses_together_pause_pairing_for_everyone(self):
        now = [1000.0]
        limiter = AttemptLimiter(per_address=5, address_window=60, overall=4, overall_window=600,
                                 clock=lambda: now[0])
        for number in range(4):
            limiter.record_failure(f"10.0.0.{number}")
        self.assertGreater(limiter.retry_after("10.0.9.9"), 0)
        now[0] += 601
        self.assertEqual(limiter.retry_after("10.0.9.9"), 0)

    def test_the_pause_for_everyone_is_for_wrong_codes_only(self):
        now = [1000.0]
        limiter = AttemptLimiter(per_address=5, address_window=60, overall=4, overall_window=600,
                                 clock=lambda: now[0])
        # Refused Plex sign-ins count against their own address and no further.
        for number in range(10):
            limiter.record_failure(f"10.0.1.{number}", by_code=False)
        self.assertEqual(limiter.retry_after("10.0.9.9"), 0)
        # Wrong codes do add up...
        for number in range(4):
            limiter.record_failure(f"10.0.0.{number}")
        self.assertGreater(limiter.retry_after("10.0.9.9"), 0)
        # ...and even then the owner can still pair through Plex.
        self.assertEqual(limiter.retry_after("10.0.9.9", by_code=False), 0)

    def test_the_allowance_for_everyone_is_generous(self):
        # A low number would let anyone on the network keep the owner from
        # pairing a phone; the code is long enough not to need one.
        limiter = AttemptLimiter()
        for number in range(150):
            limiter.record_failure(f"10.0.{number // 250}.{number % 250}")
        self.assertEqual(limiter.retry_after("10.9.9.9"), 0)

    def test_a_success_clears_that_address(self):
        limiter = AttemptLimiter(per_address=2)
        limiter.record_failure("10.0.0.5")
        limiter.record_failure("10.0.0.5")
        self.assertGreater(limiter.retry_after("10.0.0.5"), 0)
        limiter.record_success("10.0.0.5")
        self.assertEqual(limiter.retry_after("10.0.0.5"), 0)


class WhereToLookForPlexTests(unittest.TestCase):
    def test_an_address_from_the_settings_is_tried_as_written_first(self):
        link = plex.PlexLink(("http://192.168.1.10:32400", "https://plex.example:32400"))
        self.assertEqual(link.candidates(), [
            "http://192.168.1.10:32400", "https://192.168.1.10:32400",
            "https://plex.example:32400", "http://plex.example:32400",
        ])

    def test_addresses_the_helper_thinks_of_are_tried_over_https_first(self):
        found = plex.PlexLink().candidates()
        self.assertEqual(found[:2], ["https://host.docker.internal:32400", "http://host.docker.internal:32400"])
        self.assertEqual(len(found), len(set(found)))
        for secure, plain in zip(found[0::2], found[1::2]):
            self.assertTrue(secure.startswith("https://"))
            self.assertEqual(plain, "http://" + secure[len("https://"):])
        self.assertIn("https://plex:32400", found)


class WhoTheHelperRunsAsTests(unittest.TestCase):
    def _proc(self, cmdline: bytes | None, status: str | None) -> str:
        root = tempfile.mkdtemp(prefix="phlix-proc-")
        self.addCleanup(shutil.rmtree, root, True)
        os.makedirs(os.path.join(root, "1"))
        if cmdline is not None:
            with open(os.path.join(root, "1", "cmdline"), "wb") as handle:
                handle.write(cmdline)
        if status is not None:
            with open(os.path.join(root, "1", "status"), "w", encoding="ascii") as handle:
                handle.write(status)
        return root

    def test_root_is_recognised_from_the_first_process(self):
        helper = b"python\x00-m\x00phlix_upload\x00"
        self.assertTrue(main_module._helper_runs_as_root(self._proc(helper, "Name:\tpython\nUid:\t0\t0\t0\t0\n")))
        self.assertFalse(main_module._helper_runs_as_root(
            self._proc(helper, "Name:\tpython\nUid:\t1000\t1000\t1000\t1000\n")))

    def test_anything_else_is_not_taken_for_root(self):
        # Another program is process 1 (an init), or nothing can be read.
        self.assertFalse(main_module._helper_runs_as_root(self._proc(b"/sbin/tini\x00--\x00python\x00", "Uid:\t0\t0\t0\t0\n")))
        self.assertFalse(main_module._helper_runs_as_root(self._proc(None, None)))
        self.assertFalse(main_module._helper_runs_as_root(self._proc(b"python\x00-m\x00phlix_upload\x00", "Uid:\n")))
        self.assertFalse(main_module._helper_runs_as_root("/nonexistent"))


class DroppingRootTests(unittest.TestCase):
    def test_a_temporary_folder_made_by_root_becomes_the_helpers_own(self):
        # The fix for an emptied upload folder: a person makes .phlix-upload-tmp, usually as root.
        root = tempfile.mkdtemp(prefix="phlix-root-")
        self.addCleanup(shutil.rmtree, root, True)
        config = config_module.load({"UPLOAD_DIR": os.path.join(root, "photos"),
                                     "CONFIG_DIR": os.path.join(root, "config"), "PUID": "1000", "PGID": "100"})
        os.makedirs(config.temp_dir)
        owners = []
        with mock.patch.object(os, "geteuid", return_value=0), \
                mock.patch.object(os, "chown", lambda path, uid, gid, **_: owners.append((path, uid, gid))), \
                mock.patch.object(os, "setgroups", create=True), mock.patch.object(os, "setgid"), \
                mock.patch.object(os, "setuid"):
            main_module.drop_privileges(config)
        self.assertIn((config.temp_dir, 1000, 100), owners)
        # Nothing else in the upload folder is touched.
        self.assertEqual([path for path, _, _ in owners if path.startswith(config.upload_dir)], [config.temp_dir])


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="phlix-store-")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.store = Store(os.path.join(self.root, "config", "helper.db"))
        # Looked up when it runs: two tests reopen the store.
        self.addCleanup(lambda: self.store.close())

    def test_the_server_id_survives_a_restart(self):
        first = self.store.server_id
        self.store.close()
        self.store = Store(os.path.join(self.root, "config", "helper.db"))
        self.assertEqual(self.store.server_id, first)
        self.assertRegex(first, r"^[0-9a-f-]{36}$")

    def test_pairing_gives_a_token_that_finds_the_device(self):
        device, token = self.store.pair_device("device-0001", "iPhone", "Anna’s iPhone", "code")
        self.assertEqual(device.folder, "Anna’s iPhone")
        self.assertEqual(self.store.device_for_token(token).id, "device-0001")
        self.assertIsNone(self.store.device_for_token(token + "x"))
        self.assertIsNone(self.store.device_for_token(""))

    def test_the_token_is_not_kept_in_the_database(self):
        _, token = self.store.pair_device("device-0001", "iPhone", "iPhone", "code")
        self.store.close()
        with open(os.path.join(self.root, "config", "helper.db"), "rb") as handle:
            self.assertNotIn(token.encode(), handle.read())
        self.store = Store(os.path.join(self.root, "config", "helper.db"))

    def test_two_phones_with_one_name_get_two_folders(self):
        first, _ = self.store.pair_device("device-0001", "iPhone", "iPhone", "code")
        second, _ = self.store.pair_device("device-0002", "iPhone", "iphone", "code")
        third, _ = self.store.pair_device("device-0003", "iPhone", "iPhone", "plex")
        self.assertEqual([first.folder, second.folder, third.folder], ["iPhone", "iphone 2", "iPhone 3"])

    def test_pairing_again_keeps_the_folder_and_replaces_the_token(self):
        _, old = self.store.pair_device("device-0001", "iPhone", "Family", "code")
        device, new = self.store.pair_device("device-0001", "Renamed", "Something Else", "plex")
        self.assertEqual((device.folder, device.name, device.paired_via), ("Family", "Renamed", "plex"))
        self.assertIsNone(self.store.device_for_token(old))
        self.assertEqual(self.store.device_for_token(new).id, "device-0001")
        self.assertEqual(len(self.store.devices()), 1)

    def test_unpairing_keeps_the_records_of_its_files(self):
        _, token = self.store.pair_device("device-0001", "iPhone", "iPhone", "code")
        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/x.jpg", 10, "photo", None)
        self.assertTrue(self.store.remove_device("device-0001"))
        self.assertFalse(self.store.remove_device("device-0001"))
        self.assertIsNone(self.store.device_for_token(token))
        self.assertIsNone(self.store.device_for_token(""))
        self.assertEqual(self.store.totals(), (1, 10))
        self.assertEqual(self.store.device_totals("device-0001"), (1, 10))
        self.assertEqual(self.store.devices(), [])
        self.assertEqual([device.paired for device in self.store.devices(include_unpaired=True)], [False])

    def test_an_unpaired_phones_folder_stays_its_own(self):
        self.store.pair_device("device-0001", "iPhone", "Family", "code")
        self.store.remove_device("device-0001")
        other, _ = self.store.pair_device("device-0002", "iPhone", "Family", "code")
        back, token = self.store.pair_device("device-0001", "iPhone", "Anything", "code")
        self.assertEqual((other.folder, back.folder, back.paired), ("Family 2", "Family", True))
        self.assertEqual(self.store.device_for_token(token).id, "device-0001")

    def test_known_keys_in_large_batches(self):
        self.store.pair_device("device-0001", "iPhone", "iPhone", "code")
        keys = [f"{number:032d}" for number in range(1300)]
        for key in keys[::2]:
            self.store.record_asset("device-0001", key, "a" * 64, f"iPhone/{key}.jpg", 1, "photo", None)
        self.assertEqual(self.store.known_keys("device-0001", keys), set(keys[::2]))
        self.assertEqual(self.store.known_keys("device-0002", keys), set())
        self.assertEqual(self.store.known_keys("device-0001", []), set())
        self.assertEqual(self.store.device_totals("device-0001"), (650, 650))

    def test_a_folder_another_phone_had_stays_its_own(self):
        self.store.pair_device("device-0001", "iPhone", "Family", "code")
        moved, _ = self.store.pair_device("device-0001", "iPhone", "Jason", "code", switch_folder=True)
        other, _ = self.store.pair_device("device-0002", "iPhone", "family", "code")
        back, _ = self.store.pair_device("device-0001", "iPhone", "FAMILY", "code", switch_folder=True)
        self.assertEqual((moved.folder, other.folder, back.folder), ("Jason", "family 2", "Family"))
        self.assertEqual(sorted(self.store.all_folders()),
                         [("device-0001", "Family"), ("device-0001", "Jason"), ("device-0002", "family 2")])

    def test_the_writes_of_a_check_never_undo_a_newer_record(self):
        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/x.jpg", 10, "photo", None)
        seen = self.store.asset("device-0001", "k" * 32)
        # The photo was sent again while a check looked: same path, one more return.
        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/x.jpg", 10, "photo", None, returned=True)
        self.assertFalse(self.store.flag_missing(seen, 1))
        self.assertIsNone(self.store.asset("device-0001", "k" * 32).missing_at)
        now = self.store.asset("device-0001", "k" * 32)
        self.assertTrue(self.store.flag_missing(now, 1))
        self.assertTrue(self.store.flag_missing(now, 2))
        self.assertEqual(self.store.asset("device-0001", "k" * 32).missing_at, 1)
        self.assertEqual(self.store.device_totals("device-0001"), (0, 0))
        self.assertIsNone(self.store.sha_at_path("iPhone/x.jpg"))
        self.assertEqual(self.store.present_count(), 0)
        self.assertEqual(self.store.totals(), (0, 0))
        # Found moved; a second finding from an older look changes nothing.
        self.assertTrue(self.store.repoint(now, "Sorted/x.jpg"))
        self.assertFalse(self.store.repoint(now, "Elsewhere/x.jpg"))
        self.assertEqual(self.store.asset("device-0001", "k" * 32).relpath, "Sorted/x.jpg")
        self.assertEqual(self.store.device_totals("device-0001"), (1, 10))
        self.assertEqual(self.store.totals(), (1, 10))
        # A twin is noted only for a photo the device has no record of.
        twin = self.store.asset("device-0001", "k" * 32)
        self.assertFalse(self.store.record_twin("device-0001", "k" * 32, "b" * 64, twin))
        self.assertTrue(self.store.record_twin("device-0002", "j" * 32, "a" * 64, twin))
        self.assertEqual(self.store.asset("device-0002", "j" * 32).relpath, "Sorted/x.jpg")

    def test_a_deleted_folder_restarts_the_count_and_a_newer_record_is_still_noticed(self):
        def returned(times):
            for _ in range(times):
                self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/2026/x.jpg", 10, "photo", None,
                                        returned=True)
            return self.store.asset("device-0001", "k" * 32)

        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/2026/x.jpg", 10, "photo", None)
        seen = returned(3)
        self.assertEqual(seen.returns, 3)
        # The photo was sent again while a check looked: the write of the check changes nothing.
        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/2026/x.jpg", 10, "photo", None,
                                returned=True)
        self.assertFalse(self.store.flag_missing(seen, 1, restart=True))
        now = self.store.asset("device-0001", "k" * 32)
        self.assertEqual((now.returns, now.missing_at), (4, None))
        self.assertTrue(self.store.flag_missing(now, 1, restart=True))
        now = self.store.asset("device-0001", "k" * 32)
        self.assertEqual((now.returns, now.missing_at), (0, 1))
        # Without it the count stays.
        seen = returned(2)
        self.assertTrue(self.store.flag_missing(seen, 2))
        self.assertEqual(self.store.asset("device-0001", "k" * 32).returns, 2)

    def test_counts_made_by_helper_1_0_2_start_again_once(self):
        path = os.path.join(self.root, "config", "helper.db")

        def count_after_reopening(set_to):
            with self.store.transaction():
                self.store._db.execute("UPDATE assets SET returns = ?", (set_to,))
            self.store.close()
            self.store = Store(path)
            return self.store.asset("device-0001", "k" * 32).returns

        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/2026/x.jpg", 10, "photo", None)
        # A new file is marked from the start: its counts are 1.0.3's own.
        self.assertEqual(count_after_reopening(3), 3)
        # A file that helper 1.0.2 left has no mark.
        self.store._db.execute("DELETE FROM meta WHERE key = 'returns_restarted'")
        self.assertEqual(count_after_reopening(3), 0)
        self.assertEqual(self.store.asset("device-0001", "k" * 32).relpath, "iPhone/2026/x.jpg")
        self.assertEqual(count_after_reopening(3), 3)

    def test_the_count_restarts_under_a_deleted_folder_and_nowhere_else(self):
        paths = ["50%/2026/x.jpg", "50%/2026/2026-11/x.jpg", "50%/2026 b/x.jpg", "50%/20260/x.jpg",
                 "50% off/2026/x.jpg", "50X/2026/x.jpg", "50%/x.jpg", "50%/2026"]
        for number, path in enumerate(paths):
            # Stored, and sent again twice.
            for _ in range(3):
                self.store.record_asset(f"device-000{number % 2}", f"{number:032d}", "a" * 64, path, 1, "photo",
                                        None, returned=True)
        self.assertEqual(self.store.restart_returns_under("50%/2026/"), 2)
        self.assertEqual(self.store.restart_returns_under("50%/2026/"), 0)
        counts = {path: self.store.asset(f"device-000{number % 2}", f"{number:032d}").returns
                  for number, path in enumerate(paths)}
        self.assertEqual(counts, {path: 0 if path.startswith("50%/2026/") else 2 for path in paths})

    def test_a_renamed_folder_moves_every_record_under_it_and_no_other(self):
        paths = ["50%/2026/x.jpg", "50% off/2026/x.jpg", "a_b/x.jpg", "aXb/x.jpg", "a_b 2/x.jpg", "a_bc/x.jpg"]
        for number, path in enumerate(paths):
            self.store.record_asset(f"device-000{number % 2}", f"{number:032d}", "a" * 64, path, 1, "photo", None)
        self.assertEqual(self.store.relocate("device-0000", "50%", "Fifty", "Fifty"), 1)
        self.assertEqual(self.store.relocate("device-0000", "a_b", "Renamed", "Renamed"), 1)
        after = sorted(self.store.asset(f"device-000{number % 2}", f"{number:032d}").relpath
                       for number in range(len(paths)))
        self.assertEqual(after, sorted(["Fifty/2026/x.jpg", "50% off/2026/x.jpg", "Renamed/x.jpg", "aXb/x.jpg",
                                        "a_b 2/x.jpg", "a_bc/x.jpg"]))

    def test_content_can_be_found_by_hash_and_by_path(self):
        self.store.record_asset("device-0001", "k" * 32, "a" * 64, "iPhone/x.jpg", 10, "photo", None)
        self.store.record_asset("device-0002", "j" * 32, "a" * 64, "iPhone/x.jpg", 10, "photo", None)
        self.assertEqual(len(self.store.assets_with_sha("a" * 64)), 2)
        self.assertEqual(self.store.assets_with_sha("b" * 64), [])
        self.assertEqual(self.store.sha_at_path("iPhone/x.jpg"), "a" * 64)
        self.assertIsNone(self.store.sha_at_path("iPhone/y.jpg"))


class IdentityParsingTests(unittest.TestCase):
    def test_json(self):
        body = b'{"MediaContainer":{"size":0,"claimed":true,"machineIdentifier":"abc123","version":"1.41.2"}}'
        self.assertEqual(parse_identity(body), ("abc123", "1.41.2"))

    def test_xml(self):
        body = b'<?xml version="1.0"?>\n<MediaContainer size="0" machineIdentifier="abc123" version="1.41.2">\n'
        self.assertEqual(parse_identity(body), ("abc123", "1.41.2"))

    def test_something_else_on_that_port(self):
        self.assertIsNone(parse_identity(b"<html>router login</html>"))
        self.assertIsNone(parse_identity(b'{"MediaContainer":{}}'))
        self.assertIsNone(parse_identity(b"[]"))
        self.assertIsNone(parse_identity(b""))


if __name__ == "__main__":
    unittest.main()
