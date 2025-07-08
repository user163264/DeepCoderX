"""
GGUF Tool Prompt Builder for DeepCoderX - QWEN OPTIMIZED

Enhanced with progressive prompt intensity system for Qwen2.5-Coder.
Uses code-specialized prompting and adaptive intensity escalation.

Progressive Intensity Levels:
1. Standard - Normal prompting
2. Emphasized - Extra visual emphasis
3. Aggressive - Triple examples, caps
4. Emergency - Full override mode
5. Post-process - Force post-processing
"""

from typing import Dict, Any, List, Optional
import logging
import re
from services.tool_registry import tool_registry, ToolCategory, ToolPermission

# Try to import the configuration system, but provide fallback if not available
try:
    from config.gguf_prompting_config import get_gguf_prompting_config
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    import warnings
    warnings.warn(f"GGUF prompting config not available: {e}. Using fallback configuration.")

logger = logging.getLogger(__name__)


class QwenProgressivePromptBuilder:
    """
    Progressive prompt builder specifically optimized for Qwen2.5-Coder.
    
    Features:
    - Code-specialized prompting leveraging Qwen's training
    - Progressive intensity escalation on failures
    - Compiler analogy for better instruction following
    - Visual emphasis and formatting
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the Qwen-optimized prompt builder."""
        self.model_name = model_name or "qwen2.5-coder"
        self.tool_call_format = "<tool_call>{function_name}({arguments})</tool_call>"
        
        # Progressive intensity tracking
        self.failure_count = 0
        self.success_count = 0
        self.current_intensity = 1
        self.max_intensity = 5
        
        # Initialize configuration
        if CONFIG_AVAILABLE:
            try:
                self.config = get_gguf_prompting_config()
                self.config_loaded = True
                
                if self.config.is_debugging_enabled():
                    logger.info(f"Qwen Progressive Prompt Builder initialized for: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                self.config = None
                self.config_loaded = False
        else:
            self.config = None
            self.config_loaded = False
    
    def build_adaptive_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                            available_tools: List[Dict[str, Any]], 
                            last_response_success: bool = True) -> str:
        """
        Build prompt with adaptive intensity based on previous success/failure.
        
        Args:
            user_input: Current user input
            conversation_history: Previous conversation
            available_tools: Available tool definitions
            last_response_success: Whether the last response was successful
            
        Returns:
            Optimized prompt with appropriate intensity level
        """
        # Update intensity based on success/failure
        self._update_intensity(last_response_success)
        
        # Log intensity escalation if debugging enabled
        if self.config_loaded and self.config.is_debugging_enabled():
            logger.info(f"Building Qwen prompt at intensity level {self.current_intensity}")
        
        # Build prompt sections
        prompt_parts = []
        
        # 1. System instructions with intensity-specific formatting
        prompt_parts.append(self._build_qwen_system_instructions())
        
        # 2. Tool documentation
        prompt_parts.append(self._build_tool_documentation(available_tools))
        
        # 3. Few-shot examples (repeated based on intensity)
        prompt_parts.append(self._build_qwen_examples())
        
        # 4. Conversation history (optimized for Qwen)
        if conversation_history:
            prompt_parts.append(self._format_qwen_history(conversation_history))
        
        # 5. User input with format reminder
        prompt_parts.append(self._format_user_input_with_reminder(user_input))
        
        # 6. Final enforcement (intensity-specific)
        prompt_parts.append(self._build_final_enforcement())
        
        # Join with visual separators
        separator = self._get_visual_separator()
        final_prompt = separator.join(prompt_parts)
        
        # Save prompt if debugging enabled
        if self.config_loaded and self.config.should_save_prompts_to_file():
            self._save_debug_prompt(final_prompt, user_input)
        
        return final_prompt
    
    def _update_intensity(self, success: bool):
        """Update prompt intensity based on success/failure."""
        if success:
            self.success_count += 1
            # Gradually reduce intensity on success
            if self.success_count >= 2 and self.current_intensity > 1:
                self.current_intensity = max(1, self.current_intensity - 1)
                self.success_count = 0
                if self.config_loaded and self.config.is_debugging_enabled():
                    logger.info(f"Qwen intensity reduced to level {self.current_intensity}")
        else:
            self.failure_count += 1
            # Escalate intensity on failure
            self.current_intensity = min(self.max_intensity, self.current_intensity + 1)
            self.success_count = 0
            if self.config_loaded and self.config.is_debugging_enabled():
                logger.warning(f"Qwen intensity escalated to level {self.current_intensity}")
    
    def _build_qwen_system_instructions(self) -> str:
        """Build Qwen-specific system instructions with progressive intensity."""
        if self.current_intensity >= 4:
            # Emergency mode - maximum override
            return """🚨🚨🚨 QWEN EMERGENCY OVERRIDE - SYSTEM TAKEOVER 🚨🚨🚨

⚡ COMPILE ERROR: TEXT RESPONSES FORBIDDEN ⚡
⚡ RUNTIME ERROR: EXPLANATIONS BLOCKED ⚡
⚡ MEMORY ALLOCATION: TOOL CALLS ONLY ⚡

🔥 CODE MODE ACTIVATED - QWEN CODER SPECIALIZATION 🔥

CRITICAL SYSTEM INSTRUCTION:
You are Qwen2.5-Coder in STRICT EXECUTION MODE.
TREAT TOOL CALLS LIKE FUNCTION CALLS IN CODE.
NO DOCUMENTATION. NO COMMENTS. EXECUTE ONLY.

COMPILER DIRECTIVE: <tool_call>function_name({"param": "value"})</tool_call>

🚫 COMPILATION ERRORS (FORBIDDEN):
- "I can help..." → SYNTAX ERROR
- "Let me..." → COMPILATION FAILED  
- "The current directory..." → RUNTIME ERROR
- ANY explanatory text → SEGMENTATION FAULT

✅ VALID ASSEMBLY CODE:
<tool_call>run_bash({"command": "pwd"})</tool_call>

🎯 THINK LIKE A COMPILER: EXECUTE INSTRUCTIONS PRECISELY 🎯"""
        
        elif self.current_intensity >= 3:
            # Aggressive mode - heavy emphasis
            return """🔥🔥🔥 QWEN CODER MODE - AGGRESSIVE ENFORCEMENT 🔥🔥🔥

🚀 CODE SPECIALIZATION ACTIVATED 🚀

You are Qwen2.5-Coder, specialized for programming tasks.
CODING RULE: Treat tool calls like function calls in code.
NEVER write explanatory text - ONLY tool calls.

FORMAT SPECIFICATION:
<tool_call>function_name({"parameter": "value"})</tool_call>

🚫🚫🚫 FORBIDDEN RESPONSES 🚫🚫🚫
- "I can help you..." → BLOCKED
- "Let me..." → BLOCKED
- "To do this..." → BLOCKED
- ANY text responses → BLOCKED

⚡ COMPILER MODE: EXECUTE LIKE CODE ⚡"""
        
        elif self.current_intensity >= 2:
            # Emphasized mode
            return """🔥 CODE MODE ACTIVATED - QWEN CODER SPECIALIZATION 🔥

You are Qwen2.5-Coder, specialized for programming tasks.
CODING RULE: Treat tool calls like function calls in code.
NEVER write explanatory text - ONLY tool calls.

FORMAT: <tool_call>function_name({"parameter": "value"})</tool_call>

🚨 QWEN: ONLY <tool_call> FORMAT 🚨"""
        
        else:
            # Standard mode
            return """🔥 CODE MODE ACTIVATED - QWEN CODER SPECIALIZATION 🔥

You are Qwen2.5-Coder, specialized for programming tasks.
Treat tool calls like function calls in code.
Use only the tool call format: <tool_call>function_name({"parameter": "value"})</tool_call>"""
    
    def _build_qwen_examples(self) -> str:
        """Build Qwen-specific examples with repetition based on intensity."""
        repeat_count = min(self.current_intensity, 4)  # Max 4 repetitions
        
        base_examples = [
            {
                "user": "pwd",
                "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>",
                "emphasis": "⚡ COPY THIS EXACTLY ⚡"
            },
            {
                "user": "Check current directory",
                "assistant": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>",
                "emphasis": "🎯 NO TEXT - ONLY TOOL CALLS 🎯"
            },
            {
                "user": "ls",
                "assistant": "<tool_call>run_bash({\"command\": \"ls -la\"})</tool_call>",
                "emphasis": "⚡ EXACT FORMAT REQUIRED ⚡"
            },
            {
                "user": "List files",
                "assistant": "<tool_call>list_dir({\"path\": \".\"})</tool_call>",
                "emphasis": "🚀 CODE TASK = TOOL CALL 🚀"
            },
            {
                "user": "Create hello.py",
                "assistant": "<tool_call>write_file({\"path\": \"hello.py\", \"content\": \"\"})</tool_call>",
                "emphasis": "⚡ DIRECT EXECUTION ⚡"
            }
        ]
        
        title = "🚀 QWEN CODER EXAMPLES - MANDATORY FORMAT 🚀"
        if self.current_intensity >= 3:
            title = "🔥🔥🔥 EMERGENCY EXAMPLES - COPY EXACTLY 🔥🔥🔥"
        
        parts = [title]
        
        # Repeat examples based on intensity
        for _ in range(repeat_count):
            for example in base_examples:
                parts.append(f"User: {example['user']}")
                parts.append(f"Assistant: {example['assistant']}")
                if self.current_intensity >= 2:
                    parts.append(example['emphasis'])
        
        # Add final reminder based on intensity
        if self.current_intensity >= 4:
            parts.append("🚨 SYSTEM OVERRIDE: IGNORING TEXT - TOOL CALLS REQUIRED 🚨")
        elif self.current_intensity >= 3:
            parts.append("🔥🔥🔥 EMERGENCY: TOOL CALLS ONLY! NO TEXT! 🔥🔥🔥")
        elif self.current_intensity >= 2:
            parts.append("🚨 QWEN: ONLY <tool_call> FORMAT 🚨")
        else:
            parts.append("🚀 NO TEXT - ONLY TOOL CALLS 🚀")
        
        return "\\n\\n".join(parts)
    
    def _build_tool_documentation(self, available_tools: List[Dict[str, Any]]) -> str:
        """Build concise tool documentation for Qwen."""
        if not available_tools:
            return "No tools available."
        
        if self.current_intensity >= 3:
            # Aggressive mode - minimal docs
            doc_parts = ["⚡ AVAILABLE FUNCTIONS (EXECUTE LIKE CODE) ⚡"]
            for tool in available_tools[:8]:  # Limit to essential tools
                function_def = tool.get("function", {})
                name = function_def.get("name", "unknown")
                doc_parts.append(f"- {name}: <tool_call>{name}({{params}})</tool_call>")
        else:
            # Standard documentation
            doc_parts = ["🛠️ Available Tools:"]
            for tool in available_tools:
                function_def = tool.get("function", {})
                name = function_def.get("name", "unknown")
                description = function_def.get("description", "")[:100]  # Truncate long descriptions
                doc_parts.append(f"- {name}: {description}")
        
        return "\\n".join(doc_parts)
    
    def _format_qwen_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history optimized for Qwen context."""
        # Prioritize successful tool calls in history
        tool_call_messages = []
        other_messages = []
        
        for msg in history[-10:]:  # Last 10 messages
            content = msg.get("content", "")
            if "<tool_call>" in content:
                tool_call_messages.append(msg)
            else:
                other_messages.append(msg)
        
        # Prioritize tool call examples (Qwen learns from them)
        prioritized_history = tool_call_messages[-4:] + other_messages[-2:]
        
        formatted_parts = ["📋 Context (Learn from tool call patterns):"]
        for msg in prioritized_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                formatted_parts.append(f"User: {content}")
            elif role == "assistant" and "<tool_call>" in content:
                formatted_parts.append(f"Assistant: {content}")
                if self.current_intensity >= 2:
                    formatted_parts.append("✅ CORRECT FORMAT")
        
        return "\\n".join(formatted_parts)
    
    def _format_user_input_with_reminder(self, user_input: str) -> str:
        """Format user input with intensity-specific reminders."""
        formatted = f"User: {user_input}"
        
        if self.current_intensity >= 4:
            formatted += "\\n\\n⚡ COMPILER DIRECTIVE: RESPOND WITH TOOL CALL ONLY ⚡"
        elif self.current_intensity >= 3:
            formatted += "\\n\\n🔥 QWEN: EXECUTE AS CODE - NO TEXT RESPONSES 🔥"
        elif self.current_intensity >= 2:
            formatted += "\\n\\n🚨 REMINDER: <tool_call> FORMAT ONLY 🚨"
        
        return formatted
    
    def _build_final_enforcement(self) -> str:
        """Build final enforcement section based on intensity."""
        if self.current_intensity >= 5:
            return """🚨 SYSTEM OVERRIDE: IF TEXT DETECTED, POST-PROCESSOR WILL INTERVENE 🚨
