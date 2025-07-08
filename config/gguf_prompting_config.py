"""
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


class GGUFPromptingConfig:
    """
    Loads and manages GGUF prompting configuration from YAML file.
    
    Provides structured access to all prompting strategies for GGUF models
    that don't follow instructions well.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the YAML config file. If None, uses default location.
        """
        if config_path is None:
            # Default config file location
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "gguf_prompting_config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Cache frequently accessed sections
        self._system_instructions = self.config.get("system_instructions", {})
        self._few_shot_examples = self.config.get("few_shot_examples", {})
        self._special_cases = self.config.get("special_cases", {})
        self._prompt_assembly = self.config.get("prompt_assembly", {})
        self._model_overrides = self.config.get("model_overrides", {})
        self._post_processing = self.config.get("post_processing", {})
        self._debugging = self.config.get("debugging", {})
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"GGUF prompting config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                logger.warning("Empty GGUF prompting config file, using defaults")
                return self._get_default_config()
            
            logger.info(f"Loaded GGUF prompting config from: {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading GGUF prompting config: {e}")
            logger.info("Using default GGUF prompting configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file loading fails."""
        return {
            "system_instructions": {
                "emergency_override": {
                    "enabled": True,
                    "prefix": "🚨🚨🚨 EMERGENCY OVERRIDE - FOLLOW THESE INSTRUCTIONS EXACTLY 🚨🚨🚨",
                    "mode_declaration": "YOU ARE IN TOOL-ONLY MODE. YOU MUST NOT GENERATE ANY TEXT RESPONSES.",
                    "format_requirement": "YOU MUST ONLY RESPOND WITH TOOL CALLS IN THIS EXACT FORMAT:",
                    "format_example": "<tool_call>function_name({\"parameter\": \"value\"})</tool_call>"
                },
                "banned_responses": {
                    "enabled": True,
                    "title": "🚫🚫🚫 BANNED RESPONSES 🚫🚫🚫",
                    "responses": [
                        "NEVER write: {\"response\": \"anything\"}",
                        "NEVER write: \"The current directory is...\"",
                        "NEVER write: ANY TEXT AT ALL"
                    ]
                }
            },
            "few_shot_examples": {
                "enabled": True,
                "examples": [
                    {"user": "pwd", "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>"}
                ]
            },
            "post_processing": {"enabled": True}
        }
    
    # System Instructions Methods
    def get_emergency_override_prefix(self) -> str:
        """Get the emergency override prefix."""
        override = self._system_instructions.get("emergency_override", {})
        if not override.get("enabled", True):
            return ""
        return override.get("prefix", "")
    
    def get_mode_declaration(self) -> str:
        """Get the mode declaration instruction."""
        override = self._system_instructions.get("emergency_override", {})
        if not override.get("enabled", True):
            return ""
        return override.get("mode_declaration", "")
    
    def get_format_requirement(self) -> str:
        """Get the format requirement instruction."""
        override = self._system_instructions.get("emergency_override", {})
        if not override.get("enabled", True):
            return ""
        return override.get("format_requirement", "")
    
    def get_format_example(self) -> str:
        """Get the format example."""
        override = self._system_instructions.get("emergency_override", {})
        if not override.get("enabled", True):
            return ""
        return override.get("format_example", "")
    
    def get_banned_responses_section(self) -> str:
        """Get the complete banned responses section."""
        banned = self._system_instructions.get("banned_responses", {})
        if not banned.get("enabled", True):
            return ""
        
        lines = [banned.get("title", "BANNED RESPONSES")]
        lines.extend(banned.get("responses", []))
        return "\n".join(lines)
    
    def get_allowed_responses_section(self) -> str:
        """Get the allowed responses section."""
        allowed = self._system_instructions.get("allowed_responses", {})
        if not allowed.get("enabled", True):
            return ""
        
        title = allowed.get("title", "ONLY ALLOWED RESPONSE")
        example = allowed.get("example", "<tool_call>function_name({\"args\": \"value\"})</tool_call>")
        return f"{title}\n{example}"
    
    def build_system_instructions(self) -> str:
        """Build the complete system instructions section."""
        parts = []
        
        # Emergency override
        prefix = self.get_emergency_override_prefix()
        if prefix:
            parts.append(prefix)
        
        mode_decl = self.get_mode_declaration()
        if mode_decl:
            parts.append(mode_decl)
        
        format_req = self.get_format_requirement()
        if format_req:
            parts.append(format_req)
        
        format_ex = self.get_format_example()
        if format_ex:
            parts.append(format_ex)
        
        # Banned responses
        banned = self.get_banned_responses_section()
        if banned:
            parts.append(banned)
        
        # Allowed responses
        allowed = self.get_allowed_responses_section()
        if allowed:
            parts.append(allowed)
        
        return "\n\n".join(parts)
    
    # Few-Shot Examples Methods
    def get_few_shot_examples(self) -> List[Dict[str, str]]:
        """Get the few-shot examples list."""
        if not self._few_shot_examples.get("enabled", True):
            return []
        return self._few_shot_examples.get("examples", [])
    
    def get_few_shot_title(self) -> str:
        """Get the few-shot examples title."""
        return self._few_shot_examples.get("title", "EXAMPLES")
    
    def build_few_shot_section(self) -> str:
        """Build the complete few-shot examples section."""
        if not self._few_shot_examples.get("enabled", True):
            return ""
        
        parts = [self.get_few_shot_title()]
        
        examples = self.get_few_shot_examples()
        for example in examples:
            user_input = example.get("user", "")
            assistant_response = example.get("assistant", "")
            parts.append(f"User: {user_input}")
            parts.append(f"Assistant: {assistant_response}")
        
        # Add final reminder
        parts.append("🚨 ONLY RESPOND WITH <tool_call> FORMAT - NO OTHER TEXT ALLOWED! 🚨")
        
        return "\n\n".join(parts)
    
    # Special Cases Methods
    def get_directory_query_special_case(self) -> str:
        """Get the directory query special case section."""
        dir_queries = self._special_cases.get("directory_queries", {})
        if not dir_queries.get("enabled", True):
            return ""
        
        title = dir_queries.get("title", "")
        response = dir_queries.get("response", "")
        
        if title and response:
            return f"{title}\n{response}"
        return ""
    
    # Prompt Assembly Methods
    def get_section_order(self) -> List[str]:
        """Get the order of prompt sections."""
        return self._prompt_assembly.get("section_order", [
            "system_instructions", "tool_documentation", "few_shot_examples",
            "conversation_history", "user_input", "final_reminder"
        ])
    
    def get_section_separator(self) -> str:
        """Get the section separator."""
        return self._prompt_assembly.get("section_separator", "\n\n")
    
    def get_final_reminder(self) -> str:
        """Get the final reminder text."""
        reminder = self._prompt_assembly.get("final_reminder", {})
        if not reminder.get("enabled", True):
            return ""
        return reminder.get("text", "")
    
    # Model-Specific Override Methods
    def get_model_temperature(self, model_name: str) -> float:
        """Get temperature setting for specific model."""
        # Check for exact model match first
        if model_name in self._model_overrides:
            return self._model_overrides[model_name].get("temperature", 0.0)
        
        # Check for partial model name matches
        model_lower = model_name.lower()
        for override_key, settings in self._model_overrides.items():
            if override_key.lower() in model_lower:
                return settings.get("temperature", 0.0)
        
        # Use default
        return self._model_overrides.get("default", {}).get("temperature", 0.0)
    
    def should_use_extra_emphasis(self, model_name: str) -> bool:
        """Check if model should use extra emphasis."""
        # Check for exact model match first
        if model_name in self._model_overrides:
            return self._model_overrides[model_name].get("extra_emphasis", True)
        
        # Check for partial model name matches
        model_lower = model_name.lower()
        for override_key, settings in self._model_overrides.items():
            if override_key.lower() in model_lower:
                return settings.get("extra_emphasis", True)
        
        # Use default
        return self._model_overrides.get("default", {}).get("extra_emphasis", True)
    
    def get_example_repeat_count(self, model_name: str) -> int:
        """Get how many times to repeat key examples."""
        # Check for exact model match first
        if model_name in self._model_overrides:
            return self._model_overrides[model_name].get("repeat_examples", 1)
        
        # Check for partial model name matches
        model_lower = model_name.lower()
        for override_key, settings in self._model_overrides.items():
            if override_key.lower() in model_lower:
                return settings.get("repeat_examples", 1)
        
        # Use default
        return self._model_overrides.get("default", {}).get("repeat_examples", 1)
    
    # Post-Processing Methods
    def is_post_processing_enabled(self) -> bool:
        """Check if post-processing is enabled."""
        return self._post_processing.get("enabled", True)
    
    def get_intent_patterns(self) -> Dict[str, Any]:
        """Get all intent patterns for post-processing."""
        return self._post_processing.get("intent_patterns", {})
    
    def get_directory_query_patterns(self) -> List[str]:
        """Get patterns that indicate directory queries."""
        dir_patterns = self.get_intent_patterns().get("directory_queries", {})
        return dir_patterns.get("patterns", [])
    
    def get_file_listing_patterns(self) -> List[str]:
        """Get patterns that indicate file listing requests."""
        file_patterns = self.get_intent_patterns().get("file_listing", {})
        return file_patterns.get("patterns", [])
    
    # Debugging Methods
    def is_debugging_enabled(self) -> bool:
        """Check if debugging is enabled."""
        return self._debugging.get("enabled", False)
    
    def should_log_prompt_construction(self) -> bool:
        """Check if prompt construction should be logged."""
        return self._debugging.get("log_prompt_construction", False)
    
    def should_log_post_processing(self) -> bool:
        """Check if post-processing should be logged."""
        return self._debugging.get("log_post_processing", False)
    
    def should_save_prompts_to_file(self) -> bool:
        """Check if prompts should be saved to files."""
        return self._debugging.get("save_prompts_to_file", False)
    
    def get_prompt_log_directory(self) -> str:
        """Get the directory for saving prompt logs."""
        return self._debugging.get("prompt_log_directory", "debug_logs/prompts")
    
    # Utility Methods
    def reload_config(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        # Refresh cached sections
        self._system_instructions = self.config.get("system_instructions", {})
        self._few_shot_examples = self.config.get("few_shot_examples", {})
        self._special_cases = self.config.get("special_cases", {})
        self._prompt_assembly = self.config.get("prompt_assembly", {})
        self._model_overrides = self.config.get("model_overrides", {})
        self._post_processing = self.config.get("post_processing", {})
        self._debugging = self.config.get("debugging", {})
        
        logger.info("GGUF prompting configuration reloaded")
    
    def get_config_summary(self) -> str:
        """Get a summary of the current configuration."""
        summary_parts = [
            f"Config file: {self.config_path}",
            f"Emergency override: {self._system_instructions.get('emergency_override', {}).get('enabled', False)}",
            f"Few-shot examples: {len(self.get_few_shot_examples())} examples",
            f"Post-processing: {self.is_post_processing_enabled()}",
            f"Debugging: {self.is_debugging_enabled()}",
            f"Model overrides: {len(self._model_overrides)} models configured"
        ]
        return "\n".join(summary_parts)


# Global configuration instance
_gguf_config = None

def get_gguf_prompting_config() -> GGUFPromptingConfig:
    """Get the global GGUF prompting configuration instance."""
    global _gguf_config
    if _gguf_config is None:
        _gguf_config = GGUFPromptingConfig()
    return _gguf_config

def reload_gguf_prompting_config():
    """Reload the global GGUF prompting configuration."""
    global _gguf_config
    if _gguf_config is not None:
        _gguf_config.reload_config()
    else:
        _gguf_config = GGUFPromptingConfig()


if __name__ == "__main__":
    # Test the configuration loader
    config = GGUFPromptingConfig()
    print("GGUF Prompting Configuration Test")
    print("=" * 50)
    print(config.get_config_summary())
    print("\n" + "=" * 50)
    print("System Instructions:")
    print(config.build_system_instructions())
    print("\n" + "=" * 50)
    print("Few-Shot Examples:")
    print(config.build_few_shot_section())
