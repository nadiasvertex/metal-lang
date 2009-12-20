from __future__ import with_statement

import expr
import typesys

ONE=0
ONE_OR_MORE=1
ZERO_OR_MORE=2
ZERO_OR_ONE=3

def any_literal(acceptable, s, log):
    "Matches patterns like [a-zA-Z] or [0-9]"
    lit=""
    cont=True
    loc=s.getLoc()
    
    with s:
       while cont:                
           c=s.peek()           
           if (c!=None) and (c in acceptable):
            lit+=s.read()
           else:
               if len(lit)==0:
                s.rollback()
                return None
               else:
                cont=False
           
    return { "value" : lit, "loc" : loc }
   
def any_literal_chain(chain, s, log):
    "Matches chains of any literal strings. Like [A-Za-z_]+[A-Za-z0-9]*"
    r=[]; idx=-1
    for pattern in chain:
        idx+=1
        d=any_literal(pattern, s, log)
        if d==None and idx==0:
            return None
        elif d==None:
            break
        else:
            r.append(d)
    
    # Append the patterns        
    loc=r[0]["loc"]
    value=""
    for m in r:
        value+=m["value"]
        
    return { "value": value, "loc" : loc }  

def l_keyword(kw, s, log):
    "Matches a keyword, which is just a specific word or group of characters."
    lit=""
    cont=True
    loc=s.getLoc()
    idx=0
    
    with s:
       while cont:
           # If we are done looking, stop            
           if idx>=len(kw):
               return { "value" : lit, "loc" : loc }
               
           c=s.peek()           
           if (c!=None) and (c==kw[idx]):
            lit+=s.read()
            idx+=1
           else:
            # Keyword matches must be entire               
            s.rollback()
            return None
               
           
    

def any_keyword(kw_list, s, log):
    "Matches any keyword in the list."    
    for kw in kw_list:
        result =  l_keyword(kw, s, log)
        if result != None:
            return result
        
        continue
    
    return None

def rule_chain(chain, s, log):
    "Matches chains of rules, but allows more sophisticated matching semantics.  Each rule is a function with a specific signature and return value."
    r=[]; idx=-1
    with s:
        idx=0
        while idx<len(chain):
            matcher, pred = chain[idx]         
            d=matcher(s, log)
            if d==None:
                # Check rules on None return.
                if pred in [ZERO_OR_MORE, ZERO_OR_ONE]:
                    idx+=1
                    continue
                else:
                    s.rollback()
                    return None
            else:
                # Check rules on Something return.
                r.append(d)
                if pred in [ONE, ZERO_OR_ONE]:
                    idx+=1                
                    
    return r

def any_rule(rules, s, log):
    "Matches any of the rules in the list once."
    for rule in rules:        
        d=rule(s,log)
        if d==None:
            continue
        else:
            return d

def l_int(s, log):
    "Matches any decimal integer, returns a dictionary with the matcher signature."
    return any_literal("0123456789", s, log)    
    
    
def l_int_expr(s, log):
    "Matches any decimal integer, returns an integer leaf expression."
    d=l_int(s,log)
    return expr.newInt(d["loc"], int(d["value"])) if d!=None else None

def l_float(s, log):
    "Matches any decimal floating point value, returns a dict with the matcher sig."
    ep = lambda s, log: any_literal(".", s, log)
    
    # Match a rule chain for the float expression
    d = rule_chain([(l_int, ONE), (ep, ONE), (l_int, ZERO_OR_MORE)], s, log) 
    
    # Concatenate the return
    if d!=None:
        sval=""
        for p in d:
            sval+=p["value"]
            
        return { "value":sval, "loc":d[0]["loc"] }
    else:
        return None
    
def l_float_expr(s, log):
    "Matches any floating point expresion, returns a float leaf expression."
    d = l_float(s, log)
    return expr.newFloat(d["loc"], float(d["value"])) if d!= None else None
   
def l_ident(s, log):
    "Matches any valid identifier, returns the identifier name and location dictionary."
    a1 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    a2 = a1 + "0123456789"
    
    d = any_literal_chain([a1, a2], s, log)
    if d==None:
        return None
    
    return { "ident" : d["value"], "loc" : d["loc"] }
   



LONG=1
SHORT=2

# The recognized escape sequences
escapes = { "n" : "\n",
            "t" : "\t",
            "r" : "\r",
            "\\" : "\\",
            "'"  : "'",
            '"'  : '"',
            "b"  : "\b",
            "a"  : "\a",
          }
            
            
            

def l_string(s, log):
    "Match any of the kinds of strings that metal is capable of accepting."
    loc=s.getLoc()
    
    # Decide which kind of string we are matching.
    c = s.peek()
    if c == "'":
        q="'"
    elif c == '"':
        q='"'
    else:
        return None
    
    sval=""
    stype=0
    c=s.read()
    with s:
        tmp1=s.read()
        tmp2=s.peek()
        if tmp1==q and tmp2==q:
            # A long string
            stype=LONG
            tmp2=s.read()
        elif tmp1==q:
            # An empty string
            return {"value": "", "loc":loc}
        else:
            # A short string
            stype=SHORT
            sval=tmp1
            
        # At this point we have established that we are inside a short string or a long string.
        # We now consume tokens accordingly.
        finished=False
        in_escape=False
        while not finished:
            c=s.read()
            if c==None:
                log.error(loc, "Unterminated string literal. The end of the file ocurred inside of a string.  You probably forgot the closing ' or \"" )
                return {"value" : sval, "loc" : loc}
            
            if c==q and in_escape==False:
                # If this is a short string we're done
                if stype==SHORT:
                    return {"value" : sval, "loc" : loc }
                else:
                    #Otherwise we need to do some lookahead to see if this is the end of a long string.
                    tmp1=s.read()
                    tmp2=s.peek()
                    
                    if tmp1 == None or tmp2 == None:
                        # Error - we aren't done with our string and we have and end of file
                        log.error(loc, "Unterminated string literal. The end of the file ocurred inside of a string.  You probably forgot the closing ' or \"" )
                        return {"value" : sval, "loc" : loc}
                          
                    if tmp1==q and tmp2==q:
                        # Yes, this is the end
                        tmp2=s.read()
                        return {"value":sval, "loc":loc}
                    else:
                        # Nope                        
                        sval+=c
                        sval+=tmp1
                        continue 
                    
                
            elif in_escape:
                sval+=escapes[c]
                in_escape=False
                
            else:
                if c=="\\":
                    in_escape=True
                    continue
                else:
                    sval+=c
                
            
def l_string_expr(s, log):
    "Returns a string expression"
    d=l_string(s,log)
    return expr.newString(d["loc"], str(d["value"])) if d!=None else None
     
        