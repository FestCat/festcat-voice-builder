;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                     ;;;
;;;                     Carnegie Mellon University                      ;;;
;;;                  and Alan W Black and Kevin Lenzo                   ;;;
;;;                      Copyright (c) 1998-2005                        ;;;
;;;                        All Rights Reserved.                         ;;;
;;;                                                                     ;;;
;;; Permission is hereby granted, free of charge, to use and distribute ;;;
;;; this software and its documentation without restriction, including  ;;;
;;; without limitation the rights to use, copy, modify, merge, publish, ;;;
;;; distribute, sublicense, and/or sell copies of this work, and to     ;;;
;;; permit persons to whom this work is furnished to do so, subject to  ;;;
;;; the following conditions:                                           ;;;
;;;  1. The code must retain the above copyright notice, this list of   ;;;
;;;     conditions and the following disclaimer.                        ;;;
;;;  2. Any modifications must be clearly marked as such.               ;;;
;;;  3. Original authors' names are not deleted.                        ;;;
;;;  4. The authors' names are not used to endorse or promote products  ;;;
;;;     derived from this software without specific prior written       ;;;
;;;     permission.                                                     ;;;
;;;                                                                     ;;;
;;; CARNEGIE MELLON UNIVERSITY AND THE CONTRIBUTORS TO THIS WORK        ;;;
;;; DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING     ;;;
;;; ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT  ;;;
;;; SHALL CARNEGIE MELLON UNIVERSITY NOR THE CONTRIBUTORS BE LIABLE     ;;;
;;; FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES   ;;;
;;; WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN  ;;;
;;; AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,         ;;;
;;; ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF      ;;;
;;; THIS SOFTWARE.                                                      ;;;
;;;                                                                     ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;                                                                      ;;
;;;  A generic voice definition file for a hts synthesizer               ;;
;;;  Customized for: upc_ca_SPEAKER                                         ;;
;;;                                                                      ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;; ------------------------------------------------------------------- ;;;
;;; Extension to Catalan:                                               ;;;
;;; Antonio Bonafonte                                                   ;;;
;;; Universitat Politecnica de Catalunya                                ;;;
;;; 2007, Barcelona, Spain                                              ;;;
;;; ------------------------------------------------------------------- ;;;

