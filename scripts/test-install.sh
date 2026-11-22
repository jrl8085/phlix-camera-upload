#!/usr/bin/env bash
# Tests for install.sh, without Docker.
#
#   bash scripts/test-install.sh            test with every one of sh, dash and bash that is here
#   bash scripts/test-install.sh dash       test with one shell
#
# A stand-in for the docker command takes the place of Docker. It writes
# down every call it gets and answers the way Docker does: with a version,
# with "Started", with a health state, or with one of Docker's own errors.
# Each test runs the installer in a new, empty home folder and then looks at
# what the installer said, which docker calls it made, and which files it
# wrote. The installer runs without a terminal, as it does in a script.
#
# Needs bash, python3 and ruby. Nothing outside a temporary folder is
# touched, and that folder is removed at the end.

set -u

REPO=$(cd "$(dirname "$0")/.." && pwd)
PYTHON=$(command -v python3) || { echo "test-install: python3 is needed" >&2; exit 2; }
RUBY=$(command -v ruby) || { echo "test-install: ruby is needed" >&2; exit 2; }
WORK=$(mktemp -d "${TMPDIR:-/tmp}/phlix-install-test.XXXXXX") || exit 2
trap 'rm -rf "$WORK"' EXIT

# The installer sees these tools and no others. A real docker on this
# machine is therefore never reached, whatever a test does.
mkdir -p "$WORK/tools"
for tool in sed awk grep cat ls mkdir rm mv cp cmp date head cut tr id hostname ip route ipconfig chown; do
    found=$(command -v "$tool" 2>/dev/null) || continue
    case $found in
        /*) ln -s "$found" "$WORK/tools/$tool" ;;
    esac
done

# -- the stand-ins -----------------------------------------------------------

mkdir -p "$WORK/shim" "$WORK/shim-nodocker" "$WORK/shim-standalone" "$WORK/shim-root"

cat >"$WORK/shim/docker" <<'STAND_IN'
#!/bin/sh
# A stand-in for docker, for testing install.sh without Docker.
# It writes every call to $FAKE_STATE/calls.log and prints plausible output.
# FAKE_MODE chooses what goes wrong: ok, denied, down, nocompose, composev1,
# pullfail, portbusy, nameconflict, loop, exits, slow, doctorproblem.
mode=${FAKE_MODE:-ok}
state=${FAKE_STATE:?FAKE_STATE is not set}
printf '%s\n' "$*" >>"$state/calls.log"

case "$1" in
version)
    case $mode in
    denied) echo "permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get \"http://%2Fvar%2Frun%2Fdocker.sock/v1.47/version\": dial unix /var/run/docker.sock: connect: permission denied" >&2; exit 1 ;;
    down) echo "Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?" >&2; exit 1 ;;
    esac
    echo "${FAKE_DOCKER_VERSION:-27.3.1}"; exit 0 ;;
compose)
    shift
    file=
    if [ "$1" = -f ]; then file=$2; shift 2; fi
    if [ "$1" = --file ]; then file=$2; shift 2; fi
    case "$1" in
    down) rm -f "$state/container"; echo " Container phlix-camera-upload  Removed"; exit 0 ;;
    version)
        case $mode in
        nocompose) echo "docker: 'compose' is not a docker command." >&2; exit 1 ;;
        composev1) echo "docker: 'compose' is not a docker command." >&2; exit 1 ;;
        esac
        echo "${FAKE_COMPOSE_VERSION:-2.29.7}"; exit 0 ;;
    config)
        # Really read the file, as Compose would.
        "${FAKE_RUBY:-ruby}" -ryaml -e 'd = YAML.load_file(ARGV[0]); s = d["services"]["phlix-camera-upload"]; abort("no source") unless s["volumes"][0]["source"].is_a?(String)' "$file" || { echo "validating $file: yaml: invalid" >&2; exit 15; }
        exit 0 ;;
    pull)
        if [ "$mode" = pullfail ]; then echo "Error response from daemon: Head \"https://ghcr.io/v2/jrl8085/phlix-camera-upload/manifests/1\": denied" >&2; exit 1; fi
        echo " phlix-camera-upload Pulling"; echo " phlix-camera-upload Pulled"; exit 0 ;;
    up)
        case $mode in
        portbusy) echo "Error response from daemon: driver failed programming external connectivity on endpoint phlix-camera-upload (0a1b): Bind for 0.0.0.0:7459 failed: port is already allocated" >&2; exit 1 ;;
        nameconflict) echo "Error response from daemon: Conflict. The container name \"/phlix-camera-upload\" is already in use by container \"0a1b2c3d\". You have to remove (or rename) that container to be able to reuse that name." >&2; exit 1 ;;
        esac
        : >"$state/container"; echo 0 >"$state/inspects"
        echo " Network phlix-camera-upload_default  Created"; echo " Container phlix-camera-upload  Started"; exit 0 ;;
    esac ;;
ps)
    if [ -f "$state/container" ] || [ "${FAKE_EXISTING:-0}" = 1 ]; then echo phlix-camera-upload; fi
    exit 0 ;;
image)
    [ "${FAKE_LOCAL_IMAGE:-0}" = 1 ]; exit $? ;;
inspect)
    case "$3" in
    *working_dir*) echo "${FAKE_ORIGIN:-}"; exit 0 ;;
    "{{.State.Health.Status}}") echo healthy; exit 0 ;;
    *State.Status*)
        n=$(cat "$state/inspects" 2>/dev/null || echo 0); n=$((n + 1)); echo "$n" >"$state/inspects"
        case $mode in
        loop) echo "restarting 2 starting" ;;
        exits) echo "exited 0 none" ;;
        slow) echo "running 0 starting" ;;
        *) if [ "$n" -le 2 ]; then echo "running 0 starting"; else echo "running 0 healthy"; fi ;;
        esac
        exit 0 ;;
    esac ;;
logs)
    echo "2026-11-22 09:00:00 INFO    Phlix Camera Upload 1.0.0"
    echo "2026-11-22 09:00:00 INFO    Pairing code: K7QM-3XPD"
    echo "2026-11-22 09:00:00 ERROR   Nothing is mounted at /photos."
    exit 0 ;;
exec)
    if [ "$5 $6" = "phlix_upload doctor" ]; then
        echo "Phlix Camera Upload 1.0.0"
        echo "OK       The helper is running on port 7459"
        if [ "$mode" = doctorproblem ]; then
            echo "PROBLEM  The helper cannot write to the upload folder /photos. It belongs to user 0, group 0."
            echo "         Fix: Set PUID and PGID in the Compose file to the user and group that own your photo folders (the command \`ls -ldn\` on the folder shows them), then run: docker compose up -d"
            echo "1 to fix."; exit 1
        fi
        echo "OK       The upload folder /photos can be written to."
        echo "OK       224.7 GB free on the upload disk."
        echo "OK       Plex Media Server found: its owner can pair from Phlix without a code."
        echo "OK       0 paired, 0 files stored (0 bytes)."
        echo "NOTE     Pairing code: run \`python -m phlix_upload code\` the same way to see it."
        echo "Nothing needs fixing."; exit 0
    fi ;;
esac
echo "fake docker: unexpected call: $*" >&2
echo "UNEXPECTED $*" >>"$state/calls.log"
exit 97
STAND_IN

# The old stand-alone docker-compose.
cat >"$WORK/shim-standalone/docker-compose" <<'STAND_IN'
#!/bin/sh
state=${FAKE_STATE:?}
printf 'docker-compose %s\n' "$*" >>"$state/calls.log"
if [ "$1" = version ]; then echo "${FAKE_STANDALONE_VERSION:-1.29.2}"; exit 0; fi
exec "${0%/*}/docker" compose "$@"
STAND_IN

# An instant sleep, so that waiting costs no time.
printf '#!/bin/sh\nexit 0\n' >"$WORK/shim/sleep"

# For the test that pretends to be root: "id -u" says 0, and the home folder
# of a user comes from FAKE_HOME, so that no real home folder is touched.
printf '#!/bin/sh\nif [ "$1" = -u ]; then echo 0; exit 0; fi\nexec /usr/bin/id "$@"\n' >"$WORK/shim-root/id"
printf '#!/bin/sh\nif [ "$1" = passwd ]; then echo "$2:x:501:20::${FAKE_HOME:?}:/bin/sh"; exit 0; fi\nexit 2\n' >"$WORK/shim-root/getent"

cp "$WORK/shim/sleep" "$WORK/shim-nodocker/sleep"
cp "$WORK/shim/docker" "$WORK/shim/sleep" "$WORK/shim-standalone/"
cp "$WORK/shim/docker" "$WORK/shim/sleep" "$WORK/shim-root/"
chmod +x "$WORK"/shim*/*

