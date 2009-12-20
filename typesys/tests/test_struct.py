import sys
import unittest

import err
import typesys.builtins
import typesys.struct
import typesys.type

class TestStruct(unittest.TestCase):
    def setUp(self):
    	loc=err.location("unittest::setUp", 1, 1)
    	
    	self.log = err.new(sys.stderr)
        self.log.setIgnoreLevel(err.TRACE)
        
        typesys.type.setMachineSizes(typesys.type.UINT32, typesys.type.UINT8)
        typesys.builtins.initialize()
                    	
    	self.m  = typesys.module.new("test_module")
        self.st1 = typesys.struct.new("test_struct_type_1", loc)
        self.st2 = typesys.struct.new("test_struct_type_2", loc)
        
        self.st1.addMember("member1", typesys.type.new("test_struct_type_2", loc))
        self.st1.addMember("member2", typesys.type.new("test_struct_type_2", loc))
        
        self.m.addStruct(self.st1)
        self.m.addStruct(self.st2)
        
        
    def testAddMember(self):
    	loc=err.location("unittest::testAddMember", 1, 1)        
        self.assertTrue(self.st1.hasMember("member1"), "member1 wasn't found after adding it in.")
        
    def testMemberOrder(self):
    	loc=err.location("unittest::testMemberOrder", 1, 1)
        
        idx1 = self.st1.getMemberIndex("member1")
        idx2 = self.st1.getMemberIndex("member2")
        
        self.assertEqual(idx1, 0)
        self.assertEqual(idx2, 1)
        
    def testBindMembers(self):
    	loc=err.location("unittest::testBindMembers", 1, 1)
    	self.assertTrue(self.st1.bindMembers(self.log))
    	
    	
        
        
    	