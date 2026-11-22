#!/bin/sh
# Copies the files that https://phlixapp.com/camera-upload/ offers for
# download into a checkout of the website, so that the website never serves
# an older copy than this repository.
#
#   sh scripts/copy-to-site.sh /path/to/website/camera-upload
#
# Run it after any change to one of the three files, then publish the
# website. It copies and does nothing else.

set -eu

if [ "$#" -ne 1 ] || [ ! -d "$1" ]; then
    echo "usage: sh scripts/copy-to-site.sh /path/to/website/camera-upload" >&2
    exit 2
fi

here=$(cd "$(dirname "$0")/.." && pwd)
for name in docker-compose.yml SETUP-WITH-AI.md install.sh; do
    if cmp -s "$here/$name" "$1/$name"; then
        echo "same     $name"
    else
        cp "$here/$name" "$1/$name"
        echo "copied   $name"
    fi
done
