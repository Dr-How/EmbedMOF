#!/bin/sh
while read -r sym; do
    python3 Halfedges.py "$sym" >/dev/null 2>&1
    python3 DFSNormal.py >/dev/null 2>&1
    result=$(python3 MakeFaces.py 2>/dev/null)
    if [ "$result" = "true" ]; then
        echo "$sym"
    fi
    rm -f network_data.json
done < orthogonal-barycentric.dat > trivial-faces.dat