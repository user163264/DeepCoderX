"""
GGUF Response Post-Processor - Emergency fix for stubborn models

This module post-processes GGUF responses to convert them to tool calls when the model 
refuses to follow format. Now uses configurable intent patterns from YAML config.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

# Try to import the configuration system, but provide fallback if not available
try:
    from config.gguf_prompting_config import get_gguf_prompting_config
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    import warnings
    warnings.warn(f"GGUF prompting config not available: {e}. Using fallback post-processing.")

logger = logging.getLogger(__name__)


class GGUFResponsePostProcessor:
    """
    Post-processes GGUF model responses to convert natural language into tool calls.
    This is a fallback for models that refuse to follow tool call format.
    
    Uses configurable intent patterns from gguf_prompting_config.yaml
    """
    
    def __init__(self):
        """Initialize the post-processor with configuration."""
        self.config = get_gguf_prompting_config()
        self.intent_patterns = self._build_intent_patterns()
        
        if self.config.is_debugging_enabled():
            logger.info(f"GGUF Post-Processor initialized with {len(self.intent_patterns)} intent patterns")
    
    def _build_intent_patterns(self) -> List[Dict[str, Any]]:
        """Build intent patterns from configuration."""
        patterns = []
        
        if not self.config.is_post_processing_enabled():
            return patterns
        
        intent_patterns_config = self.config.get_intent_patterns()
        
        # Directory queries
        dir_config = intent_patterns_config.get("directory_queries", {})
        if dir_config.get("patterns"):
            patterns.append({
                "patterns": [rf"(?i){pattern}" for pattern in dir_config["patterns"]],
                "tool_call": {
                    "tool": dir_config.get("tool_call", "run_bash"),
                    **dir_config.get("parameters", {"command": "pwd"})
                }
            })
        
        # File listing
        file_config = intent_patterns_config.get("file_listing", {})
        if file_config.get("patterns"):
            patterns.append({
                "patterns": [rf"(?i){pattern}" for pattern in file_config["patterns"]],
                "tool_call": {
                    "tool": file_config.get("tool_call", "list_dir"),
                    **file_config.get("parameters", {"path": "."})
                }
            })
        
        # File creation (with parameter extraction)
        file_creation_config = intent_patterns_config.get("file_creation", {})
        if file_creation_config.get("patterns"):
            patterns.append({
                "patterns": [
                    r"(?i)create\s+(?:a\s+)?file\s+(?:called\s+|named\s+)?([^\s]+)",
                    r"(?i)make\s+(?:a\s+)?file\s+(?:called\s+|named\s+)?([^\s]+)",
                    r"(?i)touch\s+([^\s]+)"
                ],
                "tool_call": {"tool": "write_file", "path": "{match_1}", "content": ""}
            })
        
        # File reading (with parameter extraction)
        file_reading_config = intent_patterns_config.get("file_reading", {})
        if file_reading_config.get("patterns"):
            patterns.append({
                "patterns": [
                    r"(?i)read\s+(?:the\s+)?file\s+([^\s]+)",
                    r"(?i)show\s+(?:me\s+)?(?:the\s+)?(?:contents\s+of\s+)?([^\s\.]+\.[\w]+)",
                    r"(?i)cat\s+([^\s]+)",
                    r"(?i)open\s+([^\s]+)"
                ],
                "tool_call": {"tool": "read_file", "path": "{match_1}"}
            })
        
        # Git commands
        git_config = intent_patterns_config.get("git_commands", {})
        if git_config.get("patterns"):
            git_patterns = []
            for pattern in git_config["patterns"]:
                if "git status" in pattern:
                    git_patterns.append({
                        "patterns": [rf"(?i){re.escape(pattern)}"],
                        "tool_call": {"tool": "run_bash", "command": pattern}
                    })
                else:
                    # Extract command from pattern for other git commands
                    git_patterns.append({
                        "patterns": [rf"(?i){re.escape(pattern)}"],
                        "tool_call": {"tool": "run_bash", "command": pattern}
                    })
            patterns.extend(git_patterns)
        
        # Add fallback patterns if config is missing
        if not patterns:
            patterns = self._get_default_patterns()
        
        if self.config.should_log_post_processing():
            logger.debug(f"Built {len(patterns)} intent patterns from configuration")
        
        return patterns
    
    def _get_default_patterns(self) -> List[Dict[str, Any]]:
        """Get default intent patterns if configuration is missing."""
        return [
            {
                "patterns": [
                    r"(?i)current\s+(?:working\s+)?directory",
                    r"(?i)what\s+(?:is\s+)?(?:the\s+)?(?:current\s+)?directory",
                    r"(?i)where\s+am\s+i",
                    r"(?i)pwd"
                ],
                "tool_call": {"tool": "run_bash", "command": "pwd"}
            },
            {
                "patterns": [
                    r"(?i)list\s+(?:files|contents?|directory)",
                    r"(?i)show\s+files",
                    r"(?i)ls\b"
                ],
                "tool_call": {"tool": "list_dir", "path": "."}
            }
        ]
    
    def should_process_response(self, response: str) -> bool:
        """Check if response should be post-processed."""
        if not response:
            return False
        
        # Check if post-processing is enabled in config
        if not self.config.is_post_processing_enabled():
            return False
        
        # Check if response already contains tool calls
        if "<tool_call>" in response:
            return False
        
        # Check if response is a generic/placeholder response that should be converted
        generic_indicators = [
            "/path/to/your/project",
            "/path/to/project", 
            "current working directory is",
            "I can help",
            "Let me help",
            '{"response":',
            '"response":'
        ]
        
        should_process = any(indicator in response for indicator in generic_indicators)
        
        if self.config.should_log_post_processing() and should_process:
            logger.debug(f"Response flagged for post-processing: {response[:100]}...")
        
        return should_process
    
    def extract_user_intent(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Extract user intent and convert to tool call."""
        if not user_input:
            return None
        
        for intent in self.intent_patterns:
            for pattern in intent["patterns"]:
                match = re.search(pattern, user_input)
                if match:
                    tool_call = intent["tool_call"].copy()
                    
                    # Replace placeholders with match groups
                    for key, value in tool_call.items():
                        if isinstance(value, str) and "{match_" in value:
                            # Replace {match_1}, {match_2}, etc. with regex groups
                            for i, group in enumerate(match.groups(), 1):
                                if group:  # Only replace if group exists
                                    value = value.replace(f"{{match_{i}}}", group)
                            tool_call[key] = value
                    
                    if self.config.should_log_post_processing():
                        logger.debug(f"Matched intent pattern for '{user_input}': {tool_call}")
                    
                    return tool_call
        
        if self.config.should_log_post_processing():
            logger.debug(f"No intent pattern matched for: {user_input}")
        
        return None
    
    def process_response(self, user_input: str, model_response: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Process a model response and convert to tool calls if needed.
        
        Args:
            user_input: The original user input
            model_response: The model's response
            
        Returns:
            Tuple of (tool_calls_list, clean_response)
        """
        if not self.should_process_response(model_response):
            return [], model_response
        
        # Try to extract tool call from user intent
        tool_call = self.extract_user_intent(user_input)
        
        if tool_call:
            if self.config.should_log_post_processing():
                logger.info(f"Post-processed response: {user_input} -> {tool_call}")
            # Found a tool call - return it
            return [tool_call], ""
        
        # No clear intent found - return original response
        if self.config.should_log_post_processing():
            logger.debug(f"No post-processing applied for: {user_input}")
        
        return [], model_response
    
    def create_corrected_response(self, tool_calls: List[Dict[str, Any]]) -> str:
        """Create a corrected response in tool call format."""
        if not tool_calls:
            return ""
        
        # Convert to the expected format
        corrected_parts = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool", "unknown")
            tool_args = {k: v for k, v in tool_call.items() if k != "tool"}
            
            tool_call_str = f'<tool_call>{tool_name}({json.dumps(tool_args)})</tool_call>'
            corrected_parts.append(tool_call_str)
        
        corrected_response = "\n".join(corrected_parts)
        
        if self.config.should_log_post_processing():
            logger.debug(f"Created corrected response: {corrected_response}")
        
        return corrected_response
    
    def diagnose_response(self, user_input: str, model_response: str) -> Dict[str, Any]:
        """Diagnose why a response might need post-processing."""
        diagnosis = {
            "user_input": user_input,
            "model_response": model_response,
            "post_processing_enabled": self.config.is_post_processing_enabled(),
            "should_process": self.should_process_response(model_response),
            "has_tool_calls": "<tool_call>" in model_response,
            "generic_indicators": [],
            "matched_intent": None,
            "suggested_tool_call": None,
            "available_patterns": len(self.intent_patterns)
        }
        
        # Check for generic indicators
        generic_indicators = [
            "/path/to/your/project", "/path/to/project", 
            "current working directory is", "I can help", "Let me help",
            '{"response":', '"response":'
        ]
        
        for indicator in generic_indicators:
            if indicator in model_response:
                diagnosis["generic_indicators"].append(indicator)
        
        # Check for intent match
        tool_call = self.extract_user_intent(user_input)
        if tool_call:
            diagnosis["matched_intent"] = True
            diagnosis["suggested_tool_call"] = tool_call
        else:
            diagnosis["matched_intent"] = False
        
        return diagnosis
    
    def get_supported_intents(self) -> List[str]:
        """Get a list of supported intent types."""
        intents = []
        for pattern_group in self.intent_patterns:
            tool_call = pattern_group.get("tool_call", {})
            tool_name = tool_call.get("tool", "unknown")
            if tool_name == "run_bash":
                command = tool_call.get("command", "")
                intents.append(f"Shell command: {command}")
            else:
                intents.append(f"Tool: {tool_name}")
        return intents
    
    def reload_config(self):
        """Reload configuration and rebuild patterns."""
        self.config.reload_config()
        self.intent_patterns = self._build_intent_patterns()
        
        if self.config.is_debugging_enabled():
            logger.info(f"GGUF Post-Processor config reloaded, {len(self.intent_patterns)} patterns")


def test_post_processor():
    """Test the post-processor with common scenarios."""
    processor = GGUFResponsePostProcessor()
    
    test_cases = [
        {
            "user_input": "what is the current directory",
            "model_response": "The current working directory is /path/to/your/project",
            "expected_tool": "run_bash"
        },
        {
            "user_input": "pwd", 
            "model_response": '{"response": "The current directory is /path/to/project"}',
            "expected_tool": "run_bash"
        },
        {
            "user_input": "list files",
            "model_response": "I can help you list the files in the current directory",
            "expected_tool": "list_dir"
        },
        {
            "user_input": "create a file called test.txt",
            "model_response": "I'll create that file for you",
            "expected_tool": "write_file"
        }
    ]
    
    print("Testing GGUF Response Post-Processor:")
    print("=" * 50)
    print(f"Post-processing enabled: {processor.config.is_post_processing_enabled()}")
    print(f"Available patterns: {len(processor.intent_patterns)}")
    print(f"Supported intents: {', '.join(processor.get_supported_intents())}")
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {test['user_input']}")
        print(f"Model Response: {test['model_response']}")
        
        tool_calls, clean_response = processor.process_response(
            test['user_input'], 
            test['model_response']
        )
        
        if tool_calls:
            print(f"✅ Generated Tool Call: {tool_calls[0]}")
            corrected = processor.create_corrected_response(tool_calls)
            print(f"✅ Corrected Format: {corrected}")
        else:
            print("❌ No tool call generated")
        
        # Diagnosis
        diagnosis = processor.diagnose_response(test['user_input'], test['model_response'])
        print(f"Should Process: {diagnosis['should_process']}")
        print(f"Matched Intent: {diagnosis['matched_intent']}")


if __name__ == "__main__":
    test_post_processor()
