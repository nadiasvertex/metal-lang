# This module contains various kinds of expressions.  The expressions known how to resolve themselves.

import types

import tests
import typesys.builtins

class Expr(object):
    """Root expression class.  We know that every expression is going to have an op type, 
    at least one input and at least one output.  Expressions generally resolve input expressions from left to right.
    Child nodes are expected to be expressions, with the singular exception of leaf nodes.  These expect their values
    to be dictionaries containing {value_object, type}."""
    def __init__(self, op, loc):
        self.op=op
        self.loc=loc
        self.type = typesys.builtins.NULL_TYPE
        
    def resolve(self, scope, log):
        """Intended to resolve any outstanding references that the expression may have.  The resolve step is not intended
        to do error checking, except by failures in the resolve process of itself."""
         
        return True
    
    def check(self, scope, log):
        """Intended to enforce constraint checks.  Most errors should come from this function."""
        return True
        
    def resolveParentFirst(self):
        "Returns true if the parent op should resolve itself first and provide it's result as input to this child"
        return False
        
    def getNumOutputs(self):
        "Return the number of results.  This should be overridden by other ops if they return multiple values." 
        return 1
    
    def getNumInputs(self):
        "The number of inputs the expression expects.  This should be overridden by other ops if they expect multiple inputs."
        return 1
       
    def getOutputTypebyIndex(self, idx):
        "Gets the type of output number idx.  This should be overriden for types which have multiple outputs."
        return self.getType()
    
    def isConst(self):
        "Returns true if this node is constant. What that means is different for various node types, so it must be overidden."
        return False
       
    def getType(self):
        "By default an operation as a null type.  This must be overridden by more specialized expression types."
        # Try to resolve the type of this expression.
        if self.type==typesys.builtins.NULL_TYPE:
            self.resolveType()
                        
        return self.type
        
    
class Leaf(Expr):
    def __init__(self, op, loc, value):
        Expr.__init__(self, op, loc)
        self.value=value
        
    def isConst(self):
        return self.getType().isConst()
        
    def getNumInputs(self):
        "A leaf has no inputs."
        return 0
       
class Binary(Expr):
    def __init__(self, op, loc, children):
        Expr.__init__(self, op, loc)
        
        self.children=children
        
    def isConst(self):
        return self.children[0].getType().isConst() and self.children[1].getType().isConst()
        
    def resolveType(self):
        "The type from the index is the type of the left side of the operation."
        self.type=self.children[0].getType()
    
    def getNumInputs(self):
        "Binary nodes expect two inputs."
        return 2
       
class Unary(Expr):
    def __init__(self, op, loc, child):
        Expr.__init__(self, op, loc)
        self.child=child
        
    def isConst(self):
        return self.child.getType().isConst()
        
class StructConstructor(Unary):
    def __init__(self, loc, struct_def, initializer):
        Unary.__init__(self,"struct_construct", loc, initializer);
        
        # The definition of the struct.  During parsing this gets passed
        # in as a string which is the name of the struct.                 
        self.struct_def = struct_def
        
    def resolve(self, scope, log):
        if self.child.resolve(scope, log)==False:
            return False
        
        if self.struct_def.isUnresolved():          
          if scope.hasDefinition(self.struct_def, log) == False:
              log.error(self.loc, "Cannot construct an instance of type '%s', no definition for the type was found." % self.struct_def.name)
              return False
          else:
          	  scope.updateType(self.struct_def, log)
                      
        return True
          
    def check(self, scope, log):
        if self.child.check(scope, log)==False:
            return False
        
        init_count = self.child.getNumOutputs()
        member_count = self.struct_def.getMemberCount()
        
        # Make sure we have the right number of arguments
        if init_count > member_count:
            msg = "Too many arguments in the constructor.  The type has %d members, the constructor specified %d." % (init_count, member_count) 
            log.error(self.loc, msg)
            return False
           
        # Make sure the types match.        
        for idx in range(0, init_count):
            t1 = self.struct_def.getMemberTypebyIndex(idx)
            t2 = self.child.getOutputTypebyIndex(idx)             
            if not t1.isSame(t2) and not t2.isPromotable(t1):
                msg="The types of argument %d are not the same between the struct constructor and the struct definition." % idx
                msg+="The definition claims type '%s', while the constructor uses type '%s'" % (str(t1), str(t2))
                log.error(self.loc, msg)
                return False
        
        return True
       
    def checkConst(self, scope, log):
        """Make sure that the elements of the constructor are all constant.  Return False if this is not true, and make
        an error entry in the log."""
        for idx in range(0, self.child.getNumOutputs()):
            t1 = self.child.getOutputTypebyIndex(idx)
            if not t1.isConst():
                msg = "This construct requires that all initializer expressions be constant types.  Argument %d " % idx
                msg+="of type '%s' does not fit this constraint." % str(t1)
                log.error(self.loc, msg)
                return False
            
        return True  
    
    def isConst(self):
        for idx in range(0, self.child.getNumOutputs()):
            t1 = self.child.getOutputTypebyIndex(idx)
            if not t1.isConst():
                return False
            
        return True 
            
                      
