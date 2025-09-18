#!/bin/bash
# Run CheckEmbed.py for all .stl files in the models directory

for file in models/*.stl; do
    result=$(python3 CheckEmbed.py "$file" | head -n 1)
    echo "$file: $result"
done
