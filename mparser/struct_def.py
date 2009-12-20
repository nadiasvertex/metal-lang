"""This module parses out structure definitions from an input stream"""

from __future__ import with_statement

import expr
import typesys

import common
import literals

struct_kw = lambda s, log: literals.keyword("struct", s, log)
struct_start_rules = [ (struct_kw, literals.ONE),
                       (literals.l_ident, literals.ONE),
                       (common.doc_info,  literals.ZERO_OR_ONE),
                       (common.lcurl, literals.ONE) ]
    
struct_end_rules = [(common.rcurl, literals.ONE)]
    
def struct_def(s, log):            
    pass
    
