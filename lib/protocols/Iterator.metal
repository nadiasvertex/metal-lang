/** An empty protocol we just use as an aspect tag. */
protocol Iterator {}

/** A protocol for forward iteration of a collection. */
protocol Forward
{
    aspect Iterator;
    
    /** Returns an iterator that points to the next item
     * @output next_item A generic reference to an iterator to the next item. 
     *
     * @pass Returns the next iterator
     * @fail The next_item parameter is indeterminate. */
    (ref_t next_item) next ();          
    
    /** Returns true if the next item in the sequence is valid.
     * @output has_next True if there are more items in the collection, 
     *  false otherwise. 
     *
     * @pass Returns true. There are more items in the sequence.
     * @fail Returns false. This is the last item.
     */
    (bool_t has_next) hasNext(); 
}

/** A protocol for reverse iteration of a collection. */
protocol Reverse
{
    aspect Iterator;
    
    /** Returns an iterator that points to the previous item
     * @output prev_item A generic reference to an iterator to the previous item.
     *
     * @pass Returns the next iterator
     * @fail The next_item parameter is indeterminate. */
    (ref_t prev_item) prev ();   
    
    /** Returns true if the previous item in the sequence is valid.
     * @output has_prev True if there are more items in the collection, 
     *  false otherwise. 
     *
     * @pass Returns true. There are more items in the sequence.
     * @fail Returns false. This is the last item.
     */
    (bool_t has_next) hasPrev();         
}

/** A protocol for bidirectional iteration of a collection. */
protocol Bidirectional
{    
    aspect Forward;
    aspect Reverse;       
}

