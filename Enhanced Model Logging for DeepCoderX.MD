Implementation Plan: Enhanced Model Logging for DeepCoderX
Current State Analysis
✅ Existing Logging:

Performance metrics (model loading, generation time)
Routing decisions (intent classification, confidence)
API usage (token counts)
System events and errors
Tool execution summaries

❌ Critical Gaps:

No prompt content logging - Can't see what's being sent to models
No response content logging - Can't see raw model outputs
No semantic analysis details - Can't debug JSON parsing failures
No conversation context tracking - Can't see what history is included
No tool call parameter logging - Can't debug tool execution issues

Implementation Strategy
Phase 1: Core Model Interaction Logging (Priority: HIGH)
1.1 Dual Model Handler Enhancement

File: services/dual_model_handler.py
Changes Needed:

Add prompt logging before self.semantic_parser.model() calls
Add response logging after model generation
Log semantic analysis JSON attempts and failures
Add conversation context logging in _conversation_loop_with_specialist()



1.2 Unified OpenAI Handler Enhancement

File: services/unified_openai_handler.py
Changes Needed:

Log full message history being sent to OpenAI API
Log raw API responses before processing
Log tool call parameters and results
Add conversation context tracking



1.3 GGUF Handler Enhancement (Legacy Support)

File: services/gguf_handler.py
Changes Needed:

Add prompt logging before model calls
Log raw model responses
Track conversation context



Phase 2: Logging Infrastructure (Priority: HIGH)
2.1 Enhanced Logging Utilities

File: utils/logging.py
New Functions Needed:
pythondef log_model_prompt(component: str, model_name: str, prompt: str, interaction_id: str)
def log_model_response(component: str, model_name: str, response: str, duration: float, interaction_id: str)
def log_semantic_analysis(component: str, user_input: str, result: dict, interaction_id: str)
def log_tool_execution_details(component: str, tool_calls: list, results: list, interaction_id: str)


2.2 Structured Log Storage

Directory: logs/model_interactions/
Files:

prompts_YYYYMMDD_HHMMSS.jsonl - All prompts sent to models
responses_YYYYMMDD_HHMMSS.jsonl - All model responses
semantic_YYYYMMDD_HHMMSS.jsonl - Semantic analysis attempts
tools_YYYYMMDD_HHMMSS.jsonl - Tool calls and results
context_YYYYMMDD_HHMMSS.jsonl - Conversation context snapshots



Phase 3: Debug Configuration (Priority: MEDIUM)
3.1 Environment Variables
bashDEEPCODERX_LOG_MODEL_PROMPTS=true        # Enable prompt logging
DEEPCODERX_LOG_MODEL_RESPONSES=true      # Enable response logging  
DEEPCODERX_LOG_SEMANTIC_DETAILS=true     # Enable semantic analysis logging
DEEPCODERX_LOG_TOOL_DETAILS=true         # Enable detailed tool logging
DEEPCODERX_LOG_CONVERSATION_CONTEXT=true # Enable context logging
3.2 Configuration in config_module.py
python# Debug logging configuration
DEBUG_LOGGING = {
    "model_prompts": os.getenv("DEEPCODERX_LOG_MODEL_PROMPTS", "false").lower() == "true",
    "model_responses": os.getenv("DEEPCODERX_LOG_MODEL_RESPONSES", "false").lower() == "true",
    "semantic_details": os.getenv("DEEPCODERX_LOG_SEMANTIC_DETAILS", "false").lower() == "true",
    "tool_details": os.getenv("DEEPCODERX_LOG_TOOL_DETAILS", "false").lower() == "true",
    "conversation_context": os.getenv("DEEPCODERX_LOG_CONVERSATION_CONTEXT", "false").lower() == "true"
}
Specific Implementation Steps
Step 1: Dual Model Handler Modifications
Location: services/dual_model_handler.py
Changes Required:

Add logging to _generate_with_model() method:
python# Before model call
interaction_id = f"{int(time.time())}_{id(self)}"
if config.DEBUG_LOGGING["model_prompts"]:
    log_model_prompt("DualModel", model_name, prompt, interaction_id)

