import sys
import unittest

import err
import typesys.builtins
import typesys.func
import typesys.block
import typesys.type

class TestBlock(unittest.TestCase):
    def setUp(self):
    	loc=err.location("unittest::TestBlock::setUp", 1, 1)
    	
    	self.log = err.new(sys.stderr)
        self.log.setIgnoreLevel(err.TRACE)
        
        typesys.type.setMachineSizes(typesys.type.UINT32, typesys.type.UINT8)
        typesys.builtins.initialize()
                    	
    	self.m  = typesys.module.new("test_module")
        self.f1 = typesys.func.new("test_func_1", loc)               
                             
    def testAddBlock(self):
    	loc=err.location("unittest::testAddFuncWithBlock", 1, 1)                
        t = typesys.type.new("test_func_1", loc)
        
        # Add the block
        b = typesys.block.new(loc, "test_func_1_mainline")
        
        # Add a variable
        b.addMember("local_member1", typesys.type.new("uint32_t", loc))
        
        # Add the block        
        self.f1.setMainlineBlock(b)       
        
        # Add the function
        self.m.addFunc(self.f1)
        
        # Make sure that the member is found
        self.assertTrue(b.hasMember("local_member1"), "The local variable does not exist.")
        
        
    