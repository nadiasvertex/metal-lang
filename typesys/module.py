import builtins
import types

class Module:
    """A module holds top-level items like structs, objects, functions, and constants.  It
    also holds imports of other modules, which allow it to resolve scoped namespaces."""
    
    def __init__(self, name):        
        # The name of the modules
        self.name = name
        
        # Dictionary of name to module mappings.
        self.imports = {}
        
        # Dictionary of constants.
        self.constants = {}
                
        # Dictionary of structs
        self.structs = {}
        
        # Dictionary of objects
        self.objects = {}
        
        # Dictionary of functions
        self.funcs = {}
        
        # Dictionary of globals
        self.global_vars = {}
        
        #  The string table.  All string constants have their strings added in here.  When the
        # module is transformed, these are generated as native string constants, and then assigned
        # into metal string structures. 
        self.string_table = []
        
        # The string set is used for fast lookup to make sure we don't dupe string constants.
        self.string_set = set()
        
        # The string constant dictionary maps string constants to their constant object defintions.
        self.string_constants = {}
                
        # The docstring for this module
        self.docstring=""
        
        # The location for this module
        self.loc=None
        
    def addRawStringConstant(self, value):
        """Adds a raw string constant into the string table for generation and lookup.  Returns the
        index of the string.  Note that it eliminates duplicates for smaller tables."""
        
        if value not in self.string_set:
            idx=len(self.string_table)
            self.string_table.append(value)
            self.string_set.add(value)
            return idx
        else:
            return self.string_table.index(value)
        
    def addImport(self, the_def):
        self.imports[the_def.name] = the_def
        
    def addConstant(self, the_def):
        if the_def.name == None:
            the_def.name = "__CO%d" % len(self.constants)
            
        self.constants[the_def.name] = the_def
        the_def.parent_scope = self
        
        # Adjust and consume initializer for string constant generation.
        if the_def.type_info.isString():
            if type(the_def.initializer) == types.StringType:
                  self.string_constants[the_def.initializer] = the_def.name                
                  the_def.initializer=self.addRawStringConstant(the_def.initializer)

    def findStringConstant(self, txt, loc=None):
        "Returns the name of the string constant. Adds it if it doesn't exist."
        name = self.string_constants.get(txt,None)
        if name==None:
            self.addConstant(builtins.newConstString(None, txt, loc)) 
            name = self.string_constants[txt]
        
        return name
                  
    def addGlobal(self, the_def):
        self.global_vars[the_def.name] = the_def
        the_def.parent_scope = self                   
    
    def addStruct(self, the_def):
        "Adds a struct to the object."
        self.structs[the_def.name] = the_def
        the_def.parent_scope = self
        
        # Now add type information
        the_def.onAdded(self)         
        
    def addObject(self, the_def):
        self.objects[the_def.name] = the_def
        the_def.parent_scope = self
        
    def addFunc(self, the_def):
        """Adds a function to the module. Also registers the inbound and outbound
        variable struct definitions."""
        self.funcs[the_def.name] = the_def
        the_def.parent_scope = self
        
        # Add in the struct types for the function
        self.addStruct(the_def.getInboundDef())        
        self.addStruct(the_def.getOutboundDef())
        
        # Do any necessary postprocessing
        the_def.onAdded(self)

        
    def getStructDef(self, name):
        return self.structs[name]
    
    def getString(self, idx):
        return self.string_table[idx]
       
    def hasMember(self, name):
        if name in self.global_vars: return True
        if name in self.constants:   return True
        
        return False
    
    def hasGlobal(self, name):
        if name in self.global_vars: return True        
        
    def hasConstant(self, name):
        if name in self.constants: return True
        
    def hasDefinition(self, the_type, log):
    	        # First check for scoped lookup rules
        name=the_type.name
        chain = name.split("::")
        module=self
        if len(chain)>0:
            name=chain.pop(-1)
            # Walk the chain of scopes
            for scope_name in chain:
                if not scope_name in module.imports:
                    log.error(the_type.loc, "The scoped type name '%s' refers to a module '%s' that was not imported." % (the_type.name, scope_name))
                else:
                    module=module.imports[scope_name]
                    
        # Update the definition scope and the name
        the_type.setDefinitionScope(module)
        the_type.setName(name)                        
        
        if name in module.structs: return True    
        if name in module.objects: return True    
        if name in module.funcs: return True    
        if name in module.constants: return True
        if name in module.global_vars: return True
        
        return False
    
    def updateType(self, the_type, log):
        if not the_type.hasDefinitionScope():
            log.internal(the_type.loc, "The type named '%s' has no definition scope.  It should never have gotten here." % the_type.name)
            return False
        
        # Check to make sure that the type is being updated in the right scope
        if the_type.definition_scope!=self:
            return the_type.definition_scope.updateType(the_type, log)            
                
        # Find it and update it.
        name=the_type.name
        if name in self.structs: 
            the_type.makeStruct(self.structs[the_type.name])
            
        elif name in self.objects: 
            the_type.makeObject(self.objects[the_type.name])
        
        elif name in self.funcs: 
            the_type.makeFuncRef(self.funcs[the_type.name])
            
        elif name in self.constants:
            the_type.makeConstant(self.constants[the_type.name])
            
        else:
            log.internal(the_type.loc, "The type named '%s' could not be found during type resolution.  It should never have gotten here." % the_type.name)
            return False
           
        return True
       
    def bindMembers(self, log):
        for name in self.structs:
            self.structs[name].bindMembers(log)
         
    
def new(name):
    return Module(name)
        