// Imports standard "C" library routines for console I/O into metal using alien functions.

alien "c" puts(string_t in) returns sint32_t out;

con_write_str(string_t data) returns (sint32_t chars_written)
{
	alien puts(data) returns(chars_written);
	
	pass;
}