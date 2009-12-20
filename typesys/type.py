import copy

# The types allowed by the language
NULL    = 0
UINT8   = 1
SINT8   = 2
UINT16  = 3
SINT16  = 4
UINT32  = 5
SINT32  = 6
UINT64  = 7
SINT64  = 8
FLOAT32 = 9
FLOAT64 = 10
OBJECT  = 11
FUNC    = 12
BOOL    = 13
STRING  = 14
TYPE    = 15
STRUCT  = 16
OPAQUE  = 17
UNRESOLVED = 0xffffffff

type_map = { "bool_t" : BOOL, 
             "uint8_t" : UINT8, "sint8_t" : SINT8,
             "uint16_t" : UINT16, "sint16_t" : SINT16,
             "uint32_t" : UINT32, "sint32_t" : SINT32,
             "uint64_t" : UINT64, "sint64_t" : SINT64,
             "float32_t" : FLOAT32, "float64_t" : FLOAT64,
             "string_t" : STRING,              
             "type_t" : TYPE,
             "opaque_t" : OPAQUE }
             
id_to_name_map = {
            NULL    : "null_t",
            UINT8   : "uint8_t",
            SINT8   : "sint8_t",
            UINT16  : "uint16_t",
            SINT16  : "sint16_t",
            UINT32  : "uint32_t",
            SINT32  : "sint32_t",
            UINT64  : "uint64_t",
            SINT64  : "sint64_t",
            FLOAT32 : "float32_t",
            FLOAT64 : "float64_t",
            OBJECT  : "object_t",
            FUNC    : "function_t",            
            BOOL     : "bool_t",            
            TYPE     : "type_t",
            STRING   : "string_t",
            OPAQUE   : "opaque_t",
            }
            
id_to_size_map = {
            NULL    : 0,
            UINT8   : 1,
            SINT8   : 1,
            UINT16  : 2,
            SINT16  : 2,
            UINT32  : 4,
            SINT32  : 4,
            UINT64  : 8,
            SINT64  : 8,
            FLOAT32 : 4,
            FLOAT64 : 8,                        
            BOOL     : 1,            
            }            

# The type system allows automatic type casting for the following cases
SINT8_CAST = [SINT16, SINT32, SINT64, FLOAT32, FLOAT64]
UINT8_CAST = [UINT16, SINT16, UINT32, SINT32, UINT64, SINT64, FLOAT32, FLOAT64]

SINT16_CAST = [SINT32, SINT64, FLOAT32, FLOAT64]
UINT16_CAST = [UINT32, SINT32, UINT64, SINT64, FLOAT32, FLOAT64]

SINT32_CAST = [SINT64, FLOAT32, FLOAT64]
UINT32_CAST = [UINT64, SINT64, FLOAT32, FLOAT64]

SINT64_CAST = [FLOAT64]
UINT64_CAST = [FLOAT64]

FLOAT32_CAST = [FLOAT64]

INTEGERS = [SINT8, UINT8, SINT16, UINT16, SINT32, UINT32, SINT64, UINT64]
FLOATS   = [FLOAT32, FLOAT64]

CAST = { SINT8  : SINT8_CAST,
	   	 UINT8  : UINT8_CAST,
	   	 SINT16 : SINT16_CAST,
	   	 UINT16 : UINT16_CAST,
	   	 SINT32 : SINT32_CAST,
	   	 UINT32 : UINT32_CAST,
	   	 SINT64 : SINT64_CAST,
	   	 UINT64 : UINT64_CAST,
	   	 FLOAT32 : FLOAT32_CAST }



PUBLIC=0
PRIVATE=1

WORD_SIZE = 0
CHARACTER_SIZE = 0
WORD_TYPE_ID = 0
CHARACTER_TYPE_ID = 0
WORD_TYPENAME = ""
CHARACTER_TYPENAME = ""

def setMachineSizes(word, char):
    global WORD_SIZE, CHARACTER_SIZE, WORD_TYPE, CHARACTER_TYPE, WORD_TYPE_ID, CHARACTER_TYPE_ID
    global WORD_TYPENAME, CHARACTER_TYPENAME
    
    WORD_SIZE = id_to_size_map[word]
    CHARACTER_SIZE = id_to_size_map[char]
    WORD_TYPE_ID = word
    CHARACTER_TYPE_ID = char
    WORD_TYPENAME = id_to_name_map[word]
    CHARACTER_TYPENAME = id_to_name_map[char]
    

