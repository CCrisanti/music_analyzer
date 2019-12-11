#!/bin/bash
cd ..
for f in $1/*/*.mscx; do
    ./music_analyzer -f $f
    echo " "
done

mv outFile.txt study