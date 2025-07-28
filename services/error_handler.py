"""
Standardized Error Handling for DeepCoderX

This module provides consistent error types, formatting, and handling
across all handlers and tool execution paths.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Union
from enum import Enum


class ErrorType(Enum):
    """Standard error types used throughout DeepCoderX."""
    
    # Tool-related errors
    TOOL_EXECUTION_ERROR = "Tool Execution Error"
    TOOL_VALIDATION_ERROR = "Tool Validation Error"
    TOOL_PARSING_ERROR = "Tool Parsing Error"
    
    # File system errors  
    FILE_NOT_FOUND = "File Not Found"
    FILE_PERMISSION_ERROR = "File Permission Error"
    PATH_SECURITY_ERROR = "Path Security Error"
    
    # API errors
    API_CONNECTION_ERROR = "API Connection Error"
    API_AUTHENTICATION_ERROR = "API Authentication Error"
    API_RATE_LIMIT_ERROR = "API Rate Limit Error"
    API_TIMEOUT_ERROR = "API Timeout Error"
    
    # Model errors
    MODEL_LOADING_ERROR = "Model Loading Error"
    MODEL_RESPONSE_ERROR = "Model Response Error"
    
    # Configuration errors
    CONFIG_VALIDATION_ERROR = "Configuration Error"
    PROVIDER_NOT_AVAILABLE = "Provider Not Available"
    
    # General errors
    UNKNOWN_ERROR = "Unknown Error"
    VALIDATION_ERROR = "Validation Error"


@dataclass
class StandardError:
    """Standardized error structure used throughout DeepCoderX."""
    
    type: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[str] = None
    error_code: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation for logging."""
        base = f"{self.type.value}: {self.message}"
        if self.details:
            base += f" (Details: {self.details})"
        if self.suggestions:
            base += f" | Suggestions: {self.suggestions}"
        return base


class ErrorHandler:
    """Centralized error handling and formatting."""
    
    @staticmethod
    def format_error(error: StandardError, use_rich_markup: bool = True) -> str:
        """Format error for display with optional Rich markup."""
        if use_rich_markup:
            formatted = f"[red]{error.type.value}:[/] {error.message}"
            
            if error.suggestions:
                formatted += f"\n\n💡 Suggestions: {error.suggestions}"
            
            if error.details and error.details.get("examples"):
                formatted += f"\n\n✅ Examples: {error.details['examples']}"
                
            return formatted
        else:
            # Plain text format
            formatted = f"{error.type.value}: {error.message}"
            if error.suggestions:
                formatted += f"\nSuggestions: {error.suggestions}"
            return formatted
    
    @staticmethod
    def create_tool_error(tool_name: str, message: str, suggestions: str = None) -> StandardError:
        """Create a standardized tool execution error."""
        return StandardError(
            type=ErrorType.TOOL_EXECUTION_ERROR,
            message=f"Tool '{tool_name}' failed: {message}",
            suggestions=suggestions,
            details={"tool_name": tool_name}
        )
    
    @staticmethod
    def create_file_error(operation: str, path: str, reason: str, suggestions: str = None) -> StandardError:
        """Create a standardized file operation error."""
        error_type = ErrorType.FILE_NOT_FOUND if "not found" in reason.lower() else ErrorType.FILE_PERMISSION_ERROR
        
        return StandardError(
            type=error_type,
            message=f"Cannot {operation} file '{path}': {reason}",
            suggestions=suggestions or f"Check if '{path}' exists and is accessible",
            details={"operation": operation, "path": path}
        )
    
    @staticmethod
    def create_api_error(provider: str, status_code: int = None, message: str = None) -> StandardError:
        """Create a standardized API error."""
        if status_code == 401:
            error_type = ErrorType.API_AUTHENTICATION_ERROR
            final_message = f"Authentication failed for {provider}"
            suggestions = f"Check your {provider} API key configuration"
        elif status_code == 429:
            error_type = ErrorType.API_RATE_LIMIT_ERROR
            final_message = f"Rate limit exceeded for {provider}"
            suggestions = "Wait a moment before retrying or check your API quota"
        elif status_code and status_code >= 500:
            error_type = ErrorType.API_CONNECTION_ERROR
            final_message = f"Server error from {provider} (status {status_code})"
            suggestions = "The provider service may be temporarily unavailable"
        else:
            error_type = ErrorType.API_CONNECTION_ERROR
            # FIX: Always include provider name, even with custom message
            if message:
                final_message = f"{provider}: {message}"
            else:
                final_message = f"Connection failed to {provider}"
            suggestions = "Check your internet connection and provider endpoint"
        
        return StandardError(
            type=error_type,
            message=final_message,
            suggestions=suggestions,
            details={"provider": provider, "status_code": status_code}
        )
    
    @staticmethod
    def create_validation_error(field: str, value: Any, expected: str, examples: str = None) -> StandardError:
        """Create a standardized validation error."""
        return StandardError(
            type=ErrorType.VALIDATION_ERROR,
            message=f"Invalid {field}: got '{value}', expected {expected}",
            suggestions=f"Please provide a valid {field}",
            details={"field": field, "value": value, "expected": expected, "examples": examples}
        )
    
    @staticmethod
    def create_path_security_error(path: str, reason: str = None) -> StandardError:
        """Create a standardized path security error."""
        reason = reason or "Path is outside allowed directory"
        return StandardError(
            type=ErrorType.PATH_SECURITY_ERROR,
            message=f"Security violation: {reason}",
            suggestions="Use relative paths within the project directory like 'script.py' or './folder/file.txt'",
            details={"path": path, "security_issue": reason}
        )


# Convenience functions for common error patterns
def tool_error(tool_name: str, message: str, suggestions: str = None) -> str:
    """Quick tool error formatting."""
    error = ErrorHandler.create_tool_error(tool_name, message, suggestions)
    return ErrorHandler.format_error(error)

def file_error(operation: str, path: str, reason: str, suggestions: str = None) -> str:
    """Quick file error formatting."""
    error = ErrorHandler.create_file_error(operation, path, reason, suggestions)
    return ErrorHandler.format_error(error)

def api_error(provider: str, status_code: int = None, message: str = None) -> str:
    """Quick API error formatting."""
    error = ErrorHandler.create_api_error(provider, status_code, message)
    return ErrorHandler.format_error(error)

def validation_error(field: str, value: Any, expected: str, examples: str = None) -> str:
    """Quick validation error formatting."""
    error = ErrorHandler.create_validation_error(field, value, expected, examples)
    return ErrorHandler.format_error(error)

def path_security_error(path: str, reason: str = None) -> str:
    """Quick path security error formatting."""
    error = ErrorHandler.create_path_security_error(path, reason)
    return ErrorHandler.format_error(error)


# Legacy compatibility - maintains existing error format strings
class LegacyErrorFormats:
    """Legacy error format strings for backward compatibility."""
    
    @staticmethod
    def tool_not_found(tool_name: str) -> str:
        return f"[red]Error:[/] Unknown tool: {tool_name}. Available tools: read_file, write_file, list_dir, run_bash"
    
    @staticmethod
    def missing_parameter(tool_name: str, param: str) -> str:
        return f"[red]Error:[/] {param} is required for {tool_name}."
    
    @staticmethod
    def file_not_found(path: str) -> str:
        return f"[red]Error:[/] Could not read file '{path}': File not found"
    
    @staticmethod
    def api_timeout(provider: str) -> str:
        return f"[red]API Error:[/] Request to {provider} timed out"