class Type(object):
    """The type system has to keep track of several different kinds of types.  One set is the
    'primitive' types composed of integers, floats, null, and strings.  Another set are the more
    complex composite types of arrays and structures.  Orthogonal to this are function types
    and object types.  There are 'builtin' types for messages and lambda expressions.  Finally,
    it is possible to generate a reference to any of these types."""
    
    def __init__(self, name, loc, **kw):
    	if name.startswith("@"):
    		is_ref=True
    		name=name[1:]
    	else:
    		is_ref=False    	
    	
        # Default to an unresolved type
        self.id = UNRESOLVED if name not in type_map else type_map[name]
                
        # Type is or is not a reference
        self.ref = kw.get("is_ref", is_ref)
        
        # Type has no element count, meaning it is not an array or vector.
        self.elem_count = kw.get("elem_count", 0)
        
        # Type is read only
        self.read_only=kw.get("is_read_only", True)
        
        # Type is constant
        self.const = kw.get("is_const", False)
       
        #  The name of the type. For unresolved types this will generally be the
        # name of the type that we will look for.
        self.name = name
        
        #  The scope this type was defined in.  For example, List::Node means
        # that it is a type named Node defined in module List, so this would
        # hold a reference to the List module.
        self.definition_scope = None
        
        #  The location this type was found.
        self.loc = loc
        
        # If this type is castable, this will hold the casting class
        self.castable_to=None
        
    def __str__(self):
    	t =""
    	if self.isConst(): t+="const ";
    	if self.isRef(): t+="@";
    	
    	if self.isStruct():
    		t+=self.struct_def.name
    	elif self.isFunc():
    		t+=self.func_def.name
    	elif self.isObject():
    		t+=self.object_def.name
    	else:
    	   t+=id_to_name_map[self.id]
    	
    	if self.isArray(): t+="[%d]" % (self.elem_count) 
    	if self.isVector(): t+="<%d>"% (self.elem_count)
    	
    	return t
    	
        
    def clone(self):
    	return copy.copy(self)
        
    def encodeFlags(self):
    	"""Returns a binary representation of the type flags suitable for the
    	runtime type information data representation."""
    	flags = 0
    	if self.ref: flags |= 1
    	if self.read_only: flags |= 2
    	if self.const: flags |= 4
    	
    	return flags
    
    def setTypeId(self, id):
    	self.id = id
    	    	
    def setDefinitionScope(self, scope):
    	"Set the definition scope for this type."
    	self.definition_scope = scope
    	
    def setName(self, name):
    	self.name=name
    	
    def hasDefinitionScope(self):
    	return self.definition_scope!=None
        
    def isUnresolved(self):
        """Returns True if this type is unresolved.  This is true
        for auto types and self-referential types."""
                
        return self.id == UNRESOLVED
       
    def isConst(self):
    	return self.const
       
    def isRef(self):
        "Returns true is this is a reference."        
        return self.ref
     
    def isArray(self):
        if self.elem_count != 0 and self.read_only==False:
            return True
        
        return False        
        
    def isVector(self):
        if self.elem_count > 0 and self.read_only==True:
            return True
          
        return False
       
    def isObject(self):
        return self.id == OBJECT
    
    def isFunc(self):
    	return self.id == FUNC
       
    def isStruct(self):
    	return self.id == STRUCT
    
    def isString(self):
        return self.id == STRING or (self.id==STRUCT and self.name=="string_t")
       
    def isType(self):
        return self.id == TYPE
       
    def isIndexable(self):
    	return self.isArray() or self.isString() or self.isVector() 
    
    def isInteger(self):
    	return self.id in INTEGERS
    
    def isFloat(self):
    	return self.id in FLOATS
    
    def isSame(self, ot):
    	"Returns true if this type is the same as the other type."
    	# Special case strings
    	if self.isString() and ot.isString(): return True
    	
    	# Not the same id, not the same type
    	if self.id != ot.id: return False
    	
    	if self.isRef() != ot.isRef(): return False
    	if self.isArray() != ot.isArray(): return False
    	if self.isVector() != ot.isVector(): return False
    	if self.isConst() != ot.isConst(): return False
    	    	
    	if self.isStruct():
    		if self.struct_def != ot.struct_def:
    			return False
    		
    	if self.isFunc():
            if self.func_def != ot.func_def:
                return False
               
        if self.isObject():
            if self.object_def != ot.object_def:
                return False
        
        return True
       
    def isPromotable(self, ot):
    	castable = CAST.get(self.id, None)
    	if castable == None:
    		return False
    	
    	if ot.id in castable:
    		return True
    	
    	return False
    	
       
    def getTypeInfoName(self):
    	if self.id == STRUCT:
    		return "%s_type" % self.struct_def.name
    	
    	if self.id == OBJECT:
            return "%s_type" % self.object_def.name
           
        if self.id == FUNC:
            return "%s_type" % self.func_def.name
           
        return "%s_type" % id_to_name_map[self.id]
       
    def getIndexedType(self):
    	it = self.clone()
    	it.elem_count=0
    	return it
        	
    def makeBoundedArray(self, size):
    	self.elem_count = size
    	self.read_only  = False
    	
    def makeUnboundedArray(self):
    	self.elem_count = -1
    	self.read_only  = False
       
    def makeRef(self):
    	self.ref=True
    	
    def makeConst(self):
    	self.const=True
    	self.read_only=True
       
    def makeFuncRef(self, func_def, environment=None):
        """Makes this type a reference to a function.
        func_def must be supplied and is the definition of the function referenced.
        environment is optional. If true it points to the environment information needed to execute the function"""
        
        self.id  = FUNC
        self.ref = True
        self.func_def = func_def
        self.environment=environment
        
    def makeStruct(self, struct_def, is_ref=False):
        """Makes this a type of struct, specialized to the struct def given. Optionally, make it a 
        reference."""
        
        self.id  = STRUCT
        if is_ref: self.ref = is_ref
        self.struct_def = struct_def
        
    def makeObject(self, object_def, is_ref=False):
        """Makes this a type of object, specialized to the object def given. Optionally, make it a 
        reference."""
        
        self.id  = OBJECT
        if is_ref: self.ref = is_ref
        self.object_def = object_def
        
def new(name, loc, **kw):
	return Type(name, loc, **kw)

def newStruct(st_def, loc, **kw):
	t=Type(st_def.name, loc, **kw)
	t.makeStruct(st_def)			
	return t
	
def newStructRef(st_def, loc, **kw):
	t=newStruct(st_def, loc, **kw)
	t.makeRef()
	return t               
