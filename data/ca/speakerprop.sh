#!/bin/bash


export SPEAKER="$1";
export DATASET="upc_ca";
export VER=1;
export QNUM=002;
export IDIOMA="ca";


if test "$1" = "bet" -o \
        "$1" = "eli" -o \
        "$1" = "eva" -o \
        "$1" = "mar" -o \
        "$1" = "ona"; then
   export GENDER="female";
   export LOWERF0="110";
   export UPPERF0="350";
elif test "$1" = "jan" -o \
        "$1" = "pau" -o \
        "$1" = "pep" -o \
        "$1" = "pol" -o \
        "$1" = "teo"; then
   export GENDER="male";
   export LOWERF0="60";
   export UPPERF0="200";
elif test  "$1" = "uri" ; then \
   export GENDER="male" #kid
   export LOWERF0="110"
   export UPPERF0="350"
fi
