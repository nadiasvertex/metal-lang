"""This module parses out type definitions from an input stream"""

from __future__ import with_statement

import expr
import typesys

from mparser import common
from mparser import literals

def type_def(s, log):
    type_kw = lambda s, log: literals.any_keyword(typesys.type.type_map.keys(), s, log)
    