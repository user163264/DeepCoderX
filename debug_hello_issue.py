#!/usr/bin/env python3
"""
Debug script for the "hello" prompt issue in GGUF handler.

This script analyzes why the GGUF handler is generating tool calls 
for simple conversational inputs like "hello".
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config_module import config
from models.session import CommandContext
from services.gguf_handler import GGUFLocalHandler
from utils.logging import console

def debug_hello_issue():
    """Debug the hello prompt issue step by step."""
    
    console.print("[bold blue]🔍 Debugging GGUF Hello Issue[/]")
    console.print("=" * 60)
    
    # Test input
    test_input = "hello"
    
    # Create test context
    ctx = CommandContext(
        root_path=Path.cwd(),
        mcp_client=None,  # Not needed for this test
        sandbox_path=Path.cwd(),
        debug_mode=True
    )
    ctx.user_input = test_input  # Set after initialization
    
    try:
        # Initialize handler
        console.print("[yellow]1. Initializing GGUF handler...[/]")
        handler = GGUFLocalHandler(ctx, "local")
        
        # Test conversational input detection
        console.print(f"[yellow]2. Testing conversational input detection for: '{test_input}'[/]")
        is_conversational = handler._is_conversational_input(test_input)
        console.print(f"[cyan]   Result: {is_conversational}[/]")
        
        if not is_conversational:
            console.print("[red]❌ PROBLEM: 'hello' not detected as conversational![/]")
        else:
            console.print("[green]✅ 'hello' correctly detected as conversational[/]")
        
        # Test prompt building
        console.print("[yellow]3. Testing prompt building...[/]")
        available_tools = handler._get_available_tools()
        raw_prompt = handler.prompt_builder.build_prompt(
            user_input=test_input,
            conversation_history=[],
            available_tools=available_tools
        )
        
        console.print(f"[cyan]   Raw prompt length: {len(raw_prompt)} characters[/]")
        console.print(f"[cyan]   Contains tool examples: {'<tool_call>' in raw_prompt}[/]")
        
        # Show prompt preview
        console.print("[dim]   Raw prompt preview (first 500 chars):[/]")
        console.print(f"[dim]{raw_prompt[:500]}...[/]")
        
        # Test chat template formatting
        console.print("[yellow]4. Testing chat template formatting...[/]")
        system_prompt = handler._extract_system_prompt(raw_prompt)
        user_prompt = handler._extract_user_prompt(raw_prompt, test_input)
        
        console.print(f"[cyan]   System prompt length: {len(system_prompt)} characters[/]")
        console.print(f"[cyan]   User prompt: '{user_prompt}'[/]")
        
        formatted_prompt = handler.chat_formatter.format_prompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            conversation_history=[]
        )
        
        console.print(f"[cyan]   Formatted prompt length: {len(formatted_prompt)} characters[/]")
        console.print(f"[cyan]   Chat template type: {handler.chat_formatter.model_type}[/]")
        
        # Show formatted prompt preview
        console.print("[dim]   Formatted prompt preview (first 800 chars):[/]")
        console.print(f"[dim]{formatted_prompt[:800]}...[/]")
        
        # Test model generation
        console.print("[yellow]5. Testing model response generation...[/]")
        try:
            response = handler._generate_gguf_response(formatted_prompt)
            console.print(f"[cyan]   Generated response length: {len(response)} characters[/]")
            console.print(f"[cyan]   Response preview:[/] {response[:200]}...")
            
            # Test tool call parsing
            console.print("[yellow]6. Testing tool call parsing...[/]")
            tool_calls, clean_response = handler.tool_parser.parse_and_execute_format(response)
            
            console.print(f"[cyan]   Tool calls found: {len(tool_calls)}[/]")
            console.print(f"[cyan]   Clean response: '{clean_response}'[/]")
            
            if tool_calls:
                console.print("[red]❌ PROBLEM: Tool calls generated for conversational input![/]")
                for i, call in enumerate(tool_calls):
                    console.print(f"[red]   Tool call {i+1}: {call}[/]")
            else:
                console.print("[green]✅ No tool calls generated (correct for conversational input)[/]")
                
        except Exception as e:
            console.print(f"[red]❌ Model generation failed: {e}[/]")
            return
        
        # Analysis summary
        console.print("\n" + "=" * 60)
        console.print("[bold yellow]🎯 ANALYSIS SUMMARY[/]")
        console.print(f"[cyan]Input: '{test_input}'[/]")
        console.print(f"[cyan]Conversational detection: {is_conversational}[/]")
        console.print(f"[cyan]Tool calls generated: {len(tool_calls)}[/]")
        console.print(f"[cyan]Clean response available: {bool(clean_response)}[/]")
        
        if is_conversational and tool_calls:
            console.print("[red]🚨 ROOT CAUSE: Despite detecting conversational input, tool calls are still generated![/]")
            console.print("[yellow]💡 SOLUTION: Need to implement bypass logic for conversational inputs[/]")
        elif not is_conversational:
            console.print("[red]🚨 ROOT CAUSE: Conversational input detection is failing![/]")
            console.print("[yellow]💡 SOLUTION: Need to improve _is_conversational_input() method[/]")
        else:
            console.print("[green]✅ Everything looks correct - investigate elsewhere[/]")
            
    except Exception as e:
        console.print(f"[bold red]❌ Handler initialization failed: {e}[/]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/]")

def test_conversational_patterns():
    """Test various conversational input patterns."""
    
    console.print("\n[bold blue]🧪 Testing Conversational Input Patterns[/]")
    console.print("=" * 60)
    
    # Create minimal handler for testing
    ctx = CommandContext(
        root_path=Path.cwd(),
        mcp_client=None,
        sandbox_path=Path.cwd(),
        debug_mode=False
    )
    ctx.user_input = "test"
    
    try:
        handler = GGUFLocalHandler(ctx, "local")
        
        test_inputs = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "how are you",
            "what are you",
            "who are you",
            "what can you do",
            "tell me about yourself",
            "explain quantum physics",
            "what is python",
            "create a file",  # This should NOT be conversational
            "run pwd command",  # This should NOT be conversational
            "help me debug",  # This should NOT be conversational
        ]
        
        for test_input in test_inputs:
            is_conversational = handler._is_conversational_input(test_input)
            status = "✅ CONV" if is_conversational else "🔧 TOOL"
            console.print(f"[cyan]{status}[/] '{test_input}' -> {is_conversational}")
            
    except Exception as e:
        console.print(f"[red]Testing failed: {e}[/]")

if __name__ == "__main__":
    debug_hello_issue()
    test_conversational_patterns()
