alien "c" open (string_t in, uint32_t in) returns sint32_t out;
alien "c" write (sint32_t in, uint8_t in ptr, sint32_t in) returns uint32_t out;

file_open(string_t filename, uint32_t mode) returns (sint32_t fd:required)
{	
	
	alien open(filename, mode) returns(fd); 
	
	pass;	
}

file_write(uint32_t fd, string_t data, uint32_t size_data) returns (sint32_t bytes_written)

	//invariant enter:
	//	size_data<=sizeof(data),
	//	isnull(data)!=true;
 

{
	
	alien write(fd, data, size_data) returns(bytes_written); 
	
	pass;	
}
