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

import traceback

class FrameworkParser:
    "Parses compiler framework files and stores them in a dictionary for transformation purposes."
    def __init__(self):
        self.d = {}
        self.in_def = False
        self.defname = None
        self.lines=[]
        self.comment = "#"
    
    def get_dictionary(self):
        "Return the dictionary filled with parsing results."
        return self.d
                
    def set_comment(self, c):
        "Set the comment character that the parser will recognize."
        self.comment = c
        
    def process_line(self, line):
        raw_line=line[:-1]
        line=line.strip()
        
        if len(line) == 0:
            return 
        
        # If we see an enter block tag, mark that and eat it.
        if len(line)>=2 and line[:2] == "${":
            self.in_def=True
            line=line[2:]
            
        # If we see an exit block tag, mark that and eat it.
        if len(line)>=2 and line[:2] == "$}":
            self.in_def=False
            if self.defname!=None:
                self.d[self.defname] = "\n".join(self.lines)
                
            self.lines=[]
            self.defname=None
            line=line[2:]
            
        # If there's something left to process, do that.
        if len(line):
            # If it's a comment, process that
            if len(line)>=len(self.comment) and line[:len(self.comment)] == self.comment:
                return
            
            # Otherwise decide what to do with it.  
            if not self.in_def:
                self.defname=line
                return
            else:
                self.lines.append(raw_line)
                
        
    def parse(self, filename, log):
        try:
            f=open(filename)
        except:
            log.internal(None, "FrameworkParser: could not open file '%s'" % filename)
            log.internal(None, traceback.format_exc())
            return False
            
        lines=f.readlines()
        f.close()   
        
        for line in lines:
            self.process_line(line)
            
        return self.d