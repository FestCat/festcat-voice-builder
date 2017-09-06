(set! catalan-path (path-append (if (boundp 'datadir) datadir libdir) "upc_catalan/"))
(if (not (member_string catalan-path load-path))
                      (set! load-path (cons catalan-path load-path)))

(require 'upc_ca_generic_phoneset)
(upc_ca_generic::select_phoneset)

