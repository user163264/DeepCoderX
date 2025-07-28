"""
GGUF Tool Prompt Builder for DeepCoderX - LLAMA OPTIMIZED

Semantic-first approach for Llama models with intelligent intent classification.
Clean, conversation-aware system that routes appropriately between natural conversation
and tool usage based on semantic understanding.
"""

from typing import Dict, Any, List, Optional
import logging
from services.tool_registry import tool_registry, ToolCategory, ToolPermission

logger = logging.getLogger(__name__)


class LlamaSemanticPromptBuilder:
    """
    Semantic-first prompt builder optimized for Llama models.
    
    Features:
    - Intelligent conversation vs tool routing
    - Clean, semantic-based prompting
    - Llama chat template compatibility
    - Context-aware response generation
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the Llama-optimized prompt builder."""
        self.model_name = model_name or "llama"
        self.tool_call_format = "<tool_call>{function_name}({arguments})</tool_call>"
        
        logger.info(f"Llama Semantic Prompt Builder initialized for: {self.model_name}")
        
    def build_semantic_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                            available_tools: List[Dict[str, Any]]) -> str:
        """
        Build semantically-aware prompt that routes appropriately between conversation and tools.
        
        Args:
            user_input: Current user input
            conversation_history: Previous conversation context
            available_tools: Available tool definitions
            
        Returns:
            Semantically optimized prompt
        """
        # Semantic analysis - determine if this requires tools or conversation
        requires_tools = self._semantic_analysis(user_input)
        
        if requires_tools:
            return self._build_tool_oriented_prompt(user_input, conversation_history, available_tools)
        else:
            return self._build_conversational_prompt(user_input, conversation_history)
    
    def _semantic_analysis(self, user_input: str) -> bool:
        """
        Analyze user input semantically to determine if tools are needed.
        
        Returns:
            True if tools should be used, False for conversational response
        """
        input_lower = user_input.lower().strip()
        
        # File system operations - definitely need tools
        fs_indicators = [
            'pwd', 'ls', 'cd', 'mkdir', 'rm', 'cp', 'mv',
            'cat', 'echo', 'touch', 'find', 'grep',
            'current directory', 'list files', 'create file',
            'delete file', 'move file', 'copy file',
            'show contents', 'file contents', 'directory contents'
        ]
        
        # Development operations - need tools
        dev_indicators = [
            'git', 'python', 'node', 'npm', 'pip',
            'run script', 'execute', 'compile',
            'install', 'build', 'test',
            'create project', 'scaffold'
        ]
        
        # File path patterns - need tools
        has_file_path = ('/' in user_input or 
                        user_input.endswith(('.py', '.js', '.txt', '.md', '.json', '.yaml', '.yml')) or
                        '.' in user_input and not user_input.endswith('?'))
        
        # Check for tool-requiring patterns
        for indicator in fs_indicators + dev_indicators:
            if indicator in input_lower:
                return True
                
        # Check for file paths
        if has_file_path and not self._is_conversational(user_input):
            return True
            
        # Default to conversation for unclear cases
        return False
    
    def _is_conversational(self, user_input: str) -> bool:
        """Check if input is clearly conversational."""
        input_lower = user_input.lower().strip()
        
        conversational_patterns = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon',
            'how are you', 'what are you', 'who are you',
            'what is', 'what are', 'how does', 'why does',
            'can you explain', 'tell me about', 'help me understand',
            'thank you', 'thanks', 'bye', 'goodbye'
        ]
        
        for pattern in conversational_patterns:
            if input_lower.startswith(pattern) or pattern in input_lower:
                return True
                
        # Questions that end with '?' are often conversational
        if user_input.strip().endswith('?') and len(user_input.split()) <= 10:
            return True
            
        return False
    
    def _build_conversational_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]]) -> str:
        """Build prompt for conversational responses."""
        prompt_parts = []
        
        # System instructions for conversation
        prompt_parts.append("""You are a helpful AI coding assistant. 

Respond naturally and conversationally to greetings, questions, and general chat.
Be friendly, informative, and helpful.

For coding questions or explanations, provide clear, accurate information.
Keep responses concise but informative.""")
        
        # Add relevant conversation history
        if conversation_history:
            history_parts = ["Previous conversation:"]
            for msg in conversation_history[-4:]:  # Last 4 messages for context
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role in ["user", "assistant"]:
                    history_parts.append(f"{role.title()}: {content}")
            prompt_parts.append("\n".join(history_parts))
        
        # User input
        prompt_parts.append(f"User: {user_input}")
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def _build_tool_oriented_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                                  available_tools: List[Dict[str, Any]]) -> str:
        """Build prompt for tool-requiring tasks."""
        prompt_parts = []
        
        # System instructions for tool usage
        prompt_parts.append("""You are a helpful AI coding assistant with access to system tools.

For file operations, directory commands, and coding tasks, use the appropriate tools.

Tool call format: <tool_call>function_name({"parameter": "value"})</tool_call>

CRITICAL: All tool calls must include JSON parameters in curly braces.
For shell commands, use: run_bash({"command": "your_command"})

Respond with tool calls only - no explanatory text needed for simple operations.""")
        
        # Tool documentation
        if available_tools:
            tool_docs = self._build_clean_tool_docs(available_tools)
            prompt_parts.append(tool_docs)
        
        # Examples
        prompt_parts.append("""
IMPORTANT: Tool calls MUST include proper JSON parameters!

Examples:

User: pwd
Assistant: <tool_call>run_bash({"command": "pwd"})</tool_call>

User: ls
Assistant: <tool_call>run_bash({"command": "ls"})</tool_call>

User: ls -la
Assistant: <tool_call>run_bash({"command": "ls -la"})</tool_call>

User: list files
Assistant: <tool_call>list_dir({"path": "."})</tool_call>

User: create hello.py
Assistant: <tool_call>write_file({"path": "hello.py", "content": "print('Hello, World!')"})</tool_call>

User: show directory contents
Assistant: <tool_call>list_dir({"path": "."})</tool_call>

For shell commands: Always use run_bash with command parameter
For directory listing: Use list_dir OR run_bash
For file creation: Use write_file with path and content parameters""")
        
        # Conversation context if relevant
        if conversation_history:
            recent_context = []
            for msg in conversation_history[-3:]:  # Last 3 for recent context
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role in ["user", "assistant"]:
                    recent_context.append(f"{role.title()}: {content}")
            if recent_context:
                prompt_parts.append("Recent context:\n" + "\n".join(recent_context))
        
        # User input
        prompt_parts.append(f"User: {user_input}")
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    def _build_clean_tool_docs(self, available_tools: List[Dict[str, Any]]) -> str:
        """Build clean, concise tool documentation."""
        if not available_tools:
            return "No tools available."
        
        doc_parts = ["Available tools:"]
        
        for tool in available_tools:
            function_def = tool.get("function", {})
            name = function_def.get("name", "unknown")
            description = function_def.get("description", "")
            
            # Keep descriptions concise
            if len(description) > 80:
                description = description[:77] + "..."
            
            doc_parts.append(f"- {name}: {description}")
        
        return "\n".join(doc_parts)


