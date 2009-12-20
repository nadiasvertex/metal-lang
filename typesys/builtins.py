import const
import err
import globalvar
import struct
import type

loc = err.location("-builtin-", 1, 1)

# The built-in null type
NULL_TYPE = type.Type("null_t", loc)
type.id = type.NULL
type.const = True

STRING_STRUCT = None
TYPE_STRUCT   = None
TYPE_NODE_STRUCT = None

STR_FLAG_CONST = 1

def create_builtin_type_info(m, id):
	name = type.id_to_name_map[id]	
	the_def = globalvar.new("%s_type" % name, 
                                type.newStruct(TYPE_STRUCT, loc),
                                { 
                                 "name"    : m.findStringConstant(name, loc),
                                 "type_id" : str(id)
                                }
                               )
	
	return the_def

def initialize():
    global STRING_STRUCT, TYPE_STRUCT, TYPE_NODE_STRUCT
    global WORD_TYPE, CHARACTER_TYPE, NULL_TYPE
    
    char_array = type.new("%s" % type.CHARACTER_TYPENAME, loc)
    char_array.makeUnboundedArray()
    
    STRING_STRUCT = struct.new("string_t", loc)
    TYPE_STRUCT = struct.new("type_t", loc)
    TYPE_NODE_STRUCT = struct.new("type_node_t", loc)
    
    STRING_STRUCT.addMember("flags", type.new(type.WORD_TYPENAME, loc))
    STRING_STRUCT.addMember("length", type.new(type.WORD_TYPENAME, loc))
    STRING_STRUCT.addMember("data", char_array)
    
    TYPE_STRUCT.addMember("name", type.newStructRef(STRING_STRUCT, loc))
    TYPE_STRUCT.addMember("type_id", type.new("uint8_t", loc))    
    TYPE_STRUCT.addMember("attr_count", type.new(type.WORD_TYPENAME, loc))
    TYPE_STRUCT.addMember("attrs", type.newStructRef(TYPE_NODE_STRUCT, loc))    
    TYPE_STRUCT.addMember("msg_table_size", type.new(type.WORD_TYPENAME, loc))
    TYPE_STRUCT.addMember("msgs", type.newStructRef(TYPE_STRUCT, loc))
    
    TYPE_NODE_STRUCT.addMember("name", type.newStructRef(STRING_STRUCT, loc))
    TYPE_NODE_STRUCT.addMember("type_info", type.newStructRef(TYPE_STRUCT, loc))
    TYPE_NODE_STRUCT.addMember("flags", type.new(type.WORD_TYPENAME, loc))
    
def initialize_module(m):
    global STRING_STRUCT, TYPE_STRUCT, TYPE_NODE_STRUCT
    m.addStruct(STRING_STRUCT)
    m.addStruct(TYPE_STRUCT)
    m.addStruct(TYPE_NODE_STRUCT)
    
    for id in type.INTEGERS:
    	m.addGlobal(create_builtin_type_info(m,id))
    	
    for id in type.FLOATS:
        m.addGlobal(create_builtin_type_info(m,id))
        
    m.addGlobal(create_builtin_type_info(m, type.NULL))
    
def newConstString(name, text, loc):
    global STRING_STRUCT
    return const.new(name, type.newStruct(STRING_STRUCT, loc), text)
    
    
     
