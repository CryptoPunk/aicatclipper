#!/bin/bash

set -x

usage() { echo "Usage: $0 INPUT_VIDEO" 1>&2; exit 1; }

INPUT_VIDEO=$1

shift

if [ "$#" -gt 0 ]; then
    usage
fi

TMPDIR=$(mktemp -d)

VID_REPACK="${TMPDIR}/full.mp4"

ffmpeg -y -i "$INPUT_VIDEO" -c:v copy -an -sn "$VID_REPACK"

python3 detect_scenes.py "$VID_REPACK"
python3 vlmtag.py "$VID_REPACK"
python3 clip_video.py "$VID_REPACK"