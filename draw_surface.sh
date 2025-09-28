#!/bin/sh
sym="$1"
python3 Halfedges.py "$sym" >/dev/null 2>&1
python3 DFSNormal.py >/dev/null 2>&1
python3 MakeFaces.py >/dev/null 2>&1
python3 DrawSurface.py o/dev/null 2>&1
rm -f *.json