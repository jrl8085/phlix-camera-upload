#!/bin/sh
# Smoke test for a running Phlix Camera Upload helper.
#
# Usage:
#   smoke-test.sh BASE_URL PAIRING_CODE [PHOTOS_DIR]
#
#   BASE_URL      Where the helper answers, for example https://192.168.1.10:7459
#   PAIRING_CODE  The helper's pairing code. Print it with:
#                   docker exec phlix-camera-upload python -m phlix_upload code
#   PHOTOS_DIR    Optional. The upload folder as this machine sees it. When
#                 given, the test also checks that the uploaded file is on
#                 disk at the path the helper reported, with the right bytes.
#
# What it does: it acts like a phone. It asks the helper who it is and whether
# it can do its job, pairs with the pairing code as a device named "Smoke
# Test", uploads one small picture, uploads it again, asks which pictures the
# helper has, reads the status, checks that a wrong token is refused, and
# unpairs. It also sends the same picture as a second device, "Smoke Test 2",
# twice, and checks that the helper stores nothing twice and never says where
# the first device's file is.
#
# What it leaves behind: one small grey picture in a "Smoke Test" folder
# inside the upload folder, and two unpaired entries in the helper's device
# list, "Smoke Test" and "Smoke Test 2". The helper never deletes a file, so
# delete that folder yourself when you are done.
#
# Needs sh, curl and python3. The exit status is 0 when every check passed,
# 1 when a check failed, and 2 when the test could not start.

set -u

usage() {
    echo "Usage: smoke-test.sh BASE_URL PAIRING_CODE [PHOTOS_DIR]" >&2
    echo "Example: smoke-test.sh https://192.168.1.10:7459 K7QM-3XPD" >&2
    exit 2
}

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    usage
fi

BASE=${1%/}
CODE=$2
PHOTOS_DIR=${3:-}

case $BASE in
    http://* | https://*) ;;
    *)
        echo "smoke-test: BASE_URL must start with http:// or https://" >&2
        exit 2
        ;;
esac

for tool in curl python3; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "smoke-test: $tool is needed, and it is not installed" >&2
        exit 2
    fi
done

WORK=$(mktemp -d "${TMPDIR:-/tmp}/phlix-smoke-test.XXXXXX") || exit 2
trap 'rm -rf "$WORK"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

BODY=$WORK/body
PASSED=0
FAILED=0
STATUS=000

# A 16 x 16 grey JPEG of 342 bytes, in base64. Each run writes a comment
# into its copy, so every run uploads a file the helper has not seen before.
PICTURE='
/9j/4AAQSkZJRgABAQAASABIAAD/wAALCAAQABABAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAEC
AwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0Kx
wRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1
dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ
2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9sAQwAEBAQEBAQGBAQGCQYGBgkMCQkJCQwPDAwMDAwPEg8P
Dw8PDxISEhISEhISFRUVFRUVGRkZGRkcHBwcHBwcHBwc/90ABAAC/9oACAEBAAA/ACiv/9Aor//Z
'

pass() {
    PASSED=$((PASSED + 1))
    printf 'PASS  %s\n' "$1"
}

# fail WHAT [WHY]
fail() {
    FAILED=$((FAILED + 1))
    printf 'FAIL  %s\n' "$1"
    if [ "$#" -gt 1 ] && [ -n "$2" ]; then
        printf '      %s\n' "$2"
    fi
}

# skip WHAT: a check that cannot run because an earlier one failed.
skip() {
    printf 'SKIP  %s\n' "$1"
}

finish() {
    echo
    if [ "$FAILED" -eq 0 ]; then
        printf 'Smoke test passed: %s checks.\n' "$PASSED"
        exit 0
    fi
    printf 'Smoke test FAILED: %s of %s checks failed.\n' "$FAILED" "$((PASSED + FAILED))"
    exit 1
}

# call METHOD PATH [more curl options]
# Sends one request. Leaves the HTTP status in STATUS ("000" when there was
# no answer) and the body of the answer in the file $BODY.
# --insecure: the helper's certificate is self-signed.
# --noproxy:  the helper is on the local network, never behind a web proxy.
call() {
    call_method=$1
    call_path=$2
    shift 2
    : >"$BODY"
    STATUS=$(curl --silent --show-error --insecure --noproxy '*' \
        --connect-timeout 10 --max-time 120 \
        --output "$BODY" --write-out '%{http_code}' \
        --request "$call_method" "$@" "$BASE$call_path" 2>"$WORK/curl-error") || STATUS=000
}