# Runs a command in a new session, so that it has no terminal to ask on.
cat >"$WORK/no-terminal.py" <<'LAUNCHER'
import os
import sys

child = os.fork()
if child == 0:
    os.setsid()
    os.execvp(sys.argv[1], sys.argv[1:])
_, status = os.waitpid(child, 0)
sys.exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)
LAUNCHER

# -- the tools of the tests ---------------------------------------------------

pass=0
fail=0
total_pass=0
total_fail=0
NAME=
T=
OUT=
STATUS=0
SHIM=

new_case() {  # new_case NAME: a new home folder, library folder and docker state
    NAME=$1
    T="$WORK/cases/$(printf '%s' "$NAME" | tr -c 'A-Za-z0-9' '-')"
    rm -rf "$T"
    mkdir -p "$T/home" "$T/lib" "$T/state"
    OUT="$T/out.txt"
}

# run [VAR=value ...] -- [installer options]
# Leaves the exit status in STATUS and what the installer said in $OUT.
run() {
    local envs=()
    while [ "$1" != -- ]; do
        envs+=("$1")
        shift
    done
    shift
    env -i HOME="$T/home" FAKE_STATE="$T/state" FAKE_RUBY="$RUBY" PATH="${SHIM:-$WORK/shim}:$WORK/tools" TERM=dumb \
        ${envs[@]+"${envs[@]}"} "$PYTHON" "$WORK/no-terminal.py" "$SH_PATH" "$REPO/install.sh" "$@" >"$OUT" 2>&1 </dev/null
    STATUS=$?
}

