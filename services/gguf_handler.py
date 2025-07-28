"""
GGUF Handler for DeepCoderX using llama-cpp-python directly

This implementation uses the llama-cpp-python library directly for loading and 
running GGUF models, providing optimal performance and full control.
"""

import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

# Direct llama-cpp-python import
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    raise ImportError("llama-cpp-python is required for GGUF handling. Install with: pip install llama-cpp-python")

from config_module import config
from utils.logging import console, log_api_usage
from models.session import CommandContext
from models.router import CommandHandler
from services.tool_executor import ToolExecutor
from services.simplified_gguf_prompt import SimplifiedGGUFPromptBuilder
from services.gguf_tool_parser import GGUFToolCallParser
from services.gguf_context_manager import GGUFContextManager
from services.gguf_response_postprocessor import GGUFResponsePostProcessor
from services.tool_registry import tool_registry


class ChatTemplateFormatter:
    """
    Model-specific chat template formatter for GGUF models.
    
    This class provides the missing layer between YAML configuration and llama-cpp-python
    inference by applying model-specific chat templates for optimal performance.
    """
    
    def __init__(self, model_path: str = None, model_name: str = None):
        self.model_path = model_path
        self.model_name = model_name or ""
        self.model_type = self._detect_model_type()
        
    def _detect_model_type(self) -> str:
        """
        Detect model type from name and path for template selection.
        """
        # Combine model path and name for detection
        model_info = f"{self.model_path or ''} {self.model_name}".lower()
        
        # Llama models
        if any(indicator in model_info for indicator in ["llama", "llama-3", "llama-2", "llama3", "llama2"]):
            return "llama"
        
        # Qwen models
        elif any(indicator in model_info for indicator in ["qwen", "qwen2", "qwen2.5", "qw"]):
            return "qwen"
        
        # Phi models
        elif any(indicator in model_info for indicator in ["phi", "phi-3", "phi3"]):
            return "phi"
        
        # Gemma models
        elif any(indicator in model_info for indicator in ["gemma", "gemma-2"]):
            return "gemma"
        
        # Mistral models
        elif any(indicator in model_info for indicator in ["mistral", "mixtral", "codestral"]):
            return "mistral"
        
        # Generic fallback
        else:
            return "generic"
    
    def format_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using model-specific chat template.
        
        Args:
            system_prompt: System instruction
            user_prompt: User message
            conversation_history: Previous conversation messages
            
        Returns:
            Formatted prompt with model-specific chat template
        """
        if self.model_type == "llama":
            return self._format_llama_prompt(system_prompt, user_prompt, conversation_history)
        elif self.model_type == "qwen":
            return self._format_qwen_prompt(system_prompt, user_prompt, conversation_history)
        elif self.model_type == "phi":
            return self._format_phi_prompt(system_prompt, user_prompt, conversation_history)
        elif self.model_type == "gemma":
            return self._format_gemma_prompt(system_prompt, user_prompt, conversation_history)
        elif self.model_type == "mistral":
            return self._format_mistral_prompt(system_prompt, user_prompt, conversation_history)
        else:
            return self._format_generic_prompt(system_prompt, user_prompt, conversation_history)
    
    def _format_llama_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using Llama 3.2 chat template.
        
        Template:
        <|start_header_id|>system<|end_header_id|>
        {system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>
        {user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
        
        Note: <|begin_of_text|> is automatically added by llama-cpp-python
        """
        # Don't add <|begin_of_text|> as llama-cpp-python adds it automatically
        formatted = f"<|start_header_id|>system<|end_header_id|>\n{system_prompt}<|eot_id|>"
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role in ["user", "assistant"]:
                    formatted += f"<|start_header_id|>{role}<|end_header_id|>\n{content}<|eot_id|>"
        
        # Add current user prompt
        formatted += f"<|start_header_id|>user<|end_header_id|>\n{user_prompt}<|eot_id|>"
        formatted += "<|start_header_id|>assistant<|end_header_id|>\n"
        
        return formatted
    
    def _format_qwen_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using Qwen chat template.
        
        Template:
        <|im_start|>system
        {system_prompt}<|im_end|>
        <|im_start|>user
        {user_prompt}<|im_end|>
        <|im_start|>assistant
        """
        formatted = f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role in ["user", "assistant"]:
                    formatted += f"<|im_start|>{role}\n{content}<|im_end|>\n"
        
        # Add current user prompt
        formatted += f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        formatted += "<|im_start|>assistant\n"
        
        return formatted
    
    def _format_phi_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using Phi-3 chat template.
        
        Template:
        <|system|>
        {system_prompt}<|end|>
        <|user|>
        {user_prompt}<|end|>
        <|assistant|>
        """
        formatted = f"<|system|>\n{system_prompt}<|end|>\n"
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role in ["user", "assistant"]:
                    formatted += f"<|{role}|>\n{content}<|end|>\n"
        
        # Add current user prompt
        formatted += f"<|user|>\n{user_prompt}<|end|>\n"
        formatted += "<|assistant|>\n"
        
        return formatted
    
    def _format_gemma_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using Gemma chat template.
        
        Template:
        <start_of_turn>user
        {system_prompt}
        
        {user_prompt}<end_of_turn>
        <start_of_turn>model
        """
        # Gemma combines system and user prompt
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        formatted = f"<start_of_turn>user\n{combined_prompt}<end_of_turn>\n"
        
        # Add conversation history (simplified for Gemma)
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    formatted += f"<start_of_turn>user\n{content}<end_of_turn>\n"
                elif role == "assistant":
                    formatted += f"<start_of_turn>model\n{content}<end_of_turn>\n"
        
        formatted += "<start_of_turn>model\n"
        
        return formatted
    
    def _format_mistral_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using Mistral chat template.
        
        Template:
        <s>[INST] {system_prompt}
        
        {user_prompt} [/INST]
        """
        # Mistral combines system and user prompt
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        formatted = f"<s>[INST] {combined_prompt} [/INST]"
        
        # Note: Mistral conversation history is more complex, simplified here
        if conversation_history:
            # For simplicity, append to the instruction
            history_context = "\n\nPrevious conversation:\n"
            for message in conversation_history[-3:]:  # Last 3 messages
                role = message.get("role", "user")
                content = message.get("content", "")
                history_context += f"{role}: {content}\n"
            formatted = f"<s>[INST] {system_prompt}{history_context}\n{user_prompt} [/INST]"
        
        return formatted
    
    def _format_generic_prompt(self, system_prompt: str, user_prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Format prompt using generic template for unrecognized models.
        
        Template:
        System: {system_prompt}
        
        User: {user_prompt}
        
        Assistant:
        """
        formatted = f"System: {system_prompt}\n\n"
        
        # Add conversation history
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "user").title()
                content = message.get("content", "")
                formatted += f"{role}: {content}\n\n"
        
        # Add current user prompt
        formatted += f"User: {user_prompt}\n\nAssistant: "
        
        return formatted
    
    def get_model_info(self) -> Dict[str, str]:
        """
        Get information about detected model type and template.
        """
        return {
            "model_type": self.model_type,
            "model_path": self.model_path or "Unknown",
            "model_name": self.model_name,
            "template_format": f"{self.model_type.title()} chat template"
        }


class GGUFLocalHandler(CommandHandler):
    """
    Direct GGUF model handler using llama-cpp-python for macOS.
    
    Features:
    - Direct GGUF model loading with llama-cpp-python
    - Metal acceleration for Apple Silicon
    - Optimized memory management
    - Advanced tool calling with manual parsing
    - Resource cleanup and management
    """
    
    def __init__(self, context: CommandContext, provider_name: str = "local"):
        super().__init__(context)
        self.provider_name = provider_name
        self.provider_config = config.PROVIDERS.get(provider_name)
        
        if not self.provider_config:
            raise ValueError(f"Unknown GGUF provider: {provider_name}")
        
        if not self.provider_config["enabled"]:
            raise ValueError(f"GGUF provider '{provider_name}' is not enabled")
        
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError("llama-cpp-python is required for direct GGUF handling")
        
        # Direct GGUF model setup
        self._model = None
        self.model_path = self._get_model_path()
        
        # Initialize GGUF-specific components
        self.prompt_builder = SimplifiedGGUFPromptBuilder()
        self.tool_parser = GGUFToolCallParser()
        self.context_manager = GGUFContextManager(provider_name)
        self.tool_executor = ToolExecutor(self.ctx)
        self.post_processor = GGUFResponsePostProcessor()
        
        # Initialize chat template formatter
        self.chat_formatter = ChatTemplateFormatter(
            model_path=self.model_path,
            model_name=self.provider_config.get("name", "")
        )
        
        # Configuration
        self.max_tool_iterations = self.provider_config.get("max_tool_iterations", 5)
        self.debug_mode = self.ctx.debug_mode
        
        # Initialize known tools for parser validation
        available_tools = self._get_available_tools()
        tool_names = [tool["function"]["name"] for tool in available_tools]
        self.tool_parser.set_known_tools(tool_names)
        
        if self.debug_mode:
            console.print(f"[bold green]Initialized GGUF handler for {provider_name}[/]")
            console.print(f"[blue]Model path: {self.model_path}[/]")
            console.print(f"[blue]Available tools: {', '.join(tool_names)}[/]")
            
            # Show chat template information
            template_info = self.chat_formatter.get_model_info()
            console.print(f"[cyan]Chat template: {template_info['template_format']} ({template_info['model_type']})[/]")
            console.print(f"[cyan]Model detection: {template_info['model_name']}[/]")
    
    def _get_model_path(self) -> str:
        """Get the GGUF model path from configuration."""
        # Check for explicit model path in config
        if hasattr(config, 'LOCAL_MODEL_PATH') and config.LOCAL_MODEL_PATH:
            model_path = Path(config.LOCAL_MODEL_PATH)
            if model_path.exists():
                return str(model_path)
        
        # Fallback to common locations
        common_paths = [
            Path.home() / ".cache" / "lm-studio" / "models" / "Qwen" / "Qwen2.5-Coder-1.5B-Instruct-GGUF" / "qwen2.5-coder-1.5b-instruct-q8_0.gguf",
            Path.home() / "models" / "qwen2.5-coder-1.5b-instruct-q8_0.gguf",
            Path("./models/qwen2.5-coder-1.5b-instruct-q8_0.gguf"),
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError(f"GGUF model not found. Please set LOCAL_MODEL_PATH in config.")
    
    @property
    def model(self) -> Llama:
        """Lazy load the GGUF model with optimized settings."""
        if self._model is None:
            if self.debug_mode:
                console.print(f"[yellow]Loading GGUF model: {self.model_path}[/]")
            
            model_config = self._get_model_config()
            
            try:
                self._model = Llama(
                    model_path=self.model_path,
                    **model_config
                )
                
                if self.debug_mode:
                    console.print(f"[green]✓ GGUF model loaded successfully[/]")
                    
            except Exception as e:
                console.print(f"[red]✗ Failed to load GGUF model: {e}[/]")
                raise
        
        return self._model
    
    def _get_model_config(self) -> Dict[str, Any]:
        """Get optimized model configuration for Apple Silicon with Metal acceleration."""
        model_config = {
            # Context window
            "n_ctx": 4096,  # 4K context window for good performance
            
            # Batch processing
            "n_batch": 512,  # Batch size for processing
            
            # Threading
            "n_threads": None,  # Auto-detect optimal thread count
            
            # Memory management
            "use_mmap": True,  # Use memory mapping for faster loading
            "use_mlock": False,  # Don't lock memory by default
            
            # Precision
            "f16_kv": True,  # Use half precision for key/value cache
            
            # Apple Silicon Metal acceleration
            "n_gpu_layers": -1,  # Use all available GPU layers with Metal
            
            # Reduce verbosity - only show verbose output in debug mode
            "verbose": False,  # Set to False to reduce Metal initialization output
        }
        
        if self.debug_mode:
            console.print("[blue]Using Metal acceleration for Apple Silicon[/]")
        
        return model_config
    

    
    def can_handle(self) -> bool:
        """Determine if this handler can process the current request."""
        if not self.provider_config["enabled"]:
            return False
        
        user_input = self.ctx.user_input.lower()
        
        # Handle explicit provider requests
        if user_input.startswith(f"@{self.provider_name}"):
            return True
        
        # Handle if this is the default provider and no other provider specified
        if self.provider_name == config.DEFAULT_PROVIDER:
            # Check if user specified a different provider
            for provider_name in config.PROVIDERS.keys():
                if provider_name != self.provider_name and user_input.startswith(f"@{provider_name}"):
                    return False  # Let the other provider handle it
            return True  # No other provider specified, use default
        
        return False
    
    def handle(self) -> None:
        """Main processing method for GGUF models with tool calling."""
        self.ctx.model_name = self.provider_config["name"]
        
        if self.debug_mode:
            console.print(f"[bold blue]Processing with GGUF handler: {self.provider_name}[/]")
        
        # Optimize context for new request
        self.context_manager.optimize_for_new_request(self.ctx.user_input)
        
        # Add user message to context
        self.context_manager.add_user_message(self.ctx.user_input)
        
        # Main conversation loop with tool calling
        self._conversation_loop()
        
        # Save context after processing
        self.context_manager.save_session()
    
    def _is_conversational_input(self, user_input: str) -> bool:
        """Check if input is conversational and doesn't need tool calls."""
        user_input_lower = user_input.lower().strip()
        
        # Simple greetings and questions that should get direct responses
        conversational_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what are you", "who are you", "what can you do",
            "tell me about", "explain", "describe", "what is", "what are"
        ]
        
        # Check if input starts with conversational patterns
        for pattern in conversational_patterns:
            if user_input_lower.startswith(pattern):
                return True
        
        # Check for simple questions
        if user_input_lower.endswith('?') and len(user_input_lower.split()) <= 5:
            # Short questions are likely conversational
            return True
        
        return False
    
    def _generate_conversational_response(self) -> None:
        """
        Generate a direct conversational response without tool calling.
        
        This method handles simple greetings and questions that don't require
        tool execution, providing a faster response path.
        """
        try:
            # Create a simple conversational system prompt without tool examples
            conversational_system = (
                "You are a helpful coding assistant. Respond in a friendly, "
                "conversational manner to simple greetings and questions. "
                "Keep your responses brief and natural."
            )
            
            # Get conversation history for context
            conversation_history = self.context_manager.get_conversation_history()
            formatted_history = self._format_conversation_history(conversation_history)
            
            # Format using chat template
            prompt = self.chat_formatter.format_prompt(
                system_prompt=conversational_system,
                user_prompt=self.ctx.user_input,
                conversation_history=formatted_history
            )
            
            if self.debug_mode:
                console.print(f"[cyan]Generating conversational response (no tools)[/]")
                console.print(f"[dim]Prompt length: {len(prompt)} characters[/]")
            
            # Generate simple response
            response = self._generate_gguf_response(prompt)
            
            if response:
                self.ctx.response = response
                self.context_manager.add_assistant_message(response)
                
                if self.debug_mode:
                    console.print(f"[green]Conversational response generated: {response[:100]}...[/]")
            else:
                self.ctx.response = "Hello! I'm here to help with your coding tasks."
                self.context_manager.add_assistant_message(self.ctx.response)
                
        except Exception as e:
            if self.debug_mode:
                console.print(f"[red]Error generating conversational response: {e}[/]")
            
            # Fallback to simple greeting
            self.ctx.response = "Hello! I'm DeepCoderX, your coding assistant. How can I help you today?"
            self.context_manager.add_assistant_message(self.ctx.response)
    
    def _conversation_loop(self) -> None:
        """Multi-turn conversation loop with manual tool calling."""
        iteration = 0
        
        # CRITICAL FIX: Handle simple conversational inputs directly without tool calling
        if iteration == 0 and self._is_conversational_input(self.ctx.user_input):
            if self.debug_mode:
                console.print(f"[cyan]Detected conversational input, generating direct response (bypassing tool calling)[/]")
            
            # Generate conversational response without tool calling prompts
            self._generate_conversational_response()
            return
        
        while iteration < self.max_tool_iterations:
            if self.debug_mode:
                console.print(f"[yellow]GGUF iteration {iteration + 1}/{self.max_tool_iterations}[/]")
            
            # Build prompt with tool examples and conversation history
            conversation_history = self.context_manager.get_conversation_history()
            available_tools = self._get_available_tools()
            
            # PHASE 2: Use simplified prompt builder for 70-90% reduction
            prompt = self.prompt_builder.build_prompt(
                user_input=self.ctx.user_input if iteration == 0 else "",
                conversation_history=conversation_history,
                available_tools=available_tools
            )
            
            if self.debug_mode:
                console.print(f"[dim]Simplified prompt length: {len(prompt)} characters[/]")
                console.print(f"[cyan]PHASE 2: Using SimplifiedGGUFPromptBuilder (70-90% reduction)[/]")
                if len(conversation_history) > 0:
                    console.print(f"[cyan]Included {len(conversation_history)} conversation history messages[/]")
                
                # Check if this was a direct shortcut
                if "<tool_call>" in prompt and len(prompt) < 100:
                    console.print(f"[green]Direct shortcut executed: {prompt.strip()}[/]")
            
            # Handle direct shortcuts (no model inference needed)
            if "<tool_call>" in prompt and len(prompt) < 100:
                if self.debug_mode:
                    console.print(f"[green]Direct shortcut bypassing model inference[/]")
                response = prompt.strip()
            else:
                # Generate response from GGUF model
                self.ctx.status_message = f"Thinking with {self.provider_config['name']}..."
                response = self._generate_gguf_response(prompt)
            
            try:
                
                if not response:
                    self.ctx.response = "[red]Error:[/] No response from GGUF model"
                    return
                
                if self.debug_mode:
                    console.print(f"[dim]Raw GGUF response: {response[:200]}...[/]")
                
                # Parse for tool calls
                tool_calls, clean_response = self.tool_parser.parse_and_execute_format(response)
                
                # CRITICAL FIX: Limit tool calls to prevent excessive repetition
                if len(tool_calls) > 3:  # Reasonable limit for multiple tool calls
                    if self.debug_mode:
                        console.print(f"[yellow]Warning: {len(tool_calls)} tool calls detected, limiting to first 3[/]")
                    tool_calls = tool_calls[:3]
                
                # POST-PROCESSING: If no tool calls found, try to extract from user intent
                if not tool_calls:
                    if self.debug_mode:
                        console.print(f"[yellow]No tool calls found, trying post-processing...[/]")
                    
                    post_tool_calls, post_clean_response = self.post_processor.process_response(
                        self.ctx.user_input, response
                    )
                    
                    if post_tool_calls:
                        if self.debug_mode:
                            console.print(f"[green]Post-processor generated {len(post_tool_calls)} tool calls[/]")
                        
                        tool_calls = post_tool_calls
                        clean_response = post_clean_response
                
                if not tool_calls:
                    # No tools called, this is the final response
                    self.ctx.response = clean_response or response
                    self.context_manager.add_assistant_message(self.ctx.response)
                    
                    if self.debug_mode:
                        console.print(f"[green]Final response (no tools): {self.ctx.response[:100]}...[/]")
                    break
                
                # Execute tools and prepare for next iteration
                self._execute_tool_calls(tool_calls, response)
                iteration += 1
                
            except Exception as e:
                self.ctx.response = f"[red]GGUF Error:[/] {str(e)}"
                if self.debug_mode:
                    console.print(f"[bold red]GGUF Error:[/] {e}")
                return
        
        # Handle iteration limit reached
        if iteration >= self.max_tool_iterations:
            self.ctx.response = f"[yellow]Tool calling reached maximum iterations ({self.max_tool_iterations}). Final response: {clean_response or 'No response'}[/]"
            self.context_manager.add_assistant_message(self.ctx.response)
    
    def _generate_gguf_response(self, prompt: str) -> str:
        """Generate response using llama-cpp-python directly."""
        try:
            start_time = time.time()
            
            # Get generation parameters
            temperature = self.provider_config.get("temperature", 0.0)
            max_tokens = self.provider_config.get("max_tokens", 2048)
            
            # Generate completion with improved stop sequences to prevent repetition
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.15,  # Increased to reduce repetition
                stop=[
                    "Human:", "User:", "Assistant:",  # Role-based stops
                    "\n\n",  # Natural paragraph breaks
                    "</tool_call>\n\n",  # Stop after tool call completion
                    "---",  # Section separators
                    "\n\n---"  # Legacy format
                ],
                echo=False  # Don't echo the prompt back
            )
            
            end_time = time.time()
            
            # Extract the generated text
            if isinstance(response, dict) and "choices" in response:
                generated_text = response["choices"][0]["text"]
            else:
                generated_text = str(response)
            
            # Log performance metrics
            if self.debug_mode:
                duration = end_time - start_time
                console.print(f"[dim]GGUF generation took {duration:.2f}s[/]")
                
                # Token usage (if available)
                if isinstance(response, dict) and "usage" in response:
                    usage = response["usage"]
                    console.print(f"[dim]Tokens - Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                                f"Completion: {usage.get('completion_tokens', 'N/A')}, "
                                f"Total: {usage.get('total_tokens', 'N/A')}[/]")
            
            return generated_text.strip()
            
        except Exception as e:
            console.print(f"[red]GGUF generation error: {e}[/]")
            raise
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools for the current provider."""
        # Get tools from registry based on provider permissions
        if self.provider_name == "local":
            # Local provider gets all tools including system access
            from services.tool_registry import ToolPermission
            return tool_registry.get_openai_definitions(max_permissions=ToolPermission.SYSTEM_ACCESS)
        else:
            # Other providers get limited tools (no run_bash)
            from services.tool_registry import ToolPermission
            return tool_registry.get_openai_definitions(max_permissions=ToolPermission.WRITE_ALLOWED)
    
    def _deduplicate_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tool calls to prevent repetitive execution."""
        if not tool_calls:
            return tool_calls
        
        unique_calls = []
        seen_signatures = set()
        
        for call in tool_calls:
            # Create a hashable signature for the tool call
            call_signature = tuple(sorted(call.items()))
            
            if call_signature not in seen_signatures:
                seen_signatures.add(call_signature)
                unique_calls.append(call)
            elif self.debug_mode:
                console.print(f"[yellow]Skipping duplicate tool call: {call}[/]")
        
        if self.debug_mode and len(unique_calls) != len(tool_calls):
            console.print(f"[cyan]Deduplication: {len(tool_calls)} -> {len(unique_calls)} tool calls[/]")
        
        return unique_calls
    
    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]], original_response: str) -> None:
        """Execute tool calls and update context."""
        # CRITICAL FIX: Deduplicate tool calls to prevent repetitive execution
        unique_tool_calls = self._deduplicate_tool_calls(tool_calls)
        
        if self.debug_mode:
            console.print(f"[blue]Executing {len(unique_tool_calls)} tool calls[/]")
        
        # Add the original response to context (before tool execution)
        self.context_manager.add_assistant_message(original_response)
        
        # Execute each unique tool call
        tool_results = []
        for tool_call in unique_tool_calls:
            try:
                # Execute tool using unified executor
                result = self.tool_executor.execute_tool(tool_call)
                tool_results.append(result)
                
                if self.debug_mode:
                    console.print(f"[green]✓ Tool executed: {tool_call.get('tool', 'unknown')}[/]")
                
            except Exception as e:
                error_result = f"Tool execution error: {str(e)}"
                tool_results.append(error_result)
                
                if self.debug_mode:
                    console.print(f"[red]✗ Tool error: {e}[/]")
        
        # Add tool results to context
        if tool_results:
            combined_results = "\n\n".join([f"Tool result: {result}" for result in tool_results])
            self.context_manager.add_tool_message(combined_results)
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.context_manager.clear_history()
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get current context summary."""
        return self.context_manager.get_context_summary()
    
    def diagnose_tool_calling(self, test_input: str = "create a file called test.txt") -> Dict[str, Any]:
        """
        Diagnostic method to test tool calling functionality.
        
        Args:
            test_input: Test input to diagnose
            
        Returns:
            Diagnostic information
        """
        diagnostics = {
            "provider_name": self.provider_name,
            "provider_config": self.provider_config,
            "model_path": self.model_path,
            "available_tools": len(self._get_available_tools()),
            "max_iterations": self.max_tool_iterations,
            "test_input": test_input,
            "inference_mode": "direct_llama_cpp",
            "chat_template": self.chat_formatter.get_model_info()
        }
        
        try:
            # Test model loading
            try:
                model = self.model  # This will trigger lazy loading
                diagnostics["model_loading"] = {
                    "success": True,
                    "model_path": self.model_path
                }
            except Exception as e:
                diagnostics["model_loading"] = {
                    "success": False,
                    "error": str(e)
                }
                return diagnostics  # Can't continue without model
            
            # Test prompt building
            available_tools = self._get_available_tools()
            test_prompt = self.prompt_builder.build_prompt(
                user_input=test_input,
                conversation_history=[],
                available_tools=available_tools
            )
            
            diagnostics["prompt_building"] = {
                "success": True,
                "prompt_length": len(test_prompt),
                "has_tool_examples": "<tool_call>" in test_prompt
            }
            
            # Test GGUF response generation
            try:
                test_response = self._generate_gguf_response(test_prompt)
                diagnostics["response_generation"] = {
                    "success": True,
                    "response_length": len(test_response),
                    "response_preview": test_response[:200]
                }
                
                # Test tool call parsing
                tool_calls, clean_response = self.tool_parser.parse_and_execute_format(test_response)
                diagnostics["tool_parsing"] = {
                    "success": True,
                    "tool_calls_found": len(tool_calls),
                    "tool_calls": tool_calls,
                    "clean_response": clean_response[:200] if clean_response else None
                }
                
            except Exception as e:
                diagnostics["response_generation"] = {
                    "success": False,
                    "error": str(e)
                }
            
        except Exception as e:
            diagnostics["prompt_building"] = {
                "success": False,
                "error": str(e)
            }
        
        return diagnostics
    
    # Old prompt extraction methods removed - using simplified system directly
    
    def _format_conversation_history(self, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format conversation history for chat template compatibility.
        
        Args:
            conversation_history: Raw conversation history from context manager
            
        Returns:
            Formatted conversation history with role and content keys
        """
        formatted_history = []
        
        for message in conversation_history:
            # Handle different possible formats from context manager
            if isinstance(message, dict):
                role = message.get("role", "user")
                content = message.get("content", message.get("message", ""))
                
                # Normalize role names
                if role.lower() in ["human", "user"]:
                    role = "user"
                elif role.lower() in ["assistant", "ai", "bot"]:
                    role = "assistant"
                
                if content and content.strip():
                    formatted_history.append({
                        "role": role,
                        "content": content.strip()
                    })
        
        return formatted_history
    
    def test_tool_execution(self, tool_name: str = "write_file", 
                          test_args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Test tool execution functionality.
        
        Args:
            tool_name: Tool to test
            test_args: Arguments for tool
            
        Returns:
            Test results
        """
        if test_args is None:
            test_args = {"path": "gguf_test.txt", "content": "GGUF test content"}
        
        test_tool_call = {"tool": tool_name, **test_args}
        
        try:
            result = self.tool_executor.execute_tool(test_tool_call)
            
            return {
                "success": True,
                "tool_call": test_tool_call,
                "result": str(result),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "tool_call": test_tool_call,
                "result": None,
                "error": str(e)
            }
    
    def __del__(self):
        """Cleanup model resources."""
        if self._model is not None:
            try:
                # llama-cpp-python handles cleanup automatically
                if self.debug_mode:
                    console.print("[dim]GGUF model cleanup completed[/]")
            except:
                pass  # Ignore cleanup errors


# Convenience functions for testing and integration
def create_gguf_handler(context: CommandContext, provider_name: str = "local") -> GGUFLocalHandler:
    """Create a GGUF handler instance."""
    return GGUFLocalHandler(context, provider_name)


def test_gguf_functionality(provider_name: str = "local") -> Dict[str, Any]:
    """Test GGUF functionality without full context."""
    from models.session import CommandContext
    
    # Create minimal context for testing
    test_ctx = CommandContext(
        user_input="create a file called test.txt",
        root_path=Path.cwd(),
        debug_mode=True
    )
    
    try:
        handler = GGUFLocalHandler(test_ctx, provider_name)
        return handler.diagnose_tool_calling()
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "provider_name": provider_name
        }