# field FILE NAME.NAME...
# Prints one value from a JSON file, or nothing when it is not there.
field() {
    python3 -c '
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        value = json.load(handle)
    for part in sys.argv[2].split("."):
        value = value[part]
except Exception:
    sys.exit(0)
if isinstance(value, bool):
    print("true" if value else "false")
elif value is None:
    print("null")
elif isinstance(value, (dict, list)):
    print(json.dumps(value, separators=(",", ":")))
else:
    print(value)
' "$1" "$2"
}

# is_empty_text FILE NAME: true when the JSON value is there and is "".
is_empty_text() {
    python3 -c '
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    sys.exit(0 if json.load(handle).get(sys.argv[2]) == "" else 1)
' "$1" "$2" 2>/dev/null
}

# pair_as DEVICE_ID NAME: pairs with the pairing code. The answer is in $BODY.
pair_as() {
    python3 -c '
import json
import sys

print(json.dumps({"method": "code", "code": sys.argv[1], "deviceId": sys.argv[2],
                  "deviceName": sys.argv[3], "folderName": sys.argv[3]}))
' "$CODE" "$1" "$2" >"$WORK/pair.json"
    call POST /api/v1/pair --header 'Content-Type: application/json' --data-binary "@$WORK/pair.json"
}

# The reason a check failed: the status, then the helper's own error message,
# or curl's, or else the start of the answer. An answer that holds a device
# token is never shown.
why() {
    why_text=$(field "$BODY" error.message)
    if [ -z "$why_text" ] && [ -s "$WORK/curl-error" ]; then
        why_text=$(head -n 1 "$WORK/curl-error")
    fi
    if [ -z "$why_text" ] && ! grep -q deviceToken "$BODY"; then
        why_text="The answer was: $(cut -c 1-300 "$BODY" | head -n 1)"
    fi
    printf 'HTTP %s. %s' "$STATUS" "$why_text"
}

# upload KEY TOKEN
upload() {
    call PUT "/api/v1/assets/$1" \
        --header "Authorization: Bearer $2" \
        --header 'Content-Type: application/octet-stream' \
        --header "X-Phlix-Filename: $NAME" \
        --header "X-Phlix-SHA256: $SHA256" \
        --header "X-Phlix-Created: $CREATED" \
        --header 'X-Phlix-Kind: photo' \
        --upload-file "$WORK/picture.jpg"
}

printf 'Phlix Camera Upload smoke test: %s\n' "$BASE"

# -- 1. Is anything there ---------------------------------------------------

call GET /healthz
if [ "$STATUS" = 200 ] && [ "$(cat "$BODY")" = ok ]; then
    pass "healthz answers ok"
else
    fail "healthz answers ok" "$(why)"
    if [ "$STATUS" = 000 ]; then
        echo "      Nothing answered at $BASE. Check the address, and use https:// unless the helper runs with TLS=off."
        finish
    fi
fi

call GET /api/v1/hello
SERVICE=$(field "$BODY" service)
API_VERSION=$(field "$BODY" apiVersion)
if [ "$STATUS" = 200 ] && [ "$SERVICE" = phlix-camera-upload ] && [ "$API_VERSION" = 1 ]; then
    pass "hello: $SERVICE $(field "$BODY" version), API version $API_VERSION"
else
    fail "hello names the helper and API version 1" "$(why)"
    finish
fi
CODE_PAIRING=$(field "$BODY" pairing.code)

call GET /api/v1/health
if [ "$STATUS" = 200 ] && [ "$(field "$BODY" ok)" = true ]; then
    pass "health: the helper says it can do its job"
else
    fail "health: the helper says it can do its job" "$(why)"
fi

if [ "$CODE_PAIRING" != true ]; then
    fail "the helper pairs with a code" "This helper runs with PAIRING=plex, so the test cannot pair."
    finish
fi

# -- 2. Pair ----------------------------------------------------------------

