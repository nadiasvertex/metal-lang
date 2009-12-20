import frame_parse
import ops_parse
import transform_parse

import typesys

import ConfigParser
import os
import re
import time
import traceback
import types

#  The code generator will promote types up the chain of classes using this
# dictionary, in order to find matching transforms for various operations.
type_tiers = {  "bool" : "unsigned",
                "uint8" : "unsigned",
                "sint8" : "signed",
                "uint16" : "unsigned",
                "sint16" : "signed",
                "uint32" : "unsigned",
                "sint32" : "signed",
                "uint64" : "unsigned",
                "sint64" : "signed",
                "float32" : "float",
                "float64" : "float",
                
                "signed" : "integer", 
                "unsigned" : "integer",
                
                "integer" : "number",
                "float"   : "number",
                                
                "type" : "default",
                "self" : "default",
                
                "number" : "default",
                "string" : "default",
                "struct" : "default",
                "null"   : "default",
                
                "default" : None
}             

class Formatter:
    "Used to format code for the proper indent level, and just generally clean things up."
    def __init__(self):
        self.indent=0
        self.indent_item="\t"
        self.comment=";"*3
        self.indent_mark="$indent$"
        self.dedent_mark="$dedent$"
        
    def setComment(self, r):
        self.comment = r*3
    
    def enter_block(self):
        self.indent+=1
        
    def leave_block(self):
        self.indent-=1
        if self.indent<0:
            self.indent=0
            
    def reformat(self, txt):        
        lines = txt.split('\n')
        output = ""        
        for line in lines:
            l=line.strip()
            if l.startswith(self.indent_mark):
                self.enter_block()
                continue
            
            if l.startswith(self.dedent_mark):
                self.leave_block()
                continue
            
            if self.indent==0:
                output+=line+"\n"
            else:
                output+=(self.indent_item*self.indent)+l+"\n"
                
        return output
       
convert_comment_char = { "semicolon" : ";",
		      	   	     "hash"      : "#",
		      	   	     "colon"     : ":" }

