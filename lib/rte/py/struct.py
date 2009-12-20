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

// Transform a metal struct into a C struct

struct
${

class $(name):
$(members)

$}

struct_member
${
	$(tab)$(name) = $(type)
$}

struct_array_member
${
	$(tab)$(name) = $(type) # [$(size)]
$}	
	