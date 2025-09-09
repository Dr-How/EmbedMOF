#!/bin/sh
while read -r sym; do
    case "$sym" in
        \!*) continue ;;
    esac
    python3 Halfedges.py "$sym" >/dev/null 2>&1
    result=$(python3 Coplanar.py 2>/dev/null)
    if [ "$result" = "true" ]; then
        echo "$sym"
    fi
    rm -f network_data.json
done < symbols.dat > coplanar.dat