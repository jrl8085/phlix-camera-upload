"""The helper as the app meets it: over HTTP, on a real socket."""

import hashlib
import http.client
import json
import os
import socket
import ssl
import threading
import time
import unittest
import urllib.parse
from unittest import mock

from phlix_upload import SERVICE_NAME, __version__, storage
from phlix_upload import __main__ as main_module
from phlix_upload import server as server_module
from phlix_upload.pairing import AttemptLimiter
from phlix_upload.tlsutil import fingerprint

from .helpers import MACHINE_ID, OWNER_TOKEN, SHARED_TOKEN, FakePlex, key, running

CREATED = "2026-11-21T22:15:03-06:00"


class HelloAndPagesTests(unittest.TestCase):
    def test_hello_says_who_this_is(self):
        with running(NAME="Tower") as helper:
            status, body, headers = helper.request("GET", "/api/v1/hello")
        self.assertEqual(status, 200)
        self.assertEqual(body["service"], SERVICE_NAME)
        self.assertEqual(body["apiVersion"], 1)
        self.assertEqual(body["version"], __version__)
        self.assertEqual(body["name"], "Tower")
        self.assertRegex(body["serverId"], r"^[0-9a-f-]{36}$")
        self.assertEqual(body["pairing"], {"plex": False, "code": True})
        self.assertIsNone(body["plex"])
        self.assertIsNone(body["tls"])
        self.assertEqual(headers["cache-control"], "no-store")

    def test_the_status_page_gives_nothing_away(self):
        with running() as helper:
            token = helper.pair(name="Secret Phone Name")
            helper.upload(token, key(1), b"photo", filename="private-name.jpg")
            status, page, headers = helper.request("GET", "/")
            code = helper.app.pairing_code
        text = page.decode()
        self.assertEqual(status, 200)
        self.assertTrue(headers["content-type"].startswith("text/html"))
        self.assertIn("Running", text)
        self.assertIn("phlixapp.com/camera-upload", text)
        for secret in (code, code.replace("-", ""), token, "Secret Phone Name", "private-name"):
            self.assertNotIn(secret, text)

    def test_health_check_and_unknown_addresses(self):
        with running() as helper:
            self.assertEqual(helper.request("GET", "/healthz")[:2], (200, b"ok\n"))
            status, body, _ = helper.request("GET", "/api/v1/nothing")
            self.assertEqual((status, body["error"]["code"]), (404, "not_found"))
            status, body, _ = helper.request("DELETE", "/api/v1/hello")
            self.assertEqual((status, body["error"]["code"]), (405, "method_not_allowed"))
            status, body, _ = helper.request("GET", f"/api/v1/assets/{key(1)}")
            self.assertEqual((status, body["error"]["code"]), (405, "method_not_allowed"))

    def test_nothing_stored_is_ever_served_back(self):
        with running() as helper:
            token = helper.pair()
            _, body, _ = helper.upload(token, key(1), b"photo")
            for path in ("/" + body["path"], "/photos/" + body["path"], "/api/v1/assets/" + body["path"]):
                status, _, _ = helper.request("GET", urllib.parse.quote(path), token=token)
                self.assertIn(status, (404, 405))


class PairingByCodeTests(unittest.TestCase):
    def test_the_right_code_pairs(self):
        with running() as helper:
            status, body, _ = helper.request("POST", "/api/v1/pair", {
                "method": "code", "code": helper.app.pairing_code.lower().replace("-", " "),
                "deviceId": "0B5C9E4A-1111-2222-3333-444455556666", "deviceName": "iPhone",
                "folderName": "Anna’s iPhone"})
            self.assertEqual(status, 200)
            self.assertEqual(body["folder"], "Anna’s iPhone")
            self.assertEqual(body["serverId"], helper.app.store.server_id)
            self.assertGreaterEqual(len(body["deviceToken"]), 40)
            status, _, _ = helper.request("GET", "/api/v1/status", token=body["deviceToken"])
            self.assertEqual(status, 200)

    def test_a_wrong_code_does_not(self):
        with running() as helper:
            status, body, _ = helper.request("POST", "/api/v1/pair", {
                "method": "code", "code": "AAAA-AAAA", "deviceId": "device-0001", "deviceName": "iPhone"})
            self.assertEqual((status, body["error"]["code"]), (403, "code_wrong"))
            self.assertEqual(helper.app.store.devices(), [])

    def test_guessing_is_slowed_then_stopped(self):
        with running() as helper:
            wrong = {"method": "code", "code": "AAAA-AAAA", "deviceId": "device-0001", "deviceName": "iPhone"}
            for _ in range(5):
                self.assertEqual(helper.request("POST", "/api/v1/pair", wrong)[0], 403)
            status, body, headers = helper.request("POST", "/api/v1/pair", wrong)
            self.assertEqual((status, body["error"]["code"]), (429, "too_many_attempts"))
            self.assertGreater(int(headers["retry-after"]), 0)
            self.assertEqual(body["error"]["retryAfter"], int(headers["retry-after"]))
            # Even the right code has to wait now.
            right = dict(wrong, code=helper.app.pairing_code)
            self.assertEqual(helper.request("POST", "/api/v1/pair", right)[0], 429)

    def test_the_owners_own_code_is_used_when_set(self):
        with running(PAIRING_CODE="sun-flower-42") as helper:
            self.assertEqual(helper.app.pairing_code, "sun-flower-42")
            helper.pair(code="SunFlower42")

    def test_malformed_requests_are_refused(self):
        with running() as helper:
            good = {"method": "code", "code": helper.app.pairing_code, "deviceId": "device-0001",
                    "deviceName": "iPhone"}
            for change in ({"deviceId": "x"}, {"deviceId": "../../etc/passwd"}, {"deviceId": 7},
                           {"deviceName": ""}, {"deviceName": None}, {"method": "magic"}, {"method": None}):
                with self.subTest(change=change):
                    status, body, _ = helper.request("POST", "/api/v1/pair", dict(good, **change))
                    self.assertEqual((status, body["error"]["code"]), (400, "bad_request"))
            status, body, _ = helper.request("POST", "/api/v1/pair", b"not json",
                                             headers={"Content-Type": "application/json"})
            self.assertEqual((status, body["error"]["code"]), (400, "bad_request"))
            status, body, _ = helper.request("POST", "/api/v1/pair", b"[1,2]")
            self.assertEqual((status, body["error"]["code"]), (400, "bad_request"))
            self.assertEqual(helper.app.store.devices(), [])

    def test_a_hostile_folder_name_stays_inside_the_upload_folder(self):
        with running() as helper:
            token = helper.pair(folder="../../../../tmp/escape")
            status, body, _ = helper.upload(token, key(1), b"photo")
            self.assertEqual(status, 201)
            final = os.path.realpath(os.path.join(helper.upload_dir, body["path"]))
            self.assertTrue(final.startswith(os.path.realpath(helper.upload_dir) + os.sep))
            self.assertNotIn("..", body["path"].split("/"))

    def test_code_pairing_can_be_switched_off(self):
        with running(PAIRING="plex") as helper:
            status, body, _ = helper.request("POST", "/api/v1/pair", {
                "method": "code", "code": helper.app.pairing_code, "deviceId": "device-0001",
                "deviceName": "iPhone"})
            self.assertEqual((status, body["error"]["code"]), (409, "pairing_method_off"))
            self.assertFalse(helper.request("GET", "/api/v1/hello")[1]["pairing"]["code"])


