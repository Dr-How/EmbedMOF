#!/bin/sh
grep -i '^ *NAME ' rcsr3d.cgd | awk '{print $2}' | tee symbols.dat