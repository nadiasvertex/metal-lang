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

// Transform a metal function into a c function.

func_definition
${
	
def $(name) ($(func_parms)):

$}

func_declaration
${
	
# declaration: $(name) ($(func_parms))

$}

func_outbound_parm
${
$(name)	
$}

func_inbound_parm
${
$(name)	
$}	 

func_var_init
${
$(name) = $(expr);    
$}

func_call
${
$(name) ()
$}

func_call_pred
${
if($(name) ($(args))):    
    $(on_pass)    
else:    
    $(on_fail)    
$}

func_call_outbound_parm
${
$(func_name)_rv
$}

func_call_inbound_parm
${
$(leaf)
$}

func_pass
${
return True
$}

func_fail
${
return False
$}
