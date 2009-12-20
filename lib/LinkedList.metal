from protocols import List, Iterator

object ListNode
{  
    properties
    {
        ref_t  item := null;
        self_t next := null;   
        self_t prev := null;
    }
   
    /** Setter for item property. */
    set item (ref_t new_item)
    {
        if (new_item == null) fail;
        
        mutate self
        {
            self.item = new_item;            
        }
        
        pass;
    }
    
    /** Getter for item property. */
    (self_t itm:required) get item
    {
        itm := self.item;
    }  
             
    aspect Iterator.Bidirectional;
    
    /*--------------------------------------------------------
       Messages unique to this object.
      --------------------------------------------------------*/
      
   /** Link after node pnode.
    * @input pnode A reference to the node to link after. */
   () linkAfter  (self_t pnode)
   {
       if (pnode==null) fail;
       
       mutate self
       {
           prev = pnode;
           next = pnode.next;
       }
       
       mutate pnode
       {
            next = self;               
       }
       
       if (pnode.next!=null)
       {
           mutate pnode.next
           {
               prev = self;               
           }        
       }      
       
       pass;       
   }
   
   /** Link before node nnode.
    * @input nnode A reference to the node to link before. */
   () linkBefore (self_t nnode)
   {
       if (nnode==null) fail;
       
       mutate self
       {
           prev = nnode.prev;
           next = nnode;
       }
       
       mutate nnode
       {
            prev = self;               
       }
       
       if (nnode.prev!=null)
       {
           mutate nnode.prev
           {
               next = self;               
           }        
       }      
       
       pass;       
   }
   
   /** Unlink this node. */
   () unlink     ()
   {
       if (self.next!=null)
        {
            mutate self.next
            {
                prev = self.prev;   
            }        
        }
        
        if (self.prev!=null)
        {
            mutate self.prev
            {
                next = self.next;   
            }        
        }       
   }     
      
   /*--------------------------------------------------------
       Bidirectional Iterator Messages  
     --------------------------------------------------------*/
   
   next
   {
       self: hasNext() fail atBack;
       
       on atBack
       {
        fail;
       }     
       
       next_item := self.next;
       pass;    
   }
   
   hasNext
   {
       if (self.next != null)
       {
           has_next := true;
           pass;
       }
       
       has_next := false;
       fail;              
   }
   
   prev
   {
       self: hasPrev() fail atFront;
       
       on atFront
       {
        fail;
       }     
       
       prev_item := self.prev;
       pass;    
   }
   
   hasPrev
   {
       if (self.prev != null)
       {
           has_prev := true;
           pass;
       }
       
       has_prev := false;
       fail;              
   }
}


object LinkedList 
{
    properties
    {
        ListNode head;
        ListNode tail;
        
        type_t   uniform_type;
        bool_t   is_uniform;
        
        uint32_t length;        
    }    
    
    aspect List;
    
     /*--------------------------------------------------------
       List Messages  
       --------------------------------------------------------*/
       
     pushBack
     {
        on invariant_enter
        {
            item!=null; 
            self.is_uniform ? typeof(item)==self.uniform_type;            
        }
        
        ListNode node := new ListNode;        
         
        if (self.tail==null && self.head==null) activate listIsEmpty;        
        if (self.tail==self.head) activate listIsOneItem;
        
        activate normalPush;
        
        /** If the list is empty, run this code for insertion. */
        on listIsEmpty
        {               
            mutate self
            {
                head = node;
                tail = node;    
            }  
            
            node: setItem(item);    
            
            pass;            
        }
        
        on listIsOneItem
        {
            mutate self
            {
                tail = node;                
            }           
            
            node: linkAfter(head);
            
            pass;            
        }
        
        on normalPush
        {
            node: linkAfter(tail);
            
            mutate self
            {                
                tail = node;                
            }            
            
            pass;
        }     
        
        on pass
        {        
            back := node;
            
            mutate self
            {
                length+=1;   
            }
        }
        
        pass;           
     }
     
     pushFront
     {
        on invariant_enter
        {
            item!=null;   
        }
        
        ListNode node := new ListNode;        
         
        if (self.tail==null && self.head==null) activate listIsEmpty;        
        if (self.tail==self.head) activate listIsOneItem;
        
        activate normalPush;
        
        /** If the list is empty, run this code for insertion. */
        on listIsEmpty
        {               
            mutate self
            {
                head = node;
                tail = node;    
            }  
            
            node: setItem(item);    
            
            pass;            
        }
        
        on listIsOneItem
        {
            mutate self
            {
                head = node;                
            }           
            
            node: linkBefore(tail);
            
            pass;            
        }
        
        on normalPush
        {
            node: linkBefore(head);
            
            mutate self
            {                
                head = node;                
            }            
            
            pass;
        }        
                
        on pass
        {        
            front := node;
            
            mutate self
            {
                length+=1;   
            }
        }        
                
     }
     
     popBack
     {
        on invariant_enter
        {
            self.tail!=null;   
            self.head!=null;
        }                
         
         ListNode node := tail;
         
         if (self.tail==self.head) activate listIsOneItem;
         
         activate normalPop;
         
         on listIsOneItem
         {             
             mutate self
             {
                head = null;
                tail = null;   
             }
             
             pass;             
         }    
         
         on normalPop
         {            
             mutate self
             {
                 tail = node: next();                                  
             }             
             
             node: unlink();
             
             pass;
         }  
         
        on pass
        {        
            node: destroy();
            
            mutate self
            {
                length-=1;   
            }
        }         
         
         pass;
     }
     
     popFront
     {
        on invariant_enter
        {
            self.tail!=null;   
            self.head!=null;
        }
         
         ListNode node := tail;
         
         if (self.tail==self.head) activate listIsOneItem;
         
         activate normalPop;
         
         on listIsOneItem
         {             
             mutate self
             {
                head = null;
                tail = null;   
             }
             
             pass;             
         }    
         
         on normalPop
         {            
             mutate self
             {
                 head = node: next();                                  
             }             
             
             node: unlink();
             
             pass;
         }
         
        on pass
        {        
            node: destroy();
            
            mutate self
            {
                length-=1;   
            }
        }          
         
        
     }     
     
    
} // end LinkedList object