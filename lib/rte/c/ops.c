# Defines a transformation between metal operations and C operations

string.== (rte_strcmp($(left), $(right))==0)
string.!= (rte_strcmp($(left), $(right))!=0)
string.<  (rte_strcmp($(left), $(right))<0)
string.>  (rte_strcmp($(left), $(right))>0)
string.<= (rte_strcmp($(left), $(right))<=0)
string.>= (rte_strcmp($(left), $(right))>=0)
string.sizeof $(result)->length
string.isnull ($(result)->length==0)

struct.isnull ($(result)==0)

default.&  $(left) &  $(right)
default.|  $(left) |  $(right)
default.^  $(left) ^  $(right)
default.%  $(left) %  $(right)
default.<< $(left) << $(right)
default.>> $(left) >> $(right)
default.*  $(left) *  $(right)
default./  $(left) /  $(right)
default.+  $(left) +  $(right)
default.-  $(left) -  $(right)
default.!= $(left) != $(right)
default.== $(left) == $(right)
default.<= $(left) <= $(right)
default.>= $(left) >= $(right)
default.>  $(left) >  $(right)
default.<  $(left) <  $(right)

default.&& $(left) && $(right)
default.|| $(left) || $(right)

default.paren ( $(child) )

default.cast ($(new_type))($(old_value))
default.id_ref  (*$(result))
default.id_val  $(result)
default.lit $(result)
default.sizeof sizeof($(child))
