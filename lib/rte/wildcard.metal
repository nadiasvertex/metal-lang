wildcard_compare_char(char_t w, char_t t) returns (bool_t match)
	guarded
		when t == w
		{
			match := true;
			pass;
		}
		otherwise
		{
			match := false;
			pass; 			
		}

wildcard_compare_worker(string_t tame_text 		: "The text to match against",
						string_t wild_text 		: "The pattern to match.",
						uint32_t tame_index 	: "The index being considered in the tame string.",
						uint32_t wild_index 	: "The index being considered in the wild string.",
						bool_t   case_sensitive : "If the match should consider case this is true.",
						char_t   terminator     : "The terminating character.") 
							returns (bool_t matched)
	guarded
		when tame_index < tame_text.length &&
			 wild_index < wild_text.length			 
		{
			val t = tame_text[tame_index];
			val w = wild_text[wild_index];
			
			case t of
				terminator -> tame_end,
				otherwise  -> tame_check;
				
			on tame_end
			{
				case w of
					terminator -> match_complete,
					$*		   -> next_wild_char,
					otherwise  -> match_failed;			
			}
			
			on tame_check
			{
				case wildcard_compare_char(w, t) of
					true  -> chars_match,
					false -> chars_dont_match;
			}
			
			on chars_match
			{
				wildcard_compare_worker(tame_text, wild_text,
										tame_index+1, wild_index+1,
										case_sensitive, terminator);
			}
			
			on chars_dont_match : "Check to see if we are matching a wildcard character."
			{
				case w of 
					$* when wild_index+1 < wild_text.length -> check_next_wild_char,
					$* 		  -> match_complete,
					otherwise -> match_failed; 			
			}
			
			on check_next_wild_char
			{
				case wild_text[wild_index+1] of
					t -> swallow_wild_nongreedy,
					otherwise -> next_tame_char;
			}
									
			on next_tame_char
			{
				wildcard_compare_worker(tame_text, wild_text,
										tame_index+1, wild_index,
										case_sensitive, terminator);
														
			}
			
			on swallow_wild_nongreedy : "We checked the character after the wildcard, and it matches the current char. So we accept
										that match INSTEAD OF the wildcard.  This means we increment the tame index once, and the wild index
										twice."
			{
				wildcard_compare_worker(tame_text, wild_text,
										tame_index+1, wild_index+2,
										case_sensitive, terminator);
			}
						
			on match_complete
			{
				matched := true;
				pass;	
			}
			
			on match_failed
			{
				matched := false;
				pass;
			}						
		} 		
		otherwise
		{
			// Check to see which index is out of bounds
			// If it's the tame string and the only thing left in the wild string is a wildcard, then we are good.
			// If it's the wild string, then we have failed to match.
		}			

wildcard_compare(string_t tame_text, string_t wild_text, bool_t case_sensitive_compare, char_t alt_terminator) returns (bool_t matched)
		: " Performs a wildcard comparison"
	require:
		tame_text!=null
		wild_text!=null
{
	matched := matched from wildcard_compare_worker(tame_text, wild_text,
										0, 0,
										case_sensitive_compare, alt_terminator);
										
	pass;
}