check() {  # check WHAT COMMAND...: the command must succeed
    local what=$1
    shift
    if "$@"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL  [$SH] [$NAME] $what"
        tail -n 12 "$OUT" | sed 's/^/        | /'
    fi
}

status_is() { [ "$STATUS" -eq "$1" ]; }
says() { grep -qF -- "$1" "$OUT"; }
says_not() { ! grep -qF -- "$1" "$OUT"; }
called() { grep -qF -- "$1" "$T/state/calls.log" 2>/dev/null; }
not_called() { ! grep -qF -- "$1" "$T/state/calls.log" 2>/dev/null; }
no_unexpected() { ! grep -q UNEXPECTED "$T/state/calls.log" 2>/dev/null; }
COMPOSE() { echo "$T/home/phlix-camera-upload/docker-compose.yml"; }
sum_of() { cksum <"$1"; }
owner_of() { ls -ldn "$1" | awk '{ print $3 ":" $4 }'; }

# yaml FILE EXPRESSION: a value of the service, read with a real YAML reader.
yaml() {
    "$RUBY" -ryaml -rjson -e 's = YAML.load_file(ARGV[0])["services"]["phlix-camera-upload"]; puts((eval ARGV[1]).to_json)' "$1" "$2"
}

# The file the installer wrote is docker-compose.yml with one other line.
only_source_differs() {
    [ "$(diff "$REPO/docker-compose.yml" "$1" | grep -c '^[<>]')" -eq 2 ] &&
        diff "$REPO/docker-compose.yml" "$1" | grep -q '^<         source: /CHANGE/THIS/Photos/Camera Uploads$'
}

# -- the tests ---------------------------------------------------------------

