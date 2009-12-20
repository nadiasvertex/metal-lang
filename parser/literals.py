from __future__ import with_statement
import err

def any_literal(acceptable, s):
    lit=""
    cont=True
    loc=s.getLoc()
    
    with s:
       while cont:		    	
	       c=s.peek()
	       if c in acceptable:
	        lit+=s.read()
	       else:
	       	if len(lit)==0:
	        	s.rollback()
	        	return None
	        else:
	        	cont=False
	       
    return { "op" : "lit", "value" : lit, "loc" : loc }

def l_int(s):
    d = any_literal("0123456789", s)
    d["type"] = int_type
       

       
      
       
    