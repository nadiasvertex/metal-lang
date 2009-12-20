"""Provides some common parsing objects."""

from __future__ import with_statement

import expr
import typesys

import literals

ident     = literals.l_ident
colon     = lambda s, log: literals.l_keyword(":", s, log)
semicolon = lambda s, log: literals.l_keyword(";", s, log)    
lcurl    = lambda s, log: literals.l_keyword("{", s, log)
rcurl    = lambda s, log: literals.l_keyword("}", s, log)
lbrack    = lambda s, log: literals.l_keyword("[", s, log)
rbrack    = lambda s, log: literals.l_keyword("]", s, log)
lparen    = lambda s, log: literals.l_keyword("(", s, log)
rparen    = lambda s, log: literals.l_keyword(")", s, log)



doc_info  = lambda s,log: literals.rule_chain([(colon, literals.ONE), 
                                               (literals.l_string, literals.ONE_OR_MORE)],s,log)
    