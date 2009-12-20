import Iterator
import Collection

/** The base protocol for lists. */
protocol List
{  
    /** Lists are collections, so add all the collection messages here. */
    aspect Collection;     
   
   /** Pushes the item onto the front of the collection.  It becomes the new
    * first item in the collection.
    *
    * @input item The item to insert.
    * 
    * @output iterator An iterator to the inserted item.  This is only valid if
    * the insertion succeeded.  If it failed this output is indeterminate.
    *
    * @pass The item was inserted, iterator is valid.
    * @fail The item was not inserted, iterator is indeterminate. */
   (ref_t front:required) pushFront (ref_t item);
   
   /** Pushes the item onto the back of the collection.  It becomes the new
    * last item in the collection.
    *
    * @input item The item to insert.
    * 
    * @output iterator An iterator to the inserted item.  This is only valid if
    * the insertion succeeded.  If it failed this output is indeterminate.
    *
    * @pass The item was inserted, iterator is valid.
    * @fail The item was not inserted, iterator is indeterminate. */
   (ref_t back:required) pushBack (ref_t item);
   
   /** Pops the item from the front of the collection.  
    *
    * @pass The first item was removed.
    * @fail The collection is empty. */
   () popFront ();
   
   /** Pops the last item from the back of the collection.
    *
    * @pass The last item was removed.
    * @fail The collection is empty. */
   () popBack ();  
   
   /** Inserts the item into the collection after the iterator 'after'.
    * Returns an iterator to the inserted item.
    *
    * @input after The iterator to insert the item after.
    * @input item  The item to insert.
    *
    * @output iterator An iterator to the new item.
    *
    * @pass The item was inserted, iterator is valid.
    * @fail The was not inserted, iterator is indeterminate. */
    (ref_t iterator:required) insertAfter (ref_t after, ref_t item);
    
    /** Inserts the item into the collection before the iterator 'before'.
    * Returns an iterator to the inserted item.
    *
    * @input before The iterator to insert the item before.
    * @input item  The item to insert.
    *
    * @output iterator An iterator to the new item.
    *
    * @pass The item was inserted, iterator is valid.
    * @fail The was not inserted, iterator is indeterminate. */
    (ref_t iterator:required) insertBefore (ref_t before, ref_t item);       
    
}