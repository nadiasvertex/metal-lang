block
${
{
$(func_init)
$(var_declarations)    
$(invariant_enter)
 
$(block_top):	



    

	
$(code)

$(block_bottom):
0;
$(invariant_exit)

}
$}

invariant_check
${
	if (!($(result))) return 0;
$}	

var_declaration
${
	$(type) $(name);
$}

var_init
${
	$(left) = $(right)
$}

if_block
${
	
$}

else_if_block
${
	
$}