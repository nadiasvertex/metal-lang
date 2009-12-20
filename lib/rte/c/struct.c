// Transform a metal struct into a C struct

struct
${

struct $(name)
{
	$(members)
};

$}

struct_member
${
	$(type) $(name)
$}

struct_array_member
${
	$(type) $(name)[$(size)]
$}	
	