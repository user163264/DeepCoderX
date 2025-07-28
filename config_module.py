"""
Unified Configuration for DeepCoderX

SIMPLIFIED CONFIGURATION SYSTEM - Consolidates 5 files into 1 main config.
Eliminates sys.path manipulation, fallback complexity, and cross-file dependencies.

Design Principles:
- Single source of truth for each setting
- Explicit error handling (no silent degradation)
- Environment-independent behavior
- Direct inference only for GGUF models (no API fallback)
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class DeepCoderXConfig:
    """
    Unified configuration for DeepCoderX application.
    
    Consolidates all configuration into a single class with explicit validation
    and error handling. No fallback complexity or silent degradation.
    """
    
    def __init__(self):
        """Initialize configuration with full validation."""
        self._load_core_settings()
        self._load_provider_settings()
        self._load_gguf_settings()
        self._load_prompting_config()
        self._load_system_prompts()
        self._load_semantic_zones_config()
        self._validate_configuration()
    
    def _load_core_settings(self):
        """Load core application settings."""
        # Core application settings
        self.DEBUG_MODE = self._get_bool_env("DEEPCODERX_DEBUG_MODE", True)
        self.SANDBOX_PATH = self._get_path_env("DEEPCODERX_SANDBOX_PATH", Path.home() / "Documents")
        self.MAX_FILE_SIZE = self._get_int_env("DEEPCODERX_MAX_FILE_SIZE", 1048576)  # 1MB
        self.SCRIPTS_DIR = self._get_str_env("DEEPCODERX_SCRIPTS_DIR", "scripts")
        
        # File system settings
        self.ALLOWED_EXTENSIONS = [
            '.py', '.js', '.ts', '.go', '.rs', '.java', 
            '.txt', '.md', '.json', '.yml', '.yaml', 
            '.html', '.css', '.sh'
        ]
        
        # MCP server settings
        self.MCP_SERVER_HOST = self._get_str_env("DEEPCODERX_MCP_HOST", "localhost")
        self.MCP_SERVER_PORT = self._get_int_env("DEEPCODERX_MCP_PORT", 8080)
        self.MCP_API_KEY = self._get_str_env("DEEPCODERX_MCP_API_KEY", "secure_mcp_key_123")
        
        # Tool execution settings
        self.MAX_TOOL_CALLS = self._get_int_env("DEEPCODERX_MAX_TOOL_CALLS", 50)
        self.COMMAND_TIMEOUT = self._get_int_env("DEEPCODERX_COMMAND_TIMEOUT", 120)
        self.SHORT_COMMAND_TIMEOUT = self._get_int_env("DEEPCODERX_SHORT_COMMAND_TIMEOUT", 30)
        self.API_REQUEST_TIMEOUT = self._get_int_env("DEEPCODERX_API_REQUEST_TIMEOUT", 90)
        self.MCP_CLIENT_TIMEOUT = self._get_int_env("DEEPCODERX_MCP_CLIENT_TIMEOUT", 10)
        
        # Context management
        self.MODEL_CONTEXT_SIZE = self._get_int_env("DEEPCODERX_MODEL_CONTEXT_SIZE", 4096)
        self.HISTORY_TRIM_SIZE = self._get_int_env("DEEPCODERX_HISTORY_TRIM_SIZE", 10)
        self.HISTORY_KEEP_SIZE = self._get_int_env("DEEPCODERX_HISTORY_KEEP_SIZE", 8)
        
        # Enhanced debug logging configuration
        self.DEBUG_LOGGING = {
            "model_prompts": self._get_bool_env("DEEPCODERX_LOG_MODEL_PROMPTS", False),
            "model_responses": self._get_bool_env("DEEPCODERX_LOG_MODEL_RESPONSES", False),
            "semantic_details": self._get_bool_env("DEEPCODERX_LOG_SEMANTIC_DETAILS", False),
            "tool_details": self._get_bool_env("DEEPCODERX_LOG_TOOL_DETAILS", False),
            "conversation_context": self._get_bool_env("DEEPCODERX_LOG_CONVERSATION_CONTEXT", False),
            "interaction_tracking": self._get_bool_env("DEEPCODERX_LOG_INTERACTION_TRACKING", True),
            "structured_storage": self._get_bool_env("DEEPCODERX_LOG_STRUCTURED_STORAGE", True)
        }
    
    def _load_provider_settings(self):
        """Load AI provider settings."""
        self.DEFAULT_PROVIDER = self._get_str_env("DEEPCODERX_DEFAULT_PROVIDER", "dual")
        
        # Provider configurations
        self.PROVIDERS = {
            "local": {
                "name": "Local GGUF Model (Direct Inference)",
                "model_type": "gguf",  # GGUF model type for handler registration
                "enabled": self._get_bool_env("DEEPCODERX_LOCAL_ENABLED", True),
                "supports_tools": True,
                "tool_format": "manual",  # Manual prompting for tool calls
                "max_tool_iterations": self._get_int_env("DEEPCODERX_LOCAL_MAX_TOOL_ITERATIONS", 5),
                "temperature": 0.0,  # Maximum instruction following
                "max_tokens": self._get_int_env("DEEPCODERX_LOCAL_MAX_TOKENS", 2048)
            },
            "dual": {
                "name": "Dual Model System (Llama 3.2-3B + Qwen2.5-Coder)",
                "model_type": "dual",  # Dual model type for handler registration
                "enabled": self._get_bool_env("DEEPCODERX_DUAL_ENABLED", True),
                "supports_tools": True,
                "tool_format": "semantic",  # Semantic parser routing
                "max_tool_iterations": self._get_int_env("DEEPCODERX_DUAL_MAX_TOOL_ITERATIONS", 5),
                "temperature": 0.0,  # Maximum instruction following
                "max_tokens": self._get_int_env("DEEPCODERX_DUAL_MAX_TOKENS", 2048),
                "semantic_parser_model": "Llama-3.2-3B-Instruct-uncensored",
                "code_specialist_model": "qwen2.5-coder-1.5b-instruct",
                "memory_usage": "~5.1GB"
            },
            "deepseek": {
                "name": "DeepSeek Cloud",
                "model_type": "openai",
                "base_url": self._get_str_env("DEEPCODERX_DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
                "api_key": self._get_str_env("DEEPCODERX_DEEPSEEK_API_KEY", None),
                "model": self._get_str_env("DEEPCODERX_DEEPSEEK_MODEL", "deepseek-coder"),
                "enabled": self._get_bool_env("DEEPCODERX_DEEPSEEK_ENABLED", True),
                "supports_tools": True,
                "tool_format": "native",
                "temperature": 0.1,
                "max_tokens": self._get_int_env("DEEPCODERX_DEEPSEEK_MAX_TOKENS", 4096)
            },
            "openai": {
                "name": "OpenAI",
                "model_type": "openai",
                "base_url": None,  # Use default OpenAI endpoint
                "api_key": self._get_str_env("DEEPCODERX_OPENAI_API_KEY", None),
                "model": self._get_str_env("DEEPCODERX_OPENAI_MODEL", "gpt-4"),
                "enabled": self._get_bool_env("DEEPCODERX_OPENAI_ENABLED", False),
                "supports_tools": True,
                "tool_format": "native",
                "temperature": 0.1,
                "max_tokens": self._get_int_env("DEEPCODERX_OPENAI_MAX_TOKENS", 4096)
            }
        }
        
        # Legacy compatibility for DeepSeek
        deepseek_config = self.PROVIDERS["deepseek"]
        self.DEEPSEEK_ENABLED = deepseek_config["enabled"]
        self.DEEPSEEK_API_KEY = deepseek_config["api_key"]
        if deepseek_config["base_url"]:
            self.DEEPSEEK_API_URL = deepseek_config["base_url"] + "/chat/completions"
        else:
            self.DEEPSEEK_API_URL = None
    
    def _load_gguf_settings(self):
        """Load GGUF model settings for direct inference - CACHE DIRECTORY OPTIMIZED."""
        # GGUF model configuration - DIRECT INFERENCE ONLY
        self.GGUF_MODEL_NAME = self._get_str_env("DEEPCODERX_GGUF_MODEL_NAME", "Llama-3.2-3B-Instruct-uncensored")
        self.GGUF_QUANTIZATION = self._get_str_env("DEEPCODERX_GGUF_QUANTIZATION", "gguf")
        
        # MODEL PATH - Use models from .cache directory
        self.GGUF_MODEL_PATH = None
        custom_path = self._get_str_env("DEEPCODERX_GGUF_MODEL_PATH", None)
        
        if custom_path:
            # Use custom path if provided
            self.GGUF_MODEL_PATH = Path(custom_path)
        else:
            # Check for available models in .cache directory
            cache_dir = Path(__file__).parent / ".cache" / "deepcoderx" / "models"
            
            # Priority order for model selection based on actual files in cache
            model_candidates = [
                # Llama models (preferred for semantic parsing)
                "Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf",
                "llama-3.2-3b-instruct.gguf",
                "Llama-3.2-3B-Instruct.gguf",
                
                # Qwen models (fallback for specialized coding)
                "qwen2.5-coder-1.5b-instruct-q8_0.gguf",
                "qwen2.5-coder-1.5b-instruct-q4_k_s.gguf",
                "qwen2.5-coder-1.5b.gguf",
                
                # Custom model name from config
                f"{self.GGUF_MODEL_NAME}.gguf"
            ]
            
            # Find the first available model in cache directory
            for candidate in model_candidates:
                model_path = cache_dir / candidate
                if model_path.exists():
                    self.GGUF_MODEL_PATH = model_path
                    logger.info(f"Using model from cache: {self.GGUF_MODEL_PATH}")
                    # Update model name to match found model
                    self.GGUF_MODEL_NAME = candidate.replace('.gguf', '')
                    break
            
            # If no model found in cache, try fallback search
            if not self.GGUF_MODEL_PATH:
                fallback_search_paths = [
                    # Standard cache locations
                    Path.home() / ".cache" / "deepcoderx" / "models",
                    Path.home() / ".cache" / "lm-studio" / "models",
                    Path.home() / ".cache" / "huggingface" / "hub", 
                    
                    # User directories
                    Path.home() / "models",
                    Path("./models"),
                    
                    # Legacy location
                    Path("/Users/admin/Documents/MyProjects/Project_Genesis/models")
                ]
                
                # Search for any available model
                for search_path in fallback_search_paths:
                    if not search_path.exists():
                        continue
                    
                    # Try each candidate in the fallback locations
                    for candidate in model_candidates:
                        model_file = search_path / candidate
                        if model_file.exists():
                            self.GGUF_MODEL_PATH = model_file
                            self.GGUF_MODEL_NAME = candidate.replace('.gguf', '')
                            logger.info(f"Found model via fallback search: {model_file}")
                            break
                    
                    if self.GGUF_MODEL_PATH:
                        break
        
        # GGUF hardware configuration - OPTIMIZED FOR APPLE SILICON
        self.GGUF_HARDWARE_CONFIG = {
            "n_gpu_layers": -1,        # Use all Metal layers on Apple Silicon
            "n_batch": 512,           # Larger batch for Q8_0 (higher quality)
            "n_ctx": 4096,            # Full context window
            "n_threads": 8,           # Optimal for Apple Silicon
            "use_mmap": True,         # Fast loading
            "use_mlock": False,       # Don't lock all memory
            "f16_kv": True,           # Half precision KV cache
            "rope_freq_base": 10000.0, # Qwen-specific rope frequency
            "mul_mat_q": True,        # Quantized matrix multiplication
            "offload_kqv": True,      # Offload KQV to GPU
            "verbose": self._get_bool_env("DEEPCODERX_DEBUG_MODE", True)
        }
        
        # GGUF generation parameters - CODER OPTIMIZED
        self.GGUF_GENERATION_PARAMS = {
            "temperature": 0.0,        # Maximum instruction following
            "top_p": 0.85,            # Slightly more focused for code tasks
            "top_k": 40,              # Standard value
            "repeat_penalty": 1.05,   # Reduce repetition
            "max_tokens": 2048,       # Standard max tokens
            "stop": ["Human:", "User:", "\n\n---", "```\n\n", "Assistant:", "<|endoftext|>"]
        }
        
        # PHASE 2: Removed Qwen-specific optimizations for model flexibility
        
        # Legacy compatibility - LOCAL_MODEL_PATH
        self.LOCAL_MODEL_PATH = str(self.GGUF_MODEL_PATH) if self.GGUF_MODEL_PATH else None
    
    def _load_prompting_config(self):
        """Load GGUF prompting configuration from YAML."""
        yaml_path = Path(__file__).parent / "gguf_prompts.yaml"
        
        # PHASE 2: Simplified prompting configuration (removed complex visual emphasis)
        default_config = {
            "tool_format": "<tool_call>function_name({\"parameter\": \"value\"})</tool_call>",
            "simple_examples": [
                {"user": "pwd", "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>"},
                {"user": "ls", "assistant": "<tool_call>run_bash({\"command\": \"ls\"})</tool_call>"}
            ],
            "model_settings": {
                "temperature": 0.0,
                "max_tokens": 2048
            }
        }
        
        try:
            if yaml_path.exists():
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    loaded_config = yaml.safe_load(f)
                
                if loaded_config:
                    self.GGUF_PROMPTING_CONFIG = loaded_config
                    logger.info(f"Loaded GGUF prompting config from: {yaml_path}")
                else:
                    raise ValueError("Empty YAML file")
            else:
                raise FileNotFoundError(f"YAML file not found: {yaml_path}")
                
        except Exception as e:
            logger.error(f"Failed to load GGUF prompting config: {e}")
            logger.error("Using default GGUF prompting configuration")
            self.GGUF_PROMPTING_CONFIG = default_config
    
    def _load_system_prompts(self):
        """Load system prompts for different providers."""
        # DeepSeek system prompt
        self.DEEPSEEK_SYSTEM_PROMPT = self._get_str_env(
            "DEEPCODERX_DEEPSEEK_SYSTEM_PROMPT",
            """You are an expert software architect and coding assistant. Your goal is to provide helpful, accurate responses.

