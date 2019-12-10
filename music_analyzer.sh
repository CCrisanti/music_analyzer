#!/bin/bash

FILENAME=""
VERBOSE=0
while getopts "vf:" OPTION
do
	case $OPTION in
		v)
			VERBOSE=1
			;;
		f)
			FILENAME=$OPTARG
			;;
		h|\?)
			echo "CS6501 Software Artifacts Music Analyzer"
            echo " "
            echo "music_analyzer [options] -f [file]"
            echo " "
            echo "Options"
            echo "========================================================"
            echo " "
            echo "-v, --verbose    Prints all information about violations"
            echo " "
            echo "========================================================"
            break 
			;;
	esac
done

if [ "$FILENAME" == "" ]; then
    echo "Please Input .mscx file after the flag -f"
    echo " "
    echo "CS6501 Software Artifacts Music Analyzer"
    echo " "
    echo "music_analyzer [options] -f [file]"
    echo " "
    echo "Options"
    echo "========================================================"
    echo " "
    echo "-h, --help       Prints this information"
    echo "-v, --verbose    Prints all information about violations"
    echo " "
    echo "========================================================"
else
    python3 music\ parser $FILENAME $VERBOSE
fi