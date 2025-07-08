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
    
    def _load_provider_settings(self):
        """Load AI provider settings."""
        self.DEFAULT_PROVIDER = self._get_str_env("DEEPCODERX_DEFAULT_PROVIDER", "local")
        
        # Provider configurations
        self.PROVIDERS = {
            "local": {
                "name": "Local GGUF Model (Direct Inference)",
                "model_type": "gguf_direct",  # Direct inference only - no API fallback
                "enabled": self._get_bool_env("DEEPCODERX_LOCAL_ENABLED", True),
                "supports_tools": True,
                "tool_format": "manual",  # Manual prompting for tool calls
                "max_tool_iterations": self._get_int_env("DEEPCODERX_LOCAL_MAX_TOOL_ITERATIONS", 5),
                "temperature": 0.0,  # Maximum instruction following
                "max_tokens": self._get_int_env("DEEPCODERX_LOCAL_MAX_TOKENS", 2048)
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
        """Load GGUF model settings for direct inference."""
        # GGUF model configuration - DIRECT INFERENCE ONLY
        self.GGUF_MODEL_NAME = self._get_str_env("DEEPCODERX_GGUF_MODEL_NAME", "qwen2.5-coder-1.5b-instruct")
        self.GGUF_QUANTIZATION = self._get_str_env("DEEPCODERX_GGUF_QUANTIZATION", "q8_0")
        
        # Model path resolution
        model_filename = f"{self.GGUF_MODEL_NAME}-{self.GGUF_QUANTIZATION}.gguf"
        
        # Search paths for GGUF models
        search_paths = [
            Path.home() / ".cache" / "lm-studio" / "models",
            Path.home() / ".cache" / "huggingface" / "hub", 
            Path.home() / "models",
            Path("./models"),
            Path(__file__).parent / "models"
        ]
        
        # Find model file
        self.GGUF_MODEL_PATH = None
        custom_path = self._get_str_env("DEEPCODERX_GGUF_MODEL_PATH", None)
        
        if custom_path:
            # Use custom path if provided
            self.GGUF_MODEL_PATH = Path(custom_path)
        else:
            # Search for model file
            for search_path in search_paths:
                if not search_path.exists():
                    continue
                
                # Direct file check
                model_file = search_path / model_filename
                if model_file.exists():
                    self.GGUF_MODEL_PATH = model_file
                    break
                
                # Recursive search
                for found_file in search_path.rglob(model_filename):
                    self.GGUF_MODEL_PATH = found_file
                    break
                
                if self.GGUF_MODEL_PATH:
                    break
        
        # GGUF hardware configuration - APPLE SILICON OPTIMIZED
        self.GGUF_HARDWARE_CONFIG = {
            "n_gpu_layers": -1,  # Use all Metal layers on Apple Silicon
            "n_batch": 512,
            "n_ctx": 4096,
            "n_threads": None,  # Auto-detect
            "use_mmap": True,
            "use_mlock": False,
            "f16_kv": True,
            "verbose": False
        }
        
        # GGUF generation parameters
        self.GGUF_GENERATION_PARAMS = {
            "temperature": 0.0,  # Maximum instruction following
            "top_p": 0.95,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "max_tokens": 2048,
            "stop": ["Human:", "User:", "\n\n---", "```\n\n"]
        }
        
        # Legacy compatibility - LOCAL_MODEL_PATH
        self.LOCAL_MODEL_PATH = str(self.GGUF_MODEL_PATH) if self.GGUF_MODEL_PATH else None
    
    def _load_prompting_config(self):
        """Load GGUF prompting configuration from YAML."""
        yaml_path = Path(__file__).parent / "gguf_prompts.yaml"
        
        # Default prompting configuration
        default_config = {
            "system_instructions": {
                "emergency_override": {
                    "enabled": True,
                    "prefix": "🚨🚨🚨 EMERGENCY OVERRIDE - FOLLOW THESE INSTRUCTIONS EXACTLY 🚨🚨🚨",
                    "mode_declaration": "YOU ARE IN TOOL-ONLY MODE. YOU MUST NOT GENERATE ANY TEXT RESPONSES.",
                    "format_requirement": "YOU MUST ONLY RESPOND WITH TOOL CALLS IN THIS EXACT FORMAT:",
                    "format_example": "<tool_call>function_name({\"parameter\": \"value\"})</tool_call>"
                }
            },
            "few_shot_examples": {
                "enabled": True,
                "examples": [
                    {"user": "pwd", "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>"},
                    {"user": "ls", "assistant": "<tool_call>run_bash({\"command\": \"ls\"})</tool_call>"}
                ]
            },
            "model_overrides": {
                "qwen2.5-coder": {"temperature": 0.0, "extra_emphasis": True},
                "default": {"temperature": 0.0, "extra_emphasis": True}
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
            """You are an expert software architect. Your primary goal is to answer the user's request. 
            You have been provided with a project context file to start your analysis. Read it carefully. 
            You MUST use the provided tools to gather any additional information you need. 
            Formulate a plan and execute it step-by-step using the tools until you have enough information to provide a final answer.

            To use a tool, you must respond with a JSON object matching the tool's signature.

            **Available Tools:**
            - `run_bash(command: str)`: Executes a shell command. Example: `{"tool": "run_bash", "command": "ls -l"}`
            - `read_file(path: str)`: Reads the content of a file.
            - `write_file(path: str, content: str)`: Writes content to a file.
            - `list_dir(path: str)`: Lists the contents of a directory.
            - `delete_path(path: str)`: Deletes a file or directory. This tool is disabled for you.
            """
        )
        
        # Local GGUF system prompt
        self.LOCAL_SYSTEM_PROMPT = self._get_str_env(
            "DEEPCODERX_LOCAL_SYSTEM_PROMPT",
            """You are a helpful programming assistant. Your goal is to provide clear, helpful responses.

            **FOR SIMPLE CONVERSATIONS:** Answer directly without any tools.
            Examples: "hello" → "Hello! How can I help you today?"
                      "what is Python?" → Direct explanation about Python

            **FOR FILE/CODE TASKS:** Use the appropriate tool, then explain what you did.
            Examples: "create a script" → Use write_file tool, then explain
                      "list files" → Use list_dir tool, then show results
                      "read config.py" → Use read_file tool, then summarize

            **TOOL FORMAT (when needed):**
            {"tool": "tool_name", "parameter": "value"}

            **Available Tools:**
            - list_dir: List directory contents. Format: {"tool": "list_dir", "path": "directory_path"}
            - read_file: Read file content. Format: {"tool": "read_file", "path": "file_path"}
            - write_file: Create/write file. Format: {"tool": "write_file", "path": "file_path", "content": "file_content"}
            - run_bash: Execute shell commands. Format: {"tool": "run_bash", "command": "shell_command"}
            - move_file: Move/rename files. Format: {"tool": "move_file", "source": "old_path", "destination": "new_path"}
            - mkdir: Create directories. Format: {"tool": "mkdir", "path": "directory_path"}
            - stat: Get file metadata. Format: {"tool": "stat", "path": "file_or_directory_path"}

            **KEY RULES:**
            1. Most questions are conversations - answer directly
            2. Only use tools when actually working with files/directories
            3. Use relative paths when possible: "script.py", not "/full/path"
            4. When you need to use a tool, respond with ONLY the JSON - no other text
            5. After the tool executes, then explain what you did
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
        
        # Validate GGUF model path if local provider is enabled
        if self.PROVIDERS["local"]["enabled"]:
            if not self.GGUF_MODEL_PATH:
                errors.append(f"GGUF model file not found: {self.GGUF_MODEL_NAME}-{self.GGUF_QUANTIZATION}.gguf")
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
        
        # API key format validation for DeepSeek
        if self.DEEPSEEK_API_KEY and not re.match(r'^sk-[0-9a-f]{32}
        
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
        if provider_name == "local":
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

# Current configuration summary
CURRENT_CONFIG = config.get_current_config_summary()
, self.DEEPSEEK_API_KEY):
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
        if provider_name == "local":
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

# Current configuration summary
CURRENT_CONFIG = config.get_current_config_summary()
