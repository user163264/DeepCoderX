#!/usr/bin/env python3
"""
Test script to verify GGUF tool calling implementation.

This script tests all the GGUF components individually and together
to ensure the implementation works correctly.
"""

import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from services.gguf_tool_prompt import GGUFToolPromptBuilder, build_gguf_prompt
    from services.gguf_tool_parser import GGUFToolCallParser, parse_gguf_response
    from services.gguf_context_manager import GGUFContextManager
    from services.gguf_handler import GGUFLocalHandler, test_gguf_functionality
    from services.tool_registry import tool_registry
    from config import config
    from models.session import CommandContext
    from rich.console import Console
    
    console = Console()
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the DeepCoderX project directory")
    sys.exit(1)


def test_tool_registry():
    """Test that the tool registry has the expected tools."""
    console.print("[bold blue]Testing Tool Registry...[/]")
    
    tools = list(tool_registry.tools.keys())
    expected_tools = ["read_file", "write_file", "list_dir", "move_file", "mkdir", "stat", "run_bash"]
    
    console.print(f"Available tools: {tools}")
    
    missing_tools = [tool for tool in expected_tools if tool not in tools]
    if missing_tools:
        console.print(f"[red]Missing tools: {missing_tools}[/]")
        return False
    
    console.print("[green]✅ Tool Registry: All expected tools available[/]")
    return True


def test_prompt_builder():
    """Test the GGUF prompt builder."""
    console.print("[bold blue]Testing GGUF Prompt Builder...[/]")
    
    try:
        builder = GGUFToolPromptBuilder()
        available_tools = builder.get_tools_for_provider("local")
        
        test_prompt = builder.build_prompt(
            user_input="create a file called test.txt",
            conversation_history=[],
            available_tools=available_tools
        )
        
        # Check that prompt contains essential elements
        checks = [
            ("<tool_call>" in test_prompt, "Tool call format in prompt"),
            ("write_file" in test_prompt, "write_file tool documented"),
            ("Available tools:" in test_prompt, "Tools documentation section"),
            ("Examples" in test_prompt, "Examples section"),
            ("create a file called test.txt" in test_prompt, "User input included")
        ]
        
        all_passed = True
        for check_result, description in checks:
            if check_result:
                console.print(f"[green]✅ {description}[/]")
            else:
                console.print(f"[red]❌ {description}[/]")
                all_passed = False
        
        console.print(f"[dim]Prompt length: {len(test_prompt)} characters[/]")
        
        if all_passed:
            console.print("[green]✅ Prompt Builder: All checks passed[/]")
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ Prompt Builder Error: {e}[/]")
        return False


