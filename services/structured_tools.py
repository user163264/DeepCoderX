# services/structured_tools.py

import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from utils.logging import console


class ToolCallError(Exception):
    """Base exception for tool call errors."""
    pass


class ValidationError(ToolCallError):
    """Raised when tool call validation fails."""
    pass


class ParseError(ToolCallError):
    """Raised when tool call parsing fails."""
    pass


class ToolExecutionError(ToolCallError):
    """Raised when tool execution fails."""
    pass


@dataclass
class ToolCallResult:
    """Result of a tool call."""
    success: bool
    result: str
    error: Optional[str] = None
    tool_name: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class StructuredToolCall:
    """A structured representation of a tool call."""
    tool_name: str
    parameters: Dict[str, Any]
    raw_input: str
    
    def validate(self) -> bool:
        """Validate the tool call parameters."""
        if not self.tool_name:
            raise ValidationError("Tool name is required")
        
        # Tool-specific validation with helpful messages
        if self.tool_name == "read_file":
            if not self.parameters.get("path"):
                raise ValidationError('read_file requires "path" parameter. Example: {"tool": "read_file", "path": "config.py"}')
        elif self.tool_name == "write_file":
            if not self.parameters.get("path"):
                raise ValidationError('write_file requires "path" parameter. Example: {"tool": "write_file", "path": "script.py", "content": "print(\'hello\')"}')
            # content is optional - can be empty string
        elif self.tool_name == "list_dir":
            # path is optional for list_dir - defaults to current dir
            if not self.parameters.get("path"):
                # Add default path
                self.parameters["path"] = "."
        elif self.tool_name == "run_bash":
            if not self.parameters.get("command"):
                raise ValidationError('run_bash requires "command" parameter. Example: {"tool": "run_bash", "command": "ls -la"}')
        else:
            # Unknown tool - provide helpful message
            known_tools = ["read_file", "write_file", "list_dir", "run_bash"]
            raise ValidationError(f'Unknown tool "{self.tool_name}". Available tools: {", ".join(known_tools)}')
        
        return True


