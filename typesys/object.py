class Object:
	"""The object is the embodiment of a protocol.  They understand how to send and receive
	various messages.  These messages are essentially function calls.  They are decoupled from
	the low-level machine in that they are looked up by name in the dispatch table."""
	
	def __init__(self, name, loc, docstring=""):
		self.name = name
		self.loc=loc
		self.docstring=""
		
	
		