class GGUFToolPromptBuilder:
    """
    Main GGUF Tool Prompt Builder with Llama optimization.
    
    Provides clean, semantic-first prompting for Llama models.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize with Llama optimization."""
        self.model_name = model_name or "llama"
        self.semantic_builder = LlamaSemanticPromptBuilder(model_name)
        
        logger.info(f"GGUF Tool Prompt Builder initialized for: {self.model_name}")
    
    def build_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                    available_tools: List[Dict[str, Any]], 
                    last_response_success: bool = True) -> str:
        """
        Build semantically-aware prompt.
        
        Args:
            user_input: Current user input
            conversation_history: Previous conversation
            available_tools: Available tools
            last_response_success: Unused in semantic approach
            
        Returns:
            Optimized prompt string
        """
        return self.semantic_builder.build_semantic_prompt(
            user_input, conversation_history, available_tools
        )
    
    def get_tools_for_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        """Get appropriate tools for a GGUF provider."""
        if provider_name == "local":
            max_permission = ToolPermission.SYSTEM_ACCESS
        else:
            max_permission = ToolPermission.WRITE_ALLOWED
        
        return tool_registry.get_openai_definitions(max_permissions=max_permission)


# Convenience function
def build_gguf_prompt(user_input: str, conversation_history: List[Dict[str, Any]] = None, 
                     provider_name: str = "local", model_name: str = None,
                     last_response_success: bool = True) -> str:
    """
    Build GGUF prompt with semantic intelligence.
    
    Args:
        user_input: User's input
        conversation_history: Previous conversation
        provider_name: Provider name for tool selection
        model_name: Model name
        last_response_success: Unused in semantic approach
        
    Returns:
        Semantically optimized prompt string
    """
    builder = GGUFToolPromptBuilder(model_name=model_name)
    available_tools = builder.get_tools_for_provider(provider_name)
    
    return builder.build_prompt(
        user_input=user_input,
        conversation_history=conversation_history or [],
        available_tools=available_tools,
        last_response_success=last_response_success
    )


if __name__ == "__main__":
    # Test semantic approach
    print("LLAMA SEMANTIC GGUF PROMPT BUILDER TEST")
    print("=" * 50)
    
    builder = GGUFToolPromptBuilder(model_name="llama-3.2-3b")
    tools = builder.get_tools_for_provider("local")
    
    # Test conversational input
    conv_prompt = builder.build_prompt(
        user_input="hello, how are you?",
        conversation_history=[],
        available_tools=tools
    )
    
    print("Conversational Prompt:")
    print("-" * 30)
    print(conv_prompt)
    print("-" * 30)
    
    # Test tool-requiring input
    tool_prompt = builder.build_prompt(
        user_input="what is the current directory?",
        conversation_history=[],
        available_tools=tools
    )
    
    print("\nTool-Oriented Prompt:")
    print("-" * 30)
    print(tool_prompt)
    print("-" * 30)
