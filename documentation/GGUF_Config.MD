📁 Core GGUF Components:
Located in /Users/admin/Documents/DeepCoderX/services/

gguf_tool_prompt.py - Prompt builder for tool calling
gguf_tool_parser.py - Parser for extracting tool calls from responses
gguf_context_manager.py - Context and conversation history management
gguf_response_postprocessor.py - Post-processing for stubborn models

📁 Configuration Files:
Located in /Users/admin/Documents/DeepCoderX/config/

gguf_prompting_config.py - Python configuration module
gguf_prompting_config.yaml - YAML configuration file

Let me show you the structure:Fread_fileRequest{
  `head`: 20,
  `path`: `/Users/admin/Documents/DeepCoderX/services/gguf_tool_prompt.py`
}Response"""
GGUF Tool Prompt Builder for DeepCoderX

This module creates prompts with embedded tool calling examples for GGUF models
that don't support native OpenAI-style tool calling. It uses few-shot learning
to teach GGUF models the expected tool call format.

Now uses configurable prompting strategies from config/gguf_prompting_config.yaml
"""

from typing import Dict, Any, List, Optional
import logging
from services.tool_registry import tool_registry, ToolCategory, ToolPermission

# Try to import the configuration system, but provide fallback if not available
try:
    from config.gguf_prompting_config import get_gguf_prompting_config
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = FalseFread_fileRequest{
  `head`: 15,
  `path`: `/Users/admin/Documents/DeepCoderX/config/gguf_prompting_config.py`
}Response"""
GGUF Prompting Configuration Loader

This module loads and manages the GGUF custom prompting enforcement configuration
from the YAML config file, providing easy access to all prompting strategies.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)
Fread_fileRequest{
  `head`: 20,
  `path`: `/Users/admin/Documents/DeepCoderX/config/gguf_prompting_config.yaml`
}Response# GGUF Custom Prompting Enforcement Configuration
# This file contains all the prompting strategies for GGUF models that don't follow instructions well

# ==================================================
# SYSTEM INSTRUCTIONS CONFIGURATION
# ==================================================

system_instructions:
  # Emergency override language for stubborn models
  emergency_override:
    enabled: true
    prefix: "🚨🚨🚨 EMERGENCY OVERRIDE - FOLLOW THESE INSTRUCTIONS EXACTLY 🚨🚨🚨"
    mode_declaration: "YOU ARE IN TOOL-ONLY MODE. YOU MUST NOT GENERATE ANY TEXT RESPONSES."
    format_requirement: "YOU MUST ONLY RESPOND WITH TOOL CALLS IN THIS EXACT FORMAT:"
    format_example: "<tool_call>function_name({\"parameter\": \"value\"})</tool_call>"
  
  # Visual emphasis settings
  visual_emphasis:
    use_emojis: true
    use_caps: true🎯 These are the GGUF prompt config scaffolding files:
1. Services Layer (/services/):

gguf_tool_prompt.py - Main prompt builder with tool examples
gguf_tool_parser.py - Extracts and validates tool calls from responses
gguf_context_manager.py - Manages conversation history and context
gguf_response_postprocessor.py - Handles stubborn models that ignore instructions

2. Configuration Layer (/config/):

gguf_prompting_config.py - Python loader for YAML configuration
gguf_prompting_config.yaml - Comprehensive prompting strategies including:

Emergency override instructions for stubborn models
Visual emphasis settings (emojis, caps)
Tool call format examples
Few-shot learning examples



These files work together to create sophisticated prompts that teach GGUF models how to use tools through few-shot learning and visual emphasis, since GGUF models don't support native OpenAI-style tool calling.