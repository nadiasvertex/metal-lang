import sys
import unittest

import err
import typesys.builtins
import typesys.struct
import typesys.type

import expr

class TestStructExpressions(unittest.TestCase):
    def setUp(self):
    	loc=err.location("unittest::setUp", 1, 1)
    	
    	self.log = err.new(sys.stderr)
        self.log.setIgnoreLevel(err.TRACE)
        
        typesys.type.setMachineSizes(typesys.type.UINT32, typesys.type.UINT8)
        typesys.builtins.initialize()
                    	
    	self.m  = typesys.module.new("test_module")
        self.st1 = typesys.struct.new("test_struct_type_1", loc)
        self.st2 = typesys.struct.new("test_struct_type_2", loc)
        
        self.st1.addMember("member1", typesys.type.new("uint32_t", loc))
        self.st1.addMember("member2", typesys.type.new("uint64_t", loc))
        
        self.m.addStruct(self.st1)
        self.m.addStruct(self.st2)
        
        il1 = expr.InitializerList(loc, [expr.newInt(loc, 500), expr.newInt(loc, 1),], 2)
        il2 = expr.InitializerList(loc, [expr.newInt(loc, 1024), 
										 expr.newInt(loc, 1<<25),], 2)
        
        self.sc_expr1 = expr.StructConstructor(loc, self.st1, il1)
        self.sc_expr2 = expr.StructConstructor(loc, self.st1, il2)
        self.sc_expr3 = expr.StructConstructor(loc, typesys.type.new("test_struct_type_1", loc), il1)
                       
        
    def testResolve(self):
    	loc=err.location("unittest::testResolve", 1, 1)    	        
        self.assertTrue(self.sc_expr3.resolve(self.m, self.log))
        
    def testCheck(self):
    	loc=err.location("unittest::testCheck", 1, 1)                
        self.assertTrue(self.sc_expr1.check(self.m, self.log))
    	
    def testCheckConst(self):
        loc=err.location("unittest::testCheckConst", 1, 1)                
        self.assertTrue(self.sc_expr2.checkConst(self.m, self.log))
        
        
        
    	
    	
        
        
    	