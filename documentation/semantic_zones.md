# Semantic Zones Documentation

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Zone Types](#zone-types)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Technical Implementation](#technical-implementation)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

Semantic Zones in DeepCoderX provide **explicit intent signaling** to eliminate ambiguity and improve AI routing efficiency. Instead of the AI having to guess what you want, you can clearly signal your intent using semantic zone triggers.

### What Problem Do Semantic Zones Solve?

**Before Semantic Zones:**
```bash
@deepseek "help me with my config file"
# ❓ Ambiguous - Could mean:
#   • Explain configuration concepts (conversational)
#   • Read the actual config file (tool operation)
#   • Debug config issues (debugging)
```

**After Semantic Zones:**
```bash
@deepseek "explain configuration files"          # → conversational (no tools)
@deepseek "use your tools and read config.py"    # → tool_operation (file access)
@deepseek "debug this config error"              # → debug (troubleshooting)
```

### Key Benefits

- 🎯 **Explicit Intent**: Clear signaling of what you want the AI to do
- ⚡ **Efficient Routing**: Direct routing eliminates guesswork and improves speed
- 🔧 **Tool Precision**: Guaranteed tool usage when you need file operations
- 💬 **Conversation Clarity**: No inappropriate tool calls during explanations
- 📈 **Predictable Behavior**: Consistent responses based on semantic cues

---

## Quick Start

### Basic Usage Pattern

Use semantic zone triggers to clearly indicate your intent:

```bash
# Tool operations - when you want file system access
@deepseek use your tools and [what you want to do]

# Conversational - when you want explanations or chat
@deepseek explain [topic]

# Analysis - when you want code/project analysis
@deepseek analyze [what to analyze]

# Debugging - when you need troubleshooting help
@deepseek debug [what's broken]

# Creative - when you want code generation
@deepseek create [what to build]
```

### Most Common Examples

```bash
# File Operations
@deepseek use your tools and read all Python files
@deepseek use tools to audit the codebase
@deepseek file operations: list directories and check permissions

# Explanations (no tools needed)
@deepseek explain how recursive functions work
@deepseek what is the difference between async and sync?
@deepseek help me understand this error message

# Code Analysis
@deepseek analyze the project structure
@deepseek review this code for best practices
@deepseek summarize what this module does
```

---

## Zone Types

DeepCoderX includes 5 semantic zones, each with specific triggers and behaviors:

### 1. Tool Operation Zone

**Purpose**: Explicit file system operations and codebase manipulation

**Triggers**:
- `use your tools`
- `use tools`
- `file operations`
- `access files`
- `read and...`
- `write and...`
- `audit codebase`
- `check files`

**Behavior**: 
- ✅ **Force routing** to `qwen_coder` specialist
- ✅ **Tools ready** - file system access enabled
- ✅ **High confidence** threshold (0.8)

**Examples**:
```bash
@deepseek use your tools and read config.py
@deepseek use tools to audit this entire codebase
@deepseek file operations: create backup of important files
@deepseek access files and check the project structure
```

### 2. Conversational Zone

**Purpose**: Knowledge-based responses without file operations

**Triggers**:
- `explain`
- `what is`
- `how does`
- `tell me about`
- `help me understand`
- `describe`
- `define`
- `hello`, `hi`, `thanks`

**Behavior**:
- ✅ **Force routing** to `conversation` mode
- ❌ **No tools** - pure knowledge responses
- ✅ **Medium confidence** threshold (0.7)

**Examples**:
```bash
@deepseek explain how machine learning works
@deepseek what is the difference between lists and tuples?
@deepseek help me understand async/await patterns
@deepseek describe the MVC architecture pattern
```

### 3. Analysis Zone

**Purpose**: Code analysis that may require file access

**Triggers**:
- `analyze`
- `review`
- `assess`
- `evaluate`
- `summarize`
- `examine`
- `inspect`
- `study`

**Behavior**:
- 🔄 **Conditional routing** to `qwen_coder` specialist
- ✅ **Tools available** - may access files if needed
- ✅ **Medium confidence** threshold (0.6)

**Examples**:
```bash
@deepseek analyze this project's architecture
@deepseek review the code for potential improvements
@deepseek summarize what this codebase accomplishes
@deepseek examine the database schema design
```

### 4. Debug Zone

**Purpose**: Debugging and troubleshooting assistance

**Triggers**:
- `debug`
- `troubleshoot`
- `fix`
- `error`
- `issue`
- `problem`
- `bug`
- `broken`
- `not working`

**Behavior**:
- 🔄 **Conditional routing** to `qwen_coder` specialist
- ✅ **Tools available** - may access files for debugging
- ✅ **Medium-high confidence** threshold (0.65)

**Examples**:
```bash
@deepseek debug this authentication error
@deepseek fix the broken database connection
@deepseek troubleshoot why the tests are failing
@deepseek this function is not working as expected
```

### 5. Creative Zone

**Purpose**: Code generation and creative development tasks

**Triggers**:
- `create`
- `generate`
- `build`
- `make`
- `develop`
- `implement`
- `design`
- `write`

**Behavior**:
- 🔄 **Conditional routing** to `qwen_coder` specialist
- ✅ **Tools available** - may create files
- ✅ **High confidence** threshold (0.7)

**Examples**:
```bash
@deepseek create a backup script for this project
@deepseek generate a REST API endpoint for users
@deepseek build a simple web scraper
@deepseek write a function to process CSV files
```

---

## Configuration

Semantic zones are configured in a **single source of truth**: `/config_module.py`

### Zone Configuration Structure

```python
SEMANTIC_ZONES = {
    "zone_name": {
        "name": "Human-readable zone name",
        "triggers": ["list", "of", "trigger", "words"],
        "pattern_indicators": ["regex_pattern_1", "regex_pattern_2"],
        "preparation_mode": "context_preparation_type",
        "default_routing": "target_specialist",
        "confidence_boost": 0.3,  # Added to base score
        "tool_ready": True,       # Whether tools are available
        "description": "Zone description"
    }
}
```

### Detection Configuration

```python
ZONE_DETECTION_CONFIG = {
    "confidence_threshold": 0.6,         # Minimum confidence to detect zone
    "pattern_weight": 0.4,               # Weight for regex pattern matches
    "trigger_weight": 0.6,               # Weight for trigger word matches
    "unknown_zone_fallback": "conversational",  # Default when no zone detected
    "multi_zone_strategy": "highest_confidence", # How to handle multiple matches
    "case_sensitive": False,             # Case sensitivity for matching
    "enabled": True                      # Enable/disable zone detection
}
```

### Routing Rules

```python
ZONE_ROUTING_RULES = {
    "zone_name": {
        "force_routing": True,           # Override other routing logic
        "target": "qwen_coder",          # Target specialist
        "override_confidence": False,    # Use zone confidence vs intent confidence
        "minimum_confidence": 0.8        # Minimum confidence for routing
    }
}
```

### Environment Variables

You can control semantic zones behavior with environment variables:

```bash
# Enable/disable semantic zones
export DEEPCODERX_SEMANTIC_ZONES_ENABLED=true

# Debug zone detection
export DEEPCODERX_DEBUG_MODE=true
```

---

## Usage Examples

### Example Session: Project Analysis

```bash
# Start with general explanation (conversational)
@deepseek explain what a REST API is

# Then analyze the current project (analysis)
@deepseek analyze this project's API structure

# Use tools for detailed examination (tool operation)
@deepseek use your tools and read all the API endpoint files

# Debug any issues found (debug)
@deepseek debug why the authentication endpoint returns 500

# Create improvements (creative)
@deepseek create a better error handling middleware
```

### Example Session: Code Review

```bash
# Review without tools first (analysis)
@deepseek review this code for best practices

# Get detailed file analysis (tool operation)
@deepseek use your tools and audit all Python files for code quality

# Understand concepts (conversational)  
@deepseek explain what makes code "maintainable"

# Fix identified issues (debug)
@deepseek fix the circular import problem in the auth module

# Generate improvements (creative)
@deepseek create unit tests for the user management functions
```

### Example Session: Learning

```bash
# Learn concepts (conversational)
@deepseek explain how Docker containers work

# Analyze real examples (analysis)
@deepseek analyze the Docker setup in this project

# Examine actual files (tool operation)
@deepseek use your tools and read the Dockerfile and docker-compose.yml

# Troubleshoot issues (debug)
@deepseek debug why the Docker build is failing

# Create improvements (creative)
@deepseek create a multi-stage Dockerfile for production
```

---

## Advanced Features

### Pattern Matching

Semantic zones support both simple triggers and regex patterns:

```python
# Simple trigger matching
"use your tools" → tool_operation

# Regex pattern matching
r"use\s+(?:your\s+)?tools?\s+and" → tool_operation
r"^(?:explain|describe|what\s+is)" → conversational
```

### Confidence Scoring

Zone detection uses a sophisticated scoring system:

```python
score = (trigger_matches * trigger_weight) + 
        (pattern_matches * pattern_weight) + 
        zone_confidence_boost

# Example scoring:
"use your tools and read config.py"
# trigger_matches: 2 (use, tools) * 0.6 = 1.2
# pattern_matches: 1 ("use\s+(?:your\s+)?tools?\s+and") * 0.4 = 0.4  
# confidence_boost: 0.4
# total_score: 1.2 + 0.4 + 0.4 = 2.0 (capped at 1.0)
```

### Force vs Conditional Routing

**Force Routing** (always routes to target):
- `tool_operation` → Always routes to `qwen_coder`
- `conversational` → Always routes to `conversation`

**Conditional Routing** (routes based on confidence):
- `analysis` → Routes to `qwen_coder` if confidence ≥ 0.6
- `debug` → Routes to `qwen_coder` if confidence ≥ 0.65
- `creative` → Routes to `qwen_coder` if confidence ≥ 0.7

### Multi-Zone Handling

When multiple zones match, the system uses the "highest_confidence" strategy:

```bash
"create and debug this script"
# Matches: creative (confidence: 1.0), debug (confidence: 0.8)
# Winner: creative (higher confidence)
# Result: Routes to qwen_coder for code generation
```

---

## Technical Implementation

### Architecture Overview

```
User Input → Zone Detection → Intent Classification → Zone Routing → Specialist
     ↓              ↓                    ↓                ↓             ↓
"use tools..."  tool_operation    code_generation    qwen_coder    File Operations
```

### Core Components

1. **Zone Detection** (`_detect_semantic_zone()`)
   - Pattern matching with regex
   - Trigger word detection
   - Confidence scoring

2. **Routing Rules** (`_apply_zone_routing_rules()`)
   - Force routing logic
   - Confidence thresholds
   - Override mechanisms

3. **Intent Enhancement** (Enhanced `SemanticIntent` class)
   - Added zone information
   - Zone confidence tracking
   - Routing target override

### Performance Characteristics

- **Zone Detection**: ~1-2ms (pattern matching + trigger checking)
- **Memory Usage**: Minimal (configuration cached on startup)
- **Accuracy**: 100% on test cases (18/18 correct zone detection)
- **Fallback**: Graceful degradation to conversational zone

### Integration Points

Zone detection integrates with:
- **Dual Model Handler**: Primary integration point
- **Semantic Parser**: Enhanced intent classification
- **Configuration System**: Single source of truth
- **Logging System**: Comprehensive debug information

---

## Troubleshooting

### Common Issues

#### 1. Zone Not Detected

**Problem**: Input doesn't trigger expected zone
```bash
@deepseek "look at config.py"  # Doesn't trigger tool_operation
```

**Solution**: Use explicit triggers
```bash
@deepseek "use your tools and read config.py"  # Triggers tool_operation
```

#### 2. Wrong Zone Detected

**Problem**: Input triggers unexpected zone
```bash
@deepseek "analyze what is Python"  # Might trigger analysis instead of conversational
```

**Solution**: Use more specific triggers
```bash
@deepseek "explain what is Python"  # Triggers conversational
```

#### 3. Tools Not Working in Tool Zone

**Problem**: Tool operations fail despite using tool zone
```bash
@deepseek "use your tools and read nonexistent.py"  # File doesn't exist
```

**Solution**: Check file paths and permissions
```bash
@deepseek "use your tools and list files first"  # Verify file existence
```

### Debug Mode

Enable debug mode to see zone detection details:

```bash
export DEEPCODERX_DEBUG_MODE=true
```

Debug output shows:
- Zone detection scores
- Pattern matches
- Routing decisions
- Confidence calculations

Example debug output:
```
DEBUG SemanticZone: Trigger match 'use tools' in zone 'tool_operation' (+0.6)
DEBUG SemanticZone: Pattern match 'use\s+(?:your\s+)?tools?\s+and' in zone 'tool_operation' (+0.4)
INFO  SemanticZone: Detected zone: tool_operation (confidence: 1.00)
INFO  SemanticZone: Force routing zone 'tool_operation' to 'qwen_coder'
```

### Testing Zone Detection

Use the test script to validate zone detection:

```bash
cd /Users/admin/Documents/DeepCoderX
python3 test_semantic_zones.py
```

Expected output:
```
✅ 'use your tools and read config.py' → tool_operation (1.00)
✅ 'explain how functions work' → conversational (1.00)  
✅ 'analyze this project' → analysis (1.00)
Success rate: 18/18 (100.0%)
```

---

## Best Practices

### 1. Use Explicit Triggers

**Good**: Clear semantic zone triggers
```bash
@deepseek use your tools and audit the codebase
@deepseek explain how decorators work
@deepseek analyze the database schema
```

**Avoid**: Ambiguous language
```bash
@deepseek help me with files  # Unclear intent
@deepseek look at this code   # Ambiguous action
```

### 2. Match Intent to Zone

**Tool Operations**: When you need file system access
```bash
@deepseek use your tools and read all configuration files
@deepseek file operations: backup important directories
```

**Conversational**: When you want explanations
```bash
@deepseek explain the MVC design pattern
@deepseek what are the benefits of microservices?
```

**Analysis**: When you want code review/analysis
```bash
@deepseek analyze this API for security vulnerabilities
@deepseek review the code architecture for improvements
```

### 3. Progressive Workflow

Start general, then get specific:

```bash
# 1. Learn concepts
@deepseek explain what automated testing means

# 2. Analyze current state  
@deepseek analyze the existing test coverage in this project

# 3. Examine files
@deepseek use your tools and read all test files

# 4. Debug issues
@deepseek debug why the integration tests are failing

# 5. Create improvements
@deepseek create comprehensive unit tests for the auth module
```

### 4. Combine Zones Effectively

Use different zones for different aspects:

```bash
# Understanding (conversational)
@deepseek explain what makes a good API design

# Assessment (analysis)  
@deepseek analyze this API against best practices

# Investigation (tool operation)
@deepseek use your tools and examine all API endpoint files

# Problem solving (debug)
@deepseek debug the performance issues in the user endpoints

# Implementation (creative)
@deepseek create optimized versions of the slow endpoints
```

### 5. Troubleshooting Strategy

Follow this debugging approach:

```bash
# 1. Understand the error (conversational)
@deepseek explain what a 500 Internal Server Error means

# 2. Analyze the situation (analysis)
@deepseek analyze the error patterns in this application

# 3. Investigate files (tool operation)
@deepseek use your tools and read the error logs and relevant code

# 4. Debug the specific issue (debug)
@deepseek debug why the authentication endpoint returns 500 errors

# 5. Implement the fix (creative)
@deepseek create a robust error handling system for authentication
```

---

## Configuration Reference

### Complete Zone Definitions

Located in `/config_module.py`:

```python
SEMANTIC_ZONES = {
    "tool_operation": {
        "name": "Tool Operation Zone",
        "triggers": [
            "use your tools", "use tools", "file operations", 
            "read and", "write and", "audit codebase", "audit this",
            "use your tools and", "access files", "check files",
            "read file", "write file", "list directory", "run command"
        ],
        "pattern_indicators": [
            r"use\s+(?:your\s+)?tools?\s+and",
            r"file\s+operations?",
            r"audit\s+(?:this\s+)?codebase",
            r"read\s+and\s+\w+",
            r"write\s+and\s+\w+",
            r"access\s+files?",
            r"check\s+files?"
        ],
        "preparation_mode": "file_context_ready",
        "default_routing": "qwen_coder",
        "confidence_boost": 0.4,
        "tool_ready": True,
        "description": "Explicit file system operations and codebase manipulation"
    },
    
    "conversational": {
        "name": "Conversational Zone", 
        "triggers": [
            "explain", "what is", "how does", "tell me about",
            "help me understand", "describe", "define", "meaning of",
            "hello", "hi", "how are you", "thanks", "thank you"
        ],
        "pattern_indicators": [
            r"^(?:explain|describe|what\s+is|how\s+does|tell\s+me)",
            r"help\s+me\s+understand",
            r"meaning\s+of",
            r"define\s+\w+",
            r"^(?:hello|hi|hey|thanks|thank\s+you)"
        ],
        "preparation_mode": "knowledge_mode",
        "default_routing": "conversation", 
        "confidence_boost": 0.3,
        "tool_ready": False,
        "description": "Knowledge-based responses without file operations"
    },
    
    "analysis": {
        "name": "Analysis Zone",
        "triggers": [
            "analyze", "review", "assess", "evaluate", "summarize",
            "examine", "inspect", "study", "investigate"
        ],
        "pattern_indicators": [
            r"^(?:analyze|review|assess|evaluate|summarize)",
            r"examine\s+(?:this\s+)?(?:code|project|file)",
            r"inspect\s+\w+",
            r"study\s+the"
        ],
        "preparation_mode": "hybrid_mode",
        "default_routing": "qwen_coder",
        "confidence_boost": 0.35,
        "tool_ready": True,
        "description": "Code analysis that may require file access"
    },
    
    "debug": {
        "name": "Debug Zone",
        "triggers": [
            "debug", "troubleshoot", "fix", "error", "issue",
            "problem", "bug", "broken", "not working"
        ],
        "pattern_indicators": [
            r"debug\s+\w+",
            r"troubleshoot\s+\w+", 
            r"fix\s+(?:this\s+)?(?:error|issue|bug)",
            r"not\s+working",
            r"broken\s+\w+"
        ],
        "preparation_mode": "debug_context",
        "default_routing": "qwen_coder",
        "confidence_boost": 0.25,
        "tool_ready": True,
        "description": "Debugging and troubleshooting assistance"
    },
    
    "creative": {
        "name": "Creative Zone",
        "triggers": [
            "create", "generate", "build", "make", "develop",
            "implement", "design", "code", "write"
        ],
        "pattern_indicators": [
            r"^(?:create|generate|build|make)\s+",
            r"develop\s+a?\s+\w+",
            r"implement\s+\w+",
            r"design\s+\w+",
            r"write\s+(?:a?\s+)?(?:script|function|class)"
        ],
        "preparation_mode": "creation_mode",
        "default_routing": "qwen_coder", 
        "confidence_boost": 0.3,
        "tool_ready": True,
        "description": "Code generation and creative development tasks"
    }
}
```

### Detection Settings

```python
ZONE_DETECTION_CONFIG = {
    "confidence_threshold": 0.6,
    "pattern_weight": 0.4,
    "trigger_weight": 0.6, 
    "unknown_zone_fallback": "conversational",
    "multi_zone_strategy": "highest_confidence",
    "case_sensitive": False,
    "enabled": True
}
```

### Routing Rules

```python
ZONE_ROUTING_RULES = {
    "tool_operation": {
        "force_routing": True,
        "target": "qwen_coder",
        "override_confidence": True,
        "minimum_confidence": 0.8
    },
    "conversational": {
        "force_routing": True, 
        "target": "conversation",
        "override_confidence": False,
        "minimum_confidence": 0.7
    },
    "analysis": {
        "force_routing": False,
        "target": "qwen_coder",
        "override_confidence": False,
        "minimum_confidence": 0.6
    },
    "debug": {
        "force_routing": False,
        "target": "qwen_coder",
        "override_confidence": False, 
        "minimum_confidence": 0.65
    },
    "creative": {
        "force_routing": False,
        "target": "qwen_coder",
        "override_confidence": False,
        "minimum_confidence": 0.7
    }
}
```

---

## Summary

Semantic Zones provide a powerful way to explicitly communicate your intent to DeepCoderX, resulting in:

- **🎯 Clear Intent Signaling**: No more guessing what you want
- **⚡ Efficient Routing**: Direct routing to the right specialist
- **🔧 Predictable Tool Usage**: Tools used only when explicitly requested
- **💬 Clean Conversations**: No inappropriate tool calls during explanations
- **📈 Better Results**: More accurate and relevant responses

**Quick Reference**:
- `use your tools and...` → File operations
- `explain...` → Knowledge/conversation
- `analyze...` → Code analysis  
- `debug...` → Troubleshooting
- `create...` → Code generation

For support, see the troubleshooting section or enable debug mode to understand zone detection behavior.
