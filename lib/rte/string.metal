copy(string_t src     : "The source string to copy", 
     uint32_t src_idx : "The source index to copy", 
     +string_t dst    : "The destination string", 
     uint32_t dst_idx : "The destination index to copy to.") returns() 
        : "Copies the source string into the destination string."
     
    require:
        src!=null,
        dst!=null,
        dst_idx<dst.length;
          
  guarded
    when src_idx < src.length
    {
        mutate dst
        {
            data[dst_idx] $= src.data[src_idx]; 
        };
        
        rte_copy_string(src, src_idx+1, dst, dst_idx+1);            
    } 
    otherwise
    {
        pass;
    }

operator "+" string_t(string_t lstr, string_t rstr) returns (string_t result)
    : "Concatenate two strings."
    
    ensure:
        results.length == (lstr.length + rstr.length);
        
{
    var str := string_t(lstr.length + rstr.length);
    
    copy(lstr, 0, str, 0);
    copy(rstr, 0, str, lstr.length);
    
    result := str;
    pass;                         
}

fill_char(+string_t str : "The string to fill", 
          char_t c     : "The character to fill it with", 
          uint32_t start : "Start the fill at this index", 
          uint32_t count : "The number of times to fill it") returns ()
            : "Fill a string with the given character."
    require:
        start<str.length;
        
  guarded
    when count > 0    
    {
        mutate str
        {
            data[start] $= c;
        };
        
        fill_char(str, c, start+1, count-1);   
    }
    otherwise
    {
        pass;
    }

fill_str(+string_t str   : "The string to fill", 
          string_t s     : "The string to fill it with", 
          uint32_t start : "Start the fill at this index", 
          uint32_t count : "The number of times to fill it") returns ()
            : "Fill a string with the given character."
    require:
        start<str.length;
        
  guarded
    when count > 0    
    {
        copy(s, 0, str, start);
        
        fill_char(str, s, start+s.length, count-1);   
    }
    otherwise
    {
        pass;
    }


operator "*" string_t(string_t src, word_t count) returns (string_t result)
{
    val size := count * src.length;
    var str  := string_t(size);
    
    fill_str(str, src, 0, count);
    
    result := str;
    pass;
}

rte_convert_to_string(string_t in_str, uint64_t value, uint8_t base) returns (string_t str)
	require:
		base > 0,
		base < 37;
		
	ensure:
		value == 0;
			
	guarded				
		when value==0
		{
			str:=in_str;
			pass;			
		}
	
		otherwise	
		{	
		    string_t digits;		    	
			uint64_t i := value % base;
			
			digits := "0123456789abcdefghijklmnopqrstuvwxyz";
			rte_convert_to_string(in_str + digits[i] , value / base, base);
		}
		
