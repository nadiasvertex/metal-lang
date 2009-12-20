import os
import subprocess
import sys
import time
import unittest

import err
import gen
import typesys.builtins
import typesys.const
import typesys.struct
import typesys.func
import typesys.type

class TestLLVMGen(unittest.TestCase):
    def setUp(self):
        loc=err.location("unittest::setUp", 1, 1)
        
        self.log = err.new(sys.stderr)
        self.log.setIgnoreLevel(err.TRACE)
        
        self.gen = gen.new("llvm")
        self.gen.load_transforms(self.log)
        
        typesys.type.setMachineSizes(self.gen.word_type, self.gen.char_type)
        typesys.builtins.initialize()
        
        self.m  = typesys.module.new("test_module")
        self.st1 = typesys.struct.new("test_struct_type_1", loc)
        self.st2 = typesys.struct.new("test_struct_type_2", loc)
        
        self.st1.addMember("member1", typesys.type.new("test_struct_type_2", loc))
        self.st1.addMember("member2", typesys.type.new("test_struct_type_2", loc))
        
        self.m.addStruct(self.st1)
        self.m.addStruct(self.st2)
        
        self.const1 = typesys.const.new("test_string_const", typesys.type.newStruct(typesys.builtins.STRING_STRUCT, loc), "this is a test string for you")
        self.m.addConstant(self.const1)
        
        self.f1 = typesys.func.new("test_func", loc)
        self.m.addFunc(self.f1)
        
        typesys.builtins.initialize_module(self.m)
        
    def llvm_compile(self, filename):
        if sys.platform=="win32":
            cmd =r"f:\projects\llvm\Debug\bin\llvm-as -d -debug -f %s" % filename            
        elif sys.platform=="linux2":
            cmd =["/usr/local/bin/llvm-as", "-d", "-debug", "-f", filename]
                        
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.STDOUT)
        
        steps=0
        while p.poll()==None and steps<1:
        	time.sleep(5)
        	steps+=1
        	
        txt=p.stdout.read()
        rv=p.returncode
        return (True, txt) if rv==0 or rv==None else (False, txt)                 
        
    def testLoadTransforms(self):
        self.assertNotEqual(len(self.gen.frames), 0)
                
        
    def testGenCode(self):
        self.m.bindMembers(self.log)
        
        output, doc = self.gen.transform_module(True, self.m, self.log)
        self.assertNotEqual(len(output), 0)
        
        f=open("testGenCode.llvm", "w")
        f.write(output)
        f.close()   
        
        f=open("testGenCode.html", "w")
        f.write(doc)
        f.close()
        
        passed, txt = self.llvm_compile("testGenCode.llvm")        
        self.assertTrue(passed, txt)
        
        if passed==True:
            f=open("testGenCode.assembled.llvm", "w")
            f.write(txt)
            f.close()
            
        
        
        