// metal module to c code transform - each module will have this file placed in its top
string_constant
${

const struct $(name)  =  { $(length), "$(value)" };

$}

module
${

#ifndef true
#define true 1
#endif

#ifndef false
#define false 0
#endif

/* ------ RTE TYPES ------ */

/** The string type. */
struct __metal_string_t
{
    $(word_type) length;
    $(char_type) *str;
};

/** The type type. */
struct __metal_type_t
{
    $(word_type) type_id;
    
    struct __metal_string_t type_name;
    
    void *message_table;
};

/** The message type. */
struct __metal_msg_t
{
    $(word_type) nparms;
    
    struct metal_type_t **parm_type;
    void *parms[];
};

/** The message handler function type. */
typedef _Bool (*__metal_msg_handler_fn)(struct __metal_msg_t *);

/** The type for message handlers. */
struct __metal_msg_handler_t 
{
    __metal_msg_handler_fn handler;
    _Bool cached;
};

/* ----------------------- */



/* -- Struct Definitions -- */
$(struct_definitions)
/* ------------------------ */


/* ------ RTE FUNCS ------ */
//extern _Bool __rte_find_handler(__metal_msg_handler_fn *, const void *, const struct __metal_string_t *);
//extern _Bool __rte_insert_handler(void *, const struct __metal_string_t *, __metal_msg_handler_fn *);

extern _Bool __rte_acquire_memory($(word_type)*, $(word_type));
extern _Bool __rte_release_memory($(word_type)*, $(word_type));


/* ------ RTE HELPERS ---- */
static inline void *__rte_acquire_memory_expr($(word_type) size_in_bytes)
{ 
    unsigned int result; 
    
    __rte_acquire_memory(&result, size_in_bytes); 
 
    return (void *)result; 
}
        
/* ----------------------- */

// Returns -1 if s1<s2, 0 if s1==s2, and 1 if s1>s2
static inline int __metal_strcmp(const struct __metal_string_t *s1, const struct __metal_string_t *s2)
{
    $(word_type) index;
       
    if (s1==0 && s2==0) return 0;
    if (s1==0) return -1;
    if (s2==0) return 1;
    
    for(index=0; index<s1->length && index<s2->length; ++index)
    {
        if (s1->str[index] < s2->str[index]) return -1;
        if (s1->str[index] > s2->str[index]) return 1;        
    }
    
    if (s1->length<s2->length) return -1;
    if (s1->length>s2->length) return 1;
    
    return 0;
}    

/* ---------------------------------------------------------------------------------------------------------------------
 * Function Code
 * ---------------------------------------------------------------------------------------------------------------------*/
 
$(func_declarations) 
 
$(func_definitions)

$}