import sys
import unittest

import err
import typesys.builtins
import typesys.struct
import typesys.func
import typesys.type

import mparser.stream
from mparser import exprs
from expr import solver

class TestConstExpressions(unittest.TestCase):
    def setUp(self):
    	loc=err.location("unittest::setUp", 1, 1)
    	
    	self.log = err.new(sys.stderr)
        self.log.setIgnoreLevel(err.TRACE)
        
        typesys.type.setMachineSizes(typesys.type.UINT32, typesys.type.UINT8)
        typesys.builtins.initialize()
                    	
    	self.m  = typesys.module.new("test_module") 
        self.f1 = typesys.func.new("test_func_1", loc)
        self.b1 = typesys.block.new(loc, "test_func_1_mainline")       
        self.s = mparser.stream.new()
                
        # Setup a simple context: one module, one func, one block, one var.
        self.b1.addMember("local_member1", typesys.type.new("uint32_t", loc, is_const=True))        
        self.f1.setMainlineBlock(self.b1)
        self.m.addFunc(self.f1)       
    
    def testParseLiteralIsConstExpr(self):
        "Try to parse a literal expression as a constant expression"
        data="7"
        self.s.merge(data, "const_expr_data")
        rv = exprs.const_expr(self.s, self.log)
        
        self.assertNotEqual(rv, None)
        self.assertEqual(rv.op, "lit")
        
        # Run the expression solver to make sure that we get what we expect
        cs = solver.SolveConstantExpr(rv)
        result = cs()
        self.assertEqual(result.value, 7)
        
        # Verify that we know that this is a constant node.
        self.assertTrue(rv.isConst())
        
    def testParseSimpleConstExpr(self):
        "Try to parse a simple constant expression out of the data"
        data="5+10"
        self.s.merge(data, "const_expr_data")
        rv = exprs.const_expr(self.s, self.log)
        
        self.assertNotEqual(rv, None)
        self.assertEqual(rv.op, "+")
        
        # Run the expression solver to make sure that we get what we expect
        cs = solver.SolveConstantExpr(rv)
        result = cs()
        self.assertEqual(result.value, 15)
        
        # Verify that we know that this is a constant node.
        self.assertTrue(rv.isConst())
        
    def testParseCompoundConstExpr(self):
        "Try to parse a compound constant expression out of the data"
        data="8+3-2*10"
        self.s.merge(data, "const_expr_data")
        rv = exprs.const_expr(self.s, self.log)
        
        self.assertNotEqual(rv, None)
        self.assertEqual(rv.op, "*")
        
        # Run the expression solver to make sure that we get what we expect
        cs = solver.SolveConstantExpr(rv)
        result = cs()
        self.assertEqual(result.value, 90)
        
        # Verify that we know that this is a constant node.
        self.assertTrue(rv.isConst())
    
    def testParseMixedConstExpr(self):
        "Try to parse a constant expression that mixes floats and ints"
        data="2.5+10-0.5/2"
        self.s.merge(data, "const_mixed_expr_data")
        rv = exprs.const_expr(self.s, self.log)
        
        self.assertNotEqual(rv, None)
        self.assertEqual(rv.op, "/")
        
        # Run the expression solver to make sure that we get what we expect
        cs = solver.SolveConstantExpr(rv)
        result = cs()
        self.assertEqual(result.value, 6.0)
        
        # Verify that we know that this is a constant node.
        self.assertTrue(rv.isConst())
        
    def testParseStringConstExpr(self):
        "Try to parse a constant expression that contains string operations"
        loc=err.location("unittest::testParseStringConstExpr", 1, 1)
        
        data='"the"+" "+"dog"'
        self.s.merge(data, "const_string_expr_data")
        rv = exprs.const_expr(self.s, self.log)
        
        self.assertNotEqual(rv, None)
        self.assertEqual(rv.op, "+")
        
        # Run the expression solver to make sure that we get what we expect
        cs = solver.SolveConstantExpr(rv)
        result = cs()
        self.assertEqual(result.value, "the dog")
        
        # Verify that we know that this is a constant node.
        self.assertTrue(rv.isConst())    
        
        self.m  = typesys.module.new("test_module")
        self.f1 = typesys.func.new("test_func_1", loc)               
                             
    def testParseConstIdentExpr(self):
        "Try to parse a constant expression that contains a constant, initialized variable."
        loc=err.location("unittest::testParseConstIdentExpr", 1, 1)                
             
        self.assertTrue(False)
        self.log.error(loc, "Constant variable unit test is incomplete.")
        
    def testParseConstIfExpr(self):
        "Try to parse a constant expression that contains an value if condition else other_value."
        loc=err.location("unittest::testParseConstIfExpr", 1, 1)                
             
        data='2 if true else 3'
        self.s.merge(data, "const_if_expr_data")
        rv = exprs.const_if_expr(self.s, self.log)
        
        self.assertNotEqual(rv, None)
        self.assertEqual(rv.op, "if")
        
        # Run the expression solver to make sure that we get what we expect
        cs = solver.SolveConstantExpr(rv)
        result = cs()
        self.assertEqual(result.value, 2)
        
        # Verify that we know that this is a constant node.
        self.assertTrue(rv.isConst())    
          
    	
        
        
    	