class GlobalVar:
	"""This represents a global of any type.  The language definition doesn't currently
	allow global variables per-se, but the compiler has to generate certain constructs
	as global variables."""
	
	def __init__(self, name, type_info, initializer, docstring=""):
		# The name of the constant
		self.name = name
		
		# The typeinfo for the constant
		self.type_info = type_info
		
		# The initializer for the constant
		self.initializer=initializer
		
		# The docstring for the constant
		self.docstring=docstring
		
		# Scope where the constant was defined.
		self.parent_scope=None		
		
	
def new(name, type_info, initializer, docstring=""):
	return GlobalVar(name, type_info, initializer, docstring)