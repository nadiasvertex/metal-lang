from typesys import struct
from expr import solver

class Block:
    """The block is the basic unit of execution ordering.  Blocks are used for resolving local variables.  Blocks may also
    be 'lifted' into a closure with respect to lambda expressions.  In that case a block will still be part of a function."""
    def __init__(self, loc, name=None, doc_string=""):
        # List of basic blocks
        self.code = []
        
        # Location where this is defined
        self.loc = loc
        
        # Set the name of this block
        self.name = name if name else "__block_%s" % self.loc
        
        # List of local variables
        self.vars = struct.new(self.name, self.loc, doc_string)
        
        # List of initializers for defined variables.
        self.init = {}
                
        # The doc string for this block
        self.doc_string = doc_string
        
    def onAdded(self, m):
        "Called when this block is added to a module."        
        self.vars.onAdded(m)
                
    def setScope(self, parent_scope):
        "Sets the resolver scope for this block."
        self.parent_scope = parent_scope
        self.vars.setScope(parent_scope)
        
    def setInitializer(self, name, expr):
        "Sets an initializer expression for the given variable."
        self.init[name] = expr
        
    def simplify(self):
        "Walks the initializer lists and simplifies the branches as much as possible."
        for var in self.init:
            e = self.init[var]
            # Solve expression as far as possible
            if e.isConst():
                cs = solver.SolveConstantExpr(e)
                self.init[var]=cs()                
        
    def addBasicBlock(self,c):
        """A basic block is the most basic level of execution.  A basic block consists of an operation, source location information, and occasionally
        dependent data or other broken out information."""
        self.code.append(c)
        
    def addMember(self, name, type):
        "Add a local variable to this block."
        self.vars.addMember(name, type)
        
    def hasMember(self, name):
        "Returns true if the variable name is in this scope."
        if self.vars.hasMember(name): return True
        if self.parent_scope: return self.parent_scope.hasMember(name)
        return False
        
        
         
def new(self, loc, name=None, doc_string=""):
    return Block(loc, name, doc_string) 
         
    
        
    
    
        