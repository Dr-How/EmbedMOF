#!/bin/sh
while read -r sym; do
    python3 Halfedges.py "$sym" >/dev/null 2>&1
    result=$(python3 Orthogonal.py 2>/dev/null)
    if [ "$result" = "false" ]; then
        echo "$sym"
    fi
    rm -f network_data.json
done < coplanar-barycentric.dat > orthogonal-barycentric.dat