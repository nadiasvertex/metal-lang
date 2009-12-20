/** Specifies the collection protocol aspect for conformant objects. */
protocol Collection
{
   /** Gets an iterator to the collection, starting at the head. 
    * @output first An iterator pointing to the first item in the collection. 
    * 
    * @pass The iterator was returned.
    * @fail There are no items in this collection. */
   (ref_t first:required)    begin  ();
    
   /** Gets an iterator to the collection, starting at the end. 
    * @output first An iterator pointing to the last item in the collection.
    * 
    * @pass The iterator was returned.
    * @fail There are no items in this collection. */
   (ref_t last:required)     end     ();   
   
   /** Gets a reference to the first item in the collection.  Not an iterator. 
    *
    * @output first_item A reference to the first item in the collection, or null
    * if there are no items in the collection.
    * 
    * @pass The item was returned.
    * @fail There are no items in this collection. */
   (ref_t first_item:required)   front    ();
   
   /** Gets a reference to the last item in the collection.  Not an iterator. 
    *
    * @output last_item A reference to the last item in the collection, or null
    * if there are no items in the collection. 
    * 
    * @pass The item was returned.
    * @fail There are no items in this collection. */
   (ref_t last_item:required)    back    ();
   
   /** Sets whether or not the collection is a uniform collection.  Uniform 
    * collections require all object types stored in the collection to be 
    * identical.  The default is false.  NOTE: If you require a uniform 
    * collection, you must send this message when the collection is empty.
    * trying to send it when the collection has items in it will result in
    * the message failing.
    *
    * @input make_uniform If set to true, the collection will switch to 
    *  uniform mode.  If it's set to false, the collection will switch to
    * non-uniform mode. 
    * 
    * @pass The mode change was sucessful.
    * @fail The mode change failed. */
   ()   setUniformCollection    (bool_t make_uniform);
   
   /** Returns an iterator to the item found, or a null reference if it was not
    * found. For associative collections or ordered collections, this is a fast 
    * way to find items.  At the slowest it will be O(N).  
    *
    * @input key The item to find.
    *
    * @output iterator An iterator to the item, or null.
    * 
    * @pass The item was found.
    * @fail The item was not found. */
   (ref_t iterator:required) find (ref_t key)
   
   /** Inserts the item into the collection.  There is no guarantee where it
    * will be inserted.
    *
    * @input item The item to insert
    * 
    * @output iterator An iterator to the inserted item.  This is only valid if
    * the insertion succeeded.  If it failed this output is indeterminate.
    *
    * @pass The item was inserted, iterator is valid.
    * @fail The item was not inserted, iterator is indeterminate. */
   (ref_t iterator) insert (ref_t item)
   
   /** Deletes the item from the collection.  
    *
    * @input item The item to delete.
    *
    * @pass The item was inserted.
    * @fail The item was not inserted. */
   () delete (ref_t item)
}
