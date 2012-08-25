# FestCat: Síntesi de la parla en català fent servir Festival

    http://www.talp.cat/festcat
    Antonio Bonafonte
    Centre de recerca TALP, UPC
    Barcelona, Novembre 2007


## Quant al projecte FestCat
 
"Festival parla català"

El paquet FestCat consisteix en una llibreria que permet l'anàlisi de text
en català  i dades per estendre Festival per tal que parli català. 

El projecte s'ha desenvolupat al centre TALP, a la Universitat
Politècnica de Catalunya, Barcelona.

http://www.talp.cat/festcat

Està format per dos components principals:

1. Dades lingüístiques i codi per estendre Festival pel català.
   Diccionaris, transcripció fonètica, etiquetador morfo-sintàctic, etc.

  Inclou dues carpetes:
   -  `dicts/upc` (bàsicament diccionaris)
   - `upc_catalan` (bàsicament codi)

2. Veus: dades dependents del locutor 
  Hi ha una carpeta per cada veu
   - `voices/catalan/upc_ca_'nom-locutor'`

Actualment hi ha diverses veus disponibles.
Visiteu la pàgina web per obtenir últimes versions. 

## Quant als autors

Aquest projecte ha estat desenvolupat inicialment pel [Centre TALP](http://www.talp.cat),
de la [Universitat Politècnica de Catalunya](http://www.upc.edu), a Barcelona.
La major part del codi i de les dades ha estat desenvolupat 
específicament per [aquest projecte](http://www.talp.cat/festcat).

Una excepció important són els diccionaris.

La font més important per construir els diccionaris és el lèxic català
proporcionat pel projecte FreeLing, també desenvolupat, entre altres,
pel Centre de Recerca TALP. Per més informació, visiteu la [pàgina web
de FreeLing](http://nlp.lsi.upc.edu/freeling/):

El lèxic ha estat enriquit de la forma següent:
 - Les transcripcions fonètiques s'han generat automàticament utilitzant
   les eines de transcripció fonètica del TALP

 - S'ha afegit noves paraules utilitzant per assegurar millor cobertura en 
   el disseny de les veus.


## Condicions d'ús
La informació actualitzada de copyright i llicència es troba als fitxers
COPYRIGHT i LICENSE-*.txt.

## Requisits
És necessari un sistema 'Festival' en funcionament.
Comproveu la vostra distribució Linux o la pàgina web de 
[Festival](http://www.cstr.ed.ac.uk/projects/festival/)

Aquest paquet s'ha desenvolupat i provat amb la versió 2.1 
de Novembre 2010
(Executeu $ festival --version )

## Instal·lació
Hem desenvolupat diverses veus en català.
Totes comparteixen una llibreria, relacionada amb el processat del llenguatge.
Per tant, necessiteu el paquet bàsic més les veus específiques
que us interessin.

### Instal·lació del paquet bàse: `upc_ca_base`

1. Descarregueu `upc_ca_base` i descomprimiu-lo.
2. `./configure`
3. `make`
4. `make install`

Si ./configure no trobés festival o speech-tools, haureu d'especificar-ne la ruta
manualment. Feu ./configure --help per més detalls.

### Instal·lació de paquets de veu específics
1. Descarregueu el fitxer de cada veu i descomprimiu-lo
2. Copieu el directori que trobeu, p.ex: `upc_ca_ona_hts`, al directori de 
   veus. Per Exemple:
           `upc_ca_ona_hts -> 'datadir'/voices/catalan/upc_ca_ona_hts`
   
El directori 'datadir' es pot determinar amb:
    `$ festival -b '(print datadir)'`
I si festival retornés un error dient que datadir no es troba
definit, caldrà utilitzar:
    `$ festival -b '(print libdir)'`

## Ús de FestCat

Hi ha diversos programes que poden utilitzar 'Festival', com 
gnopernicus, o emacs-speak ... Aquí farem referència només a la 
utilització directa de 'Festival'. 

El *'Festival' espera  codificació ISO-8859-15*. Assegureu-vos que utilitzeu
aquesta codificació en el vostre terminal o fitxers. Si el vostre sistema
utilitza UTF-8 (tal i com ho fan moltes distribucions actuals), necessiteu
convertir el fitxer abans de la lectura. Alguns programes, com gnopernicus, 
fan la conversió internament.

Podeu fer servir la opcions de guardar del editor gedit, o fer servir
programes conversors de format, com iconv:

        $ iconv -f utf8 -t ISO-8859-15//TRANSLIT bon_dia_utf8.text > bon_dia_iso.text

 * Un test ràpid:
          $ echo "Bon dia, Catalunya" | festival --tts --language catalan

 * També podeu executar 'Festival' de manera interactiva:

        $ festival
        (language_catalan)
        (intro-catalan)
        (SayText "Bon dia, Catalunya.")
        (SayText "Bona nit.")
        (exit)

 * Si voleu especificar el locutor, introduïu la comanda per seleccionar
el locutor, en lloc de la comanda de selecció de llenguatge:

        (voice_upc_ca_ona_hts)
        (SayText "I tu, qui ets?")
        (voice_upc_ca_pau_hts)
        (SayText "Jo sóc, el que tu ets, i si et faig mal, em faig mal a mi mateix.")
        (voice_upc_ca_ona_hts)
        (SayText "Que maco. Això és de l'assemblea dels infants, oi?")
        (exit)

 * O per llegir un fitxer de text, per exemple "bon_dia.txt": 

        $ echo "Bon dia, Catalunya." > bon_dia.txt
        $ festival
        (language_catalan)
        (tts_file "bon_dia.txt")
        (exit)

 * O utilitzeu l'script text2wave per crear un fitxer .wav:

        $ text2wave -o bondia.wav   -eval '(language_catalan)' bon_dia.txt 

 * Si voleu especificar el locutor:

        $ text2wave -o bondia.wav   -eval '(voice_upc_ca_ona_hts)' bon_dia.txt 


## Agraïments
Aquest treball ha estat finançat per la [Generalitat de Catalunya](http://www.gencat.cat).

El projecte ha estat promogut per diversos Departaments de la Generalitat 
de Catalunya:

  - Departament d'Educació
  - Secretaria de Telecomunicacions i Societat de la Informació 
    del Departament de Presidència. 

i per la Universitat Politècnica de Catalunya (UPC):

  - Centre de Recerca TALP
  - Càtedra d'Accessibilitat
  - Càtedra de Programari Lliure


Llegiu el fitxer AUTHORS.ca i THANKS.ca per veure la llista de gent que ha contribuït a 
aquest projecte.

