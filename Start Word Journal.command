#!/bin/zsh
set -eu
cd -- "$(dirname -- "$0")"
printf '\nMolly’s Word Journal\n\nOpen http://127.0.0.1:5182/ in Chrome.\nKeep this window open while practising. Press Control-C to stop.\n\n'
python3 -m http.server 5182 --bind 127.0.0.1