# After model call
if config.DEBUG_LOGGING["model_responses"]:
    log_model_response("DualModel", model_name, response_text, duration, interaction_id)

Add semantic analysis logging in parse_intent() method:
python# Log semantic attempts
if config.DEBUG_LOGGING["semantic_details"]:
    log_debug("DualModel", f"[{interaction_id}] Semantic prompt: {prompt}")
    log_debug("DualModel", f"[{interaction_id}] Raw semantic response: {response_text}")
    if semantic_data:
        log_semantic_analysis("DualModel", user_input, semantic_data, interaction_id)

Add tool execution logging in _execute_tool_calls() method:
pythonif config.DEBUG_LOGGING["tool_details"]:
    log_tool_execution_details("DualModel", tool_calls, tool_results, interaction_id)


Step 2: OpenAI Handler Modifications
Location: services/unified_openai_handler.py
Changes Required:

Add logging to _create_chat_completion() method:
python# Before API call
interaction_id = f"openai_{int(time.time())}_{id(self)}"
if config.DEBUG_LOGGING["model_prompts"]:
    log_model_prompt("OpenAI", self.provider_name, 
                    json.dumps(self.message_history, indent=2), interaction_id)

# After API call
if config.DEBUG_LOGGING["model_responses"]:
    log_model_response("OpenAI", self.provider_name, 
                      response.choices[0].message.content, duration, interaction_id)

Add tool call logging in _handle_native_tool_calls() method:
pythonif config.DEBUG_LOGGING["tool_details"]:
    tool_calls_data = [{"tool": tc.function.name, "args": tc.function.arguments} 
                      for tc in message.tool_calls]
    log_tool_execution_details("OpenAI", tool_calls_data, tool_results, interaction_id)


Step 3: Analysis and Debugging Tools
3.1 Log Analysis Scripts

File: debug/analyze_model_logs.py
Purpose: Analyze prompt/response patterns, find hallucinations, performance issues
Features:

Prompt length analysis
Response time tracking
Semantic analysis failure detection
Tool usage patterns



3.2 Interactive Log Viewer

File: debug/log_viewer.py
Purpose: Real-time log viewing and filtering
Features:

Filter by model, time range, interaction type
Search prompts and responses
Export specific interactions



Configuration and Safety
Environment Setup for Development
bash# Enable comprehensive logging for debugging
export DEEPCODERX_LOG_MODEL_PROMPTS=true
export DEEPCODERX_LOG_MODEL_RESPONSES=true
export DEEPCODERX_LOG_SEMANTIC_DETAILS=true
export DEEPCODERX_LOG_TOOL_DETAILS=true
export DEEPCODERX_LOG_CONVERSATION_CONTEXT=true
Environment Setup for Production
bash# Minimal logging for production (errors only)
export DEEPCODERX_LOG_MODEL_PROMPTS=false
export DEEPCODERX_LOG_MODEL_RESPONSES=false
export DEEPCODERX_LOG_SEMANTIC_DETAILS=false
export DEEPCODERX_LOG_TOOL_DETAILS=false
export DEEPCODERX_LOG_CONVERSATION_CONTEXT=false
Benefits of Implementation

Debug Model Hallucinations: See exact prompts causing inappropriate responses
Optimize Prompts: Analyze what works and what doesn't
Performance Tuning: Track response times and identify bottlenecks
Tool Debugging: See exact parameters and results for tool calls
Context Analysis: Understand how conversation history affects responses
Error Investigation: Full context for debugging failures

Implementation Priority
Week 1:

Phase 1: Core dual model handler logging
Phase 2: Basic logging infrastructure

Week 2:

OpenAI handler logging
Debug configuration system
Basic analysis tools

Week 3:

Advanced analysis scripts
Log viewer tools
Documentation and testing

This implementation will provide comprehensive visibility into model behavior, enabling effective debugging of the current hallucination issues and future model optimization.