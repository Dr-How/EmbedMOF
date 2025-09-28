#!/bin/sh
while read -r sym; do
    if grep -qx "$sym" dfs-fail.dat || grep -qx "$sym" trivial-faces.dat; then
        continue
    fi
    echo "$sym"
done < orthogonal-barycentric.dat > band-faces.dat