class Generator:
   def __init__(self, backend):
        self.formatter=Formatter()
        self.backend=backend        
        self.ops_filename = "ops.%s" % backend        
        self.conf_filename = "%s.conf" % backend
        self.framework_files = [ "block.%s" % backend, "func.%s" % backend, "module.%s" % backend,
                                 "struct.%s" % backend, "intrinsics.%s" % backend]
        self.path = "lib/rte/%s" % backend
        
        
        #  True if infix output notation is required, otherwise we do
        # prefix notation.
        self.is_infix = False
        
        #  The register count.  Used for assigning temporary values.  It's
        # reset everytime we enter a new function, and incremented for each reg request.
        self.register=0
        
        #  The unique id counter.  Each transformation has a unique id for it's transform
        # block.  This counter keeps track of that value.
        self.transform_id=0
        
        # The dictionary of operation transforms, +, -, etc.
        self.ops = {}
        
        # The dictionary of framework transforms, struct defs, function defs, etc.
        self.frames = {}
        
        # The dictionary of settings from the *.conf file.
        self.settings = {}
        
   def is_set(self, s):
        "Returns True if the setting exists and is set to a non-zero value."
        if self.settings.has_option("language", s):
            v = int(self.settings.get("language", s))
            return v!=0
        
        return False
        
   def transform(self, d, t):
        """Transforms the string in t using the dictionary in d.
        Also adds some dictionary entries that are always available during every transform.
        
                nl: a newline character
                tab: a tab character
                id: an id that is globally unique to each translation unit. May be (and should be)
                used for uniqifying labels or other items inside transforms. 
        """
                
        d["nl"] = "\n"
        d["tab"] = "\t"
        d["id"] = self.transform_id
        d["word_type"]=self.get_word_type()
        d["char_type"]=self.get_char_type()
                
        self.transform_id+=1   
                       
        # Preprocess the transform
        t = transform_parse.preprocess(t,d)
        
        # Run the filters             
        t = transform_parse.filter(t,d)        
         
        return t.strip()
        
   def get_type_name(self, type_info, log):
        "Returns the name of the type for the target language. MUST be overridden."
        pass
        
   def get_output_filename(self, filename):
        "Returns the filename mangled to have the correct extension for the target language's output."
        filename = os.path.split(filename)[1]        
        return os.path.splitext(filename)[0] + (".%s" % self.backend)
        
   def load_transforms(self, log):        
        "Load the transformation templates."
        
        # Load the settings   
        self.settings = ConfigParser.SafeConfigParser()
        conf_filename = os.path.join(self.path, self.conf_filename)
        try:
            cf=open(conf_filename)
        except:
            log.internal(None, "Unable to load configuration file: '%s'" % conf_filename)
            log.internal(None, traceback.format_exc())
            return
             
        self.settings.readfp(cf, conf_filename)
        cf.close()          
        
        self.comment = self.settings.get("language", "one_line_comment")  
        self.is_infix = (self.settings.get("language", "expression_expansion").lower() == "infix")
        self.indent = self.settings.get("language", "indent_code")
        self.pointer = self.settings.get("language", "pointer_symbol")
        self.outbound_are_pointers = int(self.settings.get("language", "outbound_are_pointers"))
        self.always_pointers = self.settings.get("language", "always_pointers").split(" ")
        self.depth = 0
        
        if self.comment in convert_comment_char:
        	self.comment=convert_comment_char[self.comment]
        
        self.formatter.setComment(self.comment)
        
        # Default to 32-bit words and 8-bit chars
        self.word_type = typesys.type.UINT32
        self.char_type = typesys.type.UINT8
            
        # Create parser objects for the templates
        o_parser = ops_parse.OperationsParser()
        f_parser = frame_parse.FrameworkParser()
        
        # Get the filename for the operations template
        ops_filename = os.path.join(self.path, self.ops_filename)
        
        # Parse the operations template         
        self.ops = o_parser.parse(ops_filename, log)
        
        # Get and parse the files for the framework templates
        f_parser.set_comment(self.comment)
        for name in self.framework_files:
            filename = os.path.join(self.path, name)
            f_parser.parse(filename, log)
        
        # Get the dictionary from the framework parser.
        self.frames = f_parser.get_dictionary()
        
        
   def get_register(self):
        self.register+=1
        return "r%d" % self.register
    
   def get_transform(self, opr_type, the_op):
        "Gets a transform for an operation on a primitive type."
        # Assume that the primitive type has a trailing _t
        opr_type = opr_type[:-2]
        
        print "transform operator type: ", opr_type
        
        while 1:
            # Get the dictionary for operation transforms
            if opr_type in self.ops:
                odt = self.ops[opr_type]
                if the_op in odt:
                    return odt[the_op]
                    
            # Step up to the next tier of "types"
            if opr_type in type_tiers:
                opr_type = type_tiers[opr_type]                
            else:
                opr_type = None
                
            if opr_type == None:
                return None   
               
   def document_module(self, m, log):
       """Returns XHTML documentation for the module."""
       doc="<h1>%s</h1>\n<p>%s</p>\n" % (m.name, m.docstring)
       
       doc+="<h2>structs</h2>\n"
       for item in m.structs:
        doc+="<h3>%s</h3>\n<p>%s</p>\n<pre>%s</pre>\n" % (item, m.structs[item].docstring, "\n".join(m.structs[item].members))
       
       doc+="<h2>constants</h2>\n" 
       for item in m.constants:
        doc+="<h3>%s</h3>\n<p>%s</p>\n" % (item, m.constants[item].docstring)     
       
       doc+="<h2>globals</h2>\n" 
       for item in m.global_vars:
        doc+="<h3>%s</h3>\n<p>%s</p>\n" % (item, m.global_vars[item].docstring)
        
       return "<html>%s</html>" % doc
               
   def transform_module(self, is_target, m, log):
       """Transform a module.  If is_target is true, then this module is the code target for this
       run through the generator.  That means we generate functions and type_t structures.  Otherwise
       we generate type information for structs and extern function pointers, but no executable code."""
                             
       structs = self.transform_structs(m, set(), m.structs, log)
       consts  = self.transform_constants(m, log)
       globs   = self.transform_globals(m, log)
       f_decl, f_def = self.transform_functions(m, log)
       
       # Setup the module transform
       mf = self.frames["module"]
       d  = { "struct_definitions" : "\n".join(structs),
			  "object_definitions" : "",
			  "constants"          : "\n".join(consts),
			  "globals" 	   	   : "\n".join(globs),
			  "func_declarations"  : "\n".join(f_decl),
			  "func_definitions"   : "\n".join(f_def),
		    }
       
       # Transform and reformat the template
       return (self.formatter.reformat(self.transform(d, mf)),
			   self.document_module(m, log) if is_target else None)    
       
   def transform_structs(self, m, processed, to_process, log):
        struct_transforms = []
        stf = self.frames["struct"]        
        for item in to_process:              
            st_def = m.structs[item]
            if item not in processed:                                
                processed.add(item)    
                d = { "name" : item, "struct_type" : self.get_struct_sig(st_def, log) }
                struct_transforms.append(self.transform(d, stf))
            
        return struct_transforms
       
   def transform_constants(self, m, log):
       consts=[]
   
       csf = self.frames["raw_string_constant"]
       idx=0
       for s in m.string_table:
           d={"name" : "SC%d" % idx, "length" : len(s), "value" : s}
           consts.append(self.transform(d, csf))
           idx+=1        
       
       csf = self.frames["string_constant"]
       for item in m.constants:
            const_def = m.constants[item]
            if const_def.type_info.isString():
            	d = { "initialized_string_object" : self.get_initialized_string_object(m, const_def.initializer, True),
					  "name"                      : const_def.name }            	
            	consts.append(self.transform(d, csf))  
            
       return consts
   
   def transform_globals(self, m, log):
       globs=[]
       
       gf  = self.frames["global_struct"]
       idx = 0
       for item in m.global_vars:
           global_def = m.global_vars[item]
           if global_def.type_info.isStruct():
               d = { "initialized_struct" : self.get_initializer_for_struct(m, global_def.type_info.struct_def, global_def.initializer, log),
					 "name"               : global_def.name,
					 "type"	   	   	   	  : self.get_type_name(global_def.type_info, log)
				   }
               globs.append(self.transform(d, gf))
               
       return globs
   
   def transform_functions(self, m, log):
       "Generation code for function declarations."
       decls=[]
       defs=[]
       
       decl_f = self.frames["func_declaration"]
       def_f  = self.frames["func_definition"]
       for func in m.funcs:
           fd = m.funcs[func]
           d = { "name" : func,
                 "outbound_name" : fd.getOutboundSignature(),
                 "inbound_name" : fd.getInboundSignature(),                 
               }
           decls.append(self.transform(d, decl_f))
                   
       return decls, defs
       
       
def new(backend):
    if backend=="llvm":
        import gen.llvm
        return gen.llvm.new()
           
