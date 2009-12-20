const uint32_t LIBALLOC_MAGIC := 0xc001c0de;
const uint32_t LIBALLOC_DEAD  := 0xdeaddead;

/** A structure found at the top of all system allocated 
 * memory blocks. It details the usage of the memory block.
 */
struct liballoc_major_t
{
	self_t prev;		    //< Linked list information.
	self_t next;		    //< Linked list information.
	uint32_t pages;		    //< The number of pages in the block.
	uint32_t size;		    //< The number of pages in the block.
	uint32_t usage;			//< The number of bytes used in the block.
	liballoc_minor_t &first;	//< A reference to the first allocated memory in the block.	
};

/** This is a structure found at the beginning of all
 * sections in a major block which were allocated by a
 * malloc, calloc, realloc call.
 */
struct liballoc_minor_t
{
	self_t prev;		        //< Linked list information.
	self_t next;		        //< Linked list information.
	liballoc_major_t &block;	//< The owning block. A reference to the major structure.
	uint32_t magic;			    //< A magic number to idenfity correctness.
	uint32_t size; 			    //< The size of the memory allocated. Could be 1 byte or more.
	uint32_t req_size;		    //< The size of memory requested.
};

/** Information that is global to the liballoc instance is kept here. */
struct liballoc_info_t
{
    liballoc_major_t &begin;  //< The first root memory block acquired from the system.
    liballoc_major_t &end;    //< The last memory block acquired from the system.
    
    liballoc_major_t &bestBet;  //< The major with the most free memory.
    uint32_t          bestSize; //< The size of our best bet.
    
    sint32_t pageSize;		//< The size of an individual page. Set up in liballoc_init.
    sint32_t pageCount;		//< The number of pages to request per chunk. Set up in liballoc_init.
    sint64_t allocated;		//< Running total of allocated memory.
    sint64_t inuse;		    //< Running total of used memory.
    
    sint8_t alignment;       //< The alignment for memory blocks.
    
    sint64_t warningCount;		//< Number of warnings encountered
    sint64_t errorCount;		//< Number of actual errors
    sint64_t possibleOverruns;	//< Number of possible overruns
};

// The global liballoc info.
private liballoc_info_t info;

// ***************************************************************

private (liballoc_major_t &new_page:required) allocate_new_page ( uint32_t size ) : no-rte no-gc
{
	uint32_t st;
	uint32_t min_num_pages;
	uint32_t required_size;
	liballoc_major_t &maj;

    // This is how much space is required.
    required_size := size + sizeof(liballoc_major_t) + sizeof(liballoc_minor_t);
    
    // Perfect amount of space?
    min_num_pages := required_size / (info.pageSize) if (required_size % info.pageSize==0) else
          (required_size / (info.pageSize)) + 1; // No, add the buffer.
                  
    // Make sure it's >= the minimum size.
    st := min_num_pages if (st > info.pageCount) else info.pageCount;
        
    // Allocate pages from the system.
    liballoc_alloc_sysmem( st ) : fail system_memory_exhausted;
    
    on system_memory_exhausted    
    {
        mutate info
        {
            warningCount += 1;
        };
        
    	
    	trace(TRC_ERROR, "liballoc: WARNING: liballoc_alloc( %i ) return NULL\n", st );    	
    	fail;	// uh oh, we ran out of memory.
    };
    
    // Convert the new base address to a reference.
    thunk liballoc_alloc_sysmem.base_address to maj;
    
    // Setup new major block
    mutate maj
    {
        prev 	$= null;
        next 	$= null;
        pages 	$= st;
        size 	$= st * info.pageSize;
        usage 	$= sizeof(liballoc_major_t);
        first 	$= null;
    };
    
    // Adjust the allocated memory info.
    mutate info
    {
        allocated += maj.size;
    };
    
//     #ifdef DEBUG
//     printf( "liballoc: Resource allocated %x of %i pages (%i bytes) for %i size.\n", maj, st, maj->size, size );
//     
//     printf( "liballoc: Total memory usage = %i KB\n",  (int)((info.allocated / (1024))) );
//     FLUSH();
//     #endif
        
    new_page := maj;
    pass;
}

