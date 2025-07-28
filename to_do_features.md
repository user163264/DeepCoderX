# to_do_features

## CRITICAL PERFORMANCE ISSUES (HIGH PRIORITY)

### 🚨 MASSIVE PROMPT OVERHEAD - CLOUD PROVIDERS
**Issue**: Cloud providers (@deepseek, @openai) sending 16,899 characters for simple requests
**Impact**: 
- 4,000-5,000 tokens per request (huge cost)
- Slow response times (24+ seconds)
- Unnecessary project context for simple tasks

**Root Cause**: 
Unified OpenAI handler automatically includes full DeepCoderX project context (14,000+ chars) for every cloud request

**Solution Options**:
1. **Context-Aware Prompting**: Only include project context for complex analysis requests
2. **Semantic Routing**: Simple requests get minimal prompts, complex requests get full context
3. **Context Summarization**: Compress project context to essential information only
4. **Tiered System Prompts**: Different prompt levels based on request complexity

**Priority**: CRITICAL - This affects cost and performance for every cloud request

---

FRAMEWORK:

- config for multiple local LLM's to be loaded.


	-> agentic framework: can you use deepseek's analysis and pass down the instrucions to local Qwen?
	-> can we use llama as a prompt instructor?

- config for API's (multiple models)

@deepseek -> using MCP


All models + API's can use MCP functionality.

Where are the system prompt located?

1 config file for everyhing

requirements.txt -> VENV

Cool startup screen