class PostFix(Expr):
    def __init__(self, op, loc, child):
        Expr.__init__(self, op, loc)
        self.child=child
        
    def resolveParentFirst(self):
        "Postfix operations expect the parent's value as input."
        return True
    
    def isConst(self):
        return self.child.getType().isConst()
       
class Index(Expr):
    "Performs the indexing operation."
    def __init__(self, loc, source, subscript):
        Expr.__init__(self, "index", loc)
        self.src = source
        self.idx = subscript
        
    def resolveType(self):
        "The type from the index is the type of variable indexed from the source."
        self.type=self.src.getType().getIndexedType()
        
    def check(self, scope, log):
         if self.src.getType().isIndexable():
             #TODO: Check the source type for all operator functions of this type.  Check their input parameter
             # type and see if it matches with this index type.
             pass
            
         else:
           log.error(self.loc, "The type of the source for the index operation is '%s', which is not an indexable type." % self.src.getType().getTypeInfoName())            
        
            
class InitializerList(Leaf):
    """The initializer list expects one or more expressions for use in initializing something.  It is a leaf because it provides
    no operation on the expressions other than grouping.  An initializer list essentially becomes an anonymous type."""  
    def __init__(self, loc, init_leaf, num_elems):
        Leaf.__init__(self, "initializer_list", loc, init_leaf)        
        self.num_outputs = num_elems
        
    def getNumOutputs(self):
        return self.num_outputs
       
    def getOutputTypebyIndex(self, idx):    	
        return self.value[idx].getType() 
    

class LiteralLeaf(Leaf):
    def __init__(self, loc, value, type):
        Leaf.__init__(self, "lit", loc, value)
        self.type = type
        
    def isConst(self):
        return True        

def newString(loc, value):
    "Constructs a new string leaf value."
    return LiteralLeaf(loc, value, typesys.type.new("string_t", loc, is_const=True))      
        
def newInt(loc, value):
    "Constructs a new integer leaf value."
    if value<0 and value>-257:
        return LiteralLeaf(loc, value, typesys.type.new("sint8_t", loc, is_const=True))   
    elif value<256:
        return LiteralLeaf(loc, value, typesys.type.new("uint8_t", loc, is_const=True))        
       
    if value<0 and value>-65537:
        return LiteralLeaf(loc, value, typesys.type.new("sint16_t", loc, is_const=True))   
    elif value<65536:
        return LiteralLeaf(loc, value, typesys.type.new("uint16_t", loc, is_const=True)) 

    if value<0 and value>-4294967297:
        return LiteralLeaf(loc, value, typesys.type.new("sint32_t", loc, is_const=True))   
    elif value<4294967296:
        return LiteralLeaf(loc, value, typesys.type.new("uint32_t", loc, is_const=True)) 
   
    if value<0:
        return LiteralLeaf(loc, value, typesys.type.new("sint64_t", loc, is_const=True))   
    else:
        return LiteralLeaf(loc, value, typesys.type.new("uint64_t", loc, is_const=True))
    
def newFloat(loc, value):
    "Constructs a new floating point leaf value."
    return LiteralLeaf(loc, value, typesys.type.new("float_t", loc, is_const=True))
       
     
   

         