(uint32_t block:required) rte_malloc (uint32_t requested_size) : no-gc no-rte
{
	uint32_t size;	
	lock_t lock;
	
	// For alignment, we adjust size so there's enough space to align.
	size := requested_size if (info.alignment==0) else requested_size + info.alignment;
	
	// So, ideally, we really want an alignment of 0 or 1 in order
	// to save space.
	
	if ( size == 0 )
	{
    	mutate info
    	{
        	warningCount += 1;        	
    	};
		
// 		#if defined DEBUG || defined INFO
// 		printf( "liballoc: WARNING: alloc( 0 ) called from %x\n",
// 							__builtin_return_address(0) );
// 		FLUSH();
// 		#endif
        fail;
	}
	
	acquire(lock);

	if ( info.begin == null )
	{
// 		#if defined DEBUG || defined INFO
// 		#ifdef DEBUG
// 		printf( "liballoc: initialization of liballoc " VERSION "\n" );
// 		#endif
// 		atexit( liballoc_dump );
// 		FLUSH();
// 		#endif
			
		// This is the first time we are being used.
		allocate_new_page( size ) : fail init_failed;
		
		mutate info
		{
    	    info.begin $= allocate_new_page.new_page;
		};
		
		on init_failed 
		{		  
// 		  #ifdef DEBUG
// 		  printf( "liballoc: initial l_begin initialization failed\n", p); 
// 		  FLUSH();
// 		  #endif
		  fail;
		};

// 		#ifdef DEBUG
// 		printf( "liballoc: set up first memory major %x\n", l_begin );
// 		FLUSH();
// 		#endif
	};


// 	#ifdef DEBUG
// 	printf( "liballoc: %x PREFIX(malloc)( %i ): ", 
// 					__builtin_return_address(0),
// 					size );
// 	FLUSH();
// 	#endif

	// Now we need to bounce through every major and find enough space....
	
	// Use this as the iterator.
	liballoc_major_t maj;
	
	// Start at the best bet....
	if ( info.bestBet != null)
	{		
		if ( info.bestSize > (size + sizeof(liballoc_minor)))
		{
			maj := info.bestBet;
			signal found_block;
		};
	};	
	
	foreach maj in info
	{   
    	// How much free memory in the block
    	uint32_t maj_size := maj.size - maj.usage;
    	
    	// Hmm.. this one has more memory then our bestBet. Remember!		
	    mutate info if (maj_size > info.bestSize)
	    {
    	    bestBet  $= maj;
    	    bestSize $= maj_size;        	    
	    };
	
		
		// CASE 1:  There is not enough space in this major block.
		if ( maj_size < (size + sizeof(liballoc_minor )) )
		{
// 			#ifdef DEBUG
// 			printf( "CASE 1: Insufficient space in block %x\n", maj);
// 			FLUSH();
// 			#endif
				
			// Another major block next to this one?
			if ( maj.next != info.end ) 
			{
    			// Hop to that one.
				continue;
			};

			// Create a new major block next to this one and...
			allocate_new_page( size ) : fail memory_exhausted;	// next one will be okay.
			maj := allocate_new_page.new_page;
			signal found_block;
			
			// .. fall through to CASE 2 ..
		};


		
		// CASE 2: It's a brand new block.
		if ( maj.first == null )
		{
    		thunk maj + sizeof(liballoc_major_t) to maj.first;
    
    		mutate maj.first
    		{
    			magic 		$= LIBALLOC_MAGIC;
    			prev 		$= null;
    			next 		$= null;
    			block 		$= maj;
    			size 		$= size;
    			req_size 	$= req_size;
			};
			
			mutate maj
			{
    			usage 	+= size + sizeof( liballoc_minor_t );
			} 

			l_inuse += size;
						
			thunk (maj.first) + sizeof(liballoc_minor_t)) to block;

// 			ALIGN( p );
// 			
// 			#ifdef DEBUG
// 			printf( "CASE 2: returning %x\n", p); 
// 			FLUSH();
// 			#endif
			
			pass;
		}

				

		// CASE 3: Block in use and enough space at the start of the block.
		diff =  (uintptr_t)(maj->first);
		diff -= (uintptr_t)maj;
		diff -= sizeof(struct liballoc_major);

		if ( diff >= (size + sizeof(struct liballoc_minor)) )
		{
			// Yes, space in front. Squeeze in.
			maj->first->prev = (struct liballoc_minor*)((uintptr_t)maj + sizeof(struct liballoc_major) );
			maj->first->prev->next = maj->first;
			maj->first = maj->first->prev;
				
			maj->first->magic 	= LIBALLOC_MAGIC;
			maj->first->prev 	= NULL;
			maj->first->block 	= maj;
			maj->first->size 	= size;
			maj->first->req_size 	= req_size;
			maj->usage 			+= size + sizeof( struct liballoc_minor );

			l_inuse += size;

			p = (void*)((uintptr_t)(maj->first) + sizeof( struct liballoc_minor ));
			ALIGN( p );

			#ifdef DEBUG
			printf( "CASE 3: returning %x\n", p); 
			FLUSH();
			#endif
			liballoc_unlock();		// release the lock
			return p;
		}
		

		// CASE 4: There is enough space in this block. But is it contiguous?
		min = maj->first;
		
			// Looping within the block now...
		while ( min != NULL )
		{
				// CASE 4.1: End of minors in a block. Space from last and end?
				if ( min->next == NULL )
				{
					// the rest of this block is free...  is it big enough?
					diff = (uintptr_t)(maj) + maj->size;
					diff -= (uintptr_t)min;
					diff -= sizeof( struct liballoc_minor );
					diff -= min->size; 
						// minus already existing usage..

					if ( diff >= (size + sizeof( struct liballoc_minor )) )
					{
						// yay....
						min->next = (struct liballoc_minor*)((uintptr_t)min + sizeof( struct liballoc_minor ) + min->size);
						min->next->prev = min;
						min = min->next;
						min->next = NULL;
						min->magic = LIBALLOC_MAGIC;
						min->block = maj;
						min->size = size;
						min->req_size = req_size;
						maj->usage += size + sizeof( struct liballoc_minor );

						l_inuse += size;
						
						p = (void*)((uintptr_t)min + sizeof( struct liballoc_minor ));
						ALIGN( p );

						#ifdef DEBUG
						printf( "CASE 4.1: returning %x\n", p); 
						FLUSH();
						#endif
						liballoc_unlock();		// release the lock
						return p;
					}
				}



				// CASE 4.2: Is there space between two minors?
				if ( min->next != NULL )
				{
					// is the difference between here and next big enough?
					diff  = (uintptr_t)(min->next);
					diff -= (uintptr_t)min;
					diff -= sizeof( struct liballoc_minor );
					diff -= min->size;
										// minus our existing usage.

					if ( diff >= (size + sizeof( struct liballoc_minor )) )
					{
						// yay......
						new_min = (struct liballoc_minor*)((uintptr_t)min + sizeof( struct liballoc_minor ) + min->size);

						new_min->magic = LIBALLOC_MAGIC;
						new_min->next = min->next;
						new_min->prev = min;
						new_min->size = size;
						new_min->req_size = req_size;
						new_min->block = maj;
						min->next->prev = new_min;
						min->next = new_min;
						maj->usage += size + sizeof( struct liballoc_minor );
						
						l_inuse += size;
						
						p = (void*)((uintptr_t)new_min + sizeof( struct liballoc_minor ));
						ALIGN( p );


						#ifdef DEBUG
						printf( "CASE 4.2: returning %x\n", p); 
						FLUSH();
						#endif
						
						liballoc_unlock();		// release the lock
						return p;
					}
				}	// min->next != NULL

				min = min->next;
		} // while min != NULL ...



		// CASE 5: Block full! Ensure next block and loop.
		if ( maj->next == NULL ) 
		{
			#ifdef DEBUG
			printf( "CASE 5: block full\n");
			FLUSH();
			#endif

			if ( startedBet == 1 )
			{
				maj = l_begin;
				startedBet = 0;
				continue;
			}
				
			// we've run out. we need more...
			maj->next = allocate_new_page( size );		// next one guaranteed to be okay
			if ( maj->next == NULL ) break;			//  uh oh,  no more memory.....
			maj->next->prev = maj;

		}


		
	}; // foreach maj in info


	
	liballoc_unlock();		// release the lock

	
	trace(TRC_ERROR, "All cases exhausted. No memory available.\n");		
	trace(TRC_WARNING, "liballoc: WARNING: PREFIX(malloc)( %i ) returning NULL.\n" % size);
	
	fail;
	
	on fail
	{
    	release(lock);    	
	}
}