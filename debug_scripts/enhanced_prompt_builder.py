"""
Enhanced GGUF Tool Prompt Builder - FIXED VERSION

This fixes the issue where GGUF models return generic responses instead of tool calls.
The fix includes more emphatic instructions and clearer examples.
"""

from typing import Dict, Any, List, Optional
from services.tool_registry import tool_registry, ToolCategory, ToolPermission


class EnhancedGGUFToolPromptBuilder:
    """
    Enhanced prompt builder with stronger tool call instructions.
    """
    
    def __init__(self):
        self.tool_call_format = "<tool_call>{function_name}({arguments})</tool_call>"
        
        # Enhanced examples with more emphatic format
        self.core_examples = [
            {
                "user": "pwd",
                "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>"
            },
            {
                "user": "What is the current directory?",
                "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>"
            },
            {
                "user": "ls -la",
                "assistant": "<tool_call>run_bash({\"command\": \"ls -la\"})</tool_call>"
            },
            {
                "user": "Create a file called hello.txt with content 'Hello World'",
                "assistant": "<tool_call>write_file({\"path\": \"hello.txt\", \"content\": \"Hello World\"})</tool_call>"
            },
            {
                "user": "List the files in the current directory",
                "assistant": "<tool_call>list_dir({\"path\": \".\"})</tool_call>"
            },
            {
                "user": "Read the config.py file",
                "assistant": "<tool_call>read_file({\"path\": \"config.py\"})</tool_call>"
            }
        ]
    
    def build_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                    available_tools: List[Dict[str, Any]]) -> str:
        """Build an enhanced prompt with stronger tool call emphasis."""
        prompt_parts = []
        
        # 1. VERY STRONG system instructions
        prompt_parts.append(self._build_enhanced_system_instructions())
        
        # 2. Clear tool documentation
        prompt_parts.append(self._build_tool_documentation(available_tools))
        
        # 3. Enhanced examples
        prompt_parts.append(self._build_enhanced_examples())
        
        # 4. CRITICAL format reminder
        prompt_parts.append(self._build_format_reminder())
        
        # 5. Conversation history (if any)
        if conversation_history:
            prompt_parts.append(self._format_conversation_history(conversation_history))
        
        # 6. Current user input with format reminder
        prompt_parts.append(f"User: {user_input}")
        prompt_parts.append("Assistant: Remember, you MUST respond with <tool_call>function_name(json_args)</tool_call> format!")
        
        return "\n\n".join(prompt_parts)
    
    def _build_enhanced_system_instructions(self) -> str:
        """Build very strong system instructions."""
        return """🚨 CRITICAL INSTRUCTIONS FOR TOOL CALLING 🚨

You are an AI assistant that MUST use tools to perform actions. You have access to file system tools.

⚠️  ABSOLUTELY CRITICAL: When you need to do anything, you MUST respond with this EXACT format:
<tool_call>function_name({"parameter": "value"})</tool_call>

🚫 NEVER respond with generic text like "The current directory is /path/to/project"
🚫 NEVER respond with JSON blocks like {"response": "some text"}
🚫 NEVER give explanatory text without using tools

✅ ALWAYS use the <tool_call> format
✅ For ANY shell command (pwd, ls, git, etc.), use run_bash tool
✅ Use exact format: <tool_call>run_bash({"command": "actual_command"})</tool_call>

EXAMPLES OF WHAT TO DO:
- User says "pwd" → You respond: <tool_call>run_bash({"command": "pwd"})</tool_call>
- User says "ls" → You respond: <tool_call>run_bash({"command": "ls"})</tool_call>
- User says "create file" → You respond: <tool_call>write_file({"path": "filename", "content": "content"})</tool_call>

EXAMPLES OF WHAT NOT TO DO:
❌ {"response": "The current directory is /path/to/project"}
❌ "I can help you with that. The current directory is..."
❌ Any response without <tool_call> tags"""
    
    def _build_tool_documentation(self, available_tools: List[Dict[str, Any]]) -> str:
        """Build tool documentation."""
        if not available_tools:
            return "No tools available."
        
        doc_parts = ["📚 AVAILABLE TOOLS:"]
        
        for tool in available_tools:
            function_def = tool.get("function", {})
            name = function_def.get("name", "unknown")
            description = function_def.get("description", "No description")
            
            doc_parts.append(f"🔧 {name}: {description}")
        
        return "\n".join(doc_parts)
    
    def _build_enhanced_examples(self) -> str:
        """Build enhanced examples with strong format emphasis."""
        example_parts = ["🎯 EXACT EXAMPLES TO FOLLOW:"]
        example_parts.append("(Copy this format exactly!)")
        example_parts.append("")
        
        for i, example in enumerate(self.core_examples, 1):
            example_parts.append(f"Example {i}:")
            example_parts.append(f"User: {example['user']}")
            example_parts.append(f"Assistant: {example['assistant']}")
            example_parts.append("")
        
        return "\n".join(example_parts)
    
    def _build_format_reminder(self) -> str:
        """Build format reminder."""
        return """🔴 FORMAT REMINDER:
Your response MUST start with <tool_call> and end with </tool_call>
Use this exact pattern: <tool_call>function_name({"param": "value"})</tool_call>
No explanations, no JSON blocks, just the tool call."""
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history."""
        if not history:
            return ""
        
        formatted_parts = ["📝 Previous conversation:"]
        
        for message in history[-4:]:  # Keep last 4 messages
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            if role == "user":
                formatted_parts.append(f"User: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
        
        return "\n".join(formatted_parts)


def test_enhanced_prompt():
    """Test the enhanced prompt builder."""
    builder = EnhancedGGUFToolPromptBuilder()
    
    # Mock available tools for testing
    mock_tools = [
        {
            "function": {
                "name": "run_bash",
                "description": "Execute shell commands"
            }
        },
        {
            "function": {
                "name": "write_file", 
                "description": "Write content to a file"
            }
        }
    ]
    
    # Test pwd command
    prompt = builder.build_prompt("pwd", [], mock_tools)
    
    print("Enhanced Prompt for 'pwd':")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    # Check if key elements are present
    checks = [
        ("Contains run_bash", "run_bash" in prompt),
        ("Contains tool_call format", "<tool_call>" in prompt),
        ("Contains pwd example", "pwd" in prompt),
        ("Has strong instructions", "CRITICAL" in prompt),
        ("Has format reminder", "FORMAT REMINDER" in prompt)
    ]
    
    print("\nPrompt Analysis:")
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    return prompt


if __name__ == "__main__":
    test_enhanced_prompt()
