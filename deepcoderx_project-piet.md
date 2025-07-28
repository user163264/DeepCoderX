# DeepCoderX Project Overview

This document provides a comprehensive overview of the DeepCoderX application architecture, current status, and capabilities.

**Hardware:** MacBook Air M4, 24GB RAM  
**Sandbox Directory:** `/Users/admin/Documents`  
**Project Directory:** `/Users/admin/Documents/DeepCoderX`  
**Memory File:** `/Users/admin/Documents/DeepCoderX/MEMORY_FOR_NEXT_CHAT.MD`  
**Code Audit:** `/Users/admin/Documents/DeepCoderX/ASSESSMENT_PROTOCOL.md`  
**Documentation:** `/Users/admin/Documents/DeepCoderX/documentation`

## Current Status (July 2025)

**PROJECT STATUS:** PRODUCTION-READY LOCAL CODING ASSISTANT  
**CONFIGURATION:** Unified and optimized (71% complexity reduction achieved)  
**ARCHITECTURE:** Hybrid local-first + cloud-enhanced system  
**MODELS:** Direct GGUF inference with Apple Silicon Metal acceleration  

## High-Level Architecture

DeepCoderX is a command line coding tool capable of running multiple open source models locally at the same time. It has access to APIs for cloud models (DeepSeek, OpenAI, Claude, Gemini...) with API keys stored in a .env file using standard OpenAI JSON structure.

The local models use GGUF files with function calls and prompt templates instead of JSON format. Local models act like agents, able to communicate with each other to solve problems or double-check solutions. The focus is exclusively on coding, with both local and cloud models having access to file system tools.

**Core Mission:** DeepCoderX is the most powerful local coding agent (no API costs), capable of creating complex codebases, complete auditing of large codebases, debugging projects, and creating git repositories.

**Inference Engine:** At the core is the llama-cpp-python inference engine for direct GGUF model execution with Apple Silicon optimization.  
**File System Tools:** Provided by an MCP server running locally for secure sandboxed operations.

## The Command Processing Pipeline

### Current Architecture
```
Command Input → Provider Router → Handler Selection → AI Inference → Tool Execution → Response
                      ↓
        [@deepseek, @local, @openai, default]
```

### Planned Multi-Agent Architecture
**Semantic Parser:** Llama 3.2-3B-Instruct (~1.8GB)

**Why Llama 3.2 for Semantic Parser:**

1. **Speed Critical for Multi-Agent Workflow**
   - 3x faster inference than Qwen models
   - Real-time responsiveness essential for coding assistants
   - Lower latency for rapid tool call generation
   - Better throughput for multi-agent coordination

2. **Coding Context Understanding**
   - Meta's extensive coding dataset training
   - Better understanding of development commands
   - Strong comprehension of coding-related file operations
   - Good grasp of Git/development workflows

3. **Multi-Agent Architecture Benefits**
   - Fast model switching for agent coordination
   - Resource efficiency (more memory for main coding models)
   - M4 can handle multiple models loaded simultaneously

**Agent Specialization Strategy:**
```
┌─ Main Coding Agent: To be determined - Code generation/analysis
├─ Semantic Parser: Llama 3.2-3B - Fast intent classification  
├─ File Agent: Uses semantic parser for file operations
├─ Git Agent: Uses semantic parser for version control
└─ Debug Agent: Uses semantic parser for error analysis
```

**Strategic Architecture:**  
**Hybrid Local-First + Cloud-Enhanced System:**
- Local Semantic Parser: Llama 3.2-3B (instant intent classification)
- Local Main Model: To be determined 
- Cloud APIs: DeepSeek/ChatGPT for complex reasoning and architecture decisions
- Total Local Memory: ~3.3GB (plenty of headroom on 24GB system)

**Multi-Agent Workflow:**
- 90% of requests: Handled by fast local models
- 10% of requests: Routed to cloud APIs for complex tasks
- Routing Logic: Semantic parser determines complexity and routes accordingly
- Privacy-First: Sensitive code operations stay local

