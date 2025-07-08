"""
GGUF Tool Call Parser for DeepCoderX

This module extracts and parses tool calls from GGUF model responses using
pattern matching and JSON parsing. It handles the custom tool call format:
<tool_call>function_name({"parameter": "value"})</tool_call>
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from utils.logging import console


@dataclass
class ParsedToolCall:
    """Represents a parsed tool call."""
    function_name: str
    arguments: Dict[str, Any]
    raw_match: str
    start_pos: int
    end_pos: int
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """Convert to legacy tool executor format."""
        return {
            "tool": self.function_name,
            **self.arguments
        }
    
    def to_openai_format(self, call_id: str = None) -> Dict[str, Any]:
        """Convert to OpenAI tool call format."""
        return {
            "id": call_id or f"call_{self.function_name}_{hash(self.raw_match)}",
            "type": "function",
            "function": {
                "name": self.function_name,
                "arguments": json.dumps(self.arguments)
            }
        }


class GGUFToolCallParser:
    """
    Parses tool calls from GGUF model responses.
    
    Supports the format: <tool_call>function_name({"parameter": "value"})</tool_call>
    """
    
    def __init__(self):
        # Primary pattern for well-formed tool calls
        self.tool_call_pattern = r'<tool_call>(\w+)\(([^)]+)\)</tool_call>'
        
        # Fallback patterns for common malformations
        self.fallback_patterns = [
            # Missing outer tags but has function call structure
            r'(\w+)\(\s*\{[^}]+\}\s*\)',
            # Tool call with different brackets
            r'<tool_call>(\w+)\[\s*(\{[^}]+\})\s*\]</tool_call>',
            # Tool call with quotes around function name
            r'<tool_call>"(\w+)"\(([^)]+)\)</tool_call>',
        ]
        
        # Known tool names from registry for validation
        self._known_tools: Optional[List[str]] = None
    
    def parse_response(self, response: str) -> List[ParsedToolCall]:
        """
        Parse tool calls from a GGUF model response.
        
        Args:
            response: Raw response text from GGUF model
            
        Returns:
            List of parsed tool calls
        """
        if not response or not isinstance(response, str):
            return []
        
        tool_calls = []
        
        # Try primary pattern first
        tool_calls.extend(self._parse_with_pattern(response, self.tool_call_pattern))
        
        # If no matches found, try fallback patterns
        if not tool_calls:
            for pattern in self.fallback_patterns:
                fallback_calls = self._parse_with_pattern(response, pattern, is_fallback=True)
                tool_calls.extend(fallback_calls)
                if tool_calls:  # Stop at first successful fallback
                    break
        
        # Validate and clean up results
        validated_calls = []
        for call in tool_calls:
            if self._validate_tool_call(call):
                validated_calls.append(call)
        
        return validated_calls
    
    def _parse_with_pattern(self, text: str, pattern: str, is_fallback: bool = False) -> List[ParsedToolCall]:
        """Parse tool calls using a specific regex pattern."""
        matches = re.finditer(pattern, text, re.DOTALL)
        tool_calls = []
        
        for match in matches:
            try:
                if len(match.groups()) >= 2:
                    function_name = match.group(1)
                    args_str = match.group(2)
                else:
                    # Handle single group patterns
                    continue
                
                # Parse JSON arguments
                try:
                    arguments = json.loads(args_str)
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    arguments = self._attempt_json_repair(args_str)
                    if arguments is None:
                        continue
                
                # Create parsed tool call
                parsed_call = ParsedToolCall(
                    function_name=function_name,
                    arguments=arguments,
                    raw_match=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                
                tool_calls.append(parsed_call)
                
            except Exception as e:
                # Log parsing errors in debug mode
                if console:
                    console.print(f"[yellow]Warning:[/] Failed to parse tool call: {e}")
                continue
        
        return tool_calls
    
    def _attempt_json_repair(self, args_str: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair common JSON formatting issues."""
        # Remove common issues
        cleaned = args_str.strip()
        
        # Fix single quotes to double quotes
        if "'" in cleaned:
            # Simple replacement - more sophisticated logic could be added
            cleaned = cleaned.replace("'", '"')
        
        # Add missing outer braces
        if not cleaned.startswith('{'):
            cleaned = '{' + cleaned
        if not cleaned.endswith('}'):
            cleaned = cleaned + '}'
        
        # Try parsing again
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try removing common trailing characters
            for char in [',', ';', '.']:
                if cleaned.rstrip().endswith(char):
                    try:
                        return json.loads(cleaned.rstrip()[:-1] + '}')
                    except json.JSONDecodeError:
                        continue
            
            return None
    
    def _validate_tool_call(self, tool_call: ParsedToolCall) -> bool:
        """Validate a parsed tool call."""
        # Check function name is valid
        if not tool_call.function_name or not isinstance(tool_call.function_name, str):
            return False
        
        # Check arguments is a dictionary
        if not isinstance(tool_call.arguments, dict):
            return False
        
        # Check against known tools if available
        if self._known_tools and tool_call.function_name not in self._known_tools:
            return False
        
        return True
    
    def extract_clean_response(self, response: str) -> str:
        """
        Remove tool calls from response and return clean text.
        
        Args:
            response: Raw response text
            
        Returns:
            Response text with tool calls removed
        """
        # Remove all tool call patterns
        cleaned = re.sub(self.tool_call_pattern, '', response)
        
        # Remove fallback patterns too
        for pattern in self.fallback_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def has_tool_calls(self, response: str) -> bool:
        """Check if response contains any tool calls."""
        if not response:
            return False
        
        # Check primary pattern
        if re.search(self.tool_call_pattern, response):
            return True
        
        # Check fallback patterns
        for pattern in self.fallback_patterns:
            if re.search(pattern, response):
                return True
        
        return False
    
    def set_known_tools(self, tool_names: List[str]) -> None:
        """Set list of known tool names for validation."""
        self._known_tools = tool_names
    
    def parse_and_execute_format(self, response: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        Parse tool calls and return both legacy format and clean response.
        
        Args:
            response: Raw response text
            
        Returns:
            Tuple of (tool_calls_in_legacy_format, clean_response_text)
        """
        parsed_calls = self.parse_response(response)
        legacy_calls = [call.to_legacy_format() for call in parsed_calls]
        clean_response = self.extract_clean_response(response)
        
        return legacy_calls, clean_response
    
    def get_parsing_diagnostics(self, response: str) -> Dict[str, Any]:
        """
        Get detailed diagnostics about parsing a response.
        
        Args:
            response: Response text to analyze
            
        Returns:
            Dictionary with parsing diagnostics
        """
        diagnostics = {
            "original_response": response,
            "has_tool_calls": self.has_tool_calls(response),
            "tool_call_matches": [],
            "parsing_errors": [],
            "clean_response": self.extract_clean_response(response)
        }
        
        # Test each pattern
        primary_matches = list(re.finditer(self.tool_call_pattern, response))
        diagnostics["primary_pattern_matches"] = len(primary_matches)
        
        for i, pattern in enumerate(self.fallback_patterns):
            fallback_matches = list(re.finditer(pattern, response))
            diagnostics[f"fallback_pattern_{i}_matches"] = len(fallback_matches)
        
        # Try to parse and capture errors
        try:
            parsed_calls = self.parse_response(response)
            diagnostics["successfully_parsed"] = len(parsed_calls)
            diagnostics["parsed_tool_calls"] = [
                {
                    "function": call.function_name,
                    "arguments": call.arguments,
                    "raw_match": call.raw_match
                }
                for call in parsed_calls
            ]
        except Exception as e:
            diagnostics["parsing_errors"].append(str(e))
        
        return diagnostics
    
    def suggest_fixes(self, response: str) -> List[str]:
        """
        Suggest fixes for responses that failed to parse properly.
        
        Args:
            response: Response text that failed to parse
            
        Returns:
            List of suggested fixes
        """
        suggestions = []
        
        # Check for common issues
        if "tool_call" in response.lower() and not re.search(self.tool_call_pattern, response):
            suggestions.append("Tool call detected but format is incorrect. Use: <tool_call>function_name({\"param\": \"value\"})</tool_call>")
        
        if "{" in response and "}" in response and not self.has_tool_calls(response):
            suggestions.append("JSON-like structure detected. Wrap in proper tool call tags.")
        
        if re.search(r'\w+\([^)]*\)', response) and not self.has_tool_calls(response):
            suggestions.append("Function call pattern detected. Add <tool_call> tags around it.")
        
        # Check for quote issues
        if "'" in response:
            suggestions.append("Use double quotes (\") instead of single quotes (') in JSON arguments.")
        
        return suggestions


# Convenience functions for easy integration
def parse_gguf_response(response: str) -> List[Dict[str, Any]]:
    """
    Convenience function to parse GGUF response and return legacy format tool calls.
    
    Args:
        response: Raw GGUF model response
        
    Returns:
        List of tool calls in legacy format
    """
    parser = GGUFToolCallParser()
    parsed_calls = parser.parse_response(response)
    return [call.to_legacy_format() for call in parsed_calls]


def extract_clean_text(response: str) -> str:
    """
    Convenience function to extract clean text without tool calls.
    
    Args:
        response: Raw GGUF model response
        
    Returns:
        Clean response text
    """
    parser = GGUFToolCallParser()
    return parser.extract_clean_response(response)


def has_tool_calls(response: str) -> bool:
    """
    Convenience function to check if response has tool calls.
    
    Args:
        response: Raw GGUF model response
        
    Returns:
        True if tool calls detected
    """
    parser = GGUFToolCallParser()
    return parser.has_tool_calls(response)
