# FestCat Voice Builder

This set of Makefiles and templates have been written to automate the building of
[HTS](http://hts.sp.nitech.ac.jp/) voices in:

- Catalan for the [FestCat](http://festcat.talp.cat) project
- English, with the [ARCTIC](http://festvox.org/cmu_arctic/) dataset

This Makefiles and templates can be extended to support building of HTS voices 
in other languages.

# Quick Start

1. Install dependencies. You will need some general utilities:

   - C, C++ compilers
   - make
   - autoconf
   - grep, awk, sed
   - sox
   - perl
   - csh
   - I believe I also needed the Debian package `libx11-dev` to build HTS
     and *maybe?* tcl-snack. Sorry for not providing more details.

2. Register and agree to the HTK license at http://htk.eng.cam.ac.uk/ You need
   the HTK user name and password so HTK can be downloaded.

3. Train a voice. The training can take time, GB of disk and a fair amount of RAM.
   For instance, training the ona Catalan voice may take several days, <10 GB of
   hard disk space with peaks of >8??GB of RAM. In order to train HTS voices, run:


        ./configure htk_user="yourhtkuser" htk_password="yourhtkpassword"
        make ca_ona.spk
        make ca_bet.spk
        make ca_pau.spk
        make en_slt.spk
        make en_awb.spk
        make fr_zoe.spk

# Dependencies

## Language independent tools automatically downloaded, built and run

The following software is not language specific and is downloaded to the `deps` directory, 
compiled and installed automatically to the `tools` directory.

1. [Speech Tools 2.4-release](http://festvox.org/packed/festival/)
2. [Festival 2.4-release](http://festvox.org/packed/festival/)
3. [SPTK 3.10](http://sourceforge.net/projects/sp-tk)
4. [HTS-2.3.1](http://hts.sp.nitech.ac.jp/) for [HTK-3.4.1](http://htk.eng.cam.ac.uk/) (downloading HTK requires a [user and password](http://htk.eng.cam.ac.uk/register.shtml), as well as agreeing to the [non-free license](http://htk.eng.cam.ac.uk/docs/license.shtml))
5. [HDecode 3.4.1](http://htk.eng.cam.ac.uk/) (it has similar restrictions to HTK)
6. [hts_engine 1.10](http://sourceforge.net/projects/hts-engine)


## Language specific tools

Any language specific tool should be installed automatically from the Makefile available in
data/$lang.

### Catalan

This is downloaded automatically:

 - upc_ca_base (also known as festival-ca in some GNU/Linux distributions)
 - raw recordings and utt files.

### English

This is downloaded automatically:

 - festlex_CMU and festlex_POSLEX
 - recordings and utt files from ARCTIC dataset.

# Usage

Training Catalan voices may take several days, some GB of Hard disk and a lot of RAM.

In order to train HTS voices, run:

    ./configure htk_user="yourhtkuser" htk_password="yourhtkpassword"
    make ca_ona.spk
    make ca_bet.spk
    make ca_pau.spk
    make en_slt.spk
    make en_awb.spk