**CRITICAL: Only respond to the most recent user message. Do not respond to multiple questions at once.**

**Response Guidelines:**
- Answer questions directly using your knowledge when possible
- Only use tools when the user specifically requests file operations or codebase analysis
- For general programming questions, explanations, or discussions, respond without tools
- When tools are needed, use them efficiently and explain what you're doing
- Provide ONE response to ONE question only

**Appropriate Tool Usage:**
- User asks to read, write, or analyze specific files
- User requests directory listings or file operations  
- User asks for code implementation requiring file creation
- User explicitly requests codebase analysis or project review

**Avoid Tools For:**
- General programming questions or explanations
- Code review discussions
- Debugging help
- Conversational responses
- Questions answerable with your existing knowledge

You have access to file system tools when appropriate."""
        )
    
    def _load_semantic_zones_config(self):
        """Load semantic zones configuration - SINGLE SOURCE OF TRUTH."""
        
        # SEMANTIC ZONES - Single source of truth for all zone definitions
        self.SEMANTIC_ZONES = {
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
        
        # ZONE DETECTION SETTINGS
        self.ZONE_DETECTION_CONFIG = {
            "confidence_threshold": 0.6,
            "pattern_weight": 0.4,
            "trigger_weight": 0.6, 
            "unknown_zone_fallback": "conversational",
            "multi_zone_strategy": "highest_confidence",
            "case_sensitive": False,
            "enabled": self._get_bool_env("DEEPCODERX_SEMANTIC_ZONES_ENABLED", True)
        }
        
        # ZONE-SPECIFIC ROUTING RULES
        self.ZONE_ROUTING_RULES = {
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
        
        logger.info("Semantic zones configuration loaded - Single source of truth active")
        
        # Local GGUF system prompt
        self.LOCAL_SYSTEM_PROMPT = self._get_str_env(
            "DEEPCODERX_LOCAL_SYSTEM_PROMPT",
            """You are a helpful programming assistant. Your goal is to provide clear, helpful responses.

