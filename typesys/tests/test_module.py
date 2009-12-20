import sys
import unittest

import err
import typesys.builtins
import typesys.module
import typesys.struct
import typesys.func
import typesys.type

class TestModule(unittest.TestCase):
    def setUp(self):
    	loc=err.location("unittest::setUp", 1, 1)
    	
    	typesys.type.setMachineSizes(typesys.type.UINT32, typesys.type.UINT8)
    	typesys.builtins.initialize()
    	
        self.m  = typesys.module.new("test_module")
        self.m2 = typesys.module.new("test_module2")
        self.st = typesys.struct.new("test_struct", loc)
        self.f1 = typesys.func.new("test_func", loc)
        
        self.const1 = typesys.const.new("test_const", typesys.type.new("uint64_t", loc), "419")
        self.m.addConstant(self.const1)
                
        self.m.addStruct(self.st)
        self.m.addFunc(self.f1)        
        
        self.m.addImport(self.m2)
        self.m2.addStruct(self.st)
        
        self.log = err.new(sys.stderr)
        
    def testAddStruct(self):
    	loc=err.location("unittest::testAddStruct", 1, 1)
    	t = typesys.type.new("test_struct", loc)                
        self.assertTrue(self.m.hasDefinition(t, self.log))
        
    def testAddObject(self):
    	loc=err.location("unittest::testAddObject", 1, 1)
        t = typesys.type.new("test_object", loc)                
        self.assertTrue(self.m.hasDefinition(t, self.log))
    
    def testAddFunc(self):
    	loc=err.location("unittest::testAddFunc", 1, 1)
        t = typesys.type.new("test_func", loc)         
        self.assertTrue(self.m.hasDefinition(t, self.log))
    
    def testAddConstant(self):
    	loc=err.location("unittest::testAddConstant", 1, 1)
        t = typesys.type.new("test_const", loc)               
        self.assertTrue(self.m.hasDefinition(t, self.log))
    
    def testAddImport(self):
    	loc=err.location("unittest::testAddImport", 1, 1)
        t = typesys.type.new("test_module2::test_struct", loc)                
        self.assertTrue(self.m.hasDefinition(t, self.log))
    