"""
Unified OpenAI-Compatible Handler for DeepCoderX

This module provides a unified interface for all OpenAI-compatible AI providers,
eliminating code duplication and providing native tool calling support.
Supports LM Studio, DeepSeek, OpenAI, and other OpenAI-compatible endpoints.
"""

import os
import json
import re
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("OpenAI client not installed. Run: pip install openai>=1.0.0")

from config_module import config, CURRENT_CONFIG, SEMANTIC_ZONES
from utils.logging import console, log_api_usage, log_debug, log_info, log_error, log_warning
from utils.model_logging import (log_model_prompt, log_model_response, log_tool_execution_details,
                                log_conversation_context_details, log_model_error, log_model_performance)
from services.context_builder import CodeContextBuilder
from models.session import CommandContext
from models.router import CommandHandler
from services.tool_executor import ToolExecutor
from services.context_manager import ContextManager
from services.tool_registry import tool_registry, get_tools_for_provider


class UnifiedOpenAIHandler(CommandHandler):
    """
    Unified handler that works with any OpenAI-compatible API provider.
    Supports both local (LM Studio) and cloud (DeepSeek, OpenAI, etc.) providers.
    """
    
    def __init__(self, context: CommandContext, provider: str = None):
        super().__init__(context)
        self.provider_name = provider or config.DEFAULT_PROVIDER
        self.provider_config = config.PROVIDERS.get(self.provider_name)
        
        if not self.provider_config:
            raise ValueError(f"Unknown provider: {self.provider_name}")
        
        if not self.provider_config["enabled"]:
            raise ValueError(f"Provider '{self.provider_name}' is not enabled")
        
        # Initialize OpenAI client with provider-specific settings
        self._client = None
        self.session_file = self.ctx.root_path / ".deepcoderx" / f"{self.provider_name}_session.json"
        self.tool_executor = ToolExecutor(self.ctx, use_complex_path_resolution=True)
        self._load_history()
    
    @property
    def client(self) -> OpenAI:
        """Lazy load the OpenAI client on first access."""
        if self._client is None:
            client_kwargs = {
                "api_key": self.provider_config["api_key"]
            }
            
            # Set base_url for non-OpenAI providers
            if self.provider_config["base_url"]:
                client_kwargs["base_url"] = self.provider_config["base_url"]
            
            self._client = OpenAI(**client_kwargs)
            
            if self.ctx.debug_mode:
                console.print(f"[bold green]Initialized {self.provider_config['name']} client[/]")
        
        return self._client
    
    def _load_history(self):
        """Load conversation history from session file."""
        if self.session_file.exists():
            try:
                with open(self.session_file, "r") as f:
                    loaded_history = json.load(f)
                
                # Validate session for OpenAI standard compliance
                self.message_history = self._validate_session_history(loaded_history)
                
                # If validation failed, reset to clean state
                if not self.message_history:
                    self._reset_history()
                    
            except (json.JSONDecodeError, FileNotFoundError):
                self._reset_history()
        else:
            self._reset_history()
    
    def _validate_session_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate session history for OpenAI standard compliance.
        
        Ensures that:
        1. Tool messages always follow assistant messages with tool_calls
        2. No orphaned tool messages exist
        3. All tool_call_ids match existing tool calls
        """
        if not history:
            return []
        
        validated_messages = []
        pending_tool_calls = {}  # tool_call_id -> tool_call
        
        for message in history:
            role = message.get("role")
            
            if role == "system":
                validated_messages.append(message)
                
            elif role == "user":
                validated_messages.append(message)
                
            elif role == "assistant":
                validated_messages.append(message)
                
                # Track tool calls for validation
                if "tool_calls" in message:
                    for tool_call in message["tool_calls"]:
                        tool_call_id = tool_call.get("id")
                        if tool_call_id:
                            pending_tool_calls[tool_call_id] = tool_call
                            
            elif role == "tool":
                tool_call_id = message.get("tool_call_id")
                
                # Only include tool messages with valid tool_call_ids
                if tool_call_id and tool_call_id in pending_tool_calls:
                    validated_messages.append(message)
                    # Remove from pending after use
                    del pending_tool_calls[tool_call_id]
                else:
                    # Orphaned tool message - skip it
                    if self.ctx.debug_mode:
                        console.print(f"[bold yellow]WARNING:[/] Skipping orphaned tool message with ID: {tool_call_id}")
                    continue
                    
            else:
                # Unknown role - skip
                if self.ctx.debug_mode:
                    console.print(f"[bold yellow]WARNING:[/] Skipping message with unknown role: {role}")
                continue
        
        # Ensure we have at least a system message
        if not validated_messages or validated_messages[0].get("role") != "system":
            return []  # Invalid session, will trigger reset
            
        return validated_messages
    
    def _reset_history(self):
        """Reset conversation history with appropriate system prompt."""
        # Choose system prompt based on provider and use case
        if self.provider_name == "local":
            system_prompt = config.LOCAL_SYSTEM_PROMPT
        else:
            # For analysis providers like DeepSeek, include project context
            context_manager = ContextManager(self.ctx)
            if context_manager.context_file_exists():
                initial_context = context_manager.read_context_file()
            else:
                initial_context = context_manager.build_and_save_context()
            
            system_prompt = config.DEEPSEEK_SYSTEM_PROMPT + f"\n\n**Project Context File:**\n{initial_context}\n\n**Current Configuration**:\n{CURRENT_CONFIG}"
        
        self.message_history = [
            {"role": "system", "content": system_prompt}
        ]
    
    def _save_history(self):
        """Save conversation history to session file."""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "w") as f:
            json.dump(self.message_history, f, indent=2)
    
    def can_handle(self) -> bool:
        """Determine if this handler can process the current request."""
        # This will be called by specific subclasses for routing
        return True
    
    def handle(self) -> None:
        """Main processing method using OpenAI-compatible API."""
        self.ctx.model_name = self.provider_config["name"]
        
        # Handle special commands first
        if "--build-context" in self.ctx.user_input and self.provider_name != "local":
            self._handle_build_context()
            return
        
        # Parse user input and handle file references
        user_prompt = self._parse_user_input()
        self.message_history.append({"role": "user", "content": user_prompt})
        
        # Main conversation loop with tool support
        self._conversation_loop()
        
        # Save history and trim if needed
        self._maintain_history()
        self._save_history()
    
    def _handle_build_context(self):
        """Handle context building command."""
        context_manager = ContextManager(self.ctx)
        context_manager.build_and_save_context()
        self.ctx.response = f"[green]Successfully built and saved project context to {context_manager.CONTEXT_FILE_NAME}[/]."
    
    def _parse_user_input(self) -> str:
        """Parse user input, handling file references and cleaning provider prefixes."""
        # Remove provider prefixes like @deepseek, @qwen, etc.
        cleaned_input = re.sub(r'@\w+\s*', '', self.ctx.user_input).strip()
        
        # Handle file references (@filename)
        words = self.ctx.user_input.split()
        file_paths, message_words = [], []
        
        for word in words:
            if word.startswith('@') and word.lower() not in ['@qwen', '@deepseek', '@openai']:
                file_paths.append(word[1:])
            elif word.lower() not in ['@qwen', '@deepseek', '@openai']:
                message_words.append(word)
        
        cleaned_input = " ".join(message_words)
        
        # Add file contents if referenced
        file_contents = []
        for path in file_paths:
            try:
                response = self.ctx.mcp_client.read_file(path)
                if "content" in response:
                    file_contents.append(f"""--- Content from @{path} ---
{response['content']}
--- End of content ---""")
                else:
                    file_contents.append(f"--- Error reading @{path}: {response.get('error')} ---")
            except Exception as e:
                file_contents.append(f"--- Exception reading @{path}: {e} ---")
        
        if file_contents:
            cleaned_input += "\n\n" + "\n\n".join(file_contents)
        
        return cleaned_input
    
    def _conversation_loop(self):
        """Main conversation loop with native OpenAI tool calling support."""
        max_tool_calls = config.MAX_TOOL_CALLS
        
        for i in range(max_tool_calls):
            # Check for tool call limit
            if i == max_tool_calls - 1:
                if "PYTEST_CURRENT_TEST" in os.environ:
                    self.ctx.response = "[red]Operation canceled by test environment to prevent infinite loop.[/]"
                    return
                
                self.ctx.status_message = "Tool call limit reached. Asking for user confirmation."
                console.print(f"\n[bold yellow]Warning:[/] The AI has used tools {max_tool_calls} times and may be in a loop.")
                if input(f"Do you want to allow it to continue for another {max_tool_calls} calls? (y/N) ").lower() != 'y':
                    self.ctx.response = "[red]Operation canceled by user.[/]"
                    return
            
            self.ctx.status_message = f"Thinking with {self.provider_config['name']}..."
            
            try:
                # Create chat completion with native tool support
                response = self._create_chat_completion()
                
                if not response or not response.choices:
                    self.ctx.response = "[red]Error:[/] No response from AI provider"
                    return
                
                choice = response.choices[0]
                message = choice.message
                
                # Handle tool calls using native OpenAI format
                if message.tool_calls:
                    self._handle_native_tool_calls(message, response)
                    continue
                
                # No tools called, this is the final response
                self.ctx.response = message.content or "No response content"
                self.message_history.append({"role": "assistant", "content": self.ctx.response})
                break
                
            except Exception as e:
                self.ctx.response = f"[red]API Error:[/] {str(e)}"
                if self.ctx.debug_mode:
                    console.print(f"[bold red]DEBUG:[/] Full error: {e}")
                return
        else:
            self.ctx.response = f"[red]Error:[/] Exceeded maximum tool calls ({max_tool_calls})."
    
    def _should_stream_response(self, user_input: str = "") -> bool:
        """Determine if response should be streamed based on semantic zones and complexity."""
        # Check if streaming is enabled for this provider
        streaming_enabled = os.getenv(f"DEEPCODERX_STREAMING_{self.provider_name.upper()}", "true").lower() == "true"
        if not streaming_enabled:
            return False
        
        # Use the last user message if user_input not provided
        if not user_input:
            for message in reversed(self.message_history):
                if message.get("role") == "user":
                    user_input = message.get("content", "")
                    break
        
        # Basic streaming triggers
        streaming_triggers = ["create", "generate", "write", "build", "implement", 
                             "develop", "code", "script", "function", "class", "design", "make"]
        
        # Check for semantic zones that typically require streaming
        creative_triggers = SEMANTIC_ZONES.get("creative", {}).get("triggers", [])
        analysis_triggers = SEMANTIC_ZONES.get("analysis", {}).get("triggers", [])
        tool_operation_triggers = SEMANTIC_ZONES.get("tool_operation", {}).get("triggers", [])
        
        # Combined trigger analysis
        all_triggers = streaming_triggers + creative_triggers + analysis_triggers + tool_operation_triggers
        
        # Check if input contains streaming triggers
        input_lower = user_input.lower()
        trigger_found = any(trigger in input_lower for trigger in all_triggers)
        
        # Additional complexity indicators
        complexity_indicators = ["complex", "detailed", "comprehensive", "full", "complete", "thorough"]
        has_complexity = any(indicator in input_lower for indicator in complexity_indicators)
        
        # Stream if triggers found or complexity detected
        should_stream = trigger_found or has_complexity or len(user_input) > 100
        
        if self.ctx.debug_mode and should_stream:
            console.print(f"[bold cyan]DEBUG:[/] Streaming enabled for: {user_input[:50]}...")
        
        return should_stream
    
    def _handle_streaming_response(self, completion_params: dict, user_input: str = "") -> any:
        """Handle streaming response with enhanced logging and error handling."""
        interaction_id = f"stream_{self.provider_name}_{int(time.time() * 1000)}"
        
        # Enhanced logging integration
        if self.ctx.debug_mode:
            log_model_prompt(
                model_name=f"{self.provider_name}-{self.provider_config['model']}",
                prompt=json.dumps(self.message_history, indent=2),
                parameters={**completion_params, "streaming": True},
                context="cloud_api_streaming"
            )
        
        try:
            response = self.client.chat.completions.create(**completion_params)
            accumulated_text = ""
            start_time = time.time()
            chunk_count = 0
            
            console.print(f"[cyan]🌊 Streaming response from {self.provider_config['name']}...[/cyan]")
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    accumulated_text += delta
                    chunk_count += 1
                    
                    # Print with streaming style
                    console.print(delta, end="", style="green")
            
            console.print()  # New line after streaming
            duration = time.time() - start_time
            
            # Enhanced logging for streaming response
            if self.ctx.debug_mode:
                log_model_response(
                    interaction_id=interaction_id,
                    model_name=f"{self.provider_name}-{self.provider_config['model']}",
                    response=accumulated_text,
                    duration=duration,
                    context="cloud_api_streaming",
                    raw_response=None,  # Don't log full streaming response object
                    token_usage={
                        "streaming_chunks": chunk_count,
                        "response_length": len(accumulated_text),
                        "avg_chunk_time": duration / chunk_count if chunk_count > 0 else 0
                    }
                )
            
            # Create a mock response object for compatibility
            class MockChoice:
                def __init__(self, content):
                    self.message = type('obj', (object,), {'content': content, 'tool_calls': None})()
            
            class MockResponse:
                def __init__(self, content):
                    self.choices = [MockChoice(content)]
                    self.usage = None
            
            return MockResponse(accumulated_text)
            
        except Exception as e:
            # Log streaming error
            if self.ctx.debug_mode:
                log_model_error(
                    interaction_id=interaction_id,
                    error=e,
                    context={"provider": self.provider_name, "streaming": True},
                    operation="streaming_response"
                )
            
            console.print(f"[yellow]⚠️  Streaming failed, falling back to standard response...[/yellow]")
            
            # Fallback to non-streaming
            completion_params["stream"] = False
            return self._handle_standard_response(completion_params)
    
    def _handle_standard_response(self, completion_params: dict) -> any:
        """Handle standard (non-streaming) response."""
        return self.client.chat.completions.create(**completion_params)
    
    def _create_chat_completion(self):
        """Create chat completion with streaming support and appropriate parameters."""
        completion_params = {
            "model": self.provider_config["model"],
            "messages": self.message_history,
            "temperature": self.provider_config.get("temperature", 0.1),
            "max_tokens": self.provider_config.get("max_tokens", 2048)
        }
        
        # Add tools using the Tool Registry Pattern
        # This enables consistent tool calling across local and cloud models
        if self.provider_config.get("supports_tools", False):
            completion_params["tools"] = self._get_tool_definitions()
            completion_params["tool_choice"] = "auto"
        
        # Determine if we should stream this response
        should_stream = self._should_stream_response()
        
        if should_stream:
            completion_params["stream"] = True
            return self._handle_streaming_response(completion_params)
        else:
            # Standard non-streaming path with existing logging
            # Log conversation context being sent
            context_interaction_id = f"openai_context_{int(time.time())}"
            log_conversation_context_details(
                interaction_id=context_interaction_id,
                conversation_history=self.message_history,
                context_summary=f"Provider: {self.provider_name}, Model: {self.provider_config['model']}"
            )
            
            # Log prompt being sent to API
            interaction_id = log_model_prompt(
                model_name=f"{self.provider_name}-{self.provider_config['model']}",
                prompt=json.dumps(self.message_history, indent=2),
                parameters=completion_params,
                context="cloud_api"
            )
            
            start_time = time.time()
            response = self.client.chat.completions.create(**completion_params)
            duration = time.time() - start_time
            
            # Log response received
            response_content = response.choices[0].message.content if response.choices else "No response"
            log_model_response(
                interaction_id=interaction_id,
                model_name=f"{self.provider_name}-{self.provider_config['model']}",
                response=response_content,
                duration=duration,
                context="cloud_api",
                raw_response=response,
                token_usage={
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0
                } if hasattr(response, 'usage') else None
            )
            
            # Log usage if available
            if hasattr(response, 'usage') and response.usage:
                log_api_usage(self.provider_name, response.usage.total_tokens)
            
            return response
    
    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI-format tool definitions using Tool Registry."""
        # Use the centralized tool registry instead of hardcoded definitions
        tools = get_tools_for_provider(self.provider_name, self.provider_config)
        
        if self.ctx.debug_mode:
            tool_names = [tool["function"]["name"] for tool in tools]
            console.print(f"[bold blue]DEBUG:[/] Loaded {len(tools)} tools from registry: {tool_names}")
        
        return tools
    
    def _handle_native_tool_calls(self, message, response):
        """Handle native OpenAI tool calls."""
        # Generate interaction ID for tool execution tracking
        tool_interaction_id = f"openai_tools_{int(time.time())}_{id(self)}"
        
        # Convert tool calls to legacy format for logging
        tool_calls_for_logging = []
        for tool_call in message.tool_calls:
            try:
                function_args = json.loads(tool_call.function.arguments)
                legacy_tool_call = {
                    "tool": tool_call.function.name,
                    "tool_call_id": tool_call.id,
                    **function_args
                }
                tool_calls_for_logging.append(legacy_tool_call)
            except json.JSONDecodeError:
                tool_calls_for_logging.append({
                    "tool": tool_call.function.name,
                    "tool_call_id": tool_call.id,
                    "arguments_raw": tool_call.function.arguments,
                    "parse_error": True
                })
        
        # Log tool calls being executed
        log_tool_execution_details(
            interaction_id=tool_interaction_id,
            tool_calls=tool_calls_for_logging,
            execution_details={
                "provider": self.provider_name,
                "tool_count": len(message.tool_calls),
                "assistant_content": message.content
            }
        )
        
        self.message_history.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in message.tool_calls
            ]
        })
        
        # Execute each tool call
        tool_results = []
        execution_errors = []
        start_time = time.time()
        
        for i, tool_call in enumerate(message.tool_calls):
            tool_start = time.time()
            try:
                # Parse function arguments
                function_args = json.loads(tool_call.function.arguments)
                
                # Create legacy format for tool executor
                legacy_tool_call = {
                    "tool": tool_call.function.name,
                    **function_args
                }
                
                self.ctx.status = f"Using tool: {tool_call.function.name}..."
                
                # Execute using existing tool executor
                result = self.tool_executor.execute_tool(legacy_tool_call)
                tool_results.append(str(result))
                tool_duration = time.time() - tool_start
                
                # Add tool result to message history
                self.message_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
                
                if self.ctx.debug_mode:
                    console.print(f"[bold blue]Tool {tool_call.function.name} result ({tool_duration:.2f}s):[/] {result}")
                    
            except Exception as e:
                error_msg = f"Tool execution error: {str(e)}"
                tool_results.append(error_msg)
                execution_errors.append({"tool_index": i, "tool_call": tool_call.function.name, "error": str(e)})
                
                self.message_history.append({
                    "role": "tool", 
                    "tool_call_id": tool_call.id,
                    "content": error_msg
                })
                
                # Log individual tool error
                log_model_error(
                    interaction_id=tool_interaction_id,
                    error=e,
                    context={"tool_call": legacy_tool_call, "tool_index": i, "provider": self.provider_name},
                    operation=f"openai_tool_execution_{tool_call.function.name}"
                )
                
                if self.ctx.debug_mode:
                    console.print(f"[bold red]Tool error:[/] {error_msg}")
        
        total_duration = time.time() - start_time
        
        # Log final tool execution results
        log_tool_execution_details(
            interaction_id=tool_interaction_id,
            tool_calls=tool_calls_for_logging,
            tool_results=tool_results,
            execution_details={
                "provider": self.provider_name,
                "total_duration": total_duration,
                "execution_errors": execution_errors,
                "success_count": len(tool_results) - len(execution_errors),
                "error_count": len(execution_errors)
            }
        )
        
        # Log performance metrics
        log_model_performance(
            interaction_id=tool_interaction_id,
            operation="openai_tool_execution_batch",
            metrics={
                "duration": total_duration,
                "tool_count": len(message.tool_calls),
                "success_rate": (len(message.tool_calls) - len(execution_errors)) / len(message.tool_calls) if message.tool_calls else 0,
                "average_tool_time": total_duration / len(message.tool_calls) if message.tool_calls else 0,
                "provider": self.provider_name
            }
        )
    
    def _handle_legacy_tool_calls(self, model_response_text: str):
        """Handle legacy JSON tool calls for local models that don't support native tools."""
        tool_call_matches = re.findall(r'\{.*?\}', model_response_text, re.DOTALL)
        
        if not tool_call_matches:
            return False
        
        tool_results = []
        for tool_call_json in tool_call_matches:
            try:
                response_json = json.loads(tool_call_json)
                if "tool" in response_json:
                    self.ctx.status = f"Using tool: {response_json['tool']}..."
                    result = self.tool_executor.execute_tool(response_json)
                    tool_results.append(str(result))
            except json.JSONDecodeError:
                # Ignore invalid JSON
                continue
        
        if tool_results:
            self.message_history.append({"role": "assistant", "content": model_response_text})
            self.message_history.append({"role": "user", "content": f"Tool Results: \n" + "\n".join(tool_results)})
            return True
        
        return False
    
    def _maintain_history(self):
        """Maintain reasonable conversation history size."""
        if len(self.message_history) > config.HISTORY_TRIM_SIZE:
            # Keep system prompt and recent messages
            system_prompt = self.message_history[0]
            recent_messages = self.message_history[-config.HISTORY_KEEP_SIZE:]
            self.message_history = [system_prompt] + recent_messages
    
    def clear_history(self):
        """Reset conversation history and delete session file."""
        self._reset_history()
        if self.session_file.exists():
            self.session_file.unlink()
        if self.ctx.debug_mode:
            console.print(f"[bold red]DEBUG:[/] {self.provider_config['name']} conversation history cleared.")