pair_as phlix-smoke-test "Smoke Test"
TOKEN=$(field "$BODY" deviceToken)
FOLDER=$(field "$BODY" folder)
if [ "$STATUS" = 200 ] && [ -n "$TOKEN" ] && [ -n "$FOLDER" ]; then
    pass "pair with the pairing code (this device's folder is \"$FOLDER\")"
else
    fail "pair with the pairing code" "$(why)"
    finish
fi

# -- 3. Upload --------------------------------------------------------------

# Writes the picture and prints its file name, asset key, SHA-256, size,
# date, and a second asset key for the second device, one per line.
python3 -c '
import base64
import datetime
import hashlib
import os
import sys

jpeg = base64.b64decode(sys.argv[2])
now = datetime.datetime.now().astimezone().replace(microsecond=0)
run = now.strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(3).hex()
note = ("Phlix Camera Upload smoke test " + run).encode("ascii")
comment = b"\xff\xfe" + (len(note) + 2).to_bytes(2, "big") + note
cut = 4 + int.from_bytes(jpeg[4:6], "big")  # just after the JFIF header
data = jpeg[:cut] + comment + jpeg[cut:]
with open(sys.argv[1], "wb") as handle:
    handle.write(data)
digest = hashlib.sha256(data).hexdigest()
print("phlix-smoke-test-" + run + ".jpg")
print("smoke-test-" + digest[:32])
print(digest)
print(len(data))
print(now.isoformat())
print("smoke-test-two-" + digest[32:])
' "$WORK/picture.jpg" "$PICTURE" >"$WORK/picture.txt"

{
    read -r NAME
    read -r KEY
    read -r SHA256
    read -r SIZE
    read -r CREATED
    read -r SECOND_KEY
} <"$WORK/picture.txt"

upload "$KEY" "$TOKEN"
STORED_PATH=$(field "$BODY" path)
case $STORED_PATH in
    "$NAME" | */"$NAME") NAME_KEPT=yes ;;
    *) NAME_KEPT=no ;;
esac
if [ "$STATUS" = 201 ] && [ "$(field "$BODY" status)" = stored ] &&
    [ "$(field "$BODY" bytes)" = "$SIZE" ] && [ "$NAME_KEPT" = yes ]; then
    pass "upload a picture: stored as $STORED_PATH"
    UPLOADED=yes
else
    fail "upload a picture: stored, $SIZE bytes, named $NAME" "$(why)"
    UPLOADED=no
fi

if [ "$UPLOADED" = yes ]; then
    upload "$KEY" "$TOKEN"
    if [ "$STATUS" = 200 ] && [ "$(field "$BODY" status)" = duplicate ] &&
        [ "$(field "$BODY" path)" = "$STORED_PATH" ]; then
        pass "upload the same picture again: duplicate, nothing stored twice"
    else
        fail "upload the same picture again: duplicate, same path" "$(why)"
    fi
else
    skip "upload the same picture again: the first upload failed"
fi

# -- 4. The same picture from a second device -------------------------------

# Two phones that hold the same photo: it is stored once. The second phone
# is told that the helper has it, and is not told where the first one's is.
if [ "$UPLOADED" = yes ]; then
    pair_as phlix-smoke-test-2 "Smoke Test 2"
    SECOND_TOKEN=$(field "$BODY" deviceToken)
    if [ "$STATUS" = 200 ] && [ -n "$SECOND_TOKEN" ]; then
        upload "$SECOND_KEY" "$SECOND_TOKEN"
        if [ "$STATUS" = 200 ] && [ "$(field "$BODY" status)" = duplicate ] && is_empty_text "$BODY" path; then
            pass "the same picture from a second device: duplicate, and its path is not given away"
        else
            fail "the same picture from a second device: duplicate, with an empty path" "$(why)"
        fi
        # An answer can be lost on the way, and the phone then sends the
        # picture again under the same key. That answer must not say where
        # the first device's file is either.
        upload "$SECOND_KEY" "$SECOND_TOKEN"
        if [ "$STATUS" = 200 ] && [ "$(field "$BODY" status)" = duplicate ] && is_empty_text "$BODY" path; then
            pass "the second device sends it again: duplicate, and still no path"
        else
            fail "the second device sends it again: duplicate, with an empty path" "$(why)"
        fi
        call POST /api/v1/unpair --header "Authorization: Bearer $SECOND_TOKEN" --data-binary ''
        if [ "$STATUS" = 200 ]; then
            pass "unpair the second device"
        else
            fail "unpair the second device" "$(why)"
        fi
    else
        fail "pair a second device with the pairing code" "$(why)"
    fi