class PairingByPlexTests(unittest.TestCase):
    def setUp(self):
        self.plex = FakePlex()
        self.addCleanup(self.plex.close)

    def _pair(self, helper, token):
        return helper.request("POST", "/api/v1/pair", {
            "method": "plex", "plexToken": token, "deviceId": "device-0001", "deviceName": "iPhone"})

    def test_hello_names_the_plex_server_next_door(self):
        with running(PLEX_URL=self.plex.url) as helper:
            helper.app.plex.identity(wait=True)
            body = helper.request("GET", "/api/v1/hello")[1]
        self.assertEqual(body["plex"], {"machineIdentifier": MACHINE_ID})
        self.assertEqual(body["pairing"], {"plex": True, "code": True})

    def test_the_owner_pairs_without_a_code(self):
        with running(PLEX_URL=self.plex.url) as helper:
            status, body, _ = self._pair(helper, OWNER_TOKEN)
            self.assertEqual(status, 200)
            self.assertEqual(helper.app.store.devices()[0].paired_via, "plex")
            self.assertEqual(helper.request("GET", "/api/v1/status", token=body["deviceToken"])[0], 200)

    def test_the_plex_token_is_not_kept(self):
        with running(PLEX_URL=self.plex.url) as helper:
            self._pair(helper, OWNER_TOKEN)
            helper.app.store.close()
            for root, _, names in os.walk(helper.root):
                for name in names:
                    with open(os.path.join(root, name), "rb") as handle:
                        self.assertNotIn(OWNER_TOKEN.encode(), handle.read(), name)

    def test_someone_the_server_is_shared_with_does_not(self):
        with running(PLEX_URL=self.plex.url) as helper:
            status, body, _ = self._pair(helper, SHARED_TOKEN)
            self.assertEqual((status, body["error"]["code"]), (403, "plex_not_owner"))
            self.assertEqual(helper.app.store.devices(), [])

    def test_a_token_plex_does_not_know(self):
        with running(PLEX_URL=self.plex.url) as helper:
            status, body, _ = self._pair(helper, "made-up-token-000000")
            self.assertEqual((status, body["error"]["code"]), (401, "plex_token_rejected"))

    def test_wrong_plex_tokens_count_as_wrong_tries(self):
        with running(PLEX_URL=self.plex.url) as helper:
            for _ in range(5):
                self._pair(helper, "made-up-token-000000")
            self.assertEqual(self._pair(helper, OWNER_TOKEN)[0], 429)

    def test_a_plex_that_lets_anyone_in_proves_nothing(self):
        self.plex.open_access = True
        with running(PLEX_URL=self.plex.url) as helper:
            status, body, _ = self._pair(helper, "made-up-token-000000")
            self.assertEqual((status, body["error"]["code"]), (409, "plex_open_access"))
            self.assertEqual(helper.app.store.devices(), [])
            # The code still works, and it was not counted as a wrong try.
            helper.pair()

    def test_no_plex_in_reach(self):
        with running() as helper:
            status, body, _ = self._pair(helper, OWNER_TOKEN)
            self.assertEqual((status, body["error"]["code"]), (503, "plex_unreachable"))

    def test_hello_does_not_offer_plex_pairing_when_plex_lets_anyone_in(self):
        self.plex.open_access = True
        with running(PLEX_URL=self.plex.url) as helper:
            helper.app.plex.identity(wait=True)
            body = helper.request("GET", "/api/v1/hello")[1]
            self.assertEqual(body["pairing"], {"plex": False, "code": True})
            self.assertEqual(body["plex"], {"machineIdentifier": MACHINE_ID})
            health = helper.request("GET", "/api/v1/health")[1]
            self.assertEqual(health["plex"], {"found": True, "version": "1.41.2.9200", "asksForSignIn": False})
            self.assertIn("without signing in", helper.request("GET", "/")[1].decode())

    def test_plex_pairing_can_be_switched_off(self):
        with running(PLEX_URL=self.plex.url, PAIRING="code") as helper:
            status, body, _ = self._pair(helper, OWNER_TOKEN)
            self.assertEqual((status, body["error"]["code"]), (409, "pairing_method_off"))
            helper.app.plex.identity(wait=True)
            self.assertFalse(helper.request("GET", "/api/v1/hello")[1]["pairing"]["plex"])

    def test_identity_in_xml_is_understood(self):
        self.plex.identity_as_xml = True
        with running(PLEX_URL=self.plex.url) as helper:
            identity = helper.app.plex.identity(wait=True)
        self.assertEqual((identity.machine_identifier, identity.version), (MACHINE_ID, "1.41.2.9200"))

    def test_the_token_only_goes_to_the_owner_only_addresses(self):
        with running(PLEX_URL=self.plex.url) as helper:
            self._pair(helper, OWNER_TOKEN)
        with_token = [path for path, token in self.plex.requests if token == OWNER_TOKEN]
        self.assertEqual(with_token, ["/accounts", "/butler"])
        # The control request, without a token, came first.
        self.assertIn(("/accounts", None), self.plex.requests)

    def test_a_redirect_is_not_followed(self):
        with running(PLEX_URL=self.plex.url) as helper:
            status, _ = helper.app.plex._get(self.plex.url, "/redirect", OWNER_TOKEN)
        self.assertEqual(status, 302)
        self.assertNotIn("/elsewhere", [path for path, _ in self.plex.requests])