class LocalOpenAIHandler(UnifiedOpenAIHandler):
    """Specialized handler for local LM Studio provider."""
    
    ANALYSIS_KEYWORDS = {
        r'\barchitecture\b', r'\breview\b', r'\brefactor\b', r'\bdependencies\b',
        r'\bcross-file\b', r'\bcodebase\b', r'\bpattern\b', r'\banalyze\b',
        r'\bexplain\b', r'\bimprove\b', r'\boptimize\b', r'\bdesign\b'
    }
    
    def __init__(self, context: CommandContext):
        super().__init__(context, "local")
    
    def can_handle(self) -> bool:
        """Handle local requests and fallback for everything else."""
        if not self.provider_config["enabled"]:
            return False
        
        # Handle if specifically requested or if no analysis keywords present
        query = self.ctx.user_input.lower()
        is_analysis = any(re.search(pattern, query) for pattern in self.ANALYSIS_KEYWORDS)
        
        return not is_analysis or self.ctx.user_input.lower().startswith("@qwen")
    
    def _conversation_loop(self):
        """Override to use legacy JSON tool calling for local models."""
        max_tool_calls = config.MAX_TOOL_CALLS
        recent_tool_calls = []
        
        for i in range(max_tool_calls):
            if i == max_tool_calls - 1:
                if "PYTEST_CURRENT_TEST" in os.environ:
                    self.ctx.response = "[red]Operation canceled by test environment to prevent infinite loop.[/]"
                    return
                
                console.print(f"\n[bold yellow]Warning:[/] The AI has used tools {max_tool_calls} times and may be in a loop.")
                if input(f"Do you want to continue? (y/N) ").lower() != 'y':
                    self.ctx.response = "[red]Operation canceled by user.[/]"
                    return
            
            self.ctx.status_message = f"Thinking with {self.provider_config['name']}..."
            
            try:
                # Create chat completion WITHOUT tools for local models
                completion_params = {
                    "model": self.provider_config["model"],
                    "messages": self.message_history,
                    "temperature": self.provider_config.get("temperature", 0.1),
                    "max_tokens": self.provider_config.get("max_tokens", 2048)
                }
                
                response = self.client.chat.completions.create(**completion_params)
                
                # Log usage if available
                if hasattr(response, 'usage') and response.usage:
                    log_api_usage(self.provider_name, response.usage.total_tokens)
                
                model_response_text = response.choices[0].message.content or ""
                
                # Use legacy JSON tool calling for local models
                if self._handle_legacy_tool_calls(model_response_text):
                    # Check for loop detection
                    tool_call_match = re.search(r'\{.*?\}', model_response_text, re.DOTALL)
                    if tool_call_match:
                        tool_call_signature = tool_call_match.group(0).strip()
                        if tool_call_signature and len(recent_tool_calls) > 0 and recent_tool_calls[-1] == tool_call_signature:
                            self.ctx.response = "Task completed successfully."
                            self.message_history.append({"role": "assistant", "content": self.ctx.response})
                            break
                        
                        recent_tool_calls.append(tool_call_signature)
                        if len(recent_tool_calls) > 2:
                            recent_tool_calls.pop(0)
                    continue
                
                # No tools, final response
                self.ctx.response = model_response_text
                self.message_history.append({"role": "assistant", "content": self.ctx.response})
                break
                
            except Exception as e:
                self.ctx.response = f"[red]API Error:[/] {str(e)}"
                return
        else:
            self.ctx.response = f"[red]Error:[/] Exceeded maximum tool calls ({max_tool_calls})."


