#!/bin/bash


export SPEAKER="$1";
export DATASET="cmu_us";
export VER=1;
export QNUM=001;
export IDIOMA="en";
export SAMPFREQ=16000;
export FRAMESHIFT=80;
export FRAMELEN=400;
export FREQWARP=0.42;
export NORMALIZE=1; # with 0 I get out of range errors
export FFTLEN=512;

if test "$1" = "slt" -o \
        "$1" = "clb"; then
   export GENDER="female";
   export LOWERF0="80";
   export UPPERF0="350";
elif test "$1" = "bdl" -o \
        "$1" = "jmk" -o \
        "$1" = "awb" -o \
        "$1" = "rms" -o \
        "$1" = "ksp"; then
   export GENDER="male";
   export LOWERF0="40";
   export UPPERF0="280";
fi