class UploadTests(unittest.TestCase):
    def test_a_photo_lands_in_its_folder(self):
        data = os.urandom(300_000)
        with running() as helper:
            token = helper.pair(folder="Anna’s iPhone")
            status, body, _ = helper.upload(token, key(1), data, filename="IMG_1234.HEIC", created=CREATED)
            self.assertEqual(status, 201)
            self.assertEqual(body, {"status": "stored", "path": "Anna’s iPhone/2026/2026-11/IMG_1234.HEIC",
                                    "bytes": len(data)})
            final = os.path.join(helper.upload_dir, body["path"])
            with open(final, "rb") as handle:
                self.assertEqual(handle.read(), data)
            self.assertAlmostEqual(os.path.getmtime(final), storage.parse_created(CREATED).timestamp(), delta=1)
            self.assertEqual(helper.files(), ["Anna’s iPhone/2026/2026-11/IMG_1234.HEIC"])
            self.assertEqual(os.listdir(helper.app.config.temp_dir), [])

    def test_the_same_upload_again_is_recognised(self):
        with running() as helper:
            token = helper.pair()
            self.assertEqual(helper.upload(token, key(1), b"photo")[0], 201)
            status, body, _ = helper.upload(token, key(1), b"photo")
            self.assertEqual((status, body["status"]), (200, "duplicate"))
            self.assertEqual(len(helper.files()), 1)

    def test_the_same_photo_from_a_second_phone_is_stored_once(self):
        with running() as helper:
            first = helper.pair("device-0001", folder="Anna")
            second = helper.pair("device-0002", folder="Alex")
            _, stored, _ = helper.upload(first, key(1), b"shared library photo")
            status, body, _ = helper.upload(second, key(2), b"shared library photo")
            # It is told the photo is there, and not where the other phone keeps it.
            self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", ""))
            self.assertEqual(len(helper.files()), 1)
            # Nor when it sends the photo again under the same key, as a phone
            # does when the first answer was lost on the way.
            status, body, _ = helper.upload(second, key(2), b"shared library photo")
            self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", ""))
            # Nor after it asked about the photo by its checksum.
            sha = hashlib.sha256(b"shared library photo").hexdigest()
            helper.request("POST", "/api/v1/assets/check", {"items": [{"key": key(4), "sha256": sha}]}, token=second)
            status, body, _ = helper.upload(second, key(4), b"shared library photo")
            self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", ""))
            # The phone the file belongs to may know its own path, under any key
            # and however often it asks.
            for number in (3, 3, 1):
                status, body, _ = helper.upload(first, key(number), b"shared library photo")
                self.assertEqual((status, body["status"], body["path"]), (200, "duplicate", stored["path"]))
            # ...and the second phone now knows it need not send it.
            _, known, _ = helper.request("POST", "/api/v1/assets/check", {"items": [key(2)]}, token=second)
            self.assertEqual(known["known"], [key(2)])

    def test_two_phones_sending_the_same_photo_at_once(self):
        data = os.urandom(2_000_000)
        with running() as helper:
            tokens = [helper.pair(f"device-000{n}", folder=f"Phone {n}") for n in range(4)]
            results = []
            threads = [threading.Thread(target=lambda t=t, n=n: results.append(helper.upload(t, key(n), data)[0]))
                       for n, t in enumerate(tokens)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(sorted(results), [200, 200, 200, 201])
            self.assertEqual(len(helper.files()), 1)
            self.assertEqual(os.listdir(helper.app.config.temp_dir), [])

    def test_different_photos_with_one_name_are_both_kept(self):
        with running() as helper:
            token = helper.pair()
            first = helper.upload(token, key(1), b"first", filename="IMG_0001.JPG")[1]["path"]
            second = helper.upload(token, key(2), b"second", filename="IMG_0001.JPG")[1]["path"]
            self.assertEqual(first, "iPhone/2026/2026-11/IMG_0001.JPG")
            self.assertEqual(second, "iPhone/2026/2026-11/IMG_0001 (2).JPG")

    def test_a_file_deleted_on_the_server_is_stored_again_if_sent(self):
        with running() as helper:
            token = helper.pair()
            path = helper.upload(token, key(1), b"photo")[1]["path"]
            os.unlink(os.path.join(helper.upload_dir, path))
            status, body, _ = helper.upload(token, key(1), b"photo")
            self.assertEqual((status, body["status"]), (201, "stored"))
            self.assertEqual(helper.files(), [path])

    def test_a_damaged_upload_is_thrown_away(self):
        with running() as helper:
            token = helper.pair()
            status, body, _ = helper.upload(token, key(1), b"photo", sha256="0" * 64)
            self.assertEqual((status, body["error"]["code"]), (422, "checksum_mismatch"))
            self.assertEqual(helper.files(), [])
            self.assertEqual(os.listdir(helper.app.config.temp_dir), [])
            # Nothing was recorded, so the next try stores it.
            self.assertEqual(helper.upload(token, key(1), b"photo")[0], 201)

    def test_an_upload_without_a_checksum_is_still_stored(self):
        with running() as helper:
            token = helper.pair()
            self.assertEqual(helper.upload(token, key(1), b"photo", sha256="")[0], 201)

    def test_only_paired_phones_may_upload(self):
        with running() as helper:
            for token in (None, "x" * 43):
                status, body, headers = helper.upload(token, key(1), os.urandom(200_000))
                self.assertEqual((status, body["error"]["code"]), (401, "unauthorized"))
                self.assertEqual(headers.get("connection"), "close")
            self.assertEqual(helper.files(), [])

    def test_refusals(self):
        with running(MAX_UPLOAD_GB="0.001") as helper:
            token = helper.pair()
            cases = [
                (helper.upload(token, key(1), b"#!/bin/sh", filename="run.sh"), 415, "unsupported_type"),
                (helper.upload(token, key(1), b"x", filename="noextension"), 415, "unsupported_type"),
                (helper.upload(token, key(1), b"x" * 1_200_000), 413, "too_large"),
                (helper.upload(token, "short", b"photo"), 400, "bad_request"),
                (helper.upload(token, "../../../etc/passwd-" + "a" * 20, b"photo"), 400, "bad_request"),
                (helper.upload(token, key(1), b""), 400, "bad_request"),
                (helper.upload(token, key(1), b"photo", sha256="zz"), 400, "bad_request"),
            ]
            for (status, body, _), wanted_status, wanted_code in cases:
                self.assertEqual((status, body["error"]["code"]), (wanted_status, wanted_code))
            self.assertEqual(helper.files(), [])
            self.assertEqual(os.listdir(helper.app.config.temp_dir), [])

    def test_a_nearly_full_disk_refuses_before_anything_is_written(self):
        with running(MIN_FREE_GB="900000") as helper:
            token = helper.pair()
            status, body, _ = helper.upload(token, key(1), b"photo")
            self.assertEqual((status, body["error"]["code"]), (507, "insufficient_storage"))
            self.assertEqual(helper.files(), [])
            status, body, _ = helper.request("GET", "/api/v1/status", token=token)
            self.assertLess(body["storage"]["freeBytes"], body["storage"]["minFreeBytes"])

    def test_a_hostile_file_name_stays_in_its_folder(self):
        with running() as helper:
            token = helper.pair()
            status, body, _ = helper.upload(token, key(1), b"photo", filename="../../../../etc/cron.d/evil.jpg")
            self.assertEqual((status, body["path"]), (201, "iPhone/2026/2026-11/evil.jpg"))
            status, body, _ = helper.upload(token, key(2), b"photo2", filename="..\\..\\boot.jpg")
            self.assertEqual(body["path"], "iPhone/2026/2026-11/boot.jpg")

    def test_a_photo_without_a_date_goes_under_today(self):
        with running(PATH_TEMPLATE="{device}") as helper:
            token = helper.pair()
            self.assertEqual(helper.upload(token, key(1), b"photo", created=None)[1]["path"], "iPhone/IMG_0001.HEIC")
            self.assertEqual(helper.upload(token, key(2), b"photo2", created="nonsense")[1]["path"],
                             "iPhone/IMG_0001 (2).HEIC")

    def test_a_missing_length_is_refused(self):
        with running() as helper:
            token = helper.pair()
            connection = helper.connection()
            connection.putrequest("PUT", f"/api/v1/assets/{key(1)}")
            connection.putheader("Authorization", f"Bearer {token}")
            connection.putheader("Transfer-Encoding", "chunked")
            connection.endheaders()
            connection.send(b"5\r\nphoto\r\n0\r\n\r\n")
            response = connection.getresponse()
            self.assertEqual(response.status, 411)
            connection.close()

    def test_a_phone_that_disappears_mid_upload_leaves_nothing_behind(self):
        with running() as helper:
            token = helper.pair()
            raw = socket.create_connection(("127.0.0.1", helper.port), timeout=5)
            raw.sendall((f"PUT /api/v1/assets/{key(1)} HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer {token}\r\n"
                         f"X-Phlix-Filename: IMG_1.JPG\r\nContent-Length: 1000000\r\n\r\n").encode() + b"x" * 5000)
            # Wait until the upload has begun on the server. Looking for an
            # empty folder before that would pass at once, and a moment later
            # the server would make the file this test says is not there.
            for _ in range(200):
                if os.listdir(helper.app.config.temp_dir):
                    break
                threading.Event().wait(0.02)
            self.assertNotEqual(os.listdir(helper.app.config.temp_dir), [], "the upload never began")
            raw.close()
            for _ in range(200):
                if not os.listdir(helper.app.config.temp_dir):
                    break
                threading.Event().wait(0.02)
            self.assertEqual(os.listdir(helper.app.config.temp_dir), [])
            self.assertEqual(helper.files(), [])
            # The server is still answering.
            self.assertEqual(helper.request("GET", "/healthz")[0], 200)

    def test_one_connection_carries_many_uploads(self):
        with running() as helper:
            token = helper.pair()
            connection = helper.connection()
            for number in range(5):
                data = f"photo {number}".encode()
                connection.request("PUT", f"/api/v1/assets/{key(number)}", body=data, headers={
                    "Authorization": f"Bearer {token}", "X-Phlix-Filename": f"IMG_{number}.JPG",
                    "X-Phlix-Created": CREATED, "X-Phlix-SHA256": hashlib.sha256(data).hexdigest()})
                response = connection.getresponse()
                self.assertEqual(response.status, 201)
                json.loads(response.read())
            connection.close()
            self.assertEqual(len(helper.files()), 5)


class HardeningTests(unittest.TestCase):
    """What someone on the network who means harm can and cannot do."""

    def _idle(self, helper):
        """A connection that is opened and then says nothing."""
        return socket.create_connection(("127.0.0.1", helper.port), timeout=5)

    def test_one_address_cannot_take_every_connection(self):
        with running() as helper, mock.patch.object(server_module, "MAX_CONNECTIONS_PER_ADDRESS", 3):
            held = [self._idle(helper) for _ in range(3)]
            try:
                self._wait(lambda: helper.server._active_by_address.get("127.0.0.1") == 3)
                # The address has its share: one more is turned away at the door.
                with self.assertRaises((OSError, http.client.HTTPException)):
                    helper.request("GET", "/healthz")
                self.assertEqual(helper.server._active, 3)
            finally:
                for connection in held:
                    connection.close()
            # As soon as it lets go, it is served again.
            self._wait(lambda: not helper.server._active_by_address)
            self.assertEqual(helper.request("GET", "/healthz")[0], 200)

    def test_a_busy_address_does_not_keep_others_out(self):
        with running() as helper:
            # Some other address holds all it may.
            with helper.server._active_lock:
                helper.server._active += server_module.MAX_CONNECTIONS_PER_ADDRESS
                helper.server._active_by_address["192.168.1.66"] = server_module.MAX_CONNECTIONS_PER_ADDRESS
            self.assertEqual(helper.request("GET", "/healthz")[0], 200)

    def test_a_silent_connection_is_dropped(self):
        with running() as helper, mock.patch.object(server_module.Handler, "timeout", 0.3):
            connection = self._idle(helper)
            try:
                connection.sendall(b"GET /healthz HTTP/1.1\r\nHost: x")  # and nothing more
                connection.settimeout(5)
                self.assertEqual(connection.recv(100), b"")
            finally:
                connection.close()
            self._wait(lambda: helper.server._active == 0)

    def _wait(self, condition, seconds: float = 5.0):
        deadline = time.monotonic() + seconds
        while not condition() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(condition())

    def test_space_is_promised_to_the_uploads_that_are_arriving(self):
        with running() as helper:
            app = helper.app
            app.storage.disk_usage = lambda: (100, 1000)
            self.assertTrue(app.reserve_space(60))
            # The first 60 bytes are not on the disk yet, and are counted all the same.
            self.assertFalse(app.reserve_space(60))
            self.assertTrue(app.reserve_space(40))
            self.assertFalse(app.reserve_space(1))
            # What has been written, or will never come, is given back.
            app.release_space(60)
            app.release_space(40)
            app.release_space(1_000_000)
            self.assertTrue(app.reserve_space(100))

    def test_uploads_sent_at_once_cannot_fill_the_disk_past_its_floor(self):
        with running() as helper:
            token = helper.pair()
            helper.app.storage.disk_usage = lambda: (150, 1000)
            data = b"x" * 100
            # One upload is on its way: its headers and half of its bytes.
            slow = self._idle(helper)
            try:
                slow.sendall(
                    f"PUT /api/v1/assets/{key(1)} HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer {token}\r\n"
                    f"X-Phlix-Filename: IMG_0001.HEIC\r\nContent-Length: {len(data)}\r\n\r\n".encode() + data[:50]
                )
                # Its whole size is counted from the moment it is let in.
                self._wait(lambda: helper.app._promised == 100)
                # A second one of the same size no longer fits above the floor...
                status, body, _ = helper.upload(token, key(2), data, filename="IMG_0002.HEIC")
                self.assertEqual((status, body["error"]["code"]), (507, "insufficient_storage"))
                # ...and the first is unharmed.
                slow.sendall(data[50:])
                slow.settimeout(5)
                self.assertIn(b" 201 ", slow.recv(200))
            finally:
                slow.close()
            self.assertEqual(helper.app._promised, 0)
            self.assertEqual(len(helper.files()), 1)

    def test_an_upload_that_stops_half_way_gives_its_space_back(self):
        with running() as helper:
            token = helper.pair()
            helper.app.storage.disk_usage = lambda: (150, 1000)
            broken = self._idle(helper)
            try:
                broken.sendall(
                    f"PUT /api/v1/assets/{key(1)} HTTP/1.1\r\nHost: x\r\nAuthorization: Bearer {token}\r\n"
                    f"X-Phlix-Filename: IMG_0001.HEIC\r\nContent-Length: 100\r\n\r\n".encode() + b"x" * 10
                )
                self._wait(lambda: helper.app._promised == 100)
            finally:
                broken.close()
            self._wait(lambda: helper.app._promised == 0)
            self.assertEqual(os.listdir(helper.app.config.temp_dir), [])

    def test_text_that_is_not_text_is_refused_not_crashed_on(self):
        with running() as helper:
            for body in (
                b'{"method":"code","code":"x","deviceId":"device-0001","deviceName":"\\ud800"}',
                b"[" * 100_000 + b"]" * 100_000,
                b'{"a":' * 50_000 + b"1" + b"}" * 50_000,
            ):
                status, answer, _ = helper.request("POST", "/api/v1/pair", body,
                                                   headers={"Content-Type": "application/json"})
                self.assertEqual((status, answer["error"]["code"]), (400, "bad_request"), body[:40])
            self.assertEqual(helper.request("GET", "/healthz")[0], 200)

    def test_a_body_on_a_request_that_takes_none_ends_the_connection(self):
        with running() as helper:
            connection = helper.connection()
            try:
                connection.request("GET", "/api/v1/hello", body=b"GET /healthz HTTP/1.1\r\n\r\n")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.getheader("Connection"), "close")
                response.read()
            finally:
                connection.close()

    def test_a_device_named_like_a_folder_pattern_keeps_its_name(self):
        with running() as helper:
            token = helper.pair(folder="{year}")
            status, body, _ = helper.upload(token, key(1), b"photo")
            self.assertEqual(status, 201)
            self.assertEqual(body["path"], "{year}/2026/2026-11/IMG_0001.HEIC")

    def test_pairing_again_is_written_in_the_log(self):
        with running() as helper:
            first = helper.pair("device-0001")
            with self.assertLogs("phlix.server", level="WARNING") as logs:
                second = helper.pair("device-0001")
            self.assertTrue(any("has paired again" in line for line in logs.output))
            # The earlier pairing stopped working, as the log says.
            self.assertEqual(helper.request("GET", "/api/v1/status", token=first)[0], 401)
            self.assertEqual(helper.request("GET", "/api/v1/status", token=second)[0], 200)

    def test_wrong_plex_sign_ins_never_pause_pairing_with_the_code(self):
        fake = FakePlex()
        try:
            with running(PLEX_URL=fake.url) as helper:
                helper.app.limiter = AttemptLimiter(per_address=1000, overall=3)
                for _ in range(5):
                    status, _, _ = helper.request("POST", "/api/v1/pair", {
                        "method": "plex", "plexToken": "not-a-real-token", "deviceId": "device-0009",
                        "deviceName": "iPhone"})
                    self.assertEqual(status, 401)
                # Five refused sign-ins, and the code still pairs.
                helper.pair("device-0001")
                # Wrong codes are what the pause for everyone counts.
                for _ in range(3):
                    status, _, _ = helper.request("POST", "/api/v1/pair", {
                        "method": "code", "code": "WRONG-CODE", "deviceId": "device-0002", "deviceName": "iPhone"})
                    self.assertEqual(status, 403)
                status, body, _ = helper.request("POST", "/api/v1/pair", {
                    "method": "code", "code": helper.app.pairing_code, "deviceId": "device-0002",
                    "deviceName": "iPhone"})
                self.assertEqual((status, body["error"]["code"]), (429, "too_many_attempts"))
                # The owner, through Plex, is not kept waiting by it.
                status, _, _ = helper.request("POST", "/api/v1/pair", {
                    "method": "plex", "plexToken": OWNER_TOKEN, "deviceId": "device-0003", "deviceName": "iPhone"})
                self.assertEqual(status, 200)
        finally:
            fake.close()


