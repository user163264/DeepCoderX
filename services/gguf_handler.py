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
from services.gguf_tool_prompt import GGUFToolPromptBuilder
from services.gguf_tool_parser import GGUFToolCallParser
from services.gguf_context_manager import GGUFContextManager
from services.gguf_response_postprocessor import GGUFResponsePostProcessor
from services.tool_registry import tool_registry


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
        
        # Initialize GGUF-specific components
        self.prompt_builder = GGUFToolPromptBuilder()
        self.tool_parser = GGUFToolCallParser()
        self.context_manager = GGUFContextManager(provider_name)
        self.tool_executor = ToolExecutor(self.ctx)
        self.post_processor = GGUFResponsePostProcessor()
        
        # Direct GGUF model setup
        self._model = None
        self.model_path = self._get_model_path()
        
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
            
            # Verbose output for debugging
            "verbose": self.debug_mode,
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
    
    def _conversation_loop(self) -> None:
        """Multi-turn conversation loop with manual tool calling."""
        iteration = 0
        
        while iteration < self.max_tool_iterations:
            if self.debug_mode:
                console.print(f"[yellow]GGUF iteration {iteration + 1}/{self.max_tool_iterations}[/]")
            
            # Build prompt with tool examples and conversation history
            conversation_history = self.context_manager.get_conversation_history()
            available_tools = self._get_available_tools()
            
            prompt = self.prompt_builder.build_prompt(
                user_input=self.ctx.user_input if iteration == 0 else "",
                conversation_history=conversation_history,
                available_tools=available_tools
            )
            
            if self.debug_mode:
                console.print(f"[dim]Prompt length: {len(prompt)} characters[/]")
            
            # Generate response from GGUF model
            self.ctx.status_message = f"Thinking with {self.provider_config['name']}..."
            
            try:
                response = self._generate_gguf_response(prompt)
                
                if not response:
                    self.ctx.response = "[red]Error:[/] No response from GGUF model"
                    return
                
                if self.debug_mode:
                    console.print(f"[dim]Raw GGUF response: {response[:200]}...[/]")
                
                # Parse for tool calls
                tool_calls, clean_response = self.tool_parser.parse_and_execute_format(response)
                
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
            
            # Generate completion
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.1,
                stop=["Human:", "User:", "\n\n---"],  # Stop sequences
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
            return tool_registry.get_all_tools()
        else:
            # Other providers get limited tools (no run_bash)
            return tool_registry.get_non_system_tools()
    
    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]], original_response: str) -> None:
        """Execute tool calls and update context."""
        if self.debug_mode:
            console.print(f"[blue]Executing {len(tool_calls)} tool calls[/]")
        
        # Add the original response to context (before tool execution)
        self.context_manager.add_assistant_message(original_response)
        
        # Execute each tool call
        tool_results = []
        for tool_call in tool_calls:
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
            "inference_mode": "direct_llama_cpp"
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