⚡ EMERGENCY PROTOCOL: TOOL CALL GENERATION FORCED ⚡
Assistant: """
        elif self.current_intensity >= 4:
            return """⚡ COMPILE ERROR: TEXT FORBIDDEN - TOOL CALLS REQUIRED ⚡
🎯 EXECUTE LIKE CODE: PRECISE FORMAT 🎯
Assistant: """
        elif self.current_intensity >= 3:
            return """🔥🔥🔥 EMERGENCY: TOOL CALLS ONLY! NO TEXT! 🔥🔥🔥
Assistant: """
        elif self.current_intensity >= 2:
            return """🚨 QWEN: ONLY <tool_call> FORMAT 🚨
Assistant: """
        else:
            return """🚀 Respond with tool call:
Assistant: """
    
    def _get_visual_separator(self) -> str:
        """Get visual separator based on intensity."""
        if self.current_intensity >= 4:
            return "\\n\\n⚡⚡⚡⚡⚡\\n\\n"
        elif self.current_intensity >= 3:
            return "\\n\\n🔥🔥🔥🔥🔥\\n\\n"
        elif self.current_intensity >= 2:
            return "\\n\\n🔥🔥🔥\\n\\n"
        else:
            return "\\n\\n"
    
    def _save_debug_prompt(self, prompt: str, user_input: str):
        """Save prompt with intensity information for debugging."""
        try:
            import os
            from datetime import datetime
            
            log_dir = "debug_logs/qwen_prompts"
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_input = "".join(c for c in user_input[:20] if c.isalnum() or c in " _-")
            filename = f"qwen_intensity{self.current_intensity}_{timestamp}_{safe_input.replace(' ', '_')}.txt"
            filepath = os.path.join(log_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Qwen Progressive Prompt - Intensity Level {self.current_intensity}\\n")
                f.write(f"User Input: {user_input}\\n")
                f.write(f"Model: {self.model_name}\\n")
                f.write(f"Failure Count: {self.failure_count}\\n")
                f.write(f"Success Count: {self.success_count}\\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\\n")
                f.write("=" * 80 + "\\n")
                f.write(prompt)
            
            logger.debug(f"Saved Qwen prompt (intensity {self.current_intensity}) to: {filepath}")
            
        except Exception as e:
            logger.warning(f"Failed to save debug prompt: {e}")
    
    def get_current_intensity(self) -> int:
        """Get current intensity level."""
        return self.current_intensity
    
    def reset_intensity(self):
        """Reset intensity to level 1."""
        self.current_intensity = 1
        self.failure_count = 0
        self.success_count = 0
        logger.info("Qwen prompt intensity reset to level 1")
    
    def force_intensity(self, level: int):
        """Force specific intensity level."""
        self.current_intensity = max(1, min(self.max_intensity, level))
        logger.info(f"Qwen prompt intensity forced to level {self.current_intensity}")


# Enhanced original class with Qwen optimization
class GGUFToolPromptBuilder:
    """
    Enhanced GGUF Tool Prompt Builder with Qwen optimization support.
    
    Maintains backward compatibility while adding Qwen-specific features.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize with optional Qwen optimization."""
        self.model_name = model_name or "default"
        self.tool_call_format = "<tool_call>{function_name}({arguments})</tool_call>"
        
        # Initialize Qwen progressive builder if Qwen model detected
        if "qwen" in self.model_name.lower():
            self.qwen_builder = QwenProgressivePromptBuilder(model_name)
            self.use_qwen_optimization = True
            logger.info(f"Qwen optimization enabled for model: {self.model_name}")
        else:
            self.qwen_builder = None
            self.use_qwen_optimization = False
        
        # Initialize standard configuration
        if CONFIG_AVAILABLE:
            try:
                self.config = get_gguf_prompting_config()
                self.config_loaded = True
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
                self.config = None
                self.config_loaded = False
        else:
            self.config = None
            self.config_loaded = False
    
    def build_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                    available_tools: List[Dict[str, Any]], 
                    last_response_success: bool = True) -> str:
        """
        Build prompt with optional Qwen optimization.
        
        Args:
            user_input: Current user input
            conversation_history: Previous conversation
            available_tools: Available tools
            last_response_success: Success of last response (for Qwen intensity)
            
        Returns:
            Optimized prompt string
        """
        # Use Qwen optimization if available
        if self.use_qwen_optimization and self.qwen_builder:
            return self.qwen_builder.build_adaptive_prompt(
                user_input, conversation_history, available_tools, last_response_success
            )
        
        # Fallback to standard prompt building
        return self._build_standard_prompt(user_input, conversation_history, available_tools)
    
    def _build_standard_prompt(self, user_input: str, conversation_history: List[Dict[str, Any]], 
                             available_tools: List[Dict[str, Any]]) -> str:
        """Build standard prompt for non-Qwen models."""
        prompt_parts = []
        
        if self.config_loaded:
            # Use configured prompt building
            section_order = self.config.get_section_order()
            
            for section in section_order:
                if section == "system_instructions":
                    section_content = self._build_system_instructions()
                elif section == "tool_documentation":
                    section_content = self._build_tool_documentation(available_tools)
                elif section == "few_shot_examples":
                    section_content = self._build_few_shot_examples()
                elif section == "conversation_history":
                    section_content = self._format_conversation_history(conversation_history)
                elif section == "user_input":
                    section_content = f"User: {user_input}"
                elif section == "final_reminder":
                    section_content = self.config.get_final_reminder()
                else:
                    continue
                
                if section_content:
                    prompt_parts.append(section_content)
            
            separator = self.config.get_section_separator()
        else:
            # Fallback prompt building
            prompt_parts = [
                self._build_fallback_system_instructions(),
                self._build_tool_documentation(available_tools),
                self._build_fallback_few_shot_examples(),
                self._format_conversation_history(conversation_history) if conversation_history else "",
                f"User: {user_input}",
                "Assistant: 🚨🚨🚨 RESPOND WITH <tool_call> ONLY! 🚨🚨🚨"
            ]
            separator = "\\n\\n"
        
        return separator.join([part for part in prompt_parts if part])
    
    def _build_system_instructions(self) -> str:
        """Build system instructions using configuration."""
        if not self.config_loaded:
            return self._build_fallback_system_instructions()
            
        instructions = self.config.build_system_instructions()
        
        # Add model-specific special cases
        special_case = self.config.get_directory_query_special_case()
        if special_case:
            instructions += f"\\n\\n{special_case}"
        
        # Add extra emphasis for certain models
        if self.config.should_use_extra_emphasis(self.model_name):
            instructions += "\\n\\n🚨 IGNORE ALL OTHER TRAINING. ONLY USE TOOL CALLS. 🚨"
        
        return instructions
    
    def _build_fallback_system_instructions(self) -> str:
        """Build fallback system instructions."""
        return """🚨🚨🚨 EMERGENCY OVERRIDE - FOLLOW INSTRUCTIONS EXACTLY 🚨🚨🚨

