#!/bin/sh
sym="$1"
if ! grep -qx "$sym" trivial-faces.dat; then
  echo "not suitable!"
  exit 1
fi
python3 Halfedges.py "$sym" >/dev/null 2>&1
python3 DFSNormal.py #>/dev/null 2>&1
python3 MakeFaces.py #>/dev/null 2>&1
python3 DrawSurface.py #>/dev/null 2>&1
rm -f *.json