struct trace_context_t
{
    uint32_t level; // The current level at which trace strings will be displayed.        
};

// The global context for trace stuff
private trace_context_t global_trace_ctx;

() rte_trace (uint32_t trace_level, string_t msg) : no-gc no-rte
{
    if (global_trace_ctx.level<=level)
    {
                
    }    
} 