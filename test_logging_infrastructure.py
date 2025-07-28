#!/usr/bin/env python3
"""
Test script for enhanced model interaction logging infrastructure.

This script validates that all logging functions work correctly and creates
sample log entries for testing the structured storage system.
"""

import os
import sys
import time
import json
from pathlib import Path

# Add the DeepCoderX directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import enhanced logging functions
from utils.logging import (
    log_model_prompt, log_model_response, log_semantic_analysis,
    log_tool_execution_details, log_conversation_context, log_interaction_summary,
    get_model_interactions_summary, MODEL_INTERACTIONS_DIR,
    console, setup_component_logger
)

def test_basic_infrastructure():
    """Test basic logging infrastructure setup."""
    console.print("[bold blue]Testing Basic Logging Infrastructure[/bold blue]")
    
    # Test directory creation
    assert MODEL_INTERACTIONS_DIR.exists(), f"Model interactions directory not found: {MODEL_INTERACTIONS_DIR}"
    console.print(f"✅ Model interactions directory exists: {MODEL_INTERACTIONS_DIR}")
    
    # Test component logger creation
    test_logger = setup_component_logger("TestComponent")
    assert test_logger is not None, "Failed to create component logger"
    console.print("✅ Component logger creation successful")
    
    return True

def test_environment_variables():
    """Test environment variable configuration."""
    console.print("[bold blue]Testing Environment Variable Configuration[/bold blue]")
    
    # Set test environment variables
    test_env_vars = {
        "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
        "DEEPCODERX_LOG_MODEL_RESPONSES": "true", 
        "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
        "DEEPCODERX_LOG_TOOL_DETAILS": "true",
        "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "true"
    }
    
    for var, value in test_env_vars.items():
        os.environ[var] = value
        console.print(f"✅ Set {var}={value}")
    
    # Test config import
    try:
        from config_module import DEBUG_LOGGING
        console.print(f"✅ DEBUG_LOGGING configuration loaded: {DEBUG_LOGGING}")
        
        # Verify environment variables are reflected
        expected_true_keys = ["model_prompts", "model_responses", "semantic_details", "tool_details", "conversation_context"]
        for key in expected_true_keys:
            if DEBUG_LOGGING.get(key) is True:
                console.print(f"✅ {key} enabled correctly")
            else:
                console.print(f"❌ {key} not enabled (expected True, got {DEBUG_LOGGING.get(key)})")
                
    except ImportError as e:
        console.print(f"❌ Failed to import DEBUG_LOGGING configuration: {e}")
        return False
    
    return True

def test_model_logging_functions():
    """Test all model interaction logging functions."""
    console.print("[bold blue]Testing Model Interaction Logging Functions[/bold blue]")
    
    # Generate test interaction ID
    interaction_id = f"test_{int(time.time())}"
    console.print(f"📝 Using test interaction ID: {interaction_id}")
    
    # Test log_model_prompt
    try:
        test_prompt = "You are a helpful coding assistant. Please help with the following task: Create a Python function to sort a list."
        returned_id = log_model_prompt("TestComponent", "test-model", test_prompt, interaction_id)
        console.print(f"✅ log_model_prompt successful, returned ID: {returned_id}")
    except Exception as e:
        console.print(f"❌ log_model_prompt failed: {e}")
        return False
    
    # Test log_model_response
    try:
        test_response = "Here's a Python function to sort a list:\n\ndef sort_list(items):\n    return sorted(items)"
        returned_id = log_model_response("TestComponent", "test-model", test_response, 2.5, interaction_id)
        console.print(f"✅ log_model_response successful, returned ID: {returned_id}")
    except Exception as e:
        console.print(f"❌ log_model_response failed: {e}")
        return False
    
    # Test log_semantic_analysis
    try:
        semantic_prompt = "Classify this request: 'create a Python function'"
        raw_response = '{"intent": "code_generation", "confidence": 0.95, "specialist": "qwen_coder"}'
        parsed_result = {"intent": "code_generation", "confidence": 0.95, "specialist": "qwen_coder"}
        returned_id = log_semantic_analysis("TestComponent", "create a Python function", semantic_prompt, raw_response, parsed_result, True, interaction_id)
        console.print(f"✅ log_semantic_analysis successful, returned ID: {returned_id}")
    except Exception as e:
        console.print(f"❌ log_semantic_analysis failed: {e}")
        return False
    
    # Test log_tool_execution_details
    try:
        test_tool_calls = [
            {"tool": "write_file", "filename": "sort_function.py", "content": "def sort_list(items):\n    return sorted(items)"},
            {"tool": "run_bash", "command": "python3 -m py_compile sort_function.py"}
        ]
        test_tool_results = [
            {"success": True, "message": "File written successfully"},
            {"success": True, "output": "Compilation successful"}
        ]
        returned_id = log_tool_execution_details("TestComponent", test_tool_calls, test_tool_results, interaction_id)
        console.print(f"✅ log_tool_execution_details successful, returned ID: {returned_id}")
    except Exception as e:
        console.print(f"❌ log_tool_execution_details failed: {e}")
        return False
    
    # Test log_conversation_context
    try:
        test_history = [
            {"role": "user", "content": "Hello, I need help with Python"},
            {"role": "assistant", "content": "I'd be happy to help with Python! What do you need?"},
            {"role": "user", "content": "Create a function to sort a list"}
        ]
        returned_id = log_conversation_context("TestComponent", test_history, 4096, interaction_id)
        console.print(f"✅ log_conversation_context successful, returned ID: {returned_id}")
    except Exception as e:
        console.print(f"❌ log_conversation_context failed: {e}")
        return False
    
    # Test log_interaction_summary
    try:
        log_interaction_summary(
            interaction_id=interaction_id,
            component="TestComponent",
            operation_type="code_generation",
            user_input="create a Python function to sort a list",
            final_response="Here's a Python function to sort a list:\n\ndef sort_list(items):\n    return sorted(items)",
            total_duration=5.2,
            model_calls=2,
            tool_calls=2,
            errors=0
        )
        console.print(f"✅ log_interaction_summary successful")
    except Exception as e:
        console.print(f"❌ log_interaction_summary failed: {e}")
        return False
    
    return True

