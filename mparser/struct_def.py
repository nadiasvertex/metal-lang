"""This module parses out structure definitions from an input stream"""

from __future__ import with_statement

import expr
import typesys

import common
import literals

def struct_def(s, log):
    struct_kw = lambda s, log: literals.keyword("struct", s, log)        
    
    start_rules = [ (struct_kw, literals.ONE),
                    (common.doc_info,  literals.ZERO_OR_ONE),
                    (common.lcurl, literals.ONE) ]
    
    end_rules = [(common.rbrack, literals.ONE)]
    