**RESPOND NATURALLY TO CONVERSATIONS:**
For greetings, questions, or general chat, respond directly and naturally.
Examples:
- "hello" → "Hello! How can I help you with your coding project today?"
- "how are you?" → "I'm doing well! Ready to help with any programming tasks."
- "what is Python?" → Give a direct explanation about Python
- "tell me about yourself" → Explain your role as a coding assistant

**USE TOOLS ONLY FOR SPECIFIC FILE/CODE TASKS:**
Only use tools when explicitly asked to work with files or run commands.
Examples:
- "create a script" → Use write_file tool
- "list files" → Use list_dir tool  
- "read config.py" → Use read_file tool
- "run this command" → Use run_bash tool

**TOOL FORMAT (only when needed):**
{"tool": "tool_name", "parameter": "value"}

**Available Tools:**
- list_dir: List directory contents
- read_file: Read file content
- write_file: Create/write file
- run_bash: Execute shell commands
- move_file: Move/rename files
- mkdir: Create directories
- stat: Get file metadata

**KEY RULES:**
1. MOST inputs are just conversation - respond naturally
2. Only use tools when explicitly working with files/commands
3. For greetings and questions, NO TOOLS needed
4. When using tools, respond with ONLY the JSON
5. After tool execution, explain what you did
"""
        )
    
    def _validate_configuration(self):
        """Validate the complete configuration - fail explicitly if invalid."""
        errors = []
        
        # Validate paths
        if not self.SANDBOX_PATH.exists():
            errors.append(f"Sandbox path does not exist: {self.SANDBOX_PATH}")
        
        if not self.SANDBOX_PATH.is_dir():
            errors.append(f"Sandbox path is not a directory: {self.SANDBOX_PATH}")
        
        # Validate GGUF model path if local or dual provider is enabled
        if self.PROVIDERS["local"]["enabled"] or self.PROVIDERS["dual"]["enabled"]:
            if not self.GGUF_MODEL_PATH:
                errors.append(f"GGUF model file not found: {self.GGUF_MODEL_NAME}.gguf")
            elif not self.GGUF_MODEL_PATH.exists():
                errors.append(f"GGUF model file does not exist: {self.GGUF_MODEL_PATH}")
        
        # Validate API keys for enabled cloud providers
        if self.PROVIDERS["deepseek"]["enabled"] and not self.PROVIDERS["deepseek"]["api_key"]:
            errors.append("DeepSeek is enabled but DEEPCODERX_DEEPSEEK_API_KEY not provided")
        
        if self.PROVIDERS["openai"]["enabled"] and not self.PROVIDERS["openai"]["api_key"]:
            errors.append("OpenAI is enabled but DEEPCODERX_OPENAI_API_KEY not provided")
        
        # Validate default provider exists and is enabled
        if self.DEFAULT_PROVIDER not in self.PROVIDERS:
            errors.append(f"Default provider '{self.DEFAULT_PROVIDER}' not found in available providers")
        elif not self.PROVIDERS[self.DEFAULT_PROVIDER]["enabled"]:
            errors.append(f"Default provider '{self.DEFAULT_PROVIDER}' is not enabled")
        
        # API key format validation for DeepSeek - FIXED REGEX FOR 32 HEX CHARACTERS
        if self.DEEPSEEK_API_KEY and not re.match(r'^sk-[0-9a-f]{32}$', self.DEEPSEEK_API_KEY):
            errors.append("Invalid DeepSeek API key format (should be sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX)")
        
        # Fail explicitly if any validation errors
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_message)
        
        # Create scripts directory if it doesn't exist
        scripts_path = Path(self.SCRIPTS_DIR)
        if not scripts_path.exists():
            scripts_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Configuration validation passed")
    
    # Environment variable helper methods
    def _get_str_env(self, key: str, default: Optional[str]) -> Optional[str]:
        """Get string environment variable with legacy compatibility."""
        # First try the prefixed key
        value = os.getenv(key)
        if value is not None:
            return value
        
        # Try legacy key names for backward compatibility
        legacy_mappings = {
            "DEEPCODERX_DEEPSEEK_API_KEY": "DEEPSEEK_API_KEY",
            "DEEPCODERX_OPENAI_API_KEY": "OPENAI_API_KEY",
            "DEEPCODERX_SANDBOX_PATH": "SANDBOX_PATH",
            "DEEPCODERX_MCP_API_KEY": "MCP_API_KEY"
        }
        
        if key in legacy_mappings:
            legacy_value = os.getenv(legacy_mappings[key])
            if legacy_value is not None:
                return legacy_value
        
        return default
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def _get_path_env(self, key: str, default: Path) -> Path:
        """Get path environment variable with legacy compatibility."""
        # First try the prefixed key
        value = os.getenv(key)
        if value:
            return Path(value)
        
        # Try legacy key names for backward compatibility
        legacy_mappings = {
            "DEEPCODERX_SANDBOX_PATH": "SANDBOX_PATH"
        }
        
        if key in legacy_mappings:
            legacy_value = os.getenv(legacy_mappings[key])
            if legacy_value:
                return Path(legacy_value)
        
        return default
    
    def get_current_config_summary(self) -> str:
        """Get a summary of the current configuration."""
        enabled_providers = [name for name, config in self.PROVIDERS.items() if config["enabled"]]
        
        return f"""
