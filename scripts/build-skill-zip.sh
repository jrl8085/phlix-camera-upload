#!/bin/sh
# Packs the skill for the Claude apps (claude.ai and Claude Desktop).
#
#   sh scripts/build-skill-zip.sh
#
# It writes dist/phlix-camera-upload-setup.zip. The ZIP holds one folder,
# phlix-camera-upload-setup, with the file SKILL.md in it. That is the form
# the Claude apps ask for under Customize > Skills > Upload a skill.
#
# Attach the ZIP to each GitHub release under the same name. The README
# links to the newest one:
#   https://github.com/jrl8085/phlix-camera-upload/releases/latest/download/phlix-camera-upload-setup.zip
#
# Needs zip, or python3 when there is no zip.

set -eu

NAME=phlix-camera-upload-setup
ROOT=$(cd "$(dirname "$0")/.." && pwd)
SKILL=$ROOT/skills/$NAME/SKILL.md
OUT=$ROOT/dist/$NAME.zip

if [ ! -f "$SKILL" ]; then
    echo "build-skill-zip: $SKILL is missing" >&2
    exit 1
fi

WORK=$(mktemp -d "${TMPDIR:-/tmp}/phlix-skill-zip.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/$NAME" "$ROOT/dist"
cp "$SKILL" "$WORK/$NAME/SKILL.md"
rm -f "$OUT"

if command -v zip >/dev/null 2>&1; then
    (cd "$WORK" && zip -q -r -X "$OUT" "$NAME")
elif command -v python3 >/dev/null 2>&1; then
    (cd "$WORK" && python3 -m zipfile -c "$OUT" "$NAME")
else
    echo "build-skill-zip: zip or python3 is needed" >&2
    exit 1
fi

echo "Wrote dist/$NAME.zip"