class CheckStatusAndUnpairTests(unittest.TestCase):
    def test_check_says_which_photos_are_already_here(self):
        with running() as helper:
            token = helper.pair()
            helper.upload(token, key(1), b"one")
            helper.upload(token, key(3), b"three", filename="IMG_0003.HEIC")
            status, body, _ = helper.request("POST", "/api/v1/assets/check",
                                             {"items": [key(1), key(2), {"key": key(3)}, key(4)]}, token=token)
            self.assertEqual((status, body), (200, {"known": [key(1), key(3)]}))

    def test_check_with_a_hash_finds_a_photo_another_phone_sent(self):
        data = b"a photo both phones hold"
        with running() as helper:
            first = helper.pair("device-0001", folder="Anna")
            second = helper.pair("device-0002", folder="Alex")
            helper.upload(first, key(1), data)
            items = [{"key": key(2), "sha256": hashlib.sha256(data).hexdigest().upper()},
                     {"key": key(3), "sha256": hashlib.sha256(b"new").hexdigest()}]
            _, body, _ = helper.request("POST", "/api/v1/assets/check", {"items": items}, token=second)
            self.assertEqual(body, {"known": [key(2)]})
            self.assertEqual(helper.app.store.device_totals("device-0002")[0], 1)

    def test_one_phone_cannot_see_what_another_sent(self):
        with running() as helper:
            first = helper.pair("device-0001", folder="Anna")
            second = helper.pair("device-0002", folder="Alex")
            helper.upload(first, key(1), b"one")
            _, body, _ = helper.request("POST", "/api/v1/assets/check", {"items": [key(1)]}, token=second)
            self.assertEqual(body, {"known": []})

    def test_check_refuses_nonsense(self):
        with running() as helper:
            token = helper.pair()
            for payload in ({"items": "all"}, {"items": ["short"]}, {"items": [{"sha256": "a" * 64}]},
                            {"items": [key(1)] * 2001}, {}):
                status, body, _ = helper.request("POST", "/api/v1/assets/check", payload, token=token)
                self.assertEqual((status, body["error"]["code"]), (400, "bad_request"))
            status, body, _ = helper.request("POST", "/api/v1/assets/check", {"items": [key(1)]})
            self.assertEqual((status, body["error"]["code"]), (401, "unauthorized"))

    def test_status_reports_space_and_this_phones_totals(self):
        with running(NAME="Tower") as helper:
            token = helper.pair(folder="Anna")
            helper.upload(token, key(1), b"12345")
            status, body, _ = helper.request("GET", "/api/v1/status", token=token)
            self.assertEqual(status, 200)
            self.assertEqual(body["name"], "Tower")
            self.assertEqual(body["device"], {"id": "device-0001", "name": "iPhone", "folder": "Anna",
                                              "assetCount": 1, "bytes": 5})
            self.assertTrue(body["storage"]["writable"])
            self.assertGreater(body["storage"]["totalBytes"], 0)
            self.assertEqual(body["limits"]["maxUploadBytes"], 50 * 1024 ** 3)
            self.assertEqual(helper.request("GET", "/api/v1/status")[0], 401)
            self.assertEqual(helper.request("GET", "/api/v1/status", token="x" * 43)[0], 401)

    def test_unpairing_ends_the_token_and_keeps_the_photos(self):
        with running() as helper:
            token = helper.pair()
            helper.upload(token, key(1), b"photo")
            self.assertEqual(helper.request("POST", "/api/v1/unpair", b"", token=token)[:2],
                             (200, {"unpaired": True}))
            self.assertEqual(helper.request("GET", "/api/v1/status", token=token)[0], 401)
            self.assertEqual(len(helper.files()), 1)
            # Pairing again brings the phone back to the folder it had.
            again = helper.pair(folder="A New Name")
            self.assertEqual(helper.request("GET", "/api/v1/status", token=again)[1]["device"]["folder"], "iPhone")
            _, body, _ = helper.request("POST", "/api/v1/assets/check", {"items": [key(1)]}, token=again)
            self.assertEqual(body["known"], [key(1)])


