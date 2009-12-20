import struct

class Func:
    """Function and messages are the same thing.  The difference is basically only parameters.  A message will have a dictionary
    sent to it with all of the important stuff, while a function will generally have all of it's parameters broken out.  This 
    creates problems for the require and ensure clauses.  Instead of making the programmer do things the hard way, a function 
    will detect that it is a message and generate the correct code to make sure both that the required parameters are present,
    that they have the correct type, and that they match any other constraints the user imposes.
    
    Another important aspect of all functions (be they messages or not) is that they can be lambda expressions.  In fact, 
    sometimes the compiler will synthesize a function specifically to act as a lambda expression.  In that case, the function 
    will be associated with some data.  That data will be in the form of an anonymous struct.  The lambda expression will be 
    passed as a lambda_t, which includes a reference both to the function and to the specific data bound up in the anonymous 
    structure that is associated with the function call.
    
    In order to avoid duplicating code, anonymous structures are created for inbound and outbound parameters.  The functions
    are generated with signatures that take a read-only reference to the struct for inbound, and a write-only reference
    for outboud.
    
    The parameter passing ABI works as follows:  The caller creates storage for inbound and outbound parameters.  The caller
    is responsible for ensuring that the storage remains for the lifetime of the call.
    """
    
    def __init__(self, name, loc, **kw):
        # The name of the function
        self.name = name
        
        # The source location of the function
        self.loc = loc
        
        # The data associated with this function if it's a lambda expression
        self.closure_data = None
        
        # The require invariant code block
        self.require_block=None
        
        # The ensure invariant code block
        self.ensure_block=None
        
        # The mainline code block
        self.mainline_block=None
        
        # Inbound parameter structure
        self.inbound = struct.new(self.getInboundSignature(), loc)
        
        # Outbound parameter structure
        self.outbound = struct.new(self.getOutboundSignature(), loc)
        
        # The parent scope
        self.parent_scope = None
        
    def onAdded(self, m):
        "Called when this function is added to a module."        
        if self.mainline_block: self.mainline_block.onAdded(m)
        if self.require_block: self.require_block.onAdded(m)
        if self.ensure_block: self.ensure_block.onAdded(m)
                
    def setMainlineBlock(self, b):
        "Sets the mainline code block."
        self.mainline_block = b
        b.parent_scope = self
    
    def setRequireBlock(self, b):
        "Sets the require block"
        self.require_block = b
        b.parent_scope = self
        
    def setEnsureBlock(self, b):
        "Sets the require block"
        self.ensure_block = b
        b.parent_scope = self
    
    def getInboundSignature(self):
        "Gets the name of the struct created for inbound variables."
        return "__%s_inbound" % self.name
    
    def getInboundDef(self):
        "Gets the definition of the struct created for inbound variables."
        return self.inbound
                
    def addInboundVar(self, name, type):
        "Adds an inbound variable to this function. Returns False if the name already exists.  True otherwise."
        if self.inbound.hasMember(name):
            return False
        
        self.inbound.addMember(name, type)
        return True
    
    def getOutboundSignature(self):
        "Gets the name of the struct created for outbound variables."    
        return "__%s_outbound" % self.name
    
    def getOutboundDef(self):
        "Gets the definition of the struct created for outbound variables."
        return self.outbound    
        
    def addOutboundVar(self, name, type):
        "Adds an outbound variable to this function. Returns False if the name already exists.  True otherwise."
        if self.outbound.hasMember(name):
            return False
        
        self.outbound.addMember(name, type)
        return True
    
    def hasParm(self, name):
        "Returns True if this function has a parameter of the given name. False otherwise."
        if self.outbound.hasMember(name) or self.inbound.hasMember(name):
            return True
            
    def hasMember(self, name):
        "Returns True if the variable is visible from this context."
        
        if self.hasParm(name): return True
        if self.parent_scope: return self.parent_scope.hasMember(name)               
        return False 
        
        
def new(name, loc, **kw):
    return Func(name, loc, **kw)         
        
        
    
    
        
    
        