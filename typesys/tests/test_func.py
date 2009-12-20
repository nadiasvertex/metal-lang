import sys
import unittest

import err
import typesys.builtins
import typesys.func
import typesys.type

class TestFunc(unittest.TestCase):
    def setUp(self):
    	loc=err.location("unittest::TestFunc::setUp", 1, 1)
    	
    	self.log = err.new(sys.stderr)
        self.log.setIgnoreLevel(err.TRACE)
        
        typesys.type.setMachineSizes(typesys.type.UINT32, typesys.type.UINT8)
        typesys.builtins.initialize()
                    	
    	self.m  = typesys.module.new("test_module")
        self.f1 = typesys.func.new("test_func_1", loc)
                       
    def testAddFunc(self):
    	loc=err.location("unittest::testAddFunc", 1, 1)
        
        t = typesys.type.new("test_func_1", loc)
        self.m.addFunc(self.f1)        
        self.assertTrue(self.m.hasDefinition(t, "test_func_1"), 
                        "test_func_1 wasn't found after adding it in.")
        
    def testAddInboundParm(self):
        loc=err.location("unittest::testAddInboundParm", 1, 1)
        
        self.f1.addInboundVar("test1", typesys.type.new("uint64_t", loc))
        self.m.addFunc(self.f1)
        
        self.assertTrue(self.f1.hasParm("test1"))
        
    def testAddOutboundParm(self):
        loc=err.location("unittest::testAddOutboundParm", 1, 1)
        
        self.f1.addOutboundVar("test1", typesys.type.new("uint64_t", loc))
        self.m.addFunc(self.f1)
        
        self.assertTrue(self.f1.hasParm("test1"))
        
        
            
        
    	
        
        
    	