class CloudOpenAIHandler(UnifiedOpenAIHandler):
    """Specialized handler for cloud providers (DeepSeek, OpenAI, etc.)."""
    
    ANALYSIS_KEYWORDS = {
        r'\barchitecture\b', r'\breview\b', r'\brefactor\b', r'\bdependencies\b',
        r'\bcross-file\b', r'\bcodebase\b', r'\bpattern\b', r'\banalyze\b',
        r'\bexplain\b', r'\bimprove\b', r'\boptimize\b', r'\bdesign\b'
    }
    
    def __init__(self, context: CommandContext, provider: str = "deepseek"):
        super().__init__(context, provider)
        
        # For cloud providers, force clean session to prevent tool message format errors
        if self.provider_name != "local":
            self._force_clean_session_if_needed()
    
    def _force_clean_session_if_needed(self):
        """Force clean session for cloud providers to prevent OpenAI format violations."""
        # Check if current session has any potential tool message issues
        has_tool_issues = False
        
        for i, message in enumerate(self.message_history):
            if message.get("role") == "tool":
                # Check if previous message has tool_calls
                if i == 0 or self.message_history[i-1].get("role") != "assistant" or "tool_calls" not in self.message_history[i-1]:
                    has_tool_issues = True
                    break
        
        if has_tool_issues:
            if self.ctx.debug_mode:
                console.print(f"[bold yellow]WARNING:[/] Detected tool message format issues for {self.provider_name}. Forcing clean reset.")
            self._reset_history()
            self._save_history()
    
    def can_handle(self) -> bool:
        """Handle analysis requests and explicit provider requests."""
        if not self.provider_config["enabled"]:
            return False
        
        # Handle if explicitly requested
        if self.ctx.user_input.lower().startswith(f"@{self.provider_name}"):
            return True
        
        # Handle analysis keywords
        query = self.ctx.user_input.lower()
        if "--build-context" in query:
            return True
        
        return any(re.search(pattern, query) for pattern in self.ANALYSIS_KEYWORDS)
