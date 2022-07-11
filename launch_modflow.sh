#!/bin/bash

python3.10 /datapassing/main.py "$1" "$2" "$2".nam "$3"
cd /workspace/"$1"/modflow/"$2" || echo "Unrecognized project path" || exit
mf2005 "$2".nam