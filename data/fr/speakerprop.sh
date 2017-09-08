#!/bin/bash


export SPEAKER="$1";
export DATASET="siwis_fr";
export VER=1;
export QNAME="fr.talk";
export IDIOMA="fr";
export SAMPFREQ=44100;
export FRAMESHIFT=220;
export FRAMELEN=1100;
export FREQWARP=0.53;
export NORMALIZE=1;
export FFTLEN=2048;

if test "$1" = "zoe"; then
   export GENDER="female";
   export LOWERF0="80";
   export UPPERF0="350";
   export DIALECT="france";
fi