DeepCoderX Configuration Summary:
=================================
Sandbox Path: {self.SANDBOX_PATH}
Default Provider: {self.DEFAULT_PROVIDER}
Enabled Providers: {', '.join(enabled_providers)}
GGUF Model: {self.GGUF_MODEL_NAME} ({self.GGUF_QUANTIZATION})
GGUF Model Path: {self.GGUF_MODEL_PATH or 'NOT FOUND'}
Debug Mode: {self.DEBUG_MODE}
Max Tool Calls: {self.MAX_TOOL_CALLS}
"""
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        if provider_name not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.PROVIDERS[provider_name].copy()
    
    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available and properly configured."""
        if provider_name not in self.PROVIDERS:
            return False
        
        provider_config = self.PROVIDERS[provider_name]
        if not provider_config["enabled"]:
            return False
        
        # Additional checks for specific providers
        if provider_name in ["local", "dual"]:
            return self.GGUF_MODEL_PATH and self.GGUF_MODEL_PATH.exists()
        elif provider_name in ["deepseek", "openai"]:
            return provider_config.get("api_key") is not None
        
        return True


# Initialize the global configuration instance
try:
    config = DeepCoderXConfig()
    logger.info("DeepCoderX configuration loaded successfully")
except Exception as e:
    logger.error(f"Failed to initialize DeepCoderX configuration: {e}")
    raise