class StructuredToolParser:
    """Enhanced tool call parser that replaces fragile regex parsing."""
    
    # Known tool names for validation
    KNOWN_TOOLS = {
        "read_file": {"required": ["path"], "optional": []},
        "write_file": {"required": ["path"], "optional": ["content"]},  
        "list_dir": {"required": [], "optional": ["path"]},
        "run_bash": {"required": ["command"], "optional": []},
        "delete_path": {"required": ["path"], "optional": ["recursive"]}
    }
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def parse_tool_calls(self, model_response: str) -> List[StructuredToolCall]:
        """
        Parse tool calls from model response using multiple strategies.
        
        Returns:
            List of validated StructuredToolCall objects
        """
        if self.debug:
            console.print(f"[bold blue]-- Parsing Tool Calls --[/]")
            console.print(f"Raw response: {model_response[:200]}...")
        
        tool_calls = []
        
        # Strategy 1: Try to find complete JSON objects
        json_candidates = self._extract_json_candidates(model_response)
        
        for candidate in json_candidates:
            try:
                parsed_call = self._parse_single_json(candidate)
                if parsed_call:
                    parsed_call.validate()
                    tool_calls.append(parsed_call)
                    if self.debug:
                        console.print(f"[green]✅ Valid tool call: {parsed_call.tool_name}[/]")
            except (ValidationError, ParseError) as e:
                if self.debug:
                    console.print(f"[yellow]⚠️  Invalid tool call: {e}[/]")
                # Don't add invalid calls, but continue parsing
                continue
            except Exception as e:
                if self.debug:
                    console.print(f"[red]❌ Parsing error: {e}[/]")
                continue
        
        # Strategy 2: If no valid JSON found, try fallback patterns
        if not tool_calls:
            fallback_calls = self._try_fallback_parsing(model_response)
            tool_calls.extend(fallback_calls)
        
        if self.debug:
            console.print(f"[bold blue]-- Found {len(tool_calls)} valid tool calls --[/]")
        
        return tool_calls
    
    def _extract_json_candidates(self, text: str) -> List[str]:
        """Extract potential JSON objects from text using improved regex."""
        # Multiple strategies for finding JSON
        candidates = []
        
        # Strategy 1: Standard JSON objects
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        candidates.extend(matches)
        
        # Strategy 2: JSON in code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        code_matches = re.findall(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
        candidates.extend(code_matches)
        
        # Strategy 3: Line-by-line JSON (for single-line tool calls)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                candidates.append(line)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _parse_single_json(self, json_str: str) -> Optional[StructuredToolCall]:
        """Parse a single JSON string into a StructuredToolCall."""
        try:
            # Clean the JSON string
            json_str = json_str.strip()
            
            # Try to parse JSON directly first
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                # If direct parsing fails, try to fix common issues
                fixed_json = self._fix_malformed_json(json_str)
                if fixed_json:
                    data = json.loads(fixed_json)
                else:
                    raise
            
            if not isinstance(data, dict):
                raise ParseError(f"Expected JSON object, got {type(data)}")
            
            # Extract tool name (flexible key names)
            tool_name = data.get("tool") or data.get("tool_name") or data.get("function")
            if not tool_name:
                raise ParseError("No tool name found in JSON object. Use 'tool' key. Example: {\"tool\": \"read_file\", \"path\": \"config.py\"}")
            
            # Extract parameters (everything except tool name)
            parameters = {k: v for k, v in data.items() if k not in ["tool", "tool_name", "function"]}
            
            return StructuredToolCall(
                tool_name=tool_name,
                parameters=parameters,
                raw_input=json_str
            )
            
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON: {e}. Make sure to use proper JSON format like {{\"tool\": \"read_file\", \"path\": \"config.py\"}}")
        except Exception as e:
            raise ParseError(f"Parsing failed: {e}")
    
    def _fix_malformed_json(self, json_str: str) -> Optional[str]:
        """Try to fix common JSON formatting issues."""
        try:
            # Common issue: unescaped newlines in string values
            # Strategy: Find string values that contain unescaped newlines and fix them
            import re
            
            # First, let's try a simpler approach: escape all unescaped newlines in the entire string
            # This is safer than trying to parse specific patterns
            
            # Step 1: Find all string values in JSON that might contain unescaped characters
            # We'll look for the pattern: "key": "value with potential newlines"
            
            lines = json_str.split('\n')
            if len(lines) <= 1:
                # No newlines to fix
                return None
            
            # Try to reconstruct the JSON by joining lines and escaping content properly
            fixed_lines = []
            in_string_value = False
            current_line = ""
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Check if this line starts a string value (has : ")
                if ':' in stripped and '"' in stripped and not in_string_value:
                    # This might be the start of a multi-line string value
                    if stripped.count('"') % 2 == 1:  # Odd number of quotes means unclosed string
                        in_string_value = True
                        current_line = line
                        continue
                
                if in_string_value:
                    # We're inside a multi-line string value
                    current_line += "\\n" + line.strip()
                    
                    # Check if this line ends the string (has closing quote)
                    if '"' in line and (line.rstrip().endswith('"') or line.rstrip().endswith('"}') or line.rstrip().endswith('",')):
                        in_string_value = False
                        fixed_lines.append(current_line)
                        current_line = ""
                        continue
                else:
                    # Normal line, add as-is
                    fixed_lines.append(line)
            
            if current_line:  # Add any remaining line
                fixed_lines.append(current_line)
            
            fixed_json = '\n'.join(fixed_lines)
            
            # Test if the fix worked
            json.loads(fixed_json)
            return fixed_json
            
        except Exception:
            # If fixing fails, try a simpler approach: just escape all newlines
            try:
                # Replace all actual newlines with escaped newlines in string values
                import re
                
                # Find content between quotes and escape newlines
                def escape_newlines_in_strings(match):
                    quote = match.group(1)
                    content = match.group(2)
                    # Escape newlines and other special characters
                    escaped = content.replace('\\', '\\\\')
                    escaped = escaped.replace('\n', '\\n')
                    escaped = escaped.replace('\r', '\\r')
                    escaped = escaped.replace('\t', '\\t')
                    escaped = escaped.replace('"', '\\"')
                    return quote + escaped + quote
                
                # Pattern to match quoted strings (simple version)
                pattern = r'(")([^"]*?)(")'
                simple_fixed = re.sub(pattern, escape_newlines_in_strings, json_str, flags=re.DOTALL)
                
                # Test if this fix worked
                json.loads(simple_fixed)
                return simple_fixed
                
            except Exception:
                return None
    
    def _try_fallback_parsing(self, text: str) -> List[StructuredToolCall]:
        """Fallback parsing for non-JSON tool calls."""
        # This could be extended to handle natural language tool calls
        # For now, return empty list but log the issue
        if self.debug:
            console.print("[yellow]No valid JSON tool calls found. Make sure to use proper JSON format.[/]")
        return []
    
    def get_validation_feedback(self, error: ValidationError, tool_call: StructuredToolCall) -> str:
        """Generate helpful feedback for validation errors."""
        tool_name = tool_call.tool_name
        
        if tool_name in self.KNOWN_TOOLS:
            required = self.KNOWN_TOOLS[tool_name]["required"]
            optional = self.KNOWN_TOOLS[tool_name]["optional"]
            
            feedback = f"❌ Invalid {tool_name} call: {error}\n"
            feedback += f"📋 Required parameters: {required}\n"
            if optional:
                feedback += f"📋 Optional parameters: {optional}\n"
            
            # Show correct examples
            if tool_name == "read_file":
                feedback += '✅ Example: {"tool": "read_file", "path": "config.py"}'
            elif tool_name == "write_file":
                feedback += '✅ Example: {"tool": "write_file", "path": "script.py", "content": "print(\'hello\')"}'
            elif tool_name == "run_bash":
                feedback += '✅ Example: {"tool": "run_bash", "command": "ls -la"}'
            elif tool_name == "list_dir":
                feedback += '✅ Example: {"tool": "list_dir", "path": "."}'
                
            return feedback
        else:
            available_tools = list(self.KNOWN_TOOLS.keys())
            return f"❌ Unknown tool '{tool_name}'. Available tools: {', '.join(available_tools)}\n✅ Example: {{\"tool\": \"read_file\", \"path\": \"config.py\"}}"


class EnhancedToolExecutor:
    """Enhanced tool executor with better validation and feedback."""
    
    def __init__(self, base_executor, debug: bool = False):
        self.base_executor = base_executor
        self.debug = debug
        self.parser = StructuredToolParser(debug=debug)
    
    def execute_structured_calls(self, model_response: str) -> List[ToolCallResult]:
        """Execute all tool calls found in model response."""
        results = []
        
        try:
            tool_calls = self.parser.parse_tool_calls(model_response)
            
            if not tool_calls:
                if self.debug:
                    console.print("[dim]No tool calls found in response[/]")
                # Check if the response looks like it was trying to make a tool call
                if "{" in model_response and "tool" in model_response.lower():
                    error_result = ToolCallResult(
                        success=False,
                        result="",
                        error="Found potential tool call but couldn't parse it. Make sure to use proper JSON format like {\"tool\": \"read_file\", \"path\": \"config.py\"}",
                        tool_name="parse_error"
                    )
                    results.append(error_result)
                return results
            
            for tool_call in tool_calls:
                result = self._execute_single_call(tool_call)
                results.append(result)
                
        except Exception as e:
            # If parsing completely fails, return error result
            results.append(ToolCallResult(
                success=False,
                result="",
                error=f"Tool parsing failed: {e}. Make sure to use proper JSON format like {{\"tool\": \"read_file\", \"path\": \"config.py\"}}",
                tool_name="unknown"
            ))
        
        return results
    
    def _execute_single_call(self, tool_call: StructuredToolCall) -> ToolCallResult:
        """Execute a single validated tool call."""
        import time
        start_time = time.time()
        
        try:
            # Convert structured call back to legacy format for base executor
            legacy_call = {
                "tool": tool_call.tool_name,
                **tool_call.parameters
            }
            
            if self.debug:
                console.print(f"[bold green]→ Executing: {tool_call.tool_name}[/]")
            
            # Execute using base executor
            result_str = self.base_executor.execute_tool(legacy_call)
            execution_time = time.time() - start_time
            
            # Check if result indicates an error
            success = not result_str.startswith("[red]Error:[/]")
            
            return ToolCallResult(
                success=success,
                result=result_str,
                error=None if success else result_str,
                tool_name=tool_call.tool_name,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolCallResult(
                success=False,
                result="",
                error=f"Tool execution failed: {e}",
                tool_name=tool_call.tool_name,
                execution_time=execution_time
            )
    
    def format_results(self, results: List[ToolCallResult]) -> List[str]:
        """Format tool results for feeding back to the model."""
        formatted = []
        
        for result in results:
            if result.success:
                formatted.append(result.result)
            else:
                # Provide helpful error feedback
                error_msg = result.error or "Unknown error"
                
                # Add helpful usage examples for common errors
                if result.tool_name and result.tool_name in self.parser.KNOWN_TOOLS:
                    error_msg += f"\n\n💡 Correct usage for {result.tool_name}:"
                    
                    if result.tool_name == "read_file":
                        error_msg += '\n{"tool": "read_file", "path": "config.py"}'
                    elif result.tool_name == "write_file":
                        error_msg += '\n{"tool": "write_file", "path": "script.py", "content": "print(\'hello\')"}'
                    elif result.tool_name == "list_dir":
                        error_msg += '\n{"tool": "list_dir", "path": "."}'
                    elif result.tool_name == "run_bash":
                        error_msg += '\n{"tool": "run_bash", "command": "ls -la"}'
                
                formatted.append(error_msg)
        
        return formatted