**Important Note:** When DeepCoderX is not sure of what the user wants, go directly to 'ask human', don't guess.

## Current Implementation Status

### ✅ Completed Components

**1. Configuration System (Recently Consolidated)**
- **Status:** COMPLETE - 71% complexity reduction achieved
- **Primary Config:** `config_module.py` - Unified configuration class
- **Environment Variables:** `.env` file with legacy compatibility layer  
- **GGUF Prompting:** `gguf_prompts.yaml` - Qwen-optimized strategies
- **Validation:** Explicit validation with clear error messages
- **Backward Compatibility:** Supports both legacy and prefixed variable names

**2. GGUF Handler System (Optimized)**
- **Status:** COMPLETE - Direct inference only
- **Unified Handler:** Single GGUFLocalHandler using llama-cpp-python
- **Apple Silicon Optimization:** Metal GPU acceleration (-1 layers)
- **Progressive Prompting:** 5-level intensity escalation system
- **Qwen Specialization:** Code-focused prompting leveraging Qwen2.5-Coder training
- **Tool Call Pipeline:** 4-stage processing with format validation

**3. Multi-Provider System**
- **Cloud APIs:** DeepSeek, OpenAI with unified OpenAI-compatible handlers
- **Local GGUF:** Direct inference with progressive tool calling
- **Session Management:** Per-provider persistent conversation history
- **Security:** Sandboxed file operations via MCP server

### 🚧 In Progress

**Semantic Parser Integration** (Research completed, implementation pending)
- **Selected Model:** Llama 3.2-3B-Instruct for fast intent classification
- **Alternative:** Phi-3.5 Mini Instruct (3.8B) for accuracy-focused tasks
- **Integration Strategy:** Multi-layer tool call detection with semantic understanding

### 📋 Future Expansion Plan

**Phase 1:** Implement Llama 3.2-3B semantic parser (current)  
**Phase 2:** Research 7B parameter GGUF coding models for large project development

## Current State Management Architecture

### Multi-Layer State System

**1. Command Context State (Per-Session)**
- **File:** `models/session.py`
- **Purpose:** CommandContext class - Central state container for current session
- **State Tracked:**
  - `root_path` & `current_dir`: File system navigation state
  - `mcp_client`: MCP server connection state
  - `sandbox_path`: Security boundary state
  - `status_message`, `model_name`, `user_input`, `response`: UI state
  - `agent`: Current provider/model selection
  - `metadata`: Extensible key-value state storage
  - `abort`, `abort_reason`: Error state management
  - `dry_run`, `auto_confirm`, `debug_mode`: Execution mode flags

**2. Conversation History State (Per-Provider)**
- **File:** `services/gguf_context_manager.py`
- **GGUF Models (Manual Context Management):**
```python
class GGUFContextManager:
    # Persistent conversation state
    messages: List[ConversationMessage]  # Full conversation history
    total_tokens: int                    # Token usage tracking
    max_context_tokens: int              # Context window limits
    
    # Auto-persistence to JSON files
    session_file: Path   "~/.deepcoderx/{provider}_gguf_session.json"
```

**Features:**
- Message Persistence: Conversations saved to JSON files per provider
- Token Management: Automatic token counting and context window management
- Intelligent Truncation: Removes old messages when approaching limits
- Tool Result Integration: Tracks tool calls and their results
- Session Recovery: Loads previous conversations on restart

**3. Project Context State**
- **File:** `services/context_manager.py`
- **Features:**
  - Project Analysis: Deep codebase analysis stored in `.deepcoderx_context.md`
  - File Tree Tracking: Project structure awareness
  - One-time Analysis: Builds comprehensive project understanding

**4. Session Persistence (File-Based)**
- **Location:** `.deepcoderx/` directory
- **Current Session Files:**
```
.deepcoderx/
├── local_gguf_session.json      # GGUF model conversations
├── deepseek_session.json        # DeepSeek conversations  
├── local_session.json           # Local OpenAI conversations
└── .deepcoderx_context.md       # Project context file
```

