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

string.== $(left) == $(right)
string.!= $(left) != $(right)
string.<  $(left) < $(right)
string.>  $(left) > $(right)
string.<= $(left) <= $(right)
string.>= $(left) >= $(right)
string.isnull ($(value)==None)

struct.isnull ($(value)==None)

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

default.&&  $(left) &&  $(right)
default.||  $(left) ||  $(right)

default.paren ( $(child) )

default.cast $(new_type)($(old_value))
default.id_ref  $(value)
default.id_val  $(value)
default.lit $(value)
default.sizeof len($(value))