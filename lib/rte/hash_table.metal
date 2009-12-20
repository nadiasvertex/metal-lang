/** The node type. */
struct ht_node_t
{    
    string_t key;
    uint32_t message_handler;
    
    self_t &next;
};

/** The bucket type. */
struct ht_bucket_t
{        
    ht_node_t &begin;
    ht_node_t &end;
};

/** The table type. */
struct ht_table_t
{
    ht_bucket_t[] buckets;
    
    uint32_t length;
};

(uint32_t hash:required) hash_string32 (string_t str) : no-rte no-gc
{
    uint32_t tmp := 0;
    
    // Reduce the string to a hash
    reduce str to tmp using k, last, count
    {
      last ^= k << (count % 4);        
    };    
    
    pass; 
}

/** Work function to get the bucket.  Must never be called from any other functions than
 * insert_handler and find_handler. */
(ht_bucket_t bucket:required) get_bucket(ht_table_t table, string_t key) : no-rte no-gc
{
    hash_string32(key);
    uint32_t bucket_num := hash_string32.hash % table.length;    
        
    bucket := table.buckets[bucket_num];
    pass;
}

/** Insert a handler for a given message into the hash table. */
() rte_insert_handler(ht_table_t table, string_t key, uint32_t message_handler) : no-rte no-gc

invariant enter
{
    !isnull(table.buckets);
    sizeof(key)>0;  
    message_handler!=0; 
}

{    
    get_bucket(table, key);
    
    auto_t bucket     := get_bucket.bucket;
    
    create new_node of ht_node_t;
        
    // Link the new node to the bucket head.
    mutate new_node
    {
     next $= bucket.head;    
     key  $= key;
     message_handler $= message_handler;
    };
    
    // Make the new node the new bucket head.
    mutate bucket
    {
        head $= new_node;
    };
    
    pass;
}

/** Looks up the handler for a given message in the hash table. */
(uint32_t handler:required) rte_find_handler(ht_table_t table, string_t key) : no-rte no-gc

invariant enter
{    
    sizeof(key)>0;
}

{    
    get_bucket(table, key);
    
    auto_t bucket := get_bucket.bucket;
    
    
    foreach item in bucket
    {
        if (item.key == key)
        {
            handler := item.message_handler;
            pass;            
        };        
    };
    
    fail;
}