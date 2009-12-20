"""This module parses out expressions from an input stream"""

from __future__ import with_statement

import expr
import typesys
import types

from mparser import common
from mparser import literals

bin_ops = ["+","-","/","*","%","^","&","|","."]

def unfold_bin_expr(left, right):
    "Take a list of binary expressions and turn them into a left-recursive, depth-first tree."
    for op, opr in right:        
        op_expr = expr.Binary(op["value"], op["loc"], (left, opr))        
        left=op_expr
        
    return left
        

def const_expr(s, log):
    operands = [literals.l_float_expr,
                literals.l_int_expr,                
                literals.l_string_expr]
    
    op_kw = lambda s, log: literals.any_keyword(bin_ops, s, log)
    operand = lambda s, log: literals.any_rule(operands, s, log) 
    recurse = lambda s, log: literals.rule_chain([(op_kw, literals.ONE),
                                                  (operand, literals.ONE)], s, log)    
    rules = [(operand, literals.ONE),
             (recurse, literals.ZERO_OR_MORE)]
    
    result = literals.rule_chain(rules, s, log)
    if result!=None:
        if len(result)>1:            
            return unfold_bin_expr(result[0], result[1:])
        else:
            return result[0]
        
    return None
      