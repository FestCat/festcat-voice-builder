# FestCat: Speech Synthesis in Catalan using Festival

    http://www.talp.cat/festcat
    Antonio Bonafonte
    TALP Research Center
    Barcelona, November 2007


## About the FestCat project
 
"Festival parla català"

The FestCat package consists of a library providing
analysis of Catalan text, and the data to extend 
Festival so that it can speak Catalan.

This project has been originally developed by
the TALP Center, Universitat Politècnica de Catalunya, Barcelona.

http://www.talp.cat/festcat

Basically, there are two components:

1. Linguistic data and code to extend Festival for Catalan.
 Dictionaries, tokenizer, lts rules, POStagger data, etc.

 This includes two folders:
    1. `dicts/upc` (basically dictionaries)
    2. `upc_catalan` (basically code)

2. Voices: speaker dependent data. 
    1. There is one folder for each voice: 
            voices/catalan/upc_ca_'speaker-name'

Several voices have already been developed.
Check the web page to get the latest downloads.

## About the authors

Most of the code and data has been specifically developed for 
[this project](http://www.talp.cat/festcat) by the 
[TALP Research Center](http://www.talp.cat) at [UPC](http://www.upc.edu)

A significant exception are the dictionaries:
The main source for building the dictionaries is the Catalan lexicon
provided by the FreeLing project, also developed by the TALP Research Center
and others: please, visit [FreeLing web site](http://nlp.lsi.upc.edu/freeling/)
for more information:

The lexicon has been enriched in the following way:
 - Phonetic transcriptions have been automatically generated using the
   the TALP phonetic transcription toolkit

 - New word forms have been added using frequent words found in our corpus
   and words found in our 'speech' data to ensure better coverage when
   designing the voices.


## Terms and Conditions
For updated details on the copyright and license terms, please
see the COPYRIGHT and LICENSE-*.txt files.


## Requirements
You need a working Festival system.
Check in your Linux distribution or in the
[Festival home page](http://www.cstr.ed.ac.uk/projects/festival/)

We have been working with version "2.1 November 2010"
(Execute `$ festival --version` )

## Installation

We have developed several catalan voices.
All of them share a common library, which is language
related. Therefore, you need the 'base' package plus
the specific voices you are interested in.

### Common package

   Download the file upc_ca_base.tgz and extract the files: `$ tar -zxf upc_ca_base.tgz`.
   As it takes a while to build the package, it comes already compiled:
    ./configure && sudo make install

### Voice specific packages

   Download the file of each voice (check the web for updates)
   and extract the content. Ex: `$ tar -zxf upc_ca_ona_hts.tgz`
   
   You just need to copy several folder in the datadir of Festival.
   To find this directory, you can execute
   `$ festival -b '(print datadir)'`
   If this directory is not defined, you should use the 'libdir'
   directory: `$ festival -b '(print libdir)'`

   Copy each catalan voice, ex: upc_ca_ona_hts, in the voices
   directory. Example:
      upc_ca_ona_hts => 'datadir'/voices/catalan/upc_ca_ona_hts

## Using FestCat

There are several front-ends to be used with Festival, as 
gnopernicus, or emacs-speak ... Here we only mention the direct use of
Festival.

*Festival expects ISO-8859-15 encoding*. Be sure that you use
this encoding in your terminal or files. If your system uses UTF-8 (as
do many distributions today) you need to convert the file before reading.
Some front-ends, as gnopernicus, do the conversions for you.

You can use the "save as" options in gedit; or use programs to convert the 
format, as iconv:

        $ iconv -f utf8 -t ISO-8859-15//TRANSLIT myfile_utf8.text > myfile_latin1.text


 * A quick test:
        $ echo "Bon dia, Catalunya" | festival --tts --language catalan

 * You can also execute Festival in interactive way:

        $ festival
        (language_catalan)
        (intro-catalan)
        (SayText "Bon dia, Catalunya.")
        (SayText "Bona nit.")
        (quit)

 * If you want to specify the speaker, introduce the command to 
   select the speaker instead of the language selection command; 
   or just use it to change the speaker:

        (voice_upc_ca_ona_hts)
        (SayText "I tu, qui ets?")
        (voice_upc_ca_pau_hts)
        (SayText "Jo sóc, el que tu ets, i si et faig mal, em faig mal a mi mateix.")
        (voice_upc_ca_ona_hts)
        (SayText "Que maco. Això és de l'assemblea dels infants, oi?")
        (quit)

 * Or to read a text file, for instance "bon_dia.txt": 

        $ echo "Bon dia, Catalunya." > bon_dia.txt
        $ festival
        (language_catalan)
        (tts_file "bon_dia.txt")
        (quit)

  * Or use the text2wave script to create a .wav file:
        $ text2wave -o bondia.wav   -eval '(language_catalan)' bon_dia.txt

  * If you want to specify the speaker:
        $ text2wave -o bondia.wav   -eval '(voice_upc_ca_ona_hts)' bon_dia.txt


## Thanks and funding notice
This work has been supported by the  [Catalan Government](http://www.gencat.cat).

The project was promoted by several departments from the Catalan Government
   - Departament d'Educació
   - Secretaria de Telecomunicacions i Societat de la Informació del Departament de Presidència. 

and from the Universitat Politècnica de Catalunya (UPC)
   - TALP Research Center
   - Càtedra d'Accessibilitat
   - Càtedra de Programari Lliure

Read the AUTHORS and THANKS files to see the list of people that have 
contributed to this project.
