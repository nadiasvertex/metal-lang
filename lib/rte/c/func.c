// Transform a metal function into a c function.

func_definition
${
	
_Bool $(name) (struct $(name)_t *$(name)_args $(func_parms))

$}

func_declaration
${
	
_Bool $(name) (struct $(name)_t *$(name)_args $(func_parms));

$}

func_outbound_parm
${
	$(type) *$(name) = &($(func_name)_args->$(name));	
$}

func_inbound_parm
${
	const $(type) $(name)	
$}	

func_var_init
${
   $!if type_info.is_typed_ref * $!endif $(name) = $(expr);    
$}

func_call
${
    $(name) ($(args));
$}

func_call_pred
${
    if($(name) ($(args)))
    {
        $(on_pass)    
    }
    {
        $(on_fail)
    }
$}

func_call_outbound_parm
${
    &$(func_name)_args
$}

func_call_inbound_parm
${
    $(leaf)
$}

func_pass
${
	return true;
$}

func_fail
${
	return false;
$}
