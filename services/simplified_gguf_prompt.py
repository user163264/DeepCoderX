"""
Simplified NLP System for DeepCoderX - Coding-Only Focus

Binary classification: Tools needed vs Explanation needed
Optimized for minimal prompt overhead and fast routing decisions.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class SimplifiedCodingNLP:
    """
    Simplified NLP classifier for coding-only assistant.
    
    Binary decision: Does this need tools or just an explanation?
    """
    
    def __init__(self):
        """Initialize with coding-focused patterns."""
        
        # Direct command patterns - definitely need tools
        self.direct_commands = {
            "pwd", "ls", "cd", "mkdir", "rm", "cp", "mv", "cat", "echo", "touch",
            "git", "python", "node", "npm", "pip", "make", "gcc", "javac"
        }
        
        # File operation patterns - need tools
        self.file_operations = {
            "create file", "read file", "write file", "delete file", "move file",
            "copy file", "list files", "show files", "file contents",
            "current directory", "show directory", "directory contents"
        }
        
        # Question patterns - explanations only
        self.explanation_patterns = {
            "what is", "what does", "how does", "why does", "how to",
            "explain", "tell me about", "help me understand", "difference between",
            "can you explain", "what's the difference"
        }
        
        # File extensions that indicate file operations
        self.file_extensions = {".py", ".js", ".html", ".css", ".txt", ".md", ".json", ".yaml", ".yml"}
        
        # Command shortcuts for direct conversion
        self.command_shortcuts = {
            "pwd": 'run_bash({"command": "pwd"})',
            "ls": 'run_bash({"command": "ls"})',
            "ls -la": 'run_bash({"command": "ls -la"})',
            "ls -l": 'run_bash({"command": "ls -l"})',
            "git status": 'run_bash({"command": "git status"})',
            "current directory": 'run_bash({"command": "pwd"})',
            "list files": 'list_dir({"path": "."})',
            "show files": 'list_dir({"path": "."})'
        }
    
    def classify_request(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify request into tool_required or explanation_required.
        
        Args:
            user_input: User's input text
            
        Returns:
            Tuple of (classification, metadata)
            classification: "tool_required" or "explanation_required"
            metadata: Additional information for prompt building
        """
        input_lower = user_input.lower().strip()
        
        # Check for direct command shortcuts
        if input_lower in self.command_shortcuts:
            return "tool_required", {
                "type": "direct_command", 
                "shortcut": self.command_shortcuts[input_lower],
                "confidence": "high"
            }
        
        # Check for direct commands (pwd, ls, git, etc.)
        words = input_lower.split()
        if words and words[0] in self.direct_commands:
            return "tool_required", {
                "type": "shell_command",
                "command": user_input.strip(),
                "confidence": "high"
            }
        
        # Check for file operations
        for pattern in self.file_operations:
            if pattern in input_lower:
                return "tool_required", {
                    "type": "file_operation",
                    "pattern": pattern,
                    "confidence": "high"
                }
        
        # Check for file extensions or paths
        if self._has_file_indicator(user_input):
            return "tool_required", {
                "type": "file_reference",
                "confidence": "medium"
            }
        
        # Check for explanation patterns
        for pattern in self.explanation_patterns:
            if pattern in input_lower:
                return "explanation_required", {
                    "type": "explanation",
                    "pattern": pattern,
                    "confidence": "high"
                }
        
        # Check if it's a question
        if user_input.strip().endswith('?'):
            return "explanation_required", {
                "type": "question",
                "confidence": "medium"
            }
        
        # Default: if unclear, assume explanation for safety
        # (Better to over-explain than execute wrong commands)
        return "explanation_required", {
            "type": "default",
            "confidence": "low"
        }
    
    def _has_file_indicator(self, text: str) -> bool:
        """Check if text contains file paths or extensions."""
        # File extensions
        for ext in self.file_extensions:
            if ext in text:
                return True
        
        # Path indicators
        if any(indicator in text for indicator in ['/', './', '../', '\\']):
            return True
            
        return False
    
    def build_minimal_prompt(self, user_input: str, classification: str, 
                           metadata: Dict[str, Any], available_tools: List[Dict[str, Any]] = None) -> str:
        """
        Build minimal prompt based on classification.
        
        Args:
            user_input: User's input
            classification: "tool_required" or "explanation_required"
            metadata: Classification metadata
            available_tools: Available tools (only used for tool_required)
            
        Returns:
            Minimal prompt optimized for the specific classification
        """
        if classification == "tool_required":
            return self._build_tool_prompt(user_input, metadata, available_tools or [])
        else:
            return self._build_explanation_prompt(user_input, metadata)
    
    def _build_tool_prompt(self, user_input: str, metadata: Dict[str, Any], 
                          available_tools: List[Dict[str, Any]]) -> str:
        """Build minimal prompt for tool usage."""
        
        # Check for direct shortcuts first
        if metadata.get("type") == "direct_command":
            # For direct commands, just provide the tool call format
            return f"""You are a coding assistant. Use tools for operations.

Tool format: <tool_call>function_name({{"parameter": "value"}})</tool_call>

User: {user_input}
Assistant: <tool_call>{metadata["shortcut"]}</tool_call>"""
        
        # Standard tool prompt
        prompt = """You are a coding assistant with system access.

Tool format: <tool_call>function_name({"parameter": "value"})</tool_call>

Essential tools:
- run_bash({"command": "command"}) - Shell commands
- read_file({"path": "file"}) - Read files  
- write_file({"path": "file", "content": "text"}) - Create/write files
- list_dir({"path": "."}) - List directory contents

Examples:
User: pwd
Assistant: <tool_call>run_bash({"command": "pwd"})</tool_call>

User: create main.py
Assistant: <tool_call>write_file({"path": "main.py", "content": "# Main script\\n"})</tool_call>"""
        
        prompt += f"\n\nUser: {user_input}\nAssistant:"
        
        return prompt
    
    def _build_explanation_prompt(self, user_input: str, metadata: Dict[str, Any]) -> str:
        """Build minimal prompt for explanations."""
        
        return f"""You are a helpful coding assistant. Provide clear, concise explanations about programming concepts and technical topics.

User: {user_input}
Assistant:"""
    
    def get_prompt_size_estimate(self, classification: str) -> int:
        """Get estimated prompt size for classification type."""
        if classification == "tool_required":
            return 600  # Tool prompts with examples
        else:
            return 150  # Simple explanation prompts
    
    def process_with_shortcuts(self, user_input: str) -> Optional[str]:
        """
        Check if input can be handled directly with shortcuts.
        
        Returns:
            Direct tool call string if shortcut available, None otherwise
        """
        input_lower = user_input.lower().strip()
        return self.command_shortcuts.get(input_lower)


