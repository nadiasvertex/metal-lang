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

NONE=-1
TRACE=0
WARNING=1
ERROR=2
FATAL=3
INTERNAL=4

class location:
    "Holds the location of something parsed from an input file using file:line:column notation."
    def __init__(self, file, line, col):
        self.file = file
        self.line = line
        self.col  = col
        
    def __repr__(self):
        return "%s:%s" % (self.line, self.col)

class ErrorLog:
    "An error logging object."
    def __init__(self, err_file):
        self.err_out = err_file
        self.filename = None
        self.warnings = 0
        self.errors   = 0
        self.debug    = True
        self.ignore_level = NONE
        
    def setIgnoreLevel(self, level):
    	"Ignores all logging below or equal to the specified level"
    	self.ignore_level = level
        
    def write(self, hdr, txt):
        mx_size = 78-len(hdr)
        while len(txt):
            if len(txt)>mx_size:
                parts = txt.split()
                tmp = ""
                txt = ""
                for part in parts:
                    if len(txt)==0 and len(part) > mx_size:
                        tmp = part[0:mx_size]
                        txt = "%s " % part[mx_size:]
                        continue                        
                
                    if (len(txt) > 0) or (len(tmp) + len(part) + 1> mx_size):
                        txt += "%s " % part
                    else:
                        tmp += "%s " % part
                        
                print >>self.err_out, "%s %s" % (hdr, tmp)
            else:
                print >>self.err_out, "%s %s" % (hdr, txt)
                txt=""
            
            hdr =  "[        ]"
            
    def traceback(self):
        for line in traceback.extract_stack():
            if line[2] in ["error", "fatal", "internal"]: break
            self.write("[debug   ]", "@%s:%s:%s" % (line[0], line[1], line[2]))                
        
    def trace(self, loc, msg):
    	if self.ignore_level>=TRACE: return        
        self.write("[TRACE   ]", "@%s:%s:%s" % (loc.file, loc, msg))
        
    def warning(self, loc, msg):
    	self.warnings+=1
    	if self.ignore_level>=WARNING: return
    	
        self.write("[WARNING ]", "@%s:%s:%s" % (loc.file, loc, msg))
        
        
    def error(self, loc, msg):
    	self.errors+=1
    	if self.ignore_level>=ERROR: return
    	
        self.write("[ERROR   ]", "@%s:%s:%s" % (loc.file, loc, msg))
        if self.debug: self.traceback();
        
            
    def fatal(self, loc, msg):
    	self.errors+=1
    	if self.ignore_level>=FATAL: return
    	
        self.write("[FATAL   ]", "@%s:%s:%s" % (loc.file, loc, msg))
        if self.debug: self.traceback();
        
        
    def internal(self, loc, msg):
    	self.errors+=1
    	if self.ignore_level>=INTERNAL: return
    	
    	if loc!=None:
        	self.write("[INTERNAL]", "@%s:%s:%s" % (loc.file, loc, msg))
        else:
        	self.write("[INTERNAL]", "%s" % (msg))
        	
        if self.debug: self.traceback();
        

def new(err_file):
	return ErrorLog(err_file)
	            