class TLSTests(unittest.TestCase):
    def test_the_helper_serves_tls_with_its_own_certificate(self):
        with running(tls=True) as helper:
            status, body, _ = helper.request("GET", "/api/v1/hello")
            self.assertEqual(status, 200)
            shown = body["tls"]["sha256"]
            # What a client sees in the handshake is what hello reports and
            # what the certificate on disk hashes to: the app pins this.
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection(("127.0.0.1", helper.port), timeout=5) as raw:
                with context.wrap_socket(raw) as secure:
                    seen = hashlib.sha256(secure.getpeercert(binary_form=True)).hexdigest()
                    self.assertIn(secure.version(), ("TLSv1.2", "TLSv1.3"))
            self.assertEqual(seen, shown)
            self.assertEqual(fingerprint(os.path.join(helper.app.config.tls_dir, "cert.pem")), shown)
            self.assertEqual(os.stat(os.path.join(helper.app.config.tls_dir, "key.pem")).st_mode & 0o777, 0o600)

    def test_uploads_work_over_tls(self):
        data = os.urandom(1_500_000)
        with running(tls=True) as helper:
            token = helper.pair()
            status, body, _ = helper.upload(token, key(1), data)
            self.assertEqual(status, 201)
            with open(os.path.join(helper.upload_dir, body["path"]), "rb") as handle:
                self.assertEqual(handle.read(), data)

    def test_plain_http_to_the_tls_port_gets_nowhere_and_harms_nothing(self):
        with running(tls=True) as helper:
            plain = http.client.HTTPConnection("127.0.0.1", helper.port, timeout=5)
            with self.assertRaises((http.client.HTTPException, OSError)):
                plain.request("GET", "/api/v1/hello")
                plain.getresponse()
            plain.close()
            self.assertEqual(helper.request("GET", "/healthz")[0], 200)

    def test_a_silent_connection_does_not_block_others(self):
        with running(tls=True) as helper:
            idle = [socket.create_connection(("127.0.0.1", helper.port), timeout=5) for _ in range(5)]
            try:
                self.assertEqual(helper.request("GET", "/healthz")[0], 200)
            finally:
                for connection in idle:
                    connection.close()

    def test_the_certificate_is_made_once(self):
        with running(tls=True) as helper:
            cert = os.path.join(helper.app.config.tls_dir, "cert.pem")
            first = fingerprint(cert)
            from phlix_upload.tlsutil import ensure_certificate
            ensure_certificate(helper.app.config.tls_dir)
            self.assertEqual(fingerprint(cert), first)


