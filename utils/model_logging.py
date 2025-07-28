"""
Comprehensive Model Interaction Logging System for DeepCoderX

Provides detailed logging of all model interactions including:
- Prompts sent to models
- Raw responses received
- Semantic analysis attempts
- Tool calls and results
- Conversation context
- Performance metrics
- Error details with context

Essential for debugging model behavior, hallucinations, and performance issues.
"""

import json
import time
import os
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from utils.logging import log_debug, log_info, log_warning, setup_component_logger, LOGS_DIR


class ModelInteractionLogger:
    """
    Comprehensive logging system for all model interactions.
    
    Features:
    - Structured JSONL logs for easy analysis
    - Interaction ID tracking for correlation
    - Configurable logging levels
    - Performance metrics
    - Privacy-aware truncation options
    """
    
    def __init__(self, component_name: str = "ModelInteraction"):
        self.component_name = component_name
        self.logger = setup_component_logger(component_name)
        
        # Create model-specific log directory
        self.model_logs_dir = LOGS_DIR / "model_interactions"
        self.model_logs_dir.mkdir(exist_ok=True)
        
        # Session ID for tracking related interactions
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Counters for interaction tracking
        self.interaction_counter = 0
        
        # Configuration from environment variables
        self.config = {
            "log_prompts": os.getenv("DEEPCODERX_LOG_MODEL_PROMPTS", "true").lower() == "true",
            "log_responses": os.getenv("DEEPCODERX_LOG_MODEL_RESPONSES", "true").lower() == "true",
            "log_semantic": os.getenv("DEEPCODERX_LOG_SEMANTIC_DETAILS", "true").lower() == "true",
            "log_tools": os.getenv("DEEPCODERX_LOG_TOOL_DETAILS", "true").lower() == "true",
            "log_context": os.getenv("DEEPCODERX_LOG_CONVERSATION_CONTEXT", "true").lower() == "true",
            "truncate_long_content": os.getenv("DEEPCODERX_TRUNCATE_LOGS", "false").lower() == "true",
            "max_content_length": int(os.getenv("DEEPCODERX_MAX_LOG_LENGTH", "10000"))
        }
        
        log_info(component_name, f"Model interaction logging initialized - Session: {self.session_id}")
        log_debug(component_name, f"Logging config: {self.config}")
    
    def _get_interaction_id(self) -> str:
        """Generate unique interaction ID for tracking."""
        self.interaction_counter += 1
        return f"{self.session_id}_{self.interaction_counter:04d}"
    
    def _truncate_content(self, content: str, context: str = "content") -> str:
        """Truncate content if configured to do so."""
        if self.config["truncate_long_content"] and len(content) > self.config["max_content_length"]:
            max_len = self.config["max_content_length"]
            truncated = content[:max_len] + f"... [TRUNCATED - Original length: {len(content)}]"
            log_debug(self.component_name, f"Truncated {context} from {len(content)} to {len(truncated)} chars")
            return truncated
        return content
    
    def _write_log_entry(self, filename: str, entry: Dict[str, Any]) -> None:
        """Write log entry to JSONL file."""
        try:
            log_file = self.model_logs_dir / filename
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        except Exception as e:
            log_warning(self.component_name, f"Failed to write log entry to {filename}: {e}")
    
    def log_prompt_sent(self, model_name: str, prompt: str, parameters: Dict[str, Any] = None,
                       context: str = "generation", user_input: str = None) -> str:
        """
        Log prompt being sent to model.
        
        Args:
            model_name: Name of the model (e.g., "Llama-3.2-3B", "Qwen2.5-Coder")
            prompt: Full prompt text being sent
            parameters: Model parameters (temperature, max_tokens, etc.)
            context: Context of the call (e.g., "semantic_analysis", "code_generation")
            user_input: Original user input that triggered this prompt
            
        Returns:
            Interaction ID for tracking related logs
        """
        interaction_id = self._get_interaction_id()
        
        # Basic console logging
        log_info(self.component_name, 
                f"[{interaction_id}] PROMPT → {model_name} ({context}) - {len(prompt)} chars")
        
        if self.config["log_prompts"]:
            # Detailed prompt logging to file
            prompt_content = self._truncate_content(prompt, "prompt")
            
            prompt_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                "model_name": model_name,
                "context": context,
                "user_input": user_input,
                "prompt_length": len(prompt),
                "prompt_text": prompt_content,
                "parameters": parameters or {},
                "session_id": self.session_id
            }
            
            self._write_log_entry(f"prompts_{self.session_id}.jsonl", prompt_entry)
            
            # Debug log with truncated prompt preview
            preview = prompt[:200].replace('\n', '\\n')
            log_debug(self.component_name, f"[{interaction_id}] Prompt preview: {preview}...")
        
        return interaction_id
    
    def log_response_received(self, interaction_id: str, model_name: str, 
                            response: Union[str, Dict[str, Any]], duration: float,
                            context: str = "generation", raw_response: Any = None,
                            token_usage: Dict[str, int] = None):
        """
        Log response received from model.
        
        Args:
            interaction_id: ID from log_prompt_sent
            model_name: Name of the model
            response: Processed response (text or structured data)
            duration: Response generation time in seconds
            context: Context of the call
            raw_response: Raw response object (for debugging)
            token_usage: Token usage statistics
        """
        # Extract response text for logging
        if isinstance(response, dict):
            response_text = json.dumps(response, indent=2)
        else:
            response_text = str(response)
        
        response_length = len(response_text)
        
        # Basic console logging
        log_info(self.component_name,
                f"[{interaction_id}] RESPONSE ← {model_name} - {response_length} chars in {duration:.2f}s")
        
        if self.config["log_responses"]:
            # Detailed response logging
            response_content = self._truncate_content(response_text, "response")
            
            response_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                "model_name": model_name,
                "context": context,
                "duration_seconds": duration,
                "response_length": response_length,
                "response_text": response_content,
                "raw_response_type": type(raw_response).__name__ if raw_response else None,
                "token_usage": token_usage,
                "session_id": self.session_id
            }
            
            # Add token usage from raw response if available
            if hasattr(raw_response, 'usage'):
                response_entry["api_token_usage"] = {
                    "prompt_tokens": getattr(raw_response.usage, 'prompt_tokens', None),
                    "completion_tokens": getattr(raw_response.usage, 'completion_tokens', None),
                    "total_tokens": getattr(raw_response.usage, 'total_tokens', None)
                }
            
            self._write_log_entry(f"responses_{self.session_id}.jsonl", response_entry)
            
            # Debug log with truncated response preview
            preview = response_text[:200].replace('\n', '\\n')
            log_debug(self.component_name, f"[{interaction_id}] Response preview: {preview}...")
    
    def log_semantic_analysis(self, interaction_id: str, user_input: str, 
                            raw_response: str, parsed_result: Dict[str, Any] = None,
                            zone_info: Dict[str, Any] = None, error: str = None):
        """
        Log semantic analysis attempts and results.
        
        Args:
            interaction_id: Related interaction ID
            user_input: Original user input
            raw_response: Raw response from semantic model
            parsed_result: Parsed semantic analysis result
            zone_info: Semantic zone detection results
            error: Parse error if any
        """
        confidence = parsed_result.get('confidence', 0) if parsed_result else 0
        intent = parsed_result.get('intent_type', 'unknown') if parsed_result else 'parse_failed'
        
        log_info(self.component_name,
                f"[{interaction_id}] SEMANTIC → Intent: {intent} Confidence: {confidence:.2f}")
        
        if error:
            log_warning(self.component_name, f"[{interaction_id}] Semantic parse error: {error}")
        
        if self.config["log_semantic"]:
            semantic_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                "user_input": user_input,
                "raw_response": self._truncate_content(raw_response, "semantic_response"),
                "parsed_result": parsed_result,
                "zone_info": zone_info,
                "parse_error": error,
                "session_id": self.session_id
            }
            
            self._write_log_entry(f"semantic_{self.session_id}.jsonl", semantic_entry)
    
    def log_tool_calls(self, interaction_id: str, tool_calls: List[Dict[str, Any]], 
                      tool_results: List[str] = None, execution_details: Dict[str, Any] = None):
        """
        Log tool calls and their results.
        
        Args:
            interaction_id: Related interaction ID
            tool_calls: List of tool calls with parameters
            tool_results: Results from tool execution
            execution_details: Additional execution details
        """
        tool_names = [tc.get('tool', 'unknown') for tc in tool_calls]
        log_info(self.component_name,
                f"[{interaction_id}] TOOLS → {len(tool_calls)} calls: {', '.join(tool_names)}")
        
        if self.config["log_tools"]:
            # Truncate tool results if they're very long
            truncated_results = []
            if tool_results:
                for result in tool_results:
                    truncated_results.append(self._truncate_content(str(result), "tool_result"))
            
            tools_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                "tool_calls": tool_calls,
                "tool_results": truncated_results,
                "execution_details": execution_details,
                "session_id": self.session_id
            }
            
            self._write_log_entry(f"tools_{self.session_id}.jsonl", tools_entry)
            
            # Log individual tool calls for visibility
            for i, tool_call in enumerate(tool_calls):
                tool_name = tool_call.get('tool', 'unknown')
                log_debug(self.component_name,
                         f"[{interaction_id}] Tool {i+1}: {tool_name} with params: {tool_call}")
    
    def log_conversation_context(self, interaction_id: str, conversation_history: List[Dict[str, Any]],
                               context_summary: str = None, truncated: bool = False):
        """
        Log conversation context being sent to model.
        
        Args:
            interaction_id: Related interaction ID  
            conversation_history: Full conversation history
            context_summary: Optional summary of context
            truncated: Whether the context was truncated
        """
        history_length = len(conversation_history)
        total_chars = sum(len(str(msg.get('content', ''))) for msg in conversation_history)
        
        log_debug(self.component_name,
                 f"[{interaction_id}] CONTEXT → {history_length} messages, {total_chars} chars" + 
                 (" [TRUNCATED]" if truncated else ""))
        
        if self.config["log_context"]:
            # Truncate conversation history if needed
            truncated_history = []
            for msg in conversation_history:
                if isinstance(msg, dict) and 'content' in msg:
                    truncated_msg = msg.copy()
                    truncated_msg['content'] = self._truncate_content(str(msg['content']), "message_content")
                    truncated_history.append(truncated_msg)
                else:
                    truncated_history.append(msg)
            
            context_entry = {
                "timestamp": datetime.now().isoformat(),
                "interaction_id": interaction_id,
                "history_length": history_length,
                "total_characters": total_chars,
                "conversation_history": truncated_history,
                "context_summary": context_summary,
                "was_truncated": truncated,
                "session_id": self.session_id
            }
            
            self._write_log_entry(f"context_{self.session_id}.jsonl", context_entry)
    
    def log_error_with_context(self, interaction_id: str, error: Exception, 
                              context: Dict[str, Any] = None, operation: str = None):
        """
        Log errors with full context for debugging.
        
        Args:
            interaction_id: Related interaction ID
            error: Exception that occurred
            context: Additional context information
            operation: Operation that failed
        """
        error_msg = f"[{interaction_id}] ERROR in {operation}: {str(error)}" if operation else f"[{interaction_id}] ERROR: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        
        # Also log to errors file with context
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "interaction_id": interaction_id,
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "session_id": self.session_id
        }
        
        self._write_log_entry(f"errors_{self.session_id}.jsonl", error_entry)
    
    def log_performance_metrics(self, interaction_id: str, operation: str, 
                              metrics: Dict[str, Any]):
        """
        Log detailed performance metrics.
        
        Args:
            interaction_id: Related interaction ID
            operation: Operation name
            metrics: Performance metrics dictionary
        """
        duration = metrics.get('duration', 0)
        log_info(self.component_name, 
                f"[{interaction_id}] PERF → {operation}: {duration:.2f}s")
        
        perf_entry = {
            "timestamp": datetime.now().isoformat(),
            "interaction_id": interaction_id,
            "operation": operation,
            "metrics": metrics,
            "session_id": self.session_id
        }
        
        self._write_log_entry(f"performance_{self.session_id}.jsonl", perf_entry)
        
        # Log specific metrics
        for metric, value in metrics.items():
            log_debug(self.component_name, f"[{interaction_id}] {operation}.{metric}: {value}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session's interactions."""
        return {
            "session_id": self.session_id,
            "total_interactions": self.interaction_counter,
            "log_directory": str(self.model_logs_dir),
            "config": self.config,
            "log_files": list(self.model_logs_dir.glob(f"*_{self.session_id}.jsonl"))
        }


# Global logger instance
_global_logger = None

def get_model_logger(component_name: str = "ModelInteraction") -> ModelInteractionLogger:
    """Get or create global model logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = ModelInteractionLogger(component_name)
    return _global_logger


# Convenience functions for easy access
def log_model_prompt(model_name: str, prompt: str, parameters: Dict[str, Any] = None,
                    context: str = "generation", user_input: str = None) -> str:
    """Log prompt sent to model."""
    return get_model_logger().log_prompt_sent(model_name, prompt, parameters, context, user_input)

def log_model_response(interaction_id: str, model_name: str, response: Union[str, Dict[str, Any]], 
                      duration: float, context: str = "generation", raw_response: Any = None,
                      token_usage: Dict[str, int] = None):
    """Log response received from model."""
    get_model_logger().log_response_received(interaction_id, model_name, response, duration, 
                                           context, raw_response, token_usage)

def log_semantic_analysis_attempt(interaction_id: str, user_input: str, raw_response: str,
                                parsed_result: Dict[str, Any] = None, zone_info: Dict[str, Any] = None,
                                error: str = None):
    """Log semantic analysis attempt."""
    get_model_logger().log_semantic_analysis(interaction_id, user_input, raw_response, 
                                            parsed_result, zone_info, error)

def log_tool_execution_details(interaction_id: str, tool_calls: List[Dict[str, Any]], 
                             tool_results: List[str] = None, execution_details: Dict[str, Any] = None):
    """Log tool execution details."""
    get_model_logger().log_tool_calls(interaction_id, tool_calls, tool_results, execution_details)

def log_conversation_context_details(interaction_id: str, conversation_history: List[Dict[str, Any]],
                                   context_summary: str = None, truncated: bool = False):
    """Log conversation context details."""
    get_model_logger().log_conversation_context(interaction_id, conversation_history, 
                                               context_summary, truncated)

def log_model_error(interaction_id: str, error: Exception, context: Dict[str, Any] = None, 
                   operation: str = None):
    """Log error with model interaction context."""
    get_model_logger().log_error_with_context(interaction_id, error, context, operation)

def log_model_performance(interaction_id: str, operation: str, metrics: Dict[str, Any]):
    """Log performance metrics."""
    get_model_logger().log_performance_metrics(interaction_id, operation, metrics)
