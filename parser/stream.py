import err
import copy
        

class Stream:
    "A parse stream"
    
    def __init__(self):
        # The set of streams.
        self.streams=[]
        
        # A "pointer" to the data in the current stream.
        self.data=None 
        
        # The index of the stream we are currently in
        self.index=0
        
        # Pointer to the index of that data that we are in.
        self.at=0
        
        # The current row
        self.row=1
        
        # The current col
        self.col=1
        
        # The stack of contexts.
        self.contexts=[]
        
        # Set to true if we are in a context manager context
        self.in_context_mgr=False
        self.ctx_manager_rollback=False
        
    def __enter__(self):
        "Enter the context manager."
        self.begin_transaction()
        self.in_context_mgr=True
        return self
        
    def __exit__(self, type, value, traceback):
        "When leaving the context, check to see what to do."
        self.in_context_mgr=False
        
        if self.ctx_manager_rollback:
            self.rollback()
        else:
            self.commit()
            
        self.ctx_manager_rollback=False
        

    def merge(self, data, filename=None):
        "Merges the given data into the data stream at our current point in the stream."
        
        # Split the current stream
        tmp=self.data[0:self.at]
        tmp2=self.data[self.at:]
        
        # Duplicate it
        d1=copy.copy(self.streams[self.index])
        d1["data"] = tmp2
        self.streams[self.index]["data"] = tmp
        
        # Generate a new stream tag        
        d2= {"filename" : filename if filename!=None else d1["filename"],
             "data" : data }
        
        # Insert the new tags in reverse order so that the new data is before the split point
        self.streams.insert(self.index, d1)
        self.streams.insert(self.index, d2)
        
    def begin_transaction(self):
        "Save a context onto the stack"        
        self.contexts.append(self.streams, self.data, self.getMarker())
        
    def commit(self):
        "Pop the last save context, committing to the current state"
        if self.in_context_mgr:
            self.ctx_manager_rollback=False
            return 
                   
        self.contexts.pop()
        
    def rollback(self):
        "Restore a saved context from the stack."
        if self.in_context_mgr:
            self.ctx_manager_rollback=True
            return 
        
        ctx=self.contexts[-1]
        self.streams=ctx[0]
        self.data=ctx[1]
        self.setMarker(ctx[2])
        self.contexts.pop()                                    
    
    def getMarker(self):
        "Returns a marker to the current stream pointer."
        return { "index" : self.index, "at" : self.at, "row" : self.row, "col" : self.col}
    
    def setMarker(self, m):
        "Sets the stream position from the marker."
        self.at=m["at"]
        self.row=m["row"]
        self.col=m["col"]
        self.index=m["index"]
        
    def getLoc(self):
    	"Returns a location item."
    	return err.location(self.streams[self.index]["filename"], self.row, self.col)
        
    def peek(self):
        "Reads a single character from the stream w/o consuming it. Returns None if there is nothing left to read."
        at=self.at+1
        
        if at>len(data):
           index=self.index+1
           at=0
            
           if index>len(self.streams):
                  return None
           
        else:
           index=self.index
           
        data=self.streams[index]["data"]
            
        return data[at]
            
        
    def read(self):
        "Reads a single character from the stream. Returns None if there is nothing left to read."
        self.at+=1
        
        if self.at>len(data):
           self.index+=1
           self.at=0
            
           if self.index>len(self.streams):
                  return None
                 
           self.data=self.streams[self.index]["data"]


        if self.data[self.at]=="\n": 
            self.rows+=1
            self.cols=1
        else:
            self.cols+=1
            
        return self.data[self.at]
    
def new():
    return Stream()