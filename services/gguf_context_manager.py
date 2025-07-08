"""
GGUF Context Manager for DeepCoderX

This module handles conversation history, token management, and context window
optimization for GGUF models that require manual context management.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from utils.logging import console


@dataclass
class ConversationMessage:
    """Represents a conversation message with metadata."""
    role: str  # "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    timestamp: Optional[float] = None
    token_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "role": self.role,
            "content": self.content
        }
        
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.timestamp:
            result["timestamp"] = self.timestamp
        if self.token_count:
            result["token_count"] = self.token_count
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            tool_calls=data.get("tool_calls"),
            tool_call_id=data.get("tool_call_id"),
            timestamp=data.get("timestamp"),
            token_count=data.get("token_count")
        )


class GGUFContextManager:
    """
    Manages conversation history and context for GGUF models.
    
    Features:
    - Manual conversation history tracking
    - Token counting and context window management
    - Intelligent context truncation
    - Tool result integration
    - Session persistence
    """
    
    def __init__(self, provider_name: str = "local", session_dir: Path = None):
        self.provider_name = provider_name
        self.session_dir = session_dir or Path(".deepcoderx")
        self.session_file = self.session_dir / f"{provider_name}_gguf_session.json"
        
        # Context management settings
        self.max_context_tokens = 4000  # Conservative limit for most GGUF models
        self.max_history_messages = 20  # Maximum number of messages to keep
        self.tokens_per_char = 0.25  # Rough estimation: 1 token per 4 characters
        
        # Conversation state
        self.messages: List[ConversationMessage] = []
        self.total_tokens = 0
        
        # Load existing session
        self._load_session()
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        import time
        
        message = ConversationMessage(
            role="user",
            content=content,
            timestamp=time.time(),
            token_count=self._estimate_tokens(content)
        )
        
        self.messages.append(message)
        self.total_tokens += message.token_count
        self._manage_context_window()
    
    def add_assistant_message(self, content: str, tool_calls: List[Dict[str, Any]] = None) -> None:
        """Add an assistant message to the conversation."""
        import time
        
        message = ConversationMessage(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
            timestamp=time.time(),
            token_count=self._estimate_tokens(content)
        )
        
        self.messages.append(message)
        self.total_tokens += message.token_count
        self._manage_context_window()
    
    def add_tool_results(self, tool_calls: List[Dict[str, Any]], results: List[str]) -> None:
        """Add tool execution results to the conversation."""
        import time
        
        # Add each tool result as a separate message
        for i, (tool_call, result) in enumerate(zip(tool_calls, results)):
            tool_call_id = f"call_{tool_call.get('function_name', 'unknown')}_{i}"
            
            message = ConversationMessage(
                role="tool",
                content=str(result),
                tool_call_id=tool_call_id,
                timestamp=time.time(),
                token_count=self._estimate_tokens(str(result))
            )
            
            self.messages.append(message)
            self.total_tokens += message.token_count
        
        self._manage_context_window()
    
    def get_conversation_history(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """
        Get conversation history in a format suitable for prompt building.
        
        Args:
            include_system: Whether to include system messages
            
        Returns:
            List of message dictionaries
        """
        history = []
        
        for message in self.messages:
            # Skip system messages if not requested
            if not include_system and message.role == "system":
                continue
            
            history.append(message.to_dict())
        
        return history
    
    def get_recent_context(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [msg.to_dict() for msg in recent_messages]
    
    def get_token_count(self) -> int:
        """Get current total token count."""
        return self.total_tokens
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context state."""
        return {
            "total_messages": len(self.messages),
            "total_tokens": self.total_tokens,
            "max_context_tokens": self.max_context_tokens,
            "context_utilization": self.total_tokens / self.max_context_tokens,
            "recent_messages": len([msg for msg in self.messages[-5:]]),
            "tool_messages": len([msg for msg in self.messages if msg.role == "tool"]),
            "session_file": str(self.session_file)
        }
    
    def truncate_context(self, target_tokens: int = None) -> int:
        """
        Truncate context to fit within token limits.
        
        Args:
            target_tokens: Target token count (defaults to 80% of max)
            
        Returns:
            Number of messages removed
        """
        if target_tokens is None:
            target_tokens = int(self.max_context_tokens * 0.8)
        
        messages_removed = 0
        
        # Always keep the most recent message
        if len(self.messages) <= 1:
            return 0
        
        # Remove oldest messages until we're under the target
        while self.total_tokens > target_tokens and len(self.messages) > 1:
            removed_message = self.messages.pop(0)
            self.total_tokens -= removed_message.token_count or 0
            messages_removed += 1
        
        if messages_removed > 0:
            console.print(f"[yellow]Context truncated: removed {messages_removed} old messages[/]")
        
        return messages_removed
    
    def clear_history(self) -> None:
        """Clear all conversation history."""
        self.messages.clear()
        self.total_tokens = 0
        
        # Delete session file
        if self.session_file.exists():
            self.session_file.unlink()
        
        console.print(f"[bold red]GGUF conversation history cleared for {self.provider_name}[/]")
    
    def save_session(self) -> None:
        """Save conversation history to session file."""
        try:
            self.session_dir.mkdir(parents=True, exist_ok=True)
            
            session_data = {
                "provider_name": self.provider_name,
                "total_tokens": self.total_tokens,
                "max_context_tokens": self.max_context_tokens,
                "messages": [msg.to_dict() for msg in self.messages],
                "metadata": {
                    "last_saved": __import__("time").time(),
                    "message_count": len(self.messages)
                }
            }
            
            with open(self.session_file, "w") as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            console.print(f"[red]Warning: Failed to save GGUF session: {e}[/]")
    
    def _load_session(self) -> None:
        """Load conversation history from session file."""
        if not self.session_file.exists():
            return
        
        try:
            with open(self.session_file, "r") as f:
                session_data = json.load(f)
            
            # Validate session data
            if session_data.get("provider_name") != self.provider_name:
                console.print(f"[yellow]Warning: Session provider mismatch, starting fresh[/]")
                return
            
            # Load messages
            self.messages = [
                ConversationMessage.from_dict(msg_data)
                for msg_data in session_data.get("messages", [])
            ]
            
            # Recalculate token count
            self.total_tokens = sum(msg.token_count or 0 for msg in self.messages)
            
            # Update max context tokens if stored in session
            if "max_context_tokens" in session_data:
                self.max_context_tokens = session_data["max_context_tokens"]
            
        except Exception as e:
            console.print(f"[red]Warning: Failed to load GGUF session: {e}[/]")
            self.messages.clear()
            self.total_tokens = 0
    
    def _manage_context_window(self) -> None:
        """Automatically manage context window size."""
        # Check if we're approaching context limits
        if self.total_tokens > self.max_context_tokens:
            self.truncate_context()
        
        # Also limit by message count
        if len(self.messages) > self.max_history_messages:
            excess_messages = len(self.messages) - self.max_history_messages
            for _ in range(excess_messages):
                if len(self.messages) > 1:  # Keep at least one message
                    removed_message = self.messages.pop(0)
                    self.total_tokens -= removed_message.token_count or 0
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        if not text:
            return 0
        
        # Simple estimation: roughly 1 token per 4 characters
        # This is conservative for most models
        return max(1, int(len(text) * self.tokens_per_char))
    
    def optimize_for_new_request(self, user_input: str, expected_response_tokens: int = 500) -> None:
        """
        Optimize context for a new request by ensuring enough space.
        
        Args:
            user_input: The new user input
            expected_response_tokens: Expected tokens in response
        """
        input_tokens = self._estimate_tokens(user_input)
        required_space = input_tokens + expected_response_tokens
        
        # If we don't have enough space, truncate proactively
        available_space = self.max_context_tokens - self.total_tokens
        if available_space < required_space:
            target_tokens = self.max_context_tokens - required_space - 100  # Buffer
            self.truncate_context(target_tokens)
    
    def get_context_for_prompt(self, max_history_chars: int = 2000) -> str:
        """
        Get conversation history formatted for inclusion in prompts.
        
        Args:
            max_history_chars: Maximum characters to include
            
        Returns:
            Formatted conversation history
        """
        if not self.messages:
            return ""
        
        # Get recent messages that fit within character limit
        history_parts = []
        char_count = 0
        
        for message in reversed(self.messages):
            formatted_msg = self._format_message_for_prompt(message)
            
            if char_count + len(formatted_msg) > max_history_chars and history_parts:
                break
            
            history_parts.insert(0, formatted_msg)
            char_count += len(formatted_msg)
        
        if history_parts:
            return "\n".join(history_parts)
        else:
            return ""
    
    def _format_message_for_prompt(self, message: ConversationMessage) -> str:
        """Format a message for inclusion in prompts."""
        if message.role == "user":
            return f"User: {message.content}"
        elif message.role == "assistant":
            return f"Assistant: {message.content}"
        elif message.role == "tool":
            return f"Tool result: {message.content}"
        else:
            return f"{message.role}: {message.content}"


# Convenience functions for easy integration
def create_gguf_context_manager(provider_name: str = "local") -> GGUFContextManager:
    """Create a GGUF context manager instance."""
    return GGUFContextManager(provider_name)


def get_conversation_summary(provider_name: str = "local") -> Dict[str, Any]:
    """Get a summary of conversation state for a provider."""
    manager = GGUFContextManager(provider_name)
    return manager.get_context_summary()