def test_structured_storage():
    """Test structured log file creation and content."""
    console.print("[bold blue]Testing Structured Log Storage[/bold blue]")
    
    # Check for created log files
    log_files = list(MODEL_INTERACTIONS_DIR.glob("*.jsonl"))
    if not log_files:
        console.print("❌ No JSONL log files found")
        return False
    
    console.print(f"✅ Found {len(log_files)} log files:")
    for log_file in log_files:
        console.print(f"   📄 {log_file.name} ({log_file.stat().st_size} bytes)")
    
    # Test reading and parsing log entries
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                console.print(f"✅ {log_file.name}: {len(lines)} entries")
                
                # Validate JSON structure of last entry
                if lines:
                    last_entry = json.loads(lines[-1].strip())
                    required_fields = ["timestamp", "log_type", "interaction_id"]
                    for field in required_fields:
                        if field in last_entry:
                            console.print(f"   ✅ {field}: {last_entry[field]}")
                        else:
                            console.print(f"   ❌ Missing required field: {field}")
                            
        except Exception as e:
            console.print(f"❌ Error reading {log_file.name}: {e}")
            return False
    
    return True

def test_log_summary():
    """Test log summary functionality."""
    console.print("[bold blue]Testing Log Summary[/bold blue]")
    
    try:
        summary = get_model_interactions_summary()
        console.print(f"✅ Log summary generated successfully")
        console.print(f"   📊 Total interactions: {summary.get('total_interactions', 0)}")
        console.print(f"   📁 Log files: {len(summary.get('log_files', {}))}")
        console.print(f"   🔄 Recent activity entries: {len(summary.get('recent_activity', []))}")
        
        # Display log file details
        for filename, details in summary.get('log_files', {}).items():
            if 'error' not in details:
                console.print(f"   📄 {filename}: {details.get('entries', 0)} entries, {details.get('size_mb', 0)} MB")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Log summary failed: {e}")
        return False

def main():
    """Run all logging infrastructure tests."""
    console.print("[bold green]🧪 Enhanced Model Logging Infrastructure Test Suite[/bold green]")
    console.print(f"📁 Model interactions directory: {MODEL_INTERACTIONS_DIR}")
    console.print()
    
    tests = [
        ("Basic Infrastructure", test_basic_infrastructure),
        ("Environment Variables", test_environment_variables),
        ("Model Logging Functions", test_model_logging_functions),
        ("Structured Storage", test_structured_storage),
        ("Log Summary", test_log_summary)
    ]
    
    results = []
    for test_name, test_func in tests:
        console.print(f"\n[bold cyan]🔍 Running Test: {test_name}[/bold cyan]")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            console.print(f"[bold]{status}[/bold]: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            console.print(f"[bold red]❌ FAILED[/bold red]: {test_name} - {e}")
    
    # Summary
    console.print(f"\n[bold blue]📋 Test Results Summary[/bold blue]")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        console.print(f"  {status}: {test_name}")
    
    console.print(f"\n[bold]Overall: {passed}/{total} tests passed[/bold]")
    
    if passed == total:
        console.print("[bold green]🎉 ALL TESTS PASSED! Logging infrastructure is ready.[/bold green]")
        console.print("\n[bold]Next Steps:[/bold]")
        console.print("1. Enable logging by setting environment variables")
        console.print("2. Implement logging calls in dual_model_handler.py") 
        console.print("3. Implement logging calls in unified_openai_handler.py")
        console.print("4. Test with real DeepCoderX usage")
        return 0
    else:
        console.print(f"[bold red]❌ {total - passed} tests failed. Please fix issues before proceeding.[/bold red]")
        return 1

if __name__ == "__main__":
    exit(main())
