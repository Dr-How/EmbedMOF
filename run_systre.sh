#!/bin/sh
name="$1"
tmpfile=$(mktemp ./network_$1.cgd)
awk -v n="$name" '
  BEGIN { IGNORECASE=1 }
  $0 ~ /^CRYSTAL/ {inblock=1; block=""}
  inblock {block = block $0 "\n"}
  $0 ~ "^[[:space:]]*NAME[[:space:]]" n "$" {found=1}
  $0 ~ /^END/ && inblock {
    if (found) { printf "%s", block }
    inblock=0; found=0; block=""
  }
' rcsr3d.cgd > "$tmpfile"
java -cp Systre-19.6.0.jar org.gavrog.apps.systre.SystreCmdline -fullUnitCell -barycentric "$tmpfile"
# java -cp Systre-19.6.0.jar org.gavrog.apps.systre.SystreCmdline -fullUnitCell "$tmpfile"
rm -f "$tmpfile"