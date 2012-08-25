# FestCat Voice Builder

This set of Makefiles and templates have been written to ease the building 
of [HTS](http://hts.sp.nitech.ac.jp/) voices in Catalan for the [FestCat](http://www.talp.cat/festcat) project.

This Makefiles and templates can be extended to support building of HTS voices 
in other languages.

# Dependencies


## Dependencies which you need to install

Some dependencies are not installed automatically:

1. General utilities such as:
   - C, C++ compilers
   - make
   - grep, awk, sed
   - sox
   - perl

2. Tcl/Tk with [Snack](http://www.speech.kth.se/snack/): 
   - If you are under Debian, you will need `libsnack2-dev`.
   - If it is not available in your package manager, download and install [ActiveTcl-8.4](http://www.activestate.com/activetcl/downloads).

3. I also needed the Debian package `libx11-dev` to build HTS. Sorry for not providing more details.

## Language independent tools automatically downloaded, built and run

The following software is not language specific and is downloaded to the `deps` directory, 
compiled and installed automatically to the `tools` directory.

1. [Speech Tools 2.1-release](http://www.cstr.ed.ac.uk/projects/festival/download.html)
2. [Festival 2.1-release](http://www.cstr.ed.ac.uk/projects/festival/download.html)
3. [SPTK 3.4.1](http://sourceforge.net/projects/sp-tk)
4. [HTS-2.2](http://hts.sp.nitech.ac.jp/) for [HTK-3.4.1](http://htk.eng.cam.ac.uk/) (downloading HTK requires a [user and password](http://htk.eng.cam.ac.uk/register.shtml), as well as agreeing to the [non-free license](http://htk.eng.cam.ac.uk/docs/license.shtml))
5. [HDecode 3.4.1](http://htk.eng.cam.ac.uk/) (it has similar restrictions to HTK)
6. [hts_engine 1.0.5](http://sourceforge.net/projects/hts-engine)


## Language specific tools

Any language specific tool should be installed automatically from the Makefile available in
data/$lang.

### Catalan

This is downloaded automatically:

1. upc_ca_base (also known as festival-ca in some distributions)
2. raw recordings and utt files.

### English

Some more testing should be done maybe.

1. HTS-demo

# Usage

Training Catalan voices may take several days, some GB of Hard disk and a lot of RAM,
so bear in mind that "One does not simply... build an HTS voice".

In order to train the Catalan HTS voices, run:
        ./configure htk_user="yourhtkuser" htk_password="yourhtkpassword"
        make ca_ona.spk
        make ca_bet.spk
        make ca_pau.spk