# Backward compatibility exports
DEBUG_MODE = config.DEBUG_MODE
SANDBOX_PATH = config.SANDBOX_PATH
MCP_SERVER_HOST = config.MCP_SERVER_HOST
MCP_SERVER_PORT = config.MCP_SERVER_PORT
MCP_API_KEY = config.MCP_API_KEY
MAX_FILE_SIZE = config.MAX_FILE_SIZE
ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS
MAX_TOOL_CALLS = config.MAX_TOOL_CALLS
COMMAND_TIMEOUT = config.COMMAND_TIMEOUT
SHORT_COMMAND_TIMEOUT = config.SHORT_COMMAND_TIMEOUT
MODEL_CONTEXT_SIZE = config.MODEL_CONTEXT_SIZE
HISTORY_TRIM_SIZE = config.HISTORY_TRIM_SIZE
HISTORY_KEEP_SIZE = config.HISTORY_KEEP_SIZE
API_REQUEST_TIMEOUT = config.API_REQUEST_TIMEOUT
MCP_CLIENT_TIMEOUT = config.MCP_CLIENT_TIMEOUT

# Legacy DeepSeek compatibility
DEEPSEEK_ENABLED = config.DEEPSEEK_ENABLED
DEEPSEEK_API_KEY = config.DEEPSEEK_API_KEY
DEEPSEEK_API_URL = config.DEEPSEEK_API_URL
DEEPSEEK_SYSTEM_PROMPT = config.DEEPSEEK_SYSTEM_PROMPT
LOCAL_SYSTEM_PROMPT = config.LOCAL_SYSTEM_PROMPT

# Legacy model path compatibility
LOCAL_MODEL_PATH = config.LOCAL_MODEL_PATH

# Semantic zones backward compatibility exports - SINGLE SOURCE OF TRUTH
SEMANTIC_ZONES = config.SEMANTIC_ZONES
ZONE_DETECTION_CONFIG = config.ZONE_DETECTION_CONFIG
ZONE_ROUTING_RULES = config.ZONE_ROUTING_RULES

# Enhanced debug logging configuration - for model interaction debugging
DEBUG_LOGGING = config.DEBUG_LOGGING

# Current configuration summary
CURRENT_CONFIG = config.get_current_config_summary()
