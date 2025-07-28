"""
Enhanced Tool Registry with Built-in Tools Support for DeepCoderX

This module extends the tool registry to support OpenAI's built-in tools
alongside the existing MCP tools, providing a unified interface for all tool types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
import json
import inspect
from config import BUILTIN_TOOLS, BUILTIN_TOOLS_ENABLED, GLOBAL_TOOL_APPROVAL


class ToolType(Enum):
    """Types of tools available in the system."""
    CUSTOM = "custom"           # Custom MCP tools
    BUILTIN = "builtin"         # OpenAI built-in tools
    HYBRID = "hybrid"           # Tools that combine both approaches


class ToolCategory(Enum):
    """Categories of tools available in the system."""
    FILE_OPERATIONS = "file_operations"
    DIRECTORY_OPERATIONS = "directory_operations"
    SYSTEM_OPERATIONS = "system_operations"
    ANALYSIS_TOOLS = "analysis_tools"
    UTILITY_TOOLS = "utility_tools"
    WEB_SEARCH = "web_search"
    CODE_EXECUTION = "code_execution"
    COMPUTER_AUTOMATION = "computer_automation"
    CONTENT_GENERATION = "content_generation"


class ToolPermission(Enum):
    """Permission levels for tool usage."""
    READ_ONLY = "read_only"
    WRITE_ALLOWED = "write_allowed"
    SYSTEM_ACCESS = "system_access"
    UNRESTRICTED = "unrestricted"
    BUILTIN_SAFE = "builtin_safe"      # For OpenAI built-in tools
    REQUIRES_APPROVAL = "requires_approval"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum_values: Optional[List[str]] = None
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function parameter schema."""
        schema = {
            "type": self.type,
            "description": self.description
        }
        
        if self.enum_values:
            schema["enum"] = self.enum_values
            
        if self.default is not None:
            schema["default"] = self.default
            
        return schema


@dataclass
class BuiltInToolDefinition:
    """Definition for OpenAI built-in tools."""
    openai_name: str
    tool_type: ToolType = field(default=ToolType.BUILTIN)
    enabled: bool = field(default=True)
    requires_approval: bool = field(default=False)
    approval_settings: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    
    def to_openai_builtin_format(self) -> Dict[str, Any]:
        """Convert to OpenAI built-in tool format."""
        tool_def = {
            "type": self.openai_name,
        }
        
        # Add configuration if present
        if self.configuration:
            tool_def.update(self.configuration)
            
        return tool_def
    
    def get_approval_config(self) -> Dict[str, Any]:
        """Get approval configuration for this tool."""
        if not self.requires_approval:
            return {"require_approval": "never"}
            
        config = {"require_approval": "always"}
        if self.approval_settings:
            config.update(self.approval_settings)
            
        return config


@dataclass
class ToolDefinition:
    """Complete definition of a custom MCP tool."""
    name: str
    description: str
    category: ToolCategory
    permission: ToolPermission
    tool_type: ToolType = field(default=ToolType.CUSTOM)
    parameters: List[ToolParameter] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    executor_function: Optional[Callable] = None
    
    def get_required_parameters(self) -> List[str]:
        """Get list of required parameter names."""
        return [param.name for param in self.parameters if param.required]
    
    def get_optional_parameters(self) -> List[str]:
        """Get list of optional parameter names."""
        return [param.name for param in self.parameters if not param.required]
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_openai_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def validate_call(self, tool_call: Dict[str, Any]) -> List[str]:
        """Validate a tool call against this definition."""
        errors = []
        
        # Check required parameters
        for param_name in self.get_required_parameters():
            if param_name not in tool_call:
                errors.append(f"Missing required parameter: {param_name}")
        
        # Check parameter types (basic validation)
        for param_name, value in tool_call.items():
            if param_name == "tool":  # Skip tool name
                continue
                
            param_def = next((p for p in self.parameters if p.name == param_name), None)
            if param_def:
                # Type validation could be enhanced here
                if param_def.type == "string" and not isinstance(value, str):
                    errors.append(f"Parameter {param_name} must be a string")
                elif param_def.type == "integer" and not isinstance(value, int):
                    errors.append(f"Parameter {param_name} must be an integer")
        
        return errors


