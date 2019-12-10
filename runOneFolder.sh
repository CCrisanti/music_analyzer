#!/bin/bash

for f in $1/*/*.mscx; do
    echo $f
    ./music_analyzer.sh -f $f
    echo " "
done