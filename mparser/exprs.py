"""This module parses out expressions from an input stream"""

from __future__ import with_statement

import expr
import typesys
import types

from mparser import common
from mparser import literals


##################################################################
# Matching expressions for constant binary expressions
bin_operations =     ["+","-","/","*","%","^","&","|","."]
bin_expr_operands = [literals.l_float_expr,
                     literals.l_int_expr,                
                     literals.l_string_expr,
                     literals.l_bool_expr,]

bin_expr_operation_kw = lambda s, log: literals.any_keyword(bin_operations, s, log)    
bin_expr_operand = lambda s, log: literals.any_rule(bin_expr_operands, s, log)
bin_expr_recurse = lambda s, log: literals.rule_chain([(bin_expr_operation_kw, literals.ONE),
                                                       (bin_expr_operand, literals.ONE)], s, log)
bin_expr_rules = [(bin_expr_operand, literals.ONE),
                  (bin_expr_recurse, literals.ZERO_OR_MORE)]
        

def unfold_bin_expr(left, right):
    "Take a list of binary expressions and turn them into a left-recursive, depth-first tree."
    for op, opr in right:        
        op_expr = expr.Binary(op["value"], op["loc"], (left, opr))        
        left=op_expr
        
    return left
        

def const_expr(s, log):
    "Parse a constant expression, return an expression tree for it."
    result = literals.rule_chain(bin_expr_rules, s, log)
    if result!=None:
        if len(result)>1:            
            return unfold_bin_expr(result[0], result[1:])
        else:
            return result[0]
        
    return None

##################################################################
# Matching expressions for literal value if cond else other_value
l_if   = lambda s,log: literals.l_keyword("if", s, log)
l_else = lambda s,log: literals.l_keyword("else", s, log)

if_expr_rules = [ (const_expr, literals.ONE),
                  (l_if, literals.ONE),
                  (const_expr, literals.ONE),
                  (l_else, literals.ONE),
                  (const_expr, literals.ONE)]

def const_if_expr(s, log):    
    true_value, kw_if, cond, kw_else, false_value = literals.rule_chain(if_expr_rules, s, log) 
    return expr.IfExpr(true_value.loc, cond, true_value, false_value)    
      
