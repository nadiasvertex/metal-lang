class Constant:
	"""This represents a constant of any type.  The type associated with this object is
	set to const, read_only, and the initializer is also stored here.  The initializer is
	either a constant expression, or an index into the module's string table.  If the type
	of the constant is string_t then it is the latter, otherwise it is the former."""
	
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
		
		# Force the type info into constant
		self.type_info.makeConst()
		
	
def new(name, type_info, initializer, docstring=""):
	return Constant(name, type_info, initializer, docstring)