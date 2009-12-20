import sys
import unittest

import err
import typesys.builtins
import typesys.struct
import typesys.type

import expr

class TestInitializerListExpressions(unittest.TestCase):
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
        
        self.il1 = expr.InitializerList(loc, [expr.newInt(loc, 500), expr.newInt(loc, 1),], 2)
        self.il2 = expr.InitializerList(loc, [expr.newInt(loc, 1024), 
										      expr.newInt(loc, 1<<25),
										      expr.newInt(loc, 39)], 3)
        
    def testNumOutputs(self):
    	loc=err.location("unittest::testNumOutputs", 1, 1)    	        
        self.assertEqual(self.il1.getNumOutputs(),2)
        self.assertEqual(self.il2.getNumOutputs(),3)
        
    def testTypeByIndex(self):
    	loc=err.location("unittest::testTypeByIndex", 1, 1)
    	self.assertTrue(self.il1.getOutputTypebyIndex(0).isSame(typesys.type.new("uint16_t", loc, is_const=True)))                
           
        
        
    	
    	
        
        
    	