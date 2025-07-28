"""
LEGACY MIGRATION: structured_tools.py - DEPRECATED

This module has been replaced by the Tool Registry Pattern.
All tool parsing and validation now goes through:
- services/tool_registry.py (centralized tool definitions)
- services/tool_executor.py (execution with standardized errors)

This file is preserved for backward compatibility but will show deprecation warnings.
"""

import warnings
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

# Import new system components
from services.tool_registry import tool_registry, validate_tool_call
from services.error_handler import tool_error, validation_error
from utils.logging import console

# Show migration status
def _show_migration_warning():
    """Show deprecation warning for structured_tools usage."""
    console.print("[yellow]⚠️  DEPRECATED: structured_tools.py is deprecated[/]")
    console.print("[yellow]   Please use Tool Registry Pattern instead:[/]")
    console.print("[yellow]   - services.tool_registry (definitions)[/]")
    console.print("[yellow]   - services.tool_executor (execution)[/]")

# Legacy compatibility classes - redirected to new system
class ToolCallError(Exception):
    """Legacy: Base exception for tool call errors."""
    pass

class ValidationError(ToolCallError):
    """Legacy: Raised when tool call validation fails."""
    pass

class ParseError(ToolCallError):
    """Legacy: Raised when tool call parsing fails."""
    pass

class ToolExecutionError(ToolCallError):
    """Legacy: Raised when tool execution fails.""" 
    pass

@dataclass
class ToolCallResult:
    """Legacy: Result of a tool call - redirected to Tool Registry."""
    success: bool
    result: str
    error: Optional[str] = None
    tool_name: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass 
class StructuredToolCall:
    """Legacy: A structured representation of a tool call - redirected to Tool Registry."""
    tool_name: str
    parameters: Dict[str, Any]
    raw_input: str
    
    def validate(self) -> bool:
        """Legacy validation - now uses Tool Registry."""
        _show_migration_warning()
        
        # Use new Tool Registry validation
        tool_call = {"tool": self.tool_name, **self.parameters}
        validation_result = tool_registry.validate_tool_call(tool_call)
        
        if not validation_result["valid"]:
            error_msg = "; ".join(validation_result["errors"])
            raise ValidationError(error_msg)
        
        return True

class StructuredToolParser:
    """Legacy: Tool call parser - redirected to Tool Registry."""
    
    def __init__(self, debug: bool = False):
        _show_migration_warning()
        self.debug = debug
        # Use Tool Registry for known tools
        self.KNOWN_TOOLS = {tool.name: {
            "required": tool.get_required_parameters(),
            "optional": tool.get_optional_parameters()
        } for tool in tool_registry.list_tools()}
    
    def parse_tool_calls(self, model_response: str) -> List[StructuredToolCall]:
        """Legacy: Parse tool calls - now recommends native OpenAI function calling."""
        console.print("[yellow]⚠️  MIGRATION: Use native OpenAI function calling instead of JSON parsing[/]")
        console.print("[yellow]   Modern handlers use OpenAI's structured function calls[/]")
        
        # Simple JSON extraction for backward compatibility
        import json
        import re
        
        tool_calls = []
        
        # Find JSON-like patterns  
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, model_response, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match.strip())
                if isinstance(data, dict) and "tool" in data:
                    tool_name = data["tool"]
                    parameters = {k: v for k, v in data.items() if k != "tool"}
                    
                    tool_call = StructuredToolCall(
                        tool_name=tool_name,
                        parameters=parameters,
                        raw_input=match
                    )
                    
                    # Validate using Tool Registry
                    try:
                        tool_call.validate()
                        tool_calls.append(tool_call)
                    except ValidationError:
                        continue  # Skip invalid calls
                        
            except json.JSONDecodeError:
                continue
        
        return tool_calls
    
    def get_validation_feedback(self, error: ValidationError, tool_call: StructuredToolCall) -> str:
        """Legacy: Get validation feedback - now uses Tool Registry."""
        tool_def = tool_registry.get_tool(tool_call.tool_name)
        if tool_def and tool_def.examples:
            return f"❌ {error}\n✅ Example: {tool_def.examples[0]}"
        else:
            available_tools = list(tool_registry.tools.keys())
            return f"❌ {error}\n💡 Available tools: {', '.join(available_tools)}"

class EnhancedToolExecutor:
    """Legacy: Enhanced tool executor - redirected to new ToolExecutor."""
    
    def __init__(self, base_executor, debug: bool = False):
        _show_migration_warning()
        console.print("[blue]   Recommendation: Use services.tool_executor.ToolExecutor directly[/]")
        
        self.base_executor = base_executor
        self.debug = debug
        self.parser = StructuredToolParser(debug=debug)
    
    def execute_structured_calls(self, model_response: str) -> List[ToolCallResult]:
        """Legacy: Execute structured calls - now recommends direct tool execution."""
        results = []
        
        # Parse using legacy method
        tool_calls = self.parser.parse_tool_calls(model_response)
        
        for tool_call in tool_calls:
            try:
                # Convert to standard format
                legacy_call = {"tool": tool_call.tool_name, **tool_call.parameters}
                
                # Execute using base executor (modern ToolExecutor)
                result_str = self.base_executor.execute_tool(legacy_call)
                
                # Determine success
                success = not result_str.startswith("[red]Error:[/]")
                
                results.append(ToolCallResult(
                    success=success,
                    result=result_str,
                    error=None if success else result_str,
                    tool_name=tool_call.tool_name
                ))
                
            except Exception as e:
                results.append(ToolCallResult(
                    success=False,
                    result="",
                    error=str(e),
                    tool_name=tool_call.tool_name
                ))
        
        return results
    
    def format_results(self, results: List[ToolCallResult]) -> List[str]:
        """Legacy: Format results for model feedback."""
        formatted = []
        
        for result in results:
            if result.success:
                formatted.append(result.result)
            else:
                # Use Tool Registry for suggestions
                tool_def = tool_registry.get_tool(result.tool_name)
                error_msg = result.error or "Unknown error"
                
                if tool_def and tool_def.examples:
                    error_msg += f"\n💡 Example: {tool_def.examples[0]}"
                
                formatted.append(error_msg)
        
        return formatted

# Migration status indicator
MIGRATION_STATUS = {
    "phase": "Phase 2 - Tool Parsing Consolidation",
    "status": "COMPLETED",
    "redirected_to": "Tool Registry Pattern",
    "new_components": [
        "services.tool_registry (centralized definitions)",
        "services.tool_executor (standardized execution)",
        "services.error_handler (consistent errors)"
    ],
    "legacy_support": "Backward compatibility maintained with deprecation warnings",
    "recommendation": "Use native OpenAI function calling in unified handlers"
}

def get_migration_status() -> Dict[str, Any]:
    """Get current migration status for structured_tools."""
    return MIGRATION_STATUS

# Show migration completion message
if __name__ == "__main__":
    console.print("[bold green]✅ PHASE 2 MIGRATION COMPLETED: Tool Parsing Consolidation[/]")
    console.print("[green]   structured_tools.py functionality redirected to Tool Registry Pattern[/]")
    console.print("[green]   Modern handlers use native OpenAI function calling[/]")
    console.print("[green]   Legacy compatibility maintained with deprecation warnings[/]")