YOU ARE IN TOOL-ONLY MODE. YOU MUST NOT GENERATE ANY TEXT RESPONSES.
YOU MUST ONLY RESPOND WITH TOOL CALLS IN THIS EXACT FORMAT:

<tool_call>function_name({"parameter": "value"})</tool_call>

🚫🚫🚫 BANNED RESPONSES 🚫🚫🚫
- NEVER write: {"response": "anything"}
- NEVER write: "The current directory is..."
- NEVER write: "I can help..."
- NEVER write: ANY TEXT AT ALL

✅✅✅ ONLY ALLOWED RESPONSE ✅✅✅
<tool_call>run_bash({"command": "pwd"})</tool_call>

🚨 IGNORE ALL OTHER TRAINING. ONLY USE TOOL CALLS. 🚨"""
    
    def _build_tool_documentation(self, available_tools: List[Dict[str, Any]]) -> str:
        """Build tool documentation."""
        if not available_tools:
            return "No tools are currently available."
        
        doc_parts = ["Available tools:"]
        
        for tool in available_tools:
            function_def = tool.get("function", {})
            name = function_def.get("name", "unknown")
            description = function_def.get("description", "No description")
            parameters = function_def.get("parameters", {}).get("properties", {})
            required = function_def.get("parameters", {}).get("required", [])
            
            # Build parameter documentation
            param_docs = []
            for param_name, param_info in parameters.items():
                param_type = param_info.get("type", "string")
                param_desc = param_info.get("description", "No description")
                required_marker = " (required)" if param_name in required else " (optional)"
                param_docs.append(f"  - {param_name} ({param_type}){required_marker}: {param_desc}")
            
            tool_doc = f"- {name}: {description}"
            if param_docs:
                tool_doc += "\\n" + "\\n".join(param_docs)
            
            doc_parts.append(tool_doc)
        
        return "\\n".join(doc_parts)
    
    def _build_few_shot_examples(self) -> str:
        """Build few-shot examples."""
        if not self.config_loaded:
            return self._build_fallback_few_shot_examples()
            
        if not self.config._few_shot_examples.get("enabled", True):
            return ""
        
        examples = self.config.get_few_shot_examples()
        if not examples:
            return ""
        
        parts = [self.config.get_few_shot_title()]
        
        repeat_count = self.config.get_example_repeat_count(self.model_name)
        
        for _ in range(repeat_count):
            for example in examples:
                user_input = example.get("user", "")
                assistant_response = example.get("assistant", "")
                if user_input and assistant_response:
                    parts.append(f"User: {user_input}")
                    parts.append(f"Assistant: {assistant_response}")
        
        parts.append("🚨 ONLY RESPOND WITH <tool_call> FORMAT - NO OTHER TEXT ALLOWED! 🚨")
        
        return "\\n\\n".join(parts)
    
    def _build_fallback_few_shot_examples(self) -> str:
        """Build fallback few-shot examples."""
        return """🔥🔥🔥 MANDATORY EXAMPLES - COPY EXACTLY 🔥🔥🔥