class EnhancedToolRegistry:
    """Enhanced registry supporting both custom MCP tools and OpenAI built-in tools."""
    
    def __init__(self):
        self.custom_tools: Dict[str, ToolDefinition] = {}
        self.builtin_tools: Dict[str, BuiltInToolDefinition] = {}
        self._register_core_tools()
        self._register_builtin_tools()
    
    def register_custom_tool(self, tool_definition: ToolDefinition) -> None:
        """Register a new custom MCP tool in the registry."""
        self.custom_tools[tool_definition.name] = tool_definition
    
    def register_builtin_tool(self, tool_definition: BuiltInToolDefinition) -> None:
        """Register a new built-in tool in the registry."""
        self.builtin_tools[tool_definition.openai_name] = tool_definition
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Remove a tool from the registry."""
        removed = False
        if tool_name in self.custom_tools:
            del self.custom_tools[tool_name]
            removed = True
        if tool_name in self.builtin_tools:
            del self.builtin_tools[tool_name]
            removed = True
        return removed
    
    def get_custom_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a specific custom tool definition."""
        return self.custom_tools.get(tool_name)
    
    def get_builtin_tool(self, tool_name: str) -> Optional[BuiltInToolDefinition]:
        """Get a specific built-in tool definition."""
        return self.builtin_tools.get(tool_name)
    
    def list_custom_tools(self, category: Optional[ToolCategory] = None, 
                         permission: Optional[ToolPermission] = None) -> List[ToolDefinition]:
        """List custom tools, optionally filtered by category or permission."""
        tools = list(self.custom_tools.values())
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        if permission:
            tools = [t for t in tools if t.permission == permission]
        
        return tools
    
    def list_builtin_tools(self, enabled_only: bool = True) -> List[BuiltInToolDefinition]:
        """List built-in tools, optionally filtered by enabled status."""
        tools = list(self.builtin_tools.values())
        
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        
        return tools
    
    def get_openai_custom_definitions(self, categories: Optional[List[ToolCategory]] = None,
                                    max_permissions: Optional[ToolPermission] = None) -> List[Dict[str, Any]]:
        """Get OpenAI-format custom tool definitions."""
        tools = list(self.custom_tools.values())
        
        # Filter by categories
        if categories:
            tools = [t for t in tools if t.category in categories]
        
        # Filter by permission level
        if max_permissions:
            permission_order = [
                ToolPermission.READ_ONLY,
                ToolPermission.WRITE_ALLOWED,
                ToolPermission.SYSTEM_ACCESS,
                ToolPermission.UNRESTRICTED
            ]
            max_level = permission_order.index(max_permissions)
            tools = [t for t in tools if permission_order.index(t.permission) <= max_level]
        
        return [tool.to_openai_format() for tool in tools]
    
    def get_openai_builtin_definitions(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get OpenAI-format built-in tool definitions."""
        if not BUILTIN_TOOLS_ENABLED:
            return []
            
        tools = self.list_builtin_tools(enabled_only=enabled_only)
        return [tool.to_openai_builtin_format() for tool in tools]
    
    def get_combined_tool_definitions(self, provider_name: str, 
                                    provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get combined custom and built-in tools for a provider."""
        result = {
            "custom_tools": [],
            "builtin_tools": [],
            "total_count": 0
        }
        
        # Get custom tools based on provider type
        if provider_name == "local":
            # Local models get more permissive access
            max_permission = ToolPermission.SYSTEM_ACCESS
        else:
            # Cloud models get more restricted access
            max_permission = ToolPermission.WRITE_ALLOWED
        
        # Get custom tools if provider supports them
        if provider_config.get("supports_tools", False):
            result["custom_tools"] = self.get_openai_custom_definitions(
                max_permissions=max_permission
            )
        
        # Get built-in tools for cloud providers only
        if provider_name != "local" and BUILTIN_TOOLS_ENABLED:
            result["builtin_tools"] = self.get_openai_builtin_definitions()
        
        result["total_count"] = len(result["custom_tools"]) + len(result["builtin_tools"])
        
        return result
    
    def _register_core_tools(self) -> None:
        """Register the core MCP tools that DeepCoderX provides."""
        
        # File Operations
        self.register_custom_tool(ToolDefinition(
            name="read_file",
            description="Read the complete content of a file",
            category=ToolCategory.FILE_OPERATIONS,
            permission=ToolPermission.READ_ONLY,
            parameters=[
                ToolParameter("path", "string", "Relative path to the file to read")
            ],
            examples=[
                '{"tool": "read_file", "path": "config.py"}',
                '{"tool": "read_file", "path": "src/main.py"}'
            ]
        ))
        
        self.register_custom_tool(ToolDefinition(
            name="write_file",
            description="Write content to a file, creating it if it doesn't exist",
            category=ToolCategory.FILE_OPERATIONS,
            permission=ToolPermission.WRITE_ALLOWED,
            parameters=[
                ToolParameter("path", "string", "Relative path to the file to write"),
                ToolParameter("content", "string", "Content to write to the file")
            ],
            examples=[
                '{"tool": "write_file", "path": "script.py", "content": "print(\\"hello\\")"}',
                '{"tool": "write_file", "path": "data.txt", "content": "sample data"}'
            ]
        ))
        
        # Directory Operations
        self.register_custom_tool(ToolDefinition(
            name="list_dir",
            description="List the contents of a directory",
            category=ToolCategory.DIRECTORY_OPERATIONS,
            permission=ToolPermission.READ_ONLY,
            parameters=[
                ToolParameter("path", "string", "Relative path to the directory to list", default=".")
            ],
            examples=[
                '{"tool": "list_dir", "path": "."}',
                '{"tool": "list_dir", "path": "src"}'
            ]
        ))
        
        # Enhanced File Operations - OpenAPI 3.1 MCP Compliance
        self.register_custom_tool(ToolDefinition(
            name="move_file",
            description="Move or rename a file or directory to a new location",
            category=ToolCategory.FILE_OPERATIONS,
            permission=ToolPermission.WRITE_ALLOWED,
            parameters=[
                ToolParameter("source", "string", "Relative path to the source file or directory"),
                ToolParameter("destination", "string", "Relative path to the destination location"),
                ToolParameter("overwrite", "boolean", "Whether to overwrite destination if it exists", required=False, default=False)
            ],
            examples=[
                '{"tool": "move_file", "source": "old_file.txt", "destination": "new_file.txt"}',
                '{"tool": "move_file", "source": "temp_dir", "destination": "archive/old_data", "overwrite": true}'
            ]
        ))
        
        self.register_custom_tool(ToolDefinition(
            name="stat",
            description="Get detailed metadata information about a file or directory",
            category=ToolCategory.FILE_OPERATIONS,
            permission=ToolPermission.READ_ONLY,
            parameters=[
                ToolParameter("path", "string", "Relative path to the file or directory to inspect")
            ],
            examples=[
                '{"tool": "stat", "path": "config.py"}',
                '{"tool": "stat", "path": "src"}'
            ]
        ))
        
        # Enhanced Directory Operations
        self.register_custom_tool(ToolDefinition(
            name="mkdir",
            description="Create a new directory, optionally creating parent directories",
            category=ToolCategory.DIRECTORY_OPERATIONS,
            permission=ToolPermission.WRITE_ALLOWED,
            parameters=[
                ToolParameter("path", "string", "Relative path to the directory to create"),
                ToolParameter("parents", "boolean", "Create parent directories if they don't exist", required=False, default=True),
                ToolParameter("exist_ok", "boolean", "Don't raise error if directory already exists", required=False, default=True)
            ],
            examples=[
                '{"tool": "mkdir", "path": "new_folder"}',
                '{"tool": "mkdir", "path": "deep/nested/structure", "parents": true}'
            ]
        ))
        
        # System Operations
        self.register_custom_tool(ToolDefinition(
            name="run_bash",
            description="Execute a shell command in the project directory",
            category=ToolCategory.SYSTEM_OPERATIONS,
            permission=ToolPermission.SYSTEM_ACCESS,
            parameters=[
                ToolParameter("command", "string", "Shell command to execute")
            ],
            examples=[
                '{"tool": "run_bash", "command": "ls -la"}',
                '{"tool": "run_bash", "command": "python test.py"}'
            ]
        ))
    
    def _register_builtin_tools(self) -> None:
        """Register OpenAI built-in tools based on configuration."""
        if not BUILTIN_TOOLS_ENABLED:
            return
            
        for tool_name, config in BUILTIN_TOOLS.items():
            if config.get("enabled", False):
                # Create tool configuration based on type
                tool_config = {}
                
                if tool_name == "web_search_preview":
                    tool_config = {
                        "search_context_size": config.get("context_size", "medium")
                    }
                elif tool_name == "file_search":
                    tool_config = {
                        "max_files": config.get("max_files", 10000),
                        "max_file_size": config.get("max_file_size", 536870912)
                    }
                elif tool_name == "computer_use_preview":
                    tool_config = {
                        "browser_only": config.get("browser_only", True)
                    }
                
                # Create approval settings
                approval_settings = {}
                if config.get("requires_approval", False):
                    approval_settings["require_approval"] = "always"
                    if GLOBAL_TOOL_APPROVAL == "selective":
                        approval_settings["tool_names"] = [tool_name]
                
                self.register_builtin_tool(BuiltInToolDefinition(
                    openai_name=tool_name,
                    enabled=config["enabled"],
                    requires_approval=config.get("requires_approval", False),
                    approval_settings=approval_settings,
                    configuration=tool_config
                ))
    
    def validate_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a tool call against registered definitions."""
        tool_name = tool_call.get("tool")
        
        if not tool_name:
            return {
                "valid": False,
                "errors": ["Tool name is required"],
                "suggestions": ["Include 'tool' parameter with the tool name"]
            }
        
        # Check custom tools first
        tool_def = self.get_custom_tool(tool_name)
        if tool_def:
            errors = tool_def.validate_call(tool_call)
            
            result = {
                "valid": len(errors) == 0,
                "errors": errors,
                "tool_definition": tool_def,
                "tool_type": "custom"
            }
            
            if errors:
                result["suggestions"] = self._get_usage_suggestions(tool_def)
            
            return result
        
        # Check built-in tools
        builtin_def = self.get_builtin_tool(tool_name)
        if builtin_def:
            return {
                "valid": True,
                "errors": [],
                "tool_definition": builtin_def,
                "tool_type": "builtin"
            }
        
        # Tool not found
        available_custom = list(self.custom_tools.keys())
        available_builtin = list(self.builtin_tools.keys())
        available_tools = available_custom + available_builtin
        
        return {
            "valid": False,
            "errors": [f"Unknown tool: {tool_name}"],
            "suggestions": [f"Available tools: {', '.join(available_tools)}"]
        }
    
    def _get_usage_suggestions(self, tool_def: ToolDefinition) -> List[str]:
        """Get usage suggestions for a tool."""
        suggestions = []
        
        if tool_def.examples:
            suggestions.append(f"Example usage: {tool_def.examples[0]}")
        
        required_params = tool_def.get_required_parameters()
        if required_params:
            suggestions.append(f"Required parameters: {', '.join(required_params)}")
        
        optional_params = tool_def.get_optional_parameters()
        if optional_params:
            suggestions.append(f"Optional parameters: {', '.join(optional_params)}")
        
        return suggestions
    
    def export_documentation(self) -> str:
        """Export comprehensive documentation for all tools."""
        docs = ["# DeepCoderX Enhanced Tool Registry Documentation\n"]
        
        # Custom Tools Documentation
        docs.append("## Custom MCP Tools\n")
        
        for category in ToolCategory:
            category_tools = self.list_custom_tools(category=category)
            if not category_tools:
                continue
                
            docs.append(f"### {category.value.replace('_', ' ').title()}\n")
            
            for tool in category_tools:
                docs.append(f"#### {tool.name}")
                docs.append(f"**Description:** {tool.description}")
                docs.append(f"**Permission:** {tool.permission.value}")
                docs.append(f"**Type:** {tool.tool_type.value}")
                
                if tool.parameters:
                    docs.append("**Parameters:**")
                    for param in tool.parameters:
                        required_text = " (required)" if param.required else " (optional)"
                        docs.append(f"- `{param.name}` ({param.type}){required_text}: {param.description}")
                
                if tool.examples:
                    docs.append("**Examples:**")
                    for example in tool.examples:
                        docs.append(f"```json\n{example}\n```")
                
                docs.append("")  # Empty line
        
        # Built-in Tools Documentation
        if BUILTIN_TOOLS_ENABLED:
            docs.append("## OpenAI Built-in Tools\n")
            
            for tool_name, tool_def in self.builtin_tools.items():
                if tool_def.enabled:
                    config = BUILTIN_TOOLS.get(tool_name, {})
                    docs.append(f"### {config.get('name', tool_name)}")
                    docs.append(f"**OpenAI Name:** `{tool_name}`")
                    docs.append(f"**Description:** {config.get('description', 'No description available')}")
                    docs.append(f"**Requires Approval:** {tool_def.requires_approval}")
                    
                    if tool_def.configuration:
                        docs.append("**Configuration:**")
                        for key, value in tool_def.configuration.items():
                            docs.append(f"- `{key}`: {value}")
                    
                    docs.append("")  # Empty line
        
        return "\n".join(docs)


# Global enhanced registry instance
enhanced_tool_registry = EnhancedToolRegistry()


# Convenience functions for tool management
def get_tools_for_provider(provider_name: str, provider_config: Dict[str, Any]) -> Dict[str, Any]:
    """Get appropriate tools for a specific provider."""
    return enhanced_tool_registry.get_combined_tool_definitions(provider_name, provider_config)


def validate_tool_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a tool call using the enhanced registry."""
    return enhanced_tool_registry.validate_tool_call(tool_call)


def get_tool_definition(tool_name: str) -> Optional[Union[ToolDefinition, BuiltInToolDefinition]]:
    """Get a tool definition from the enhanced registry."""
    custom_tool = enhanced_tool_registry.get_custom_tool(tool_name)
    if custom_tool:
        return custom_tool
    return enhanced_tool_registry.get_builtin_tool(tool_name)


def list_available_tools(include_builtin: bool = True) -> Dict[str, List[str]]:
    """List available tool names by type."""
    result = {
        "custom": list(enhanced_tool_registry.custom_tools.keys()),
        "builtin": []
    }
    
    if include_builtin and BUILTIN_TOOLS_ENABLED:
        result["builtin"] = [
            name for name, tool in enhanced_tool_registry.builtin_tools.items() 
            if tool.enabled
        ]
    
    return result


def get_tool_stats() -> Dict[str, Any]:
    """Get statistics about registered tools."""
    custom_tools = enhanced_tool_registry.custom_tools
    builtin_tools = enhanced_tool_registry.builtin_tools
    
    custom_by_category = {}
    for tool in custom_tools.values():
        category = tool.category.value
        custom_by_category[category] = custom_by_category.get(category, 0) + 1
    
    enabled_builtin = len([t for t in builtin_tools.values() if t.enabled])
    
    return {
        "total_custom_tools": len(custom_tools),
        "total_builtin_tools": len(builtin_tools),
        "enabled_builtin_tools": enabled_builtin,
        "custom_tools_by_category": custom_by_category,
        "builtin_tools_enabled": BUILTIN_TOOLS_ENABLED,
        "global_approval_setting": GLOBAL_TOOL_APPROVAL
    }
