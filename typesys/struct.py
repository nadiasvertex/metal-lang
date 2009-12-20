import builtins
import globalvar
import type

class Struct:
    """A struct is basically a named tuple which is writable.  The members of the data
    structure are ordered and can be of many different types."""
    
    def __init__(self, name, loc, docstring=""):
        # The "typename" of the data structure
        self.name=name
        
        # The dict of names to type information
        self.member_types = {}
        
        # The dict of names to order information
        self.member_index = {}
        
        # The list of member names in order
        self.members = []
        
        # The set of functions that are operators for this type.
        self.operators = []    
        
        # True if this structure is a packed struct.
        self.is_packed = False
        
        # The parent scope for this struct.
        self.parent_scope = None
        
        # The location where this was defined.
        self.loc = loc
        
        self.docstring = docstring
        
    def setScope(self, scope):
        self.parent_scope=scope
        
    def addMember(self, name, type):
        "Appends a new member"
        self.members.append(name)
        self.member_types[name]=type
        self.member_index[name]=len(self.members)-1
        
    def hasMember(self, name):
        "Returns True if this struct has a member with that name."
        if name in self.member_types:
            return True
        
        return False
    
    def getMemberType(self, name):
        return self.member_types[name]
    
    def getMemberIndex(self, name):
        return self.member_index[name]
       
    def getMemberTypebyIndex(self, idx):
    	return self.member_types[self.members[idx]]
    
    def getMemberCount(self):
    	return len(self.members)
       
    def isPacked(self):
    	return self.is_packed
    
    def getTypeType(self):
    	"""Returns a global variable definition of type type_t with the initializer setup
    	to initialize it with type information for this struct's type."""
    	the_def = globalvar.new("%s_type" % self.name, 
							 	type.newStruct(builtins.TYPE_STRUCT, self.loc),
							 	{ 
								 "name"    : "%s_type_name" % self.name,
								 "type_id" : str(type.STRUCT)
								}
							   )
    	return the_def
    
    def getAttrTable(self):
        """Returns a global variable definition of type type_node_t[] with the initializer setup
        to initialize it with type information for this struct's members."""
        
        attr_nodes = []
        for item in self.members:
        	type_info = self.member_types[item]
        	node = {
                     "name"      : self.parent_scope.findStringConstant(item, type_info.loc),
                     "type_info" : type_info.getTypeInfoName(),
                     "flags"     : str(type_info.encodeFlags())                     
                   }
        	
        	attr_nodes.append(node)
        	                
        the_def = globalvar.new("%s_attr_table" % self.name, 
                                type.newStruct(builtins.TYPE_NODE_STRUCT, 
											   self.loc, 
											   elem_count=len(self.members),
											   is_read_only=False),
                                attr_nodes
                               )
        return the_def    
    
    def onAdded(self, m):
    	"Called when the module adds this struct to itself."
    	
    	# Add the RTE stuff in last
        self.addMember("reference_count", type.new(type.WORD_TYPENAME, self.loc))
        self.addMember("previous_copy", type.newStructRef(self, self.loc))
        
    	# Add some constants to make sure that we have the information we need for the type info
        m.addConstant(builtins.newConstString("%s_type_name" % self.name, self.name, self.loc))
        m.addGlobal(self.getTypeType())
               
    def getStructDependencies(self):
         "Returns a list of struct names that this struct depends on."
         
         deps = []         
         for member_name in self.member_types:
            t = self.member_types[member_name]
            if t.isStruct() and t.struct_def!=self:
               deps.append(t.name)
               
         return deps  
       
    def bindMembers(self, log):
        log.trace(self.loc, "binding members for struct %s\n" % self.name)
         
        # Bind the types
        for n in self.member_types:            
            t=self.member_types[n]            
            if t.isUnresolved():            	    
                if self.parent_scope.hasDefinition(t, log):                	
                    if self.parent_scope.updateType(t, log)==False:
                        msg  = "struct '%s' has a member named '%s' whose type name includes a scope " % (self.name, n)
                        msg += "modifier. One or more scope modifiers in type name '%s' cannot be found." % t.name
                        msg += "A previous error message should have informed you which particular scope was the problem.\n"   
                        log.error(self.loc, msg)
                        return False            
                else:
                    msg  = "struct '%s' has a member named '%s' which is supposedly of a type called '%s'.  " % (self.name, n, t.name)
                    msg += "However that type is not a primitive, nor has it been found defined in the current module." 
                    log.error(self.loc, msg)
                    return False
         
        # Add a global variable that contains the results of the attribute table resolution       
        self.parent_scope.addGlobal(self.getAttrTable())
        return True        
       
def new(name, loc, docstring=""):
    return Struct(name,loc)
