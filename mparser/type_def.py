"""This module parses out type definitions from an input stream"""

from __future__ import with_statement

import expr
import typesys

from mparser import common
from mparser import literals

type_kw = lambda s, log: literals.any_keyword(typesys.type.type_map.keys(), s, log)
type_rules = [ (type_kw, literals.ONE),
               (literals.l_ident, literals.ONE),
               (common.doc_info,  literals.ZERO_OR_ONE),
             ]


def type_def(s, log):
    pass
    