def test_tool_parser():
    """Test the GGUF tool call parser."""
    console.print("[bold blue]Testing GGUF Tool Call Parser...[/]")
    
    try:
        parser = GGUFToolCallParser()
        
        # Test cases with different response formats
        test_cases = [
            {
                "name": "Valid tool call",
                "response": 'I\'ll create that file for you.\n<tool_call>write_file({"path": "test.txt", "content": "Hello World"})</tool_call>\nFile created successfully!',
                "expected_calls": 1,
                "expected_function": "write_file"
            },
            {
                "name": "Multiple tool calls",
                "response": 'I\'ll list the directory first.\n<tool_call>list_dir({"path": "."})</tool_call>\nNow I\'ll create a file.\n<tool_call>write_file({"path": "new.txt", "content": "content"})</tool_call>',
                "expected_calls": 2,
                "expected_function": "list_dir"
            },
            {
                "name": "No tool calls",
                "response": "This is just a regular response without any tool calls.",
                "expected_calls": 0,
                "expected_function": None
            },
            {
                "name": "Malformed JSON (should be handled)",
                "response": '<tool_call>write_file({"path": "test.txt", "content": "broken json")</tool_call>',
                "expected_calls": 0,  # Should fail to parse due to malformed JSON
                "expected_function": None
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            console.print(f"[cyan]Testing: {test_case['name']}[/]")
            
            tool_calls = parser.parse_response(test_case["response"])
            
            if len(tool_calls) == test_case["expected_calls"]:
                console.print(f"[green]✅ Correct number of tool calls: {len(tool_calls)}[/]")
            else:
                console.print(f"[red]❌ Expected {test_case['expected_calls']} calls, got {len(tool_calls)}[/]")
                all_passed = False
            
            if test_case["expected_calls"] > 0 and tool_calls:
                if tool_calls[0].function_name == test_case["expected_function"]:
                    console.print(f"[green]✅ Correct function name: {tool_calls[0].function_name}[/]")
                else:
                    console.print(f"[red]❌ Expected {test_case['expected_function']}, got {tool_calls[0].function_name}[/]")
                    all_passed = False
        
        # Test clean response extraction
        dirty_response = 'Here is my response.\n<tool_call>write_file({"path": "test.txt", "content": "test"})</tool_call>\nAnd here is more text.'
        clean_response = parser.extract_clean_response(dirty_response)
        
        if "<tool_call>" not in clean_response:
            console.print("[green]✅ Clean response extraction works[/]")
        else:
            console.print("[red]❌ Clean response extraction failed[/]")
            all_passed = False
        
        if all_passed:
            console.print("[green]✅ Tool Parser: All tests passed[/]")
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ Tool Parser Error: {e}[/]")
        return False


def test_context_manager():
    """Test the GGUF context manager."""
    console.print("[bold blue]Testing GGUF Context Manager...[/]")
    
    try:
        # Use a test provider name
        manager = GGUFContextManager("test_gguf")
        
        # Test adding messages
        manager.add_user_message("Hello, please create a file")
        manager.add_assistant_message("I'll create that file for you.", [{"function_name": "write_file"}])
        manager.add_tool_results([{"function_name": "write_file"}], ["File created successfully"])
        
        # Test getting conversation history
        history = manager.get_conversation_history()
        
        checks = [
            (len(history) >= 3, f"Has conversation history: {len(history)} messages"),
            (any(msg["role"] == "user" for msg in history), "Has user message"),
            (any(msg["role"] == "assistant" for msg in history), "Has assistant message"),
            (any(msg["role"] == "tool" for msg in history), "Has tool message"),
            (manager.get_token_count() > 0, f"Token counting works: {manager.get_token_count()} tokens")
        ]
        
        all_passed = True
        for check_result, description in checks:
            if check_result:
                console.print(f"[green]✅ {description}[/]")
            else:
                console.print(f"[red]❌ {description}[/]")
                all_passed = False
        
        # Test context summary
        summary = manager.get_context_summary()
        console.print(f"[dim]Context summary: {summary}[/]")
        
        if all_passed:
            console.print("[green]✅ Context Manager: All tests passed[/]")
        
        # Clean up test session
        manager.clear_history()
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ Context Manager Error: {e}[/]")
        return False


def test_integration():
    """Test integration between components."""
    console.print("[bold blue]Testing GGUF Component Integration...[/]")
    
    try:
        # Test the convenience function
        test_prompt = build_gguf_prompt(
            user_input="create a file called integration_test.txt",
            conversation_history=[],
            provider_name="local"
        )
        
        checks = [
            (len(test_prompt) > 500, f"Prompt is substantial: {len(test_prompt)} chars"),
            ("integration_test.txt" in test_prompt, "User input in prompt"),
            ("<tool_call>" in test_prompt, "Tool call format in prompt"),
            ("write_file" in test_prompt, "Expected tool documented")
        ]
        
        all_passed = True
        for check_result, description in checks:
            if check_result:
                console.print(f"[green]✅ {description}[/]")
            else:
                console.print(f"[red]❌ {description}[/]")
                all_passed = False
        
        # Test parsing a realistic GGUF response
        mock_gguf_response = """I'll create that file for you.

<tool_call>write_file({"path": "integration_test.txt", "content": "This is a test file created by GGUF model"})</tool_call>

The file has been created successfully with the specified content."""
        
        tool_calls = parse_gguf_response(mock_gguf_response)
        
        if len(tool_calls) == 1 and tool_calls[0]["tool"] == "write_file":
            console.print("[green]✅ Mock response parsing works correctly[/]")
        else:
            console.print(f"[red]❌ Mock response parsing failed: {tool_calls}[/]")
            all_passed = False
        
        if all_passed:
            console.print("[green]✅ Integration: All tests passed[/]")
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ Integration Error: {e}[/]")
        return False


def test_configuration():
    """Test that configuration is updated correctly."""
    console.print("[bold blue]Testing Configuration Updates...[/]")
    
    try:
        # Check that local provider has GGUF configuration
        local_config = config.PROVIDERS.get("local", {})
        
        checks = [
            (local_config.get("model_type") == "gguf", "Local provider is GGUF type"),
            (local_config.get("tool_format") == "manual", "Local provider uses manual tool format"),
            (local_config.get("supports_tools") == True, "Local provider supports tools"),
            ("max_tool_iterations" in local_config, "Max tool iterations configured"),
            ("lm_studio" in config.PROVIDERS, "LM Studio provider added for OpenAI compatibility")
        ]
        
        all_passed = True
        for check_result, description in checks:
            if check_result:
                console.print(f"[green]✅ {description}[/]")
            else:
                console.print(f"[red]❌ {description}[/]")
                all_passed = False
        
        if all_passed:
            console.print("[green]✅ Configuration: All checks passed[/]")
        
        return all_passed
        
    except Exception as e:
        console.print(f"[red]❌ Configuration Error: {e}[/]")
        return False


def main():
    """Run all GGUF implementation tests."""
    console.print("[bold magenta]🧪 GGUF Tool Calling Implementation Test Suite[/]")
    console.print("=" * 60)
    
    tests = [
        ("Tool Registry", test_tool_registry),
        ("Prompt Builder", test_prompt_builder),
        ("Tool Parser", test_tool_parser),
        ("Context Manager", test_context_manager),
        ("Integration", test_integration),
        ("Configuration", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        console.print(f"\n[bold yellow]Running {test_name} Test...[/]")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            console.print(f"[red]❌ {test_name} Test Failed with Exception: {e}[/]")
            results.append((test_name, False))
    
    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold magenta]📊 Test Results Summary[/]")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[green]✅ PASSED[/]" if result else "[red]❌ FAILED[/]"
        console.print(f"{test_name:20} {status}")
    
    console.print(f"\n[bold]Overall Result: {passed}/{total} tests passed[/]")
    
    if passed == total:
        console.print("[bold green]🎉 All GGUF implementation tests passed![/]")
        console.print("[green]The GGUF tool calling implementation is ready for use.[/]")
        return True
    else:
        console.print(f"[bold red]⚠️  {total - passed} tests failed.[/]")
        console.print("[red]Please fix the issues before using GGUF tool calling.[/]")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
