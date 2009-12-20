#$licensed
#    Copyright 2006-2007 Christopher Nelson
#
#
#
#    This file is part of the metal compiler system.
#
#    The metal compiler is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    The metal compiler is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#$endlicense

import random
import re
import types

if_expr = re.compile(r"\$\!if\s*\((?P<cond>[a-zA-Z0-9._]+)\)", re.MULTILINE)
else_expr = re.compile(r"\$\!else")
endif_expr = re.compile(r"\$\!endif")

# Switch is not currently implemented.  Not sure if it's really needed yet.
switch_expr = re.compile(r"\$\!switch\s*\((?P<cond>[a-zA-Z0-9._]+)\)")
case_expr   = re.compile(r"\$\!case\s+(?P<value>[a-zA-Z0-9_.]+):")
default_expr = re.compile(r"\$\!default:")
endswitch_expr = re.compile(r"\$\!endswitch")
end_expr = re.compile(r"\$\!end")

create_label_expr = re.compile(r"\$\!create_label\s+(?P<name>[a-zA-Z0-9_]+)")
prefix_label_expr = re.compile(r"\$\!prefix_label\s+(?P<name>[a-zA-Z0-9_]+)\s(?P<val>.+?)\s")

filter_expr = re.compile(r"\$\(")
filter_end_expr = re.compile(r"\)")

g_salt=0

class Filter:
    def __init__(self, value):
        self.value=str(value)
        
    def getValue(self):
        return self.value
    
    def prefix(self, prefix_val):
        if not self.value.startswith(prefix_val):
            self.value = prefix_val+self.value
            
    def postfix(self, postfix_val):
        if not self.value.endswith(postfix_val):
            self.value += postfix_val
            
    def strip(self):
        self.value=self.value.strip()    
        
    def slice(self, start, end):
        self.value=self.value[start:end]

def parse_if(text, d,start=0):
    "Parses if/else/endif expressions.  Fully nestable."
            
    m=if_expr.search(text, start)
    if m!=None:        
        start=m.end()
        text=parse_if(text, d, start)
                        
        else_m = else_expr.search(text, start)
        if else_m!=None:
            if_body = text[start:else_m.start()]
            start=else_m.end()
            text=parse_if(text, d, start)
            
        endif_m = endif_expr.search(text, start)
        if endif_m==None:
            return text # Forgot the endif, so don't bother continuing.
        
        if else_m==None:
            if_body=text[start:endif_m.start()]
        else:
            else_body=text[start:endif_m.start()]
            
        # Evaluate the condition
        cond=m.group("cond")
        cond_pass=False
        try:
            value=long(cond.strip())
            if value!=0:
                cond_pass=True
        except ValueError:
            cond=cond.split('.')
            if d.has_key(cond[0].strip()):
                cv=d[cond[0].strip()]
                cond.pop(0)
                
                # Recursively resolve the condition parameter
                for cond_item in cond:
                    if hasattr(cv, cond_item):
                        cv=getattr(cv, cond_item)
                
                # Get it's truth value.        
                if type(cv) == types.StringType:
                    if len(cv): cond_pass=True
                else:
                    if cv: cond_pass=True
                    
        if cond_pass:
            return text[:m.start()] + if_body + text[endif_m.end():]
        else:
            if else_m!=None:
                return text[:m.start()] + else_body + text[endif_m.end():]
            else:
                return text[:m.start()] + text[endif_m.end():]
            
    else: # No if expressions
        return text

def parse_create_label(text, d):
    "Dynamically creates labels in the dictionary."  
    global g_salt
      
    while 1:
        item = create_label_expr.search(text)
        if item==None: break
        
        label_name = item.group("name")
        d[label_name] = "L%s_%s" % (str(random.randint(0,1000)), str(g_salt))
        text = text[:item.start()] + text[item.end():]
        g_salt+=1
        
    return text

def parse_prefix_label(text, d):
    "Prefixes labels with the given value."
    while 1:
        item = prefix_label_expr.search(text)
        if item==None: break
        
        prefix_info = item.group("val")
        label_name  = item.group("name")
        
        v=d[label_name]
        if not v.startswith(prefix_info):
            d[label_name]=prefix_info+v
        
        text = text[:item.start()] + text[item.end():]
        
    return text


def filter(text,d,start=0):
    "Replaces all the $(var) transforms in the file, potentially processing them with filters."    
    while start<len(text):
        m=filter_expr.search(text,start)
        if m==None: break
        
        end_m = filter_end_expr.search(text, m.end())
        if end_m==None: break # error - no end to the filter
        
        filter_text = text[m.end():end_m.start()]
        filter_chain = filter_text.split('|')
        
        key = filter_chain[0].strip()
        filter_chain.pop(0)
        
        #print key, filter_chain
        
        # If the key exists, process it
        if d.has_key(key):
            value=d[key]
            # Now run the filter chain
            f=Filter(value)
            
            for item in filter_chain:
                parts=item.split(" ")
                name=parts[0]; parts.pop(0)
                if hasattr(f, name):
                    fn=getattr(f,name)
                    fn(*parts)
                    
            value=f.getValue()
            text=text[:m.start()]+value+text[end_m.end():]    
        else:
            text=text[:m.start()]+("!!! ERROR %s DOES NOT EXIST IN TRANSFORM DICT !!!"%key)+text[end_m.end():]
                   
        
        start=m.start()
           
         
    return text
    

def preprocess(text, d):
    text = parse_if(text,d)
    text = parse_create_label(text,d)
    text = parse_prefix_label(text,d)
    
    return text                                
  
if __name__=="__main__":
    if_test = """
    $!if (1)
      outer 1
      $!if (1)
         inner 1/1
      $!else
         inner 1/0
      $!endif
    $!else      
      outer 0
      $!if (1)
         inner 0/1
      $!else
         inner 0/0
      $!endif
    $!endif"""
        
    print parse_if(if_test, {})
    
    filter_test="""  
    %type.metal_string_t = type
    {
     $(word_type|prefix %),      ;reference
     $(word_type|postfix %),      ;length
     $(char_type) *     ;str
    };"""
    
    print filter(filter_test, {"word_type" : "i32", "char_type" : "i8 *"})