else
    skip "the same picture from a second device: the first upload failed"
fi

# -- 5. Check and status ----------------------------------------------------

if [ "$UPLOADED" = yes ]; then
    printf '{"items":["%s","smoke-test-key-never-uploaded"]}' "$KEY" >"$WORK/check.json"
    call POST /api/v1/assets/check --header "Authorization: Bearer $TOKEN" \
        --header 'Content-Type: application/json' --data-binary "@$WORK/check.json"
    if [ "$STATUS" = 200 ] && [ "$(field "$BODY" known)" = "[\"$KEY\"]" ]; then
        pass "check: the helper knows the uploaded picture and no other"
    else
        fail "check: the helper knows the uploaded picture and no other" "$(why)"
    fi
else
    skip "check: the first upload failed"
fi

call GET /api/v1/status --header "Authorization: Bearer $TOKEN"
COUNT=$(field "$BODY" device.assetCount)
case $COUNT in
    '' | *[!0-9]*) COUNT=0 ;;
esac
if [ "$STATUS" != 200 ] || [ "$(field "$BODY" device.folder)" != "$FOLDER" ]; then
    fail "status: this device and its folder" "$(why)"
elif [ "$(field "$BODY" storage.writable)" != true ]; then
    fail "status: the upload folder is writable" "The helper says it cannot write to its upload folder."
elif [ "$UPLOADED" = yes ] && [ "$COUNT" -lt 1 ]; then
    fail "status: at least 1 file from this device" "The helper counts $COUNT."
else
    pass "status: $COUNT file(s) from this device, the upload folder is writable"
fi

# -- 6. A wrong token gets nowhere ------------------------------------------

WRONG_TOKEN=smoke-test-wrong-token-0000000000000000000

call GET /api/v1/status --header "Authorization: Bearer $WRONG_TOKEN"
if [ "$STATUS" = 401 ] && [ "$(field "$BODY" error.code)" = unauthorized ]; then
    pass "status with a wrong token is refused (401)"
else
    fail "status with a wrong token is refused (401)" "$(why)"
fi

call GET /api/v1/status
if [ "$STATUS" = 401 ]; then
    pass "status without a token is refused (401)"
else
    fail "status without a token is refused (401)" "$(why)"
fi

upload smoke-test-key-wrong-token "$WRONG_TOKEN"
if [ "$STATUS" = 401 ] && [ "$(field "$BODY" error.code)" = unauthorized ]; then
    pass "an upload with a wrong token is refused (401)"
else
    fail "an upload with a wrong token is refused (401)" "$(why)"
fi

# -- 7. The file on disk ----------------------------------------------------

if [ -z "$PHOTOS_DIR" ]; then
    :
elif [ "$UPLOADED" != yes ]; then
    skip "the picture is on disk: the first upload failed"
else
    STORED_FILE=${PHOTOS_DIR%/}/$STORED_PATH
    if [ ! -f "$STORED_FILE" ]; then
        fail "the picture is on disk at $STORED_FILE" "There is no such file. Is $PHOTOS_DIR the helper's upload folder?"
    elif cmp -s "$WORK/picture.jpg" "$STORED_FILE"; then
        pass "the picture is on disk with the right bytes: $STORED_FILE"
    else
        fail "the picture is on disk with the right bytes: $STORED_FILE" "The file differs from what was sent."
    fi
fi

# -- 8. Unpair --------------------------------------------------------------

call POST /api/v1/unpair --header "Authorization: Bearer $TOKEN" --data-binary ''
if [ "$STATUS" = 200 ] && [ "$(field "$BODY" unpaired)" = true ]; then
    pass "unpair"
else
    fail "unpair" "$(why)"
fi

call GET /api/v1/status --header "Authorization: Bearer $TOKEN"
if [ "$STATUS" = 401 ]; then
    pass "the token is refused after unpairing (401)"
else
    fail "the token is refused after unpairing (401)" "$(why)"
fi

if [ "$UPLOADED" = yes ]; then
    echo
    echo "Left in the upload folder: $STORED_PATH"
fi
finish
