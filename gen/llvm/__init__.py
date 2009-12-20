#$licensed
#    Copyright 2006-2007 Christopher Nelson
#
#
#
#    This file is part of the metal compiler system.
#
#    The metal compiler is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    The metal compiler is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#$endlicense

import types

import gen
import typesys.const
import typesys.struct
import typesys.type


import tests

type_map = { typesys.type.NULL    : "void",
             typesys.type.BOOL    : "i1",
             typesys.type.UINT8   : "i8",
             typesys.type.SINT8   : "i8",
             typesys.type.UINT16  : "i16",
             typesys.type.SINT16  : "i16",
             typesys.type.UINT32  : "i32",
             typesys.type.SINT32  : "i32",
             typesys.type.UINT64  : "i64",
             typesys.type.SINT64  : "i64",
             typesys.type.FLOAT32 : "float",
             typesys.type.FLOAT64 : "double",
             typesys.type.OPAQUE  : "opaque",            
            }


class LLVMGen(gen.Generator):
    "Derived class of the generator, implements some llvm specific functions."
    def __init__(self):
        gen.Generator.__init__(self, 'llvm')
        
    def get_word_type(self):
        return type_map[self.word_type]
    
    def get_char_type(self):
        return type_map[self.char_type]
        
    def get_register(self):
        r=gen.Generator.get_register(self)
        return "%" + r
       
    def get_struct_sig(self, st, log):
        "Returns the signature of a structure."
        stf = self.frames["struct_type"] if not st.isPacked() else self.frames["packed_struct_type"]
        members=[]
        for item in st.members:
            t = st.member_types[item]
            members.append(self.get_type_name(t, log))
        
        # Return the signature            
        d = { "members" : ",".join(members) }        
        return self.transform(d, stf)
                   
               
    def get_type_name(self, type_info, log):
        if type_info.isStruct():            
            tname = "%%type.%s" % type_info.name
                          
        elif type_info.isString():
            tname = "%type.string_t"            
        
        elif type_info.isType():
            tname = "%type.type_t"
                   
        else:
            try:
             tname = type_map[type_info.id]
            except:
             log.internal(type_info.loc, "There is no type for typename '%s', id '%d'\n" % (type_info.name, type_info.id))
             tname = "MISSING_TYPE_T"
            
        if type_info.isArray():
            if type_info.elem_count<0:
              tname+=" *"
            else:
              tname="[%d x %s]" % (type_info.elem_count, tname)
        
        if type_info.isRef():
            tname+=" *"
            
                
        return tname
       
    def get_initialized_string_object(self, m, str_index, is_const):
        d = {}
        flags = 0 if not is_const else typesys.builtins.STR_FLAG_CONST
        the_str = m.getString(str_index)
        
        # Assign out the values to the correct places
        st_def = m.getStructDef("string_t")
        d = { "flags"  : "$(flags)",
               "length" : "$(length)",
               "data"   :  "getelementptr([$(length) x $(char_type)]* @$(name), i32 0, i32 0)"}
        tmpl = self.get_initializer_for_struct(m, st_def, d, None)
        
        # Transform and return
        d={"flags" : str(flags), "length" : str(len(the_str)), "name" : "SC%d" % str_index}
        return self.transform(d, tmpl)     
    
    def get_initializer_for_struct(self, m, st_def, init, log):
        """Takes a struct definition, and an initializer dictionary.  It returns an
        initializer for the struct give the values in the dictionary.  Any values not
        present in the init dict will be set to zero."""
        
        # Handle arrays of structs
        if type(init) == types.ListType:
        	elems = []
        	for item in init:
        		elems.append("%%type.%s %s" % (st_def.name, self.get_initializer_for_struct(m, st_def, item, log)))
        		
        	return "[%s]" % ",".join(elems)
        
        d = {}
        for item in init:
            idx = st_def.getMemberIndex(item)
            type_name = self.get_type_name(st_def.getMemberType(item), log)
            value = init[item]
            if m.hasMember(value):
                d[idx] = "%s @%s" % (type_name, value)
            else:
                d[idx] = "%s %s" % (type_name, value)
            
        tmp = []
        for i in range(0, len(st_def.members)):
            if i in d:
                tmp.append(d[i])
            else:
                tmp.append("%s zeroinitializer" % self.get_type_name(st_def.getMemberTypebyIndex(i), log))
                        
        return "{%s}" % ",".join(tmp)
                       
    def inline_convert_to_cstring(self, input, b, log):
        "Convert a metal string to a c string inline, on the stack."
        output = self.get_register()
        wt = self.get_word_type()
        ct = self.get_char_type()
        
        t1 = self.get_register()
        t2 = self.get_register()
        t3 = self.get_register()
        
        # Make space on the stack
        mkspace = """
            ; Copy the metal string and make it into a c-string.
            %s = getelementptr %%type.metal_string_t *%s, %s 0, %s 1
            %s = load %s *%s
            %s = add  %s %s, 1
            %s = alloca %s, %s %s
            call void @llvm.memset.i32(i8 *%s, i8 0, i32 %s, i32 0) 
        """ % (t1, input, wt, wt, 
               t2, wt, t1, 
               t3, wt, t2, 
               output, ct, wt, t3,
               output, t3)
        
        t4 = self.get_register()
        t5 = self.get_register()
        # Perform the copy
        copy = """
            %s = getelementptr %%type.metal_string_t *%s, %s 0, %s 2
            %s = load %s **%s
            call void @llvm.memcpy.i32(i8 *%s, i8 *%s, i32 %s, i32 0)
            ; End copy into a c-string.
        """ % (t4, input, wt, wt,
               t5, ct, t4, 
               output, t5, t2)
        
        return (output, mkspace+copy)
    
    def inline_convert_to_raw_buffer(self, input, b, log):
        "Convert a metal string to a c string inline, on the stack."
        output = self.get_register()
        wt = self.get_word_type()
        ct = self.get_char_type()
        
        t1 = self.get_register()
        
        # Perform the copy
        thunk = """
            ; Thunk a string to a raw memory buffer.
            %s=getelementptr %%type.metal_string_t *%s, %s 0, %s 2            
            %s = load %s **%s
            ; End thunk
        """ % (t1, input, wt, wt, 
               output, ct, t1)
        
        return (output, thunk)
    
    def backend_transform_alien_decl(self, afd, m, log):
        "Transform an alien function declaration from metal to the target language."
        if afd["returns"]!=None:
            rv=type_map[afd["returns"][0]["type"]]
        else:
            rv="void"
            
        parms=[]
        for item in afd["parms"]:
            if item["type"] == typesys.types.STRING:
                parms.append("i8 *")
            else:
                parms.append("%s %s" % (type_map[item["type"]], '*' if item["is_ptr"] else ""))
                        
        return "declare %s @%s(%s)\n" % (rv, afd["name"], ",".join(parms))
        
        
    def backend_transform_alien_call(self, item, b, log):        
        "Transform an alien call from metal to the target language."
        m = b.getModule()
        afd = m.getAlienFunc(item["name"])
        
        print afd
        output=""
        
        if afd["returns"]!=None:
            rv=type_map[afd["returns"][0]["type"]]
        else:
            rv="void"
        
        
        parms=[]
        
        # Prepare our call parms
        i=-1
        for parm in item["parms"]:
            i+=1
            td, ft, type_info = self.transform_op(parm, b, log)
            output+=ft
            r = td["result"]
            
            print "parm output: ", rv, type_info
            
            p = afd["parms"][i]
            parm_type = p["type"]
            
            # Convert
            type = self.get_type_name(type_info, log)
            if type_info.isStringType():                
                if afd["call_type"] == "c":
                    # Figure out what to convert the string to.                    
                    if parm_type == typesys.types.STRING:                                       
                        type = "i8 *"
                        r, tf = self.inline_convert_to_cstring(r, b, log)                        
                        output+=tf
                    elif parm_type == typesys.type.UINT8 and p["is_ptr"]:
                        type = "i8"
                        r, tf = self.inline_convert_to_raw_buffer(r, b, log)
                        output+=tf
                    else:
                        log.error(item["loc"], "The LLVM backend won't convert the parameter %d from 'string_t' to the specified type in an alien call." % (i))
                else:
                    log.error(item["loc"], "Unknown alien call type '%s', cannot convert string parameters." % afd["call_type"])
                    log.error(afd["loc"], "This is the point of definition of the unknown alien call type.")
             
            # Type up the parms        
            r="%s %s%s" % (type, 
                           '*' if p["is_ptr"] else "",
                           r)
            
            parms.append(r)
                    
        # Construct the call
        the_call = "\ncall %s @%s(%s)\n" % (rv, item["name"], ",".join(parms))
        output += the_call
        
        return output
        
        
def new():
    "Return a new instance of an LLVM generator."
    return LLVMGen()
    