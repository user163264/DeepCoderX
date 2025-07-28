import logging
import logging.handlers
import sys
import json
import uuid
import time
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install
from typing import Dict, List, Any, Optional

# Install rich traceback for better error formatting
install(show_locals=True)

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create model interactions directory
MODEL_INTERACTIONS_DIR = LOGS_DIR / "model_interactions"
MODEL_INTERACTIONS_DIR.mkdir(exist_ok=True)

# Create console instance for rich formatting
console = Console()

class DeepCoderXFormatter(logging.Formatter):
    """Custom formatter for DeepCoderX logs with timestamps and component info"""
    
    def format(self, record):
        # Add timestamp
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add component info if available
        component = getattr(record, 'component', 'SYSTEM')
        record.component = component
        
        # Format the message
        if record.levelno >= logging.ERROR:
            return f"[{record.timestamp}] ERROR [{record.component}] {record.getMessage()}"
        elif record.levelno >= logging.WARNING:
            return f"[{record.timestamp}] WARN  [{record.component}] {record.getMessage()}"
        elif record.levelno >= logging.INFO:
            return f"[{record.timestamp}] INFO  [{record.component}] {record.getMessage()}"
        else:
            return f"[{record.timestamp}] DEBUG [{record.component}] {record.getMessage()}"

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a logger with both console and file handlers
    
    Args:
        name: Logger name (typically the component name)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler with Rich formatting (for user-visible messages)
    console_handler = RichHandler(
        console=console, 
        show_time=False, 
        show_level=True,
        rich_tracebacks=True,
        markup=True
    )
    console_handler.setLevel(logging.INFO)  # Only show INFO+ on console
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console_handler)
    
    # Error log file handler (rotating, for persistent error storage)
    error_log_path = LOGS_DIR / f"deepcoderx_errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DeepCoderXFormatter())
    logger.addHandler(error_handler)
    
    # Debug log file handler (rotating, for development debugging)
    debug_log_path = LOGS_DIR / f"deepcoderx_debug.log"
    debug_handler = logging.handlers.RotatingFileHandler(
        debug_log_path,
        maxBytes=50*1024*1024,  # 50MB
        backupCount=3,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(DeepCoderXFormatter())
    logger.addHandler(debug_handler)
    
    # Session log handler (for current session only)
    session_log_path = LOGS_DIR / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    session_handler = logging.FileHandler(session_log_path, encoding='utf-8')
    session_handler.setLevel(logging.INFO)
    session_handler.setFormatter(DeepCoderXFormatter())
    logger.addHandler(session_handler)
    
    return logger

def setup_component_logger(component_name: str) -> logging.Logger:
    """
    Create a component-specific logger with the component name
    
    Args:
        component_name: Name of the component (e.g., 'DualModelHandler', 'GGUFHandler')
    
    Returns:
        Logger configured for the specific component
    """
    logger = setup_logger(f"deepcoderx.{component_name}")
    
    # Add component name to all log records
    class ComponentFilter(logging.Filter):
        def filter(self, record):
            record.component = component_name
            return True
    
    for handler in logger.handlers:
        handler.addFilter(ComponentFilter())
    
    return logger

# Create main system logger
logger = setup_logger("deepcoderx")

# Create component-specific loggers for easy access
dual_model_logger = setup_component_logger("DualModel")
gguf_logger = setup_component_logger("GGUF")
openai_logger = setup_component_logger("OpenAI")
app_logger = setup_component_logger("App")
router_logger = setup_component_logger("Router")
tools_logger = setup_component_logger("Tools")

def log_error(component: str, message: str, exception: Exception = None):
    """
    Log an error with optional exception details
    
    Args:
        component: Component name where error occurred
        message: Error message
        exception: Optional exception object for traceback
    """
    component_logger = setup_component_logger(component)
    
    if exception:
        component_logger.error(f"{message}: {str(exception)}", exc_info=True)
        # Also log to console with rich formatting
        console.print(f"[red]ERROR [{component}]:[/] {message}")
        console.print(f"[red]Exception:[/] {str(exception)}")
    else:
        component_logger.error(message)
        console.print(f"[red]ERROR [{component}]:[/] {message}")

def log_warning(component: str, message: str):
    """
    Log a warning message
    
    Args:
        component: Component name
        message: Warning message
    """
    component_logger = setup_component_logger(component)
    component_logger.warning(message)
    console.print(f"[yellow]WARNING [{component}]:[/] {message}")

def log_info(component: str, message: str):
    """
    Log an info message
    
    Args:
        component: Component name
        message: Info message
    """
    component_logger = setup_component_logger(component)
    component_logger.info(message)

def log_debug(component: str, message: str):
    """
    Log a debug message (only to file, not console)
    
    Args:
        component: Component name
        message: Debug message
    """
    component_logger = setup_component_logger(component)
    component_logger.debug(message)

def log_api_usage(provider: str, tokens: int, cost: float = None):
    """
    Log API token usage statistics with rich formatting and file persistence
    
    Args:
        provider: API provider name
        tokens: Number of tokens used
        cost: Optional cost in USD
    """
    api_logger = setup_component_logger("API")
    
    cost_str = f" (${cost:.4f})" if cost else ""
    message = f"Usage: {provider} - {tokens} tokens{cost_str}"
    
    # Log to file
    api_logger.info(message)
    
    # Display on console with rich formatting
    console.print(f"[dim]📊 API Usage: [bold]{provider}[/] - {tokens} tokens{cost_str}[/dim]")

def log_model_loading(component: str, model_name: str, memory_usage: str = None, duration: float = None):
    """
    Log model loading events with performance metrics
    
    Args:
        component: Component loading the model
        model_name: Name of the model being loaded
        memory_usage: Optional memory usage info
        duration: Optional loading duration in seconds
    """
    model_logger = setup_component_logger(component)
    
    duration_str = f" in {duration:.2f}s" if duration else ""
    memory_str = f" ({memory_usage})" if memory_usage else ""
    message = f"Loaded model: {model_name}{memory_str}{duration_str}"
    
    model_logger.info(message)
    console.print(f"[green]✓ [{component}][/] {message}")

def log_performance(component: str, operation: str, duration: float, details: str = None):
    """
    Log performance metrics
    
    Args:
        component: Component performing the operation
        operation: Operation name
        duration: Duration in seconds
        details: Optional additional details
    """
    perf_logger = setup_component_logger(component)
    
    details_str = f" - {details}" if details else ""
    message = f"Performance: {operation} took {duration:.2f}s{details_str}"
    
    perf_logger.info(message)
    
    # Only show slow operations on console
    if duration > 5.0:
        console.print(f"[yellow]⏱ [{component}][/] {operation} took {duration:.2f}s{details_str}")

def log_routing_decision(intent_type: str, specialist: str, confidence: float, user_input: str):
    """
    Log routing decisions for debugging
    
    Args:
        intent_type: Classified intent type
        specialist: Selected specialist
        confidence: Confidence score
        user_input: User input (truncated for privacy)
    """
    routing_logger = setup_component_logger("Routing")
    
    # Truncate user input for privacy
    input_preview = user_input[:50] + "..." if len(user_input) > 50 else user_input
    
    message = f"Route: '{input_preview}' → {intent_type} → {specialist} (confidence: {confidence:.2f})"
    routing_logger.info(message)
    routing_logger.debug(f"Full routing decision: intent={intent_type}, specialist={specialist}, confidence={confidence}, input='{user_input}'")

def get_log_summary() -> dict:
    """
    Get a summary of current log files and their sizes
    
    Returns:
        Dictionary with log file information
    """
    summary = {}
    
    for log_file in LOGS_DIR.glob("*.log"):
        try:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            summary[log_file.name] = {
                'size_mb': round(size_mb, 2),
                'path': str(log_file),
                'modified': datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            summary[log_file.name] = {'error': str(e)}
    
    return summary

def setup_session_logging():
    """
    Setup logging for the current session with startup info
    """
    logger.info("="*60)
    logger.info("DeepCoderX Session Started")
    logger.info(f"Session ID: {datetime.now().strftime('%Y%m%d_%H%M%S')}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Logs directory: {LOGS_DIR}")
    logger.info("="*60)

# ===== ENHANCED MODEL INTERACTION LOGGING FUNCTIONS =====

def _get_debug_logging_config():
    """Get debug logging configuration with fallback to avoid circular imports."""
    try:
        # Try to import config - avoid circular imports
        import sys
        if 'config_module' in sys.modules:
            from config_module import DEBUG_LOGGING
            return DEBUG_LOGGING
        else:
            # Fallback configuration if config not loaded yet
            return {
                "model_prompts": False,
                "model_responses": False,
                "semantic_details": False,
                "tool_details": False,
                "conversation_context": False,
                "interaction_tracking": True,
                "structured_storage": True
            }
    except ImportError:
        # Fallback if config module not available
        return {
            "model_prompts": False,
            "model_responses": False,
            "semantic_details": False,
            "tool_details": False,
            "conversation_context": False,
            "interaction_tracking": True,
            "structured_storage": True
        }

def _generate_interaction_id() -> str:
    """Generate a unique interaction ID for tracking related logs."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"

def _write_structured_log(log_type: str, data: Dict[str, Any]):
    """Write structured log data to JSONL files."""
    debug_config = _get_debug_logging_config()
    if not debug_config.get("structured_storage", True):
        return
    
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = MODEL_INTERACTIONS_DIR / f"{log_type}_{timestamp[:8]}.jsonl"  # Daily files
        
        # Add timestamp to data
        data["timestamp"] = datetime.now().isoformat()
        data["log_type"] = log_type
        
        # Append to JSONL file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
            
    except Exception as e:
        # Fallback to regular logging if structured logging fails
        logger.error(f"Failed to write structured log for {log_type}: {e}")

def log_model_prompt(component: str, model_name: str, prompt: str, interaction_id: str = None):
    """
    Log model prompts for debugging and optimization.
    
    Args:
        component: Component making the model call (e.g., 'DualModel', 'OpenAI')
        model_name: Name of the model being called
        prompt: The prompt being sent to the model
        interaction_id: Optional interaction ID for tracking related logs
    """
    debug_config = _get_debug_logging_config()
    if not debug_config.get("model_prompts", False):
        return
    
    if not interaction_id:
        interaction_id = _generate_interaction_id()
    
    # Create component logger
    component_logger = setup_component_logger(component)
    
    # Log to standard logs
    component_logger.debug(f"[{interaction_id}] Model Prompt to {model_name}:")
    component_logger.debug(f"[{interaction_id}] Prompt Length: {len(prompt)} chars")
    component_logger.debug(f"[{interaction_id}] Prompt Preview: {prompt[:200]}...")
    
    # Log to structured storage
    _write_structured_log("prompts", {
        "interaction_id": interaction_id,
        "component": component,
        "model_name": model_name,
        "prompt": prompt,
        "prompt_length": len(prompt),
        "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt
    })
    
    return interaction_id

def log_model_response(component: str, model_name: str, response: str, duration: float, interaction_id: str = None):
    """
    Log model responses for debugging and analysis.
    
    Args:
        component: Component that made the model call
        model_name: Name of the model that responded
        response: The response from the model
        duration: Response generation duration in seconds
        interaction_id: Interaction ID for tracking related logs
    """
    debug_config = _get_debug_logging_config()
    if not debug_config.get("model_responses", False):
        return
    
    if not interaction_id:
        interaction_id = _generate_interaction_id()
    
    # Create component logger
    component_logger = setup_component_logger(component)
    
    # Log to standard logs
    component_logger.debug(f"[{interaction_id}] Model Response from {model_name}:")
    component_logger.debug(f"[{interaction_id}] Response Length: {len(response)} chars, Duration: {duration:.2f}s")
    component_logger.debug(f"[{interaction_id}] Response Preview: {response[:200]}...")
    
    # Log to structured storage
    _write_structured_log("responses", {
        "interaction_id": interaction_id,
        "component": component,
        "model_name": model_name,
        "response": response,
        "response_length": len(response),
        "duration_seconds": duration,
        "response_preview": response[:200] + "..." if len(response) > 200 else response
    })
    
    return interaction_id

def log_semantic_analysis(component: str, user_input: str, semantic_prompt: str, raw_response: str, 
                         parsed_result: Optional[Dict[str, Any]], success: bool, interaction_id: str = None):
    """
    Log semantic analysis attempts and results for debugging.
    
    Args:
        component: Component performing semantic analysis
        user_input: Original user input being analyzed
        semantic_prompt: The prompt sent for semantic analysis
        raw_response: Raw response from semantic parser
        parsed_result: Parsed semantic analysis result (None if failed)
        success: Whether parsing was successful
        interaction_id: Interaction ID for tracking
    """
    debug_config = _get_debug_logging_config()
    if not debug_config.get("semantic_details", False):
        return
    
    if not interaction_id:
        interaction_id = _generate_interaction_id()
    
    # Create component logger
    component_logger = setup_component_logger(component)
    
    # Log to standard logs
    status = "SUCCESS" if success else "FAILED"
    component_logger.debug(f"[{interaction_id}] Semantic Analysis {status}:")
    component_logger.debug(f"[{interaction_id}] User Input: {user_input[:100]}...")
    component_logger.debug(f"[{interaction_id}] Raw Response: {raw_response[:200]}...")
    if parsed_result:
        component_logger.debug(f"[{interaction_id}] Parsed Result: {parsed_result}")
    
    # Log to structured storage
    _write_structured_log("semantic", {
        "interaction_id": interaction_id,
        "component": component,
        "user_input": user_input,
        "semantic_prompt": semantic_prompt,
        "raw_response": raw_response,
        "parsed_result": parsed_result,
        "success": success,
        "user_input_length": len(user_input),
        "raw_response_length": len(raw_response)
    })
    
    return interaction_id

def log_tool_execution_details(component: str, tool_calls: List[Dict[str, Any]], 
                              tool_results: List[Dict[str, Any]], interaction_id: str = None):
    """
    Log detailed tool execution information.
    
    Args:
        component: Component executing tools
        tool_calls: List of tool calls with parameters
        tool_results: List of tool execution results
        interaction_id: Interaction ID for tracking
    """
    debug_config = _get_debug_logging_config()
    if not debug_config.get("tool_details", False):
        return
    
    if not interaction_id:
        interaction_id = _generate_interaction_id()
    
    # Create component logger
    component_logger = setup_component_logger(component)
    
    # Log to standard logs
    component_logger.debug(f"[{interaction_id}] Tool Execution Details:")
    component_logger.debug(f"[{interaction_id}] Tool Calls: {len(tool_calls)} calls")
    for i, call in enumerate(tool_calls):
        component_logger.debug(f"[{interaction_id}] Call {i+1}: {call}")
    
    component_logger.debug(f"[{interaction_id}] Tool Results: {len(tool_results)} results")
    for i, result in enumerate(tool_results):
        component_logger.debug(f"[{interaction_id}] Result {i+1}: {result}")
    
    # Log to structured storage
    _write_structured_log("tools", {
        "interaction_id": interaction_id,
        "component": component,
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "num_tool_calls": len(tool_calls),
        "num_tool_results": len(tool_results)
    })
    
    return interaction_id

def log_conversation_context(component: str, conversation_history: List[Dict[str, Any]], 
                           context_window_size: int, interaction_id: str = None):
    """
    Log conversation context being sent to models.
    
    Args:
        component: Component managing conversation context
        conversation_history: The conversation history being sent
        context_window_size: Size of context window used
        interaction_id: Interaction ID for tracking
    """
    debug_config = _get_debug_logging_config()
    if not debug_config.get("conversation_context", False):
        return
    
    if not interaction_id:
        interaction_id = _generate_interaction_id()
    
    # Create component logger
    component_logger = setup_component_logger(component)
    
    # Log to standard logs
    component_logger.debug(f"[{interaction_id}] Conversation Context:")
    component_logger.debug(f"[{interaction_id}] History Length: {len(conversation_history)} messages")
    component_logger.debug(f"[{interaction_id}] Context Window: {context_window_size} tokens")
    
    # Log to structured storage
    _write_structured_log("context", {
        "interaction_id": interaction_id,
        "component": component,
        "conversation_history": conversation_history,
        "history_length": len(conversation_history),
        "context_window_size": context_window_size,
        "total_context_chars": sum(len(str(msg)) for msg in conversation_history)
    })
    
    return interaction_id

def log_interaction_summary(interaction_id: str, component: str, operation_type: str, 
                          user_input: str, final_response: str, total_duration: float, 
                          model_calls: int = 0, tool_calls: int = 0, errors: int = 0):
    """
    Log a summary of a complete interaction for performance analysis.
    
    Args:
        interaction_id: Unique interaction identifier
        component: Component handling the interaction
        operation_type: Type of operation (conversation, tool_execution, code_generation, etc.)
        user_input: Original user input
        final_response: Final response sent to user
        total_duration: Total interaction duration in seconds
        model_calls: Number of model calls made
        tool_calls: Number of tool calls made
        errors: Number of errors encountered
    """
    debug_config = _get_debug_logging_config()
    if not debug_config.get("interaction_tracking", True):
        return
    
    # Create component logger
    component_logger = setup_component_logger(component)
    
    # Log to standard logs
    component_logger.info(f"[{interaction_id}] Interaction Summary: {operation_type} completed in {total_duration:.2f}s")
    component_logger.debug(f"[{interaction_id}] Models: {model_calls}, Tools: {tool_calls}, Errors: {errors}")
    
    # Log to structured storage
    _write_structured_log("interactions", {
        "interaction_id": interaction_id,
        "component": component,
        "operation_type": operation_type,
        "user_input": user_input,
        "final_response": final_response,
        "total_duration_seconds": total_duration,
        "model_calls": model_calls,
        "tool_calls": tool_calls,
        "errors": errors,
        "user_input_length": len(user_input),
        "final_response_length": len(final_response)
    })

def get_model_interactions_summary() -> Dict[str, Any]:
    """
    Get a summary of model interaction logs.
    
    Returns:
        Dictionary with log file statistics and recent activity
    """
    summary = {
        "log_files": {},
        "total_interactions": 0,
        "recent_activity": []
    }
    
    try:
        # Analyze log files
        for log_file in MODEL_INTERACTIONS_DIR.glob("*.jsonl"):
            try:
                size_mb = log_file.stat().st_size / (1024 * 1024)
                line_count = sum(1 for _ in open(log_file, 'r', encoding='utf-8'))
                
                summary["log_files"][log_file.name] = {
                    "size_mb": round(size_mb, 2),
                    "entries": line_count,
                    "modified": datetime.fromtimestamp(log_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                }
                
                summary["total_interactions"] += line_count
                
            except Exception as e:
                summary["log_files"][log_file.name] = {"error": str(e)}
        
        # Get recent activity from interactions log
        interactions_file = next(MODEL_INTERACTIONS_DIR.glob("interactions_*.jsonl"), None)
        if interactions_file and interactions_file.exists():
            try:
                with open(interactions_file, 'r', encoding='utf-8') as f:
                    # Get last 5 entries
                    lines = f.readlines()
                    for line in lines[-5:]:
                        try:
                            data = json.loads(line.strip())
                            summary["recent_activity"].append({
                                "time": data.get("timestamp", ""),
                                "operation": data.get("operation_type", "unknown"),
                                "duration": data.get("total_duration_seconds", 0),
                                "component": data.get("component", "unknown")
                            })
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                summary["recent_activity_error"] = str(e)
        
    except Exception as e:
        summary["error"] = str(e)
    
    return summary

def cleanup_old_logs(days_to_keep: int = 7):
    """
    Clean up log files older than specified days
    
    Args:
        days_to_keep: Number of days to keep logs (default: 7)
    """
    import time
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    cleaned_count = 0
    
    for log_file in LOGS_DIR.glob("session_*.log"):
        try:
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                cleaned_count += 1
        except Exception as e:
            logger.warning(f"Failed to clean up log file {log_file}: {e}")
    
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} old log files")

# Initialize session logging
setup_session_logging()

# Clean up old logs on startup
cleanup_old_logs()

# Export commonly used functions and loggers
__all__ = [
    'logger', 'console', 
    'dual_model_logger', 'gguf_logger', 'openai_logger', 'app_logger', 'router_logger', 'tools_logger',
    'log_error', 'log_warning', 'log_info', 'log_debug', 'log_api_usage', 
    'log_model_loading', 'log_performance', 'log_routing_decision',
    'setup_component_logger', 'get_log_summary',
    # Enhanced model interaction logging functions
    'log_model_prompt', 'log_model_response', 'log_semantic_analysis',
    'log_tool_execution_details', 'log_conversation_context', 'log_interaction_summary',
    'get_model_interactions_summary', 'MODEL_INTERACTIONS_DIR'
]
