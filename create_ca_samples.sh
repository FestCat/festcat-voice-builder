#!/bin/bash
set -ev

BASEDIR="$PWD"
WORKDIR="$BASEDIR/work/create_ca_samples/"

mkdir -p "$WORKDIR"
mkdir -p "$BASEDIR/samples"
cd "$WORKDIR"
wget http://festvox.org/packed/festival/2.4/speech_tools-2.4-release.tar.gz
wget http://festvox.org/packed/festival/2.4/festival-2.4-release.tar.gz
wget http://festcat.talp.cat/download/upc_ca_base-3.0.6.tgz
tar xzf speech_tools-2.4-release.tar.gz
tar xzf festival-2.4-release.tar.gz
mv upc_ca_base-3.0.6.tgz t_upc_ca_base-3.0.6.tgz
tar xzf t_upc_ca_base-3.0.6.tgz
cd speech_tools
./configure
make
cd ..
cd festival
./configure
make
cd ..
cd upc_ca_base-3.0.6
./configure --enable-onlyinstall --enable-festivalpath="$PWD/../festival/bin"
make install
cd ..
cd "$BASEDIR"
cp results/upc_ca*gz "$WORKDIR"
cd "$WORKDIR"
for myfile in $(ls upc_ca*gz); do
    myfilenoext=${myfile%.*}
    tar xzf "$myfile"
    cd "$myfilenoext"
    ./configure --enable-festivalpath="$WORKDIR/festival/bin"
    make
    cd "$WORKDIR"
    festival/bin/text2wave -eval "(voice_$myfilenoext)" -o "$myfilenoext.wav" "$BASEDIR/text_samples_ca.txt"
    mv "$myfilenoext.wav" "$BASEDIR/samples"
done