### State Flow Architecture

**Session Initialization:**
1. Load CommandContext: Initialize per-session state
2. Load Provider Sessions: Restore conversation history for each AI provider
3. Load Project Context: Read project analysis and file structure

**Request Processing:**
1. Route to Handler: Based on provider selection (@deepseek, @local, etc.)
2. Update Context: Add user message to conversation history
3. Execute Command: Run AI inference with full context
4. Save State: Persist conversation and update session files

**State Persistence Triggers:**
- Auto-save: After each AI response
- Manual Clear: `clear` command clears conversation history
- Session End: All handlers save state on exit

## Current Model Configuration

### Local GGUF Models
**Primary Model:** Qwen2.5-Coder 1.5B Instruct (Q8_0 quantization)
- **Location:** `.cache/deepcoderx/models/qwen2.5-coder-1.5b-instruct-q8_0.gguf`
- **Optimization:** Apple Silicon Metal acceleration, 256 batch size
- **Specialization:** Programming tasks with compiler analogy prompting
- **Progressive System:** 5-level intensity escalation for tool calling consistency

**Fallback Model:** Llama 3.2-3B Instruct (Q4_K_S quantization)
- **Purpose:** Speed comparison and semantic parsing preparation
- **Optimization:** 3x faster inference for multi-agent coordination

### Cloud Models
- **DeepSeek V3:** Complex reasoning and architectural decisions
- **OpenAI GPT:** Specialized tasks and enterprise integration
- **Routing Logic:** 90% local, 10% cloud for complex tasks

## State Management Characteristics

### Strengths
✅ **Per-Provider Isolation:** Each AI model maintains separate conversation history  
✅ **Automatic Persistence:** Conversations survive application restarts  
✅ **Token Management:** Intelligent context window handling for GGUF models  
✅ **Tool Integration:** Tool calls and results properly tracked in conversation  
✅ **Project Awareness:** File structure and codebase context maintained  

### Current Limitations
❌ **No Cross-Provider State:** Providers don't share conversation context  
❌ **Manual Token Counting:** Token estimation rather than accurate counting  
❌ **No State Synchronization:** No coordination between different session files  
❌ **Limited Context Sharing:** Project context not automatically integrated with conversations  

### Future Multi-Agent Enhancements Needed
- **Agent Coordination State:** Track which agent handled which requests
- **Shared Context Pool:** Allow agents to access relevant conversation history from other agents
- **Decision History:** Track semantic parser routing decisions
- **Multi-Model Session Management:** Coordinate between local semantic parser and main coding models

The current state management is well-architected for the planned multi-agent expansion - it already supports multiple providers with isolated conversations, which maps perfectly to the multi-agent approach where each agent (semantic parser, main coder, cloud APIs) can maintain separate but coordinated state.

## Recent Major Achievements

### Configuration Consolidation (71% Complexity Reduction)
- **Before:** 5 files, 1,384 lines, complex fallback chains
- **After:** 2 files, ~400 lines, explicit validation
- **Achievement:** Unified configuration with legacy compatibility

### GGUF Handler Optimization
- **Eliminated:** Dual handler complexity (API + direct inference)
- **Implemented:** Single direct inference path with Apple Silicon optimization
- **Result:** Simplified architecture with Metal GPU acceleration

### Startup Error Resolution
- **Fixed:** Environment variable compatibility issues
- **Implemented:** Legacy compatibility layer for seamless migration
- **Result:** Application starts successfully with existing .env files

### Qwen2.5-Coder Integration
- **Implemented:** Progressive prompting system with 5-level intensity escalation
- **Optimized:** Apple Silicon Metal acceleration with specialized settings
- **Result:** Consistent tool calling with code-specialized prompting

This architecture provides a solid foundation for the planned semantic parser integration and multi-agent system, with robust state management and optimized local inference capabilities.