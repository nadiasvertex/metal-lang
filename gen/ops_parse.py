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

import re
import traceback

op_class = re.compile("bool|uint8|sint8|uint16|sint16|uint32|sint32|uint64|sint64|float32|float64|type|self|default|number|string|struct|signed|unsigned|float|integer")
op_type  = re.compile(r"\.(cast|id_ref|id_val|lit|sizeof|isnull|typeof|typenameof|declaration|init|paren|array|<<=|>>=|<<|>>|<=|>=|==|!=|\+=|-=|\*=|/=|%=|:=|$=|\|\||&&|[-+*%&|^<>/.])")


class OperationsParser:
    def __init__(self):
        self.ops = {}
        
    def get_dictionary(self):
        return self.ops
        
    def process_lines(self, transforms, log):        
        is_cont=False
        dt=""
        
        for t in transforms:
            t=t.strip()
            if len(t)==0 or t.startswith("#"): continue
            
            # Accept blocks to continue long operations.
            if is_cont:
                if t.endswith("$}"):
                    is_cont=False
                    otd[ot_name] = dt + t[:-2]                    
                else:
                    dt+=t+"\n"
                    
                continue
            else:
                dt=""
            
            # Get the operation class
            oc = op_class.match(t)
            if oc==None:                
                log.internal(None, "op class could not be matched for generator. Bad line:")
                log.internal(None, t)                
                return False
                
            oc_name = oc.group()
            otd = self.ops[oc_name] if oc_name in self.ops else {}
            
            # Get the operation type
            t=t[oc.end():]
            ot = op_type.match(t)
            if ot==None:
                log.internal(None, "op type could not be matched for generator. Bad line:")
                log.internal(None, "%s%s" % (oc_name, t))                
                return False
                
            # Bind it into the dictionary
            ot_name=ot.group()[1:]
            dt = t[ot.end():].strip()
            
            if not dt.startswith("${"):
                otd[ot_name]=dt
            else:
                is_cont=True
                dt=dt[2:]
            
            # Update the main dictionary
            self.ops[oc_name] = otd         
            
    def parse(self, filename, log):
        try:
            f=open(filename)
        except:
            log.internal(None, "OperationsParser: could not open file '%s'" % filename)
            log.internal(None, traceback.format_exc())
            return False
            
        lines=f.readlines()
        f.close()           
        
        self.process_lines(lines, log)
        
        return self.ops