class SimplifiedGGUFPromptBuilder:
    """
    Simplified GGUF prompt builder for coding-only assistant.
    
    Replaces the complex semantic system with fast binary classification.
    """
    
    def __init__(self):
        """Initialize simplified builder."""
        self.nlp = SimplifiedCodingNLP()
        logger.info("Simplified GGUF Prompt Builder initialized")
    
    def build_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]] = None,
                    available_tools: List[Dict[str, Any]] = None) -> str:
        """
        Build optimized prompt with minimal overhead.
        
        Args:
            user_input: User's input
            conversation_history: Previous conversation (limited use)
            available_tools: Available tools
            
        Returns:
            Optimized prompt string
        """
        # Check for direct shortcuts first
        shortcut = self.nlp.process_with_shortcuts(user_input)
        if shortcut:
            return f"<tool_call>{shortcut}</tool_call>"
        
        # Classify the request
        classification, metadata = self.nlp.classify_request(user_input)
        
        # Build minimal prompt
        prompt = self.nlp.build_minimal_prompt(
            user_input, classification, metadata, available_tools
        )
        
        # Add minimal conversation context if relevant and available
        if conversation_history and len(conversation_history) > 0:
            # Only add last interaction for context
            last_msg = conversation_history[-1]
            if isinstance(last_msg, dict) and "content" in last_msg:
                context_line = f"Previous: {last_msg['content'][:100]}..."
                prompt = prompt.replace("User:", f"{context_line}\n\nUser:")
        
        logger.debug(f"Built {classification} prompt ({len(prompt)} chars) for: {user_input[:50]}...")
        
        return prompt
    
    def get_classification(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Get classification for debugging/monitoring."""
        return self.nlp.classify_request(user_input)


# Convenience function to replace the existing complex system
def build_simple_gguf_prompt(user_input: str, conversation_history: List[Dict[str, Any]] = None,
                            available_tools: List[Dict[str, Any]] = None) -> str:
    """
    Simple function to build GGUF prompts with minimal overhead.
    
    Replaces the complex GGUFToolPromptBuilder system.
    """
    builder = SimplifiedGGUFPromptBuilder()
    return builder.build_prompt(user_input, conversation_history, available_tools)


if __name__ == "__main__":
    # Test the simplified system
    print("SIMPLIFIED CODING NLP TEST")
    print("=" * 40)
    
    builder = SimplifiedGGUFPromptBuilder()
    
    test_inputs = [
        "pwd",
        "create main.py", 
        "what is Python?",
        "explain recursion",
        "ls -la",
        "git status",
        "how does git work?",
        "list files"
    ]
    
    for test_input in test_inputs:
        classification, metadata = builder.get_classification(test_input)
        prompt = builder.build_prompt(test_input)
        
        print(f"\nInput: '{test_input}'")
        print(f"Classification: {classification} ({metadata['confidence']} confidence)")
        print(f"Prompt size: {len(prompt)} characters")
        print(f"Type: {metadata['type']}")
        print("-" * 40)