;;; Try to find the directory where the voice is, this may be from
;;; .../festival/lib/voices/ or from the current directory
(if (assoc 'upc_ca_SPEAKER_hts voice-locations)
    (defvar upc_ca_SPEAKER_hts::hts_dir 
      (cdr (assoc 'upc_ca_SPEAKER_hts voice-locations)))
    (defvar upc_ca_SPEAKER_hts::hts_dir (string-append (pwd) "/"))
)

(defvar upc_ca_SPEAKER_hts::dir upc_ca_SPEAKER_hts::hts_dir)

;;; Did we succeed in finding it
(if (not (probe_file (path-append upc_ca_SPEAKER_hts::dir "festvox/")))
    (begin
     (format stderr "upc_ca_SPEAKER::hts: Can't find voice scm files they are not in\n")
     (format stderr "   %s\n" (path-append  upc_ca_SPEAKER_hts::dir "festvox/"))
     (format stderr "   Either the voice isn't linked in Festival library\n")
     (format stderr "   or you are starting festival in the wrong directory\n")
     (error)))

;;;  Add the directory that contains catalan stuff (normalization, tagger, etc.) to load-path
(set! catalan-path (path-append datadir "upc_catalan/"))
(if (not (member_string catalan-path load-path))
                      (set! load-path (cons catalan-path load-path)))

;;; General issues, as intro-catalan
(require 'upc_catalan)


;;;  Add the directory contains general voice stuff to load-path
(set! load-path (cons (path-append upc_ca_SPEAKER_hts::dir "festvox/") 
		      load-path))

(set! hts_data_dir (path-append upc_ca_SPEAKER_hts::hts_dir "hts/"))


(set! hts_feats_list
      (load (path-append hts_data_dir "label.feats") t))

(set! upc_ca_SPEAKER_hts::hts_feats_list hts_feats_list)

(require 'hts)
(require_module 'hts_engine)

;;; Voice specific parameter are defined in each of the following
;;; files
(require 'upc_ca_generic_phoneset)
(require 'upc_ca_generic_tokenizer)
(require 'upc_ca_generic_tagger)
(require 'upc_ca_generic_lexicon)
(require 'upc_ca_generic_phrasing)
;; ... and others as required

(define (upc_ca_SPEAKER_hts::voice_reset)
  "(upc_ca_SPEAKER_hts::voice_reset)
Reset global variables back to previous voice."
  (upc_ca_generic::reset_phoneset)
  (upc_ca_generic::reset_tokenizer)
  (upc_ca_generic::reset_tagger)
  (upc_ca_generic::reset_lexicon)
  (upc_ca_generic::reset_phrasing)
  t
)

(set! upc_ca_SPEAKER_hts::hts_feats_list
      (load (path-append hts_data_dir "label.feats") t))

(set! upc_ca_SPEAKER_hts::hts_engine_params
      (list
       (list "-md" (path-append hts_data_dir "dur.pdf"))
       (list "-mm" (path-append hts_data_dir "mgc.pdf"))
       (list "-mf" (path-append hts_data_dir "lf0.pdf"))

       (list "-td" (path-append hts_data_dir "tree-dur.inf"))
       (list "-tm" (path-append hts_data_dir "tree-mgc.inf"))
       (list "-tf" (path-append hts_data_dir "tree-lf0.inf"))

       (list "-dm1" (path-append hts_data_dir "mgc.win1"))
       (list "-dm2" (path-append hts_data_dir "mgc.win2"))
       (list "-dm3" (path-append hts_data_dir "mgc.win3"))
       (list "-df1" (path-append hts_data_dir "lf0.win1"))
       (list "-df2" (path-append hts_data_dir "lf0.win2"))
       (list "-df3" (path-append hts_data_dir "lf0.win3"))
       (list "-cm" (path-append hts_data_dir "gv-mgc.pdf"))
       (list "-cf" (path-append hts_data_dir "gv-lf0.pdf"))
       (list "-em"  (path-append hts_data_dir "tree-gv-mgc.inf"))
       (list "-ef"  (path-append hts_data_dir "tree-gv-lf0.inf"))

       (list "-k"  (path-append hts_data_dir "gv-switch.inf"))
       '("-s"    48000.0)
       '("-p"    240.0)
       '("-a"    0.550000)
       '("-g"    0.0)
       '("-b"    0.4)
       '("-u"    0.5)
       ))

(define (voice_upc_ca_SPEAKER_hts)
  "(voice_upc_ca_SPEAKER_hts)
Define voice for catalan."
  ;; *always* required
  (voice_reset)

  ;; Select appropriate phone set
  (upc_ca_generic::select_phoneset)

  ;; Select appropriate tokenization
  (upc_ca_generic::select_tokenizer)

  ;; For part of speech tagging
  (upc_ca_generic::select_tagger)

  (upc_ca_generic::select_lexicon)
  (upc_ca_generic::select_phrasing)

  (Param.set 'Int_Target_Method nil)
  (Param.set 'Duration_Method nil)
  (Param.set 'Int_Method nil)

  ;; Waveform synthesis model: hts
  (set! hts_engine_params upc_ca_SPEAKER_hts::hts_engine_params)
  (set! hts_feats_list upc_ca_SPEAKER_hts::hts_feats_list)
  (Param.set 'Synth_Method 'HTS)

  ;; This is where you can modify power (and sampling rate) if desired
  (set! after_synth_hooks nil)
;  (set! after_synth_hooks
;      (list
;        (lambda (utt)
;          (utt.wave.rescale utt 2.1))))

  (set! current_voice_reset upc_ca_SPEAKER_hts::voice_reset)

  (set! current-voice 'upc_ca_SPEAKER_hts)
)

(proclaim_voice
 'upc_ca_SPEAKER_hts
 '((language catalan)
   (gender female)
   (dialect central)
   (coding ISO-8859-15)
   (description
    "Catalan speaker SPEAKER from the Festcat project.")))

(provide 'upc_ca_SPEAKER_hts)