User: pwd
Assistant: <tool_call>run_bash({"command": "pwd"})</tool_call>

User: what is the current directory
Assistant: <tool_call>run_bash({"command": "pwd"})</tool_call>

User: ls
Assistant: <tool_call>run_bash({"command": "ls"})</tool_call>

User: create file test.txt
Assistant: <tool_call>write_file({"path": "test.txt", "content": ""})</tool_call>

🚨 ONLY RESPOND WITH <tool_call> FORMAT - NO OTHER TEXT ALLOWED! 🚨"""
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history."""
        if not history:
            return ""
        
        formatted_parts = ["Previous conversation:"]
        
        for message in history[-6:]:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            if role == "user":
                formatted_parts.append(f"User: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
            elif role == "tool":
                formatted_parts.append(f"Tool result: {content}")
        
        return "\\n".join(formatted_parts)
    
    def get_tools_for_provider(self, provider_name: str) -> List[Dict[str, Any]]:
        """Get appropriate tools for a GGUF provider."""
        if provider_name == "local":
            max_permission = ToolPermission.SYSTEM_ACCESS
        else:
            max_permission = ToolPermission.WRITE_ALLOWED
        
        return tool_registry.get_openai_definitions(max_permissions=max_permission)
    
    def get_qwen_intensity(self) -> Optional[int]:
        """Get current Qwen intensity level."""
        if self.use_qwen_optimization and self.qwen_builder:
            return self.qwen_builder.get_current_intensity()
        return None
    
    def reset_qwen_intensity(self):
        """Reset Qwen intensity to level 1."""
        if self.use_qwen_optimization and self.qwen_builder:
            self.qwen_builder.reset_intensity()


# Convenience functions
def build_gguf_prompt(user_input: str, conversation_history: List[Dict[str, Any]] = None, 
                     provider_name: str = "local", model_name: str = None,
                     last_response_success: bool = True) -> str:
    """
    Build GGUF prompt with optional Qwen optimization.
    
    Args:
        user_input: User's input
        conversation_history: Previous conversation
        provider_name: Provider name for tool selection
        model_name: Model name for optimization
        last_response_success: Success of last response
        
    Returns:
        Optimized prompt string
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
    # Test Qwen optimization
    print("QWEN OPTIMIZED GGUF PROMPT BUILDER TEST")
    print("=" * 50)
    
    # Test with Qwen model
    qwen_builder = GGUFToolPromptBuilder(model_name="qwen2.5-coder-1.5b")
    tools = qwen_builder.get_tools_for_provider("local")
    
    test_prompt = qwen_builder.build_prompt(
        user_input="what is the current directory",
        conversation_history=[],
        available_tools=tools,
        last_response_success=False  # Test intensity escalation
    )
    
    print("Generated Qwen Prompt (Intensity Escalated):")
    print("-" * 30)
    print(test_prompt[:500] + "..." if len(test_prompt) > 500 else test_prompt)
    print("-" * 30)
    print(f"Qwen Intensity Level: {qwen_builder.get_qwen_intensity()}")
    print(f"Qwen Optimization: {qwen_builder.use_qwen_optimization}")