class AdminCommandTests(unittest.TestCase):
    def _run(self, helper, *arguments):
        import contextlib
        import io
        from unittest import mock
        environment = {"UPLOAD_DIR": helper.upload_dir, "CONFIG_DIR": helper.app.config.config_dir}
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, environment, clear=True), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main_module.main(list(arguments))
            except SystemExit as stop:
                code = stop.code
        return code, out.getvalue(), err.getvalue()

    def test_code_devices_and_unpair(self):
        with running() as helper:
            token = helper.pair(folder="Anna")
            helper.upload(token, key(1), b"photo")
            code, out, _ = self._run(helper, "code")
            self.assertEqual((code, out.strip()), (0, helper.app.pairing_code))
            code, out, _ = self._run(helper, "devices")
            self.assertEqual(code, 0)
            self.assertIn("Anna\t1 files", out)
            self.assertNotIn(token, out)
            code, out, _ = self._run(helper, "unpair", "anna")
            self.assertEqual(code, 0)
            self.assertEqual(helper.request("GET", "/api/v1/status", token=token)[0], 401)
            self.assertEqual(self._run(helper, "unpair", "anna")[0], 1)
            out = self._run(helper, "devices")[1]
            self.assertIn("No devices are paired.", out)
            self.assertIn("Anna\t1 files\tunpaired", out)

    def test_a_new_code_replaces_the_old_one(self):
        with running() as helper:
            old = helper.app.pairing_code
            code, out, _ = self._run(helper, "new-code")
            self.assertEqual(code, 0)
            new = out.splitlines()[0]
            self.assertNotEqual(new, old)
            self.assertEqual(self._run(helper, "code")[1].strip(), new)

    def _doctor(self, helper, **environment):
        import contextlib
        import io
        from unittest import mock
        env = {"UPLOAD_DIR": helper.upload_dir, "CONFIG_DIR": helper.app.config.config_dir,
               "PORT": str(helper.port), "TLS": "on" if helper.tls else "off", "MIN_FREE_GB": "0",
               "PLEX_URL": "http://127.0.0.1:9"}
        env.update(environment)
        out = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(out):
            code = main_module.main(["doctor"])
        return code, out.getvalue()

    def test_doctor_finds_nothing_wrong_with_a_healthy_helper(self):
        for tls in (False, True):
            with running(tls=tls) as helper:
                token = helper.pair()
                helper.upload(token, key(1), b"photo")
                code, out = self._doctor(helper)
                self.assertEqual(code, 0, out)
                self.assertIn("OK       The helper is running", out)
                self.assertIn("can be written to", out)
                self.assertIn("1 paired, 1 files stored (5 bytes)", out)
                self.assertIn("Nothing needs fixing.", out)
                self.assertNotIn(helper.app.pairing_code, out)
                self.assertNotIn(token, out)

    def test_doctor_says_how_to_fix_what_is_wrong(self):
        with running() as helper:
            # A disk with too little room, as the running helper sees it.
            object.__setattr__(helper.app.config, "min_free_bytes", 10 ** 18)
            code, out = self._doctor(helper)
            self.assertEqual(code, 1, out)
            self.assertIn("PROBLEM  Only", out)
            self.assertIn("Fix: Free some space", out)
            self.assertIn("1 to fix.", out)
        # ...and a helper that is not running at all.
        code, out = self._doctor(helper)
        self.assertEqual(code, 1)
        self.assertIn("is not answering on port", out)
        self.assertIn("docker logs phlix-camera-upload", out)

    def test_plex_only_pairing_with_no_plex_is_a_problem_not_a_note(self):
        with running(PAIRING="plex") as helper:
            helper.app.plex.identity(wait=True)
            # Nobody can pair, and neither the page nor doctor says they can.
            _, page, _ = helper.request("GET", "/")
            self.assertIn(b"no phone can", page)
            self.assertNotIn(b"Pairing needs the pairing code", page)
            code, out = self._doctor(helper, PAIRING="plex")
            self.assertEqual(code, 1, out)
            self.assertIn("PROBLEM  No Plex Media Server found, and this helper pairs through Plex only", out)
            self.assertIn("Fix: Set PLEX_URL", out)
        with running() as helper:
            helper.app.plex.identity(wait=True)
            _, page, _ = helper.request("GET", "/")
            self.assertIn(b"Pairing needs the pairing code", page)
            code, out = self._doctor(helper)
            self.assertEqual(code, 0, out)
            self.assertIn("NOTE     No Plex Media Server found. Phones pair with the pairing code.", out)

    def test_doctor_asks_the_address_the_helper_listens_on(self):
        with running() as helper:
            asked = []
            real = main_module.urllib.request.OpenerDirector.open

            def spy(opener, url, *arguments, **keywords):
                asked.append(url if isinstance(url, str) else url.full_url)
                return real(opener, url, *arguments, **keywords)

            with mock.patch.object(main_module.urllib.request.OpenerDirector, "open", spy):
                self._doctor(helper)
                self._doctor(helper, BIND="0.0.0.0")
                self._doctor(helper, BIND="127.0.0.1")
                # One address only: that is where the question goes.
                self._doctor(helper, BIND="192.0.2.7")
            # (The helper under test asks Plex through the same class.)
            hosts = [url.split("//")[1].split(":")[0] for url in asked if url.endswith("/api/v1/health")]
            self.assertEqual(hosts, ["127.0.0.1", "127.0.0.1", "127.0.0.1", "192.0.2.7"])

    def test_a_data_folder_that_cannot_be_written_is_said_in_one_line(self):
        if os.geteuid() == 0:
            self.skipTest("root may write anywhere")
        import tempfile
        root = tempfile.mkdtemp(prefix="phlix-upload-test-")
        self.addCleanup(lambda: (os.chmod(os.path.join(root, "config"), 0o700), __import__("shutil").rmtree(root, True)))
        os.makedirs(os.path.join(root, "photos"))
        os.makedirs(os.path.join(root, "config"))
        os.chmod(os.path.join(root, "config"), 0o500)
        env = {"UPLOAD_DIR": os.path.join(root, "photos"), "CONFIG_DIR": os.path.join(root, "config"),
               "PORT": "17499", "BIND": "127.0.0.1", "PLEX_URL": "http://127.0.0.1:9"}
        with mock.patch.dict(os.environ, env, clear=True), self.assertLogs("phlix", level="ERROR") as logs:
            code = main_module.serve()
        self.assertEqual(code, 1)
        text = "\n".join(logs.output)
        self.assertIn("cannot use its own data folder", text)
        self.assertIn("PUID and PGID", text)
        self.assertNotIn("Traceback", text)

    def test_doctor_does_not_promise_plex_pairing_when_it_is_switched_off(self):
        plex = FakePlex()
        self.addCleanup(plex.close)
        with running(PLEX_URL=plex.url, PAIRING="code") as helper:
            helper.app.plex.identity(wait=True)
            code, out = self._doctor(helper, PLEX_URL=plex.url, PAIRING="code")
            self.assertEqual(code, 0, out)
            self.assertIn("pairing code only", out)
            self.assertNotIn("without a code", out)
        with running(PLEX_URL=plex.url) as helper:
            helper.app.plex.identity(wait=True)
            code, out = self._doctor(helper, PLEX_URL=plex.url)
            self.assertIn("its owner can pair from Phlix without a code", out)

    def test_a_photo_two_phones_hold_is_counted_once(self):
        with running() as helper:
            first = helper.pair("device-0001", folder="Anna")
            second = helper.pair("device-0002", folder="Alex")
            helper.upload(first, key(1), b"shared")
            helper.upload(second, key(2), b"shared")
            helper.upload(second, key(3), b"hers alone")
            body = helper.request("GET", "/api/v1/health")[1]
            self.assertEqual(body["files"], {"count": 2, "bytes": 16})
            self.assertEqual(body["devices"], 2)
            self.assertEqual(len(helper.files()), 2)

    def test_doctor_reports_a_wrong_setting(self):
        import contextlib
        import io
        from unittest import mock
        err = io.StringIO()
        with mock.patch.dict(os.environ, {"PORT": "seventy"}, clear=True), contextlib.redirect_stderr(err):
            self.assertEqual(main_module.main(["doctor"]), 2)
        self.assertIn("PORT", err.getvalue())

    def test_the_health_report_gives_nothing_away(self):
        with running() as helper:
            token = helper.pair(name="Secret Phone")
            helper.upload(token, key(1), b"photo", filename="private.jpg")
            status, body, _ = helper.request("GET", "/api/v1/health")
            self.assertEqual(status, 200)
            self.assertTrue(body["ok"])
            self.assertEqual(body["devices"], 1)
            self.assertEqual(body["files"], {"count": 1, "bytes": 5})
            text = str(body)
            for secret in (helper.app.pairing_code, token, "Secret Phone", "private"):
                self.assertNotIn(secret, text)

    def test_version_and_unknown_commands(self):
        with running() as helper:
            self.assertEqual(self._run(helper, "version")[:2], (0, __version__ + "\n"))
            self.assertEqual(self._run(helper, "explode")[0], 2)


if __name__ == "__main__":
    unittest.main()
