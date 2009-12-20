"""This module solves expressions at compile time.  It's general intention is to reduce
constant branches to a single node, and also to allow deep checking of constraints.

It requires a way to keep track of contexts.  It also follows all branches to ensure
constraints are not violated."""

import expr
import types
import exceptions

class SolveConstantExpr:
    "Solves a constant expression, returning a single expression as the result."
    def __init__(self, top):
        self.root = top
        
    def _get_value(self, node):
        t=node.getType()
        if t.isString():
            return '"%s"' % node.value
        else:
            return str(node.value)
                
    def _exec_binop(self, loc, op, left, right):
        # Create the code to run
        code = "%s %s %s" % (self._get_value(left), op, self._get_value(right))
        # Evaluate it
        result=eval(code)
        
        # Now create a new leaf expression of the correct type.
        rt = type(result)
        if rt == types.IntType:
            return expr.newInt(loc, result)
        elif rt == types.FloatType:
            return expr.newFloat(loc, result)
        elif rt == types.StringType:
            return expr.newString(loc, result)
        
        raise exceptions.TypeError, "Expected output to be an integer, float, or string."
        
    def _solve_node(self, node):
        """We assume that type checking has already occured, so we don't check for legalities.
        Mostly we assume that the output type will be the same type as the left side of the node."""
        
        n_inputs = node.getNumInputs()
        if n_inputs==2:
            left = self._solve_node(node.children[0])
            right = self._solve_node(node.children[1])
            return self._exec_binop(node.loc, node.op, left, right)
        elif n_inputs==1:
            child = self._solve_node(node.child)
        elif n_inputs==0:
            return node        
        
    def __call__(self):
        "Perform the solving."
        return self._solve_node(self.root)
    
    def _find_const(self, node, depth):
        """Performs the work of finding the tallest constant node."""
        depth+=1
        
        if node.isConst():
            return (node, depth)
        
        n_inputs = node.getNumInputs()
        if n_inputs==2:
            left = _find_const(node.children[0])
            right = _find_const(node.children[1])
            
            if not left: return right
            if not right: return left
            
            if left[1] >= right[1]: return left
            return right
            
        elif n_inputs==1:
            return self._find_const(self.child, depth)
            
        return None
    
    def findConstBranch(self):
        """Returns the root node of the tallest constant branch, or None if there are None.
        This function will not return leaf nodes."""
        return self._find_const(self.root, 0)[0]
    
    def _replace_branch(self, node, old, new):
        """Perform the work of replacing a branch with a different branch."""
        n_inputs = node.getNumInputs()
        if n_inputs==2:
            for idx in len(node.children):
                if node.children[idx] is old: 
                    node.children[idx] = new
                    return
                else:
                    self._replace_branch(node.children[idx], old, new)                            
        elif n_inputs==1:
            if node.child is old:
                node.child = new
            else:
                self._replace_branch(node.child, old, new)
        
    def replaceBranch(self, old, new):
        """Replace a branch with a different branch.  The root cannot be replaced."""
        self._replace_branch(self.root, old, new)                    
    
    def graft(self, scope):
        """Check this tree for places where a constant identifier is used.  Replace the
        constant with the actual value."""  
        pass
        