all_tests() {
    # ---------------------------------------------------------------- usage errors
    new_case "help";            run -- --help;                              check "exit 0" status_is 0; check "shows usage" says "Usage:"; check "no docker call" not_called version
    new_case "unknown option";  run -- --frobnicate;                        check "exit 2" status_is 2; check "names it" says "Unknown option: --frobnicate"
    new_case "missing value";   run -- --photos;                            check "exit 2" status_is 2; check "says so" says "--photos needs a value"
    for bad in 0 70000 abc 7459x ""; do
    new_case "bad port $bad";   run -- --port "$bad" --photos "$T/lib";     check "exit 2" status_is 2; check "says so" says "--port must be a number from 1 to 65535"
    done
    for bad in 192.168.1.10:32400 http://192.168.1.10:32400/web "http://a b:32400" 'http://a"b:32400' ftp://x:1 http://; do
    new_case "bad plex url $bad"; run -- --plex-url "$bad" --photos "$T/lib"; check "exit 2" status_is 2; check "says so" says "--plex-url must look like"
    done
    new_case "bad puid";        run -- --puid abc --photos "$T/lib";        check "exit 2" status_is 2
    new_case "bad pgid";        run -- --pgid -5 --photos "$T/lib";         check "exit 2" status_is 2
    new_case "yes without photos"; run -- --yes;                            check "exit 2" status_is 2; check "says so" says "--yes needs --photos"
    new_case "no terminal no photos"; run -- ;                              check "exit 2" status_is 2; check "says so" says "There is no terminal to ask questions on"; check "nothing started" not_called "compose up"
    new_case "photos is root";  run -- --yes --photos /;                    check "exit 2" status_is 2; check "says so" says "cannot be the whole disk"
    new_case "photos relative"; run -- --yes --photos "Pictures/Uploads";   check "exit 2" status_is 2; check "says so" says "full path"
    new_case "photos empty";    run -- --yes --photos "";                   check "exit 2" status_is 2; check "says so" says "cannot be empty"
    new_case "photos is a file"; : >"$T/lib/afile"; run -- --yes --photos "$T/lib/afile"; check "exit 2" status_is 2; check "says so" says "is a file, not a folder"
    new_case "parent missing";  run -- --yes --photos "$T/lib/nope/Camera Uploads"; check "exit 2" status_is 2; check "says so" says "neither does the folder above it"; check "nothing made" test ! -e "$T/lib/nope"
    new_case "photos inside dir"; run -- --yes --photos "$T/home/phlix-camera-upload/photos"; check "exit 2" status_is 2; check "says so" says "cannot be inside the install folder"
    new_case "dir inside photos"; run -- --yes --photos "$T/lib" --dir "$T/lib/install"; check "exit 2" status_is 2; check "says so" says "cannot be inside the upload folder"

    # ---------------------------------------------------------------- Docker not ready
    new_case "docker missing";  SHIM="$WORK/shim-nodocker" run -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "Docker is not installed"; check "nothing written" test ! -e "$T/home/phlix-camera-upload"
    new_case "permission denied"; run FAKE_MODE=denied -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "explains" says "This installer never uses sudo by itself"; check "gives the sudo command" says "| sudo sh"; check "nothing written" test ! -e "$T/home/phlix-camera-upload"; check "did not go on" not_called "compose"
    new_case "daemon down";     run FAKE_MODE=down -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "Docker is installed but not running"
    new_case "no compose";      run FAKE_MODE=nocompose -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "Docker Compose is not installed"
    new_case "compose v1 only"; SHIM="$WORK/shim-standalone" run FAKE_MODE=composev1 -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "too old. The helper needs version 2"
    new_case "standalone compose v2"; SHIM="$WORK/shim-standalone" run FAKE_MODE=composev1 FAKE_STANDALONE_VERSION=v2.24.5 -- --yes --photos "$T/lib"; check "exit 0" status_is 0; check "uses docker-compose" called "docker-compose pull"; check "says which" says "(docker-compose)"; check "clean" no_unexpected
    new_case "old docker";      run FAKE_DOCKER_VERSION=19.03.15 -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "is too old. The helper needs Docker 20.10"
    new_case "docker 20.10 ok"; run FAKE_DOCKER_VERSION=20.10.23 -- --yes --photos "$T/lib"; check "exit 0" status_is 0

    # ---------------------------------------------------------------- a first install, then again
    new_case "fresh install"
    run -- --yes --photos "$T/lib/Camera Uploads"
    check "exit 0" status_is 0
    check "made the folder" test -d "$T/lib/Camera Uploads"
    check "only the source line differs from the repo file" only_source_differs "$(COMPOSE)"
    check "the path in the file is the folder" test "$(yaml "$(COMPOSE)" 's["volumes"][0]["source"]')" = "\"$T/lib/Camera Uploads\""
    check "checked the file with Compose" called "docker-compose.yml.new config --quiet"
    check "pulled" called "compose pull"; check "started" called "compose up -d"; check "ran doctor" called "exec phlix-camera-upload python -m phlix_upload doctor"
    check "prints doctor output" says "Nothing needs fixing."
    check "status page address" says "Status page:     https://"
    check "certificate warning" says "Your browser warns about the certificate. That is expected"
    check "where the code is" says "docker exec phlix-camera-upload python -m phlix_upload code"
    check "three app steps" says "3. Tap Check for the Helper and follow the steps on screen."
    check "plex reminder" says "Scan my library automatically"
    check "never shows a code" says_not "K7QM"
    check "no temp files left" test -z "$(ls -A "$T/home/phlix-camera-upload" | grep -v '^docker-compose.yml$')"
    check "clean" no_unexpected
    sum1=$(sum_of "$(COMPOSE)"); : >"$T/state/calls.log"

    NAME="second run, same options"
    run -- --yes --photos "$T/lib/Camera Uploads"
    check "exit 0" status_is 0; check "kept the file" says "already as asked. Kept it."; check "file unchanged" test "$(sum_of "$(COMPOSE)")" = "$sum1"
    check "no backup made" test -z "$(ls "$T/home/phlix-camera-upload" | grep before)"; check "pulled again" called "compose pull"; check "clean" no_unexpected
    : >"$T/state/calls.log"

    NAME="third run, no options (update)"
    run -- 
    check "exit 0" status_is 0; check "says update" says "This run updates it."; check "file unchanged" test "$(sum_of "$(COMPOSE)")" = "$sum1"
    check "did not rewrite" not_called "config --quiet"; check "pulled" called "compose pull"; check "started" called "compose up -d"; check "clean" no_unexpected
    : >"$T/state/calls.log"

    NAME="change the folder, no terminal, no --yes"
    mkdir "$T/lib/Other"
    run -- --photos "$T/lib/Other"
    check "exit 1" status_is 1; check "says why" says "there is no terminal to ask on"; check "file unchanged" test "$(sum_of "$(COMPOSE)")" = "$sum1"; check "did not start" not_called "compose up"
    check "no stray file" test ! -e "$(COMPOSE).new"
    : >"$T/state/calls.log"

    NAME="change the folder with --yes"
    run -- --yes --photos "$T/lib/Other"
    check "exit 0" status_is 0; check "new folder in file" test "$(yaml "$(COMPOSE)" 's["volumes"][0]["source"]')" = "\"$T/lib/Other\""
    check "old file kept" test -n "$(ls "$T/home/phlix-camera-upload" | grep 'docker-compose.yml.before-')"
    check "old file has the old folder" grep -qF "Camera Uploads'" "$T/home/phlix-camera-upload/"docker-compose.yml.before-*
    check "clean" no_unexpected

    # ---------------------------------------------------------------- options
    new_case "port, plex url, puid, pgid"
    mkdir "$T/lib/Up"
    run -- --yes --photos "$T/lib/Up" --port 8443 --plex-url http://192.168.1.10:32400/ --puid 1000 --pgid=1001
    check "exit 0" status_is 0
    check "port" test "$(yaml "$(COMPOSE)" 's["ports"]')" = '["8443:7459"]'
    check "settings" test "$(yaml "$(COMPOSE)" 's["environment"]')" = '{"PLEX_URL":"http://192.168.1.10:32400","PUID":"1000","PGID":"1001"}'
    check "the helper accepts them" env PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -c "
    import json, subprocess, sys
    sys.path.insert(0, '$REPO')
    from phlix_upload import config
    c = config.load({'PLEX_URL': 'http://192.168.1.10:32400', 'PUID': '1000', 'PGID': '1001'})
    assert (c.puid, c.pgid, c.plex_urls) == (1000, 1001, ('http://192.168.1.10:32400',))"
    check "tells the owner to type the address" says "so type this address into the app:  https://"
    check "with the port" says ":8443"
    check "other lines untouched" test "$(diff "$REPO/docker-compose.yml" "$(COMPOSE)" | grep -c '^>')" -eq 6
    new_case "only puid";       run -- --yes --photos "$T/lib" --puid 568; check "exit 0" status_is 0; check "settings" test "$(yaml "$(COMPOSE)" 's["environment"]')" = '{"PUID":"568"}'
    new_case "image override";  run PHLIX_CAMERA_UPLOAD_IMAGE=phlix-camera-upload:ci FAKE_LOCAL_IMAGE=1 -- --yes --photos "$T/lib"; check "exit 0" status_is 0; check "image" test "$(yaml "$(COMPOSE)" 's["image"]')" = '"phlix-camera-upload:ci"'
    new_case "custom dir";      run -- --yes --photos "$T/lib" --dir "$T/home/somewhere else/helper"; check "exit 0" status_is 0; check "file there" test -f "$T/home/somewhere else/helper/docker-compose.yml"
    new_case "tilde and trailing slash"; mkdir "$T/home/Pictures"; run -- --yes --photos "~/Pictures/Camera Uploads/"; check "exit 0" status_is 0; check "folder made under home" test -d "$T/home/Pictures/Camera Uploads"; check "path in file" test "$(yaml "$(COMPOSE)" 's["volumes"][0]["source"]')" = "\"$T/home/Pictures/Camera Uploads\""
    new_case "awkward path"
    odd="$T/lib/Bob's #1: Photos \$5 & more"
    mkdir "$odd"
    run -- --yes --photos "$odd/Camera Uploads"
    check "exit 0" status_is 0; check "folder made" test -d "$odd/Camera Uploads"
    check "path survives YAML, with the dollar doubled for Compose" test "$(yaml "$(COMPOSE)" 's["volumes"][0]["source"].gsub("$$", "$")')" = "$("$RUBY" -rjson -e 'puts ARGV[0].to_json' "$odd/Camera Uploads")"
    check "dollar is doubled" grep -qF 'Photos $$5' "$(COMPOSE)"

    # ---------------------------------------------------------------- things that go wrong after the checks
    new_case "pull fails, no image here"; run FAKE_MODE=pullfail -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "The image could not be downloaded"; check "did not start" not_called "compose up"
    new_case "pull fails, image here";    run FAKE_MODE=pullfail FAKE_LOCAL_IMAGE=1 -- --yes --photos "$T/lib"; check "exit 0" status_is 0; check "says so" says "Using the image that is already here"; check "started" called "compose up -d"
    new_case "port busy";       run FAKE_MODE=portbusy -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "advice" says "Run the installer again with another port"; check "shows docker's message" says "port is already allocated"; check "no temp file" test ! -e "$T/home/phlix-camera-upload/.install-output"
    new_case "name conflict";   run FAKE_MODE=nameconflict -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "advice" says "docker rm -f phlix-camera-upload"
    new_case "restart loop";    run FAKE_MODE=loop -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "The helper started and stopped again"; check "shows the log" says "Nothing is mounted at /photos."; check "hides the code" says_not "K7QM"; check "no doctor" not_called "doctor"
    new_case "exits";           run FAKE_MODE=exits -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "The helper started and stopped again"
    new_case "never healthy";   run FAKE_MODE=slow -- --yes --photos "$T/lib"; check "exit 0" status_is 0; check "notes it" says "has not reported the helper healthy after 60 seconds"; check "asked 30 times" test "$(grep -c 'State.Status' "$T/state/calls.log")" -eq 30; check "ran doctor" called "doctor"
    new_case "doctor finds a problem"; run FAKE_MODE=doctorproblem -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "shows it" says "PROBLEM  The helper cannot write"; check "says so" says "its own check found something to fix"; check "still shows the address" says "Status page:"
    new_case "foreign container"; run FAKE_EXISTING=1 -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "This installer did not make it"; check "nothing written" test ! -e "$T/home/phlix-camera-upload"; check "did not start" not_called "compose up"
    new_case "installed elsewhere"; run FAKE_EXISTING=1 FAKE_ORIGIN=/srv/phlix -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says where" says 'already installed, from the folder /srv/phlix'
    new_case "someone else's compose file"; mkdir -p "$T/home/phlix-camera-upload"; printf 'services:\n  web:\n    image: nginx\n' >"$T/home/phlix-camera-upload/docker-compose.yml"; run -- --yes --photos "$T/lib"; check "exit 1" status_is 1; check "says so" says "belongs to something else"; check "left alone" grep -q nginx "$T/home/phlix-camera-upload/docker-compose.yml"; check "did not start" not_called "compose up"

    # ---------------------------------------------------------------- an option changes an install that exists
    new_case "port busy, then only --port"
    odd="$T/lib/Bob's #1: Photos \$5"; mkdir "$odd"
    run FAKE_MODE=portbusy -- --yes --photos "$odd"
    check "first run stops" status_is 1
    : >"$T/state/calls.log"
    run -- --yes --port 7460
    check "exit 0" status_is 0
    check "new port" test "$(yaml "$(COMPOSE)" 's["ports"]')" = '["7460:7459"]'
    check "same folder, read back from the file" test "$(yaml "$(COMPOSE)" 's["volumes"][0]["source"].gsub("$$", "$")')" = "$("$RUBY" -rjson -e 'puts ARGV[0].to_json' "$odd")"
    check "tells the owner the address" says ":7460"
    check "clean" no_unexpected
    new_case "hand-made file with the placeholder"; mkdir -p "$T/home/phlix-camera-upload"; cp "$REPO/docker-compose.yml" "$T/home/phlix-camera-upload/"; run -- --yes --port 7460; check "exit 2" status_is 2; check "says why" says "neither does the folder above it"

    new_case "options add up over runs"
    run -- --yes --photos "$T/lib" --port 8443 --plex-url https://plex.lan:32400 --puid 1000
    check "first run" status_is 0
    run -- --yes --pgid 1001
    check "exit 0" status_is 0
    check "port kept" test "$(yaml "$(COMPOSE)" 's["ports"]')" = '["8443:7459"]'
    check "settings kept and added" test "$(yaml "$(COMPOSE)" 's["environment"]')" = '{"PLEX_URL":"https://plex.lan:32400","PUID":"1000","PGID":"1001"}'
    check "folder kept" test "$(yaml "$(COMPOSE)" 's["volumes"][0]["source"]')" = "\"$T/lib\""
    run -- --yes --port 07459
    check "leading zero accepted" status_is 0; check "port written without it" test "$(yaml "$(COMPOSE)" 's["ports"]')" = '["7459:7459"]'
    check "settings still there" test "$(yaml "$(COMPOSE)" 's["environment"]')" = '{"PLEX_URL":"https://plex.lan:32400","PUID":"1000","PGID":"1001"}'
    check "explains what is carried over" says "Other changes that you made by hand are not carried over."

    # ---------------------------------------------------------------- dry run with Docker present
    new_case "dry run"
    run -- --dry-run --photos "$T/lib/Camera Uploads" --port 7460
    check "exit 0" status_is 0; check "says nothing changed" says "Nothing was changed."; check "plan" says "Write $T/home/phlix-camera-upload/docker-compose.yml"
    check "made nothing" test -z "$(find "$T/home" "$T/lib" -mindepth 1)"
    check "only looked" test "$(grep -c -v -e '^version' -e '^compose version' -e '^ps ' "$T/state/calls.log")" -eq 0
    new_case "dry run of an update"; mkdir -p "$T/home/phlix-camera-upload"; cp "$REPO/docker-compose.yml" "$T/home/phlix-camera-upload/"; before=$(sum_of "$T/home/phlix-camera-upload/docker-compose.yml"); run -- --dry-run; check "exit 0" status_is 0; check "plan keeps the file" says "Keep $T/home/phlix-camera-upload/docker-compose.yml as it is."; check "file untouched" test "$(sum_of "$T/home/phlix-camera-upload/docker-compose.yml")" = "$before"
    new_case "dry run bad folder"; run -- --dry-run --photos /; check "exit 2" status_is 2

    # ---------------------------------------------------------------- started with sudo (root is simulated)
    new_case "as root through sudo"
    mkdir -p "$T/userhome"
    SHIM="$WORK/shim-root" run SUDO_USER="$(/usr/bin/id -un)" SUDO_UID="$(/usr/bin/id -u)" SUDO_GID="$(/usr/bin/id -g)" HOME="$T/roothome" FAKE_HOME="$T/userhome" -- --yes --photos "$T/lib/Camera Uploads"
    check "exit 0" status_is 0
    check "uses the person's home, not root's" says "Install folder:  $T/userhome/phlix-camera-upload"
    check "file is there" test -f "$T/userhome/phlix-camera-upload/docker-compose.yml"
    check "root's home untouched" test ! -e "$T/roothome"
    check "commands shown with sudo" says "sudo docker exec phlix-camera-upload python -m phlix_upload code"
    check "upload folder made" test -d "$T/lib/Camera Uploads"
    check "upload folder has the owner of the folder above it" test "$(owner_of "$T/lib/Camera Uploads")" = "$(owner_of "$T/lib")"
}

if [ "$#" -gt 0 ]; then
    shells=$*
else
    shells=
    for candidate in sh dash bash; do
        if command -v "$candidate" >/dev/null 2>&1; then
            shells="$shells $candidate"
        fi
    done
fi

for SH in $shells; do
    SH_PATH=$(command -v "$SH") || { echo "test-install: there is no shell named $SH" >&2; exit 2; }
    pass=0
    fail=0
    all_tests
    echo "install.sh under $SH: $pass checks passed, $fail failed"
    total_pass=$((total_pass + pass))
    total_fail=$((total_fail + fail))
done

if [ "$total_fail" -gt 0 ]; then
    echo "FAILED: $total_fail of $((total_pass + total_fail)) checks"
    exit 1
fi
echo "All $total_pass checks passed."
