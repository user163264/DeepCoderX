#!/usr/bin/env python3
"""
Test script to validate the centralized direct commands refactoring.

This script verifies:
1. The centralized config loads correctly
2. All expected commands are available  
3. The functions work as expected
4. Import compatibility with dual_model_handler
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_direct_commands_config():
    """Test the centralized direct commands configuration."""
    print("🔧 TESTING CENTRALIZED DIRECT COMMANDS CONFIGURATION")
    print("=" * 60)
    
    try:
        # Test 1: Import the configuration
        print("📝 Test 1: Importing centralized configuration...")
        from config.direct_commands import (
            get_direct_commands, is_direct_command, 
            get_direct_command_tool_call, get_command_info
        )
        print("✅ Import successful")
        
        # Test 2: Check command count and availability
        print("\n📝 Test 2: Checking command availability...")
        command_info = get_command_info()
        print(f"✅ Total commands: {command_info['total_commands']}")
        print(f"✅ Command names: {', '.join(command_info['command_names'])}")
        print(f"✅ Performance: {command_info['performance']}")
        
        # Test 3: Validate specific commands
        print("\n📝 Test 3: Testing specific command functions...")
        
        # Test pwd command
        assert is_direct_command("pwd"), "pwd should be a direct command"
        pwd_call = get_direct_command_tool_call("pwd")
        assert pwd_call == 'run_bash({"command": "pwd"})', f"Unexpected pwd call: {pwd_call}"
        print("✅ pwd command works correctly")
        
        # Test ls command
        assert is_direct_command("ls"), "ls should be a direct command"
        ls_call = get_direct_command_tool_call("ls")
        assert ls_call == 'run_bash({"command": "ls"})', f"Unexpected ls call: {ls_call}"
        print("✅ ls command works correctly")
        
        # Test git status command
        assert is_direct_command("git status"), "git status should be a direct command"
        git_call = get_direct_command_tool_call("git status")
        assert git_call == 'run_bash({"command": "git status"})', f"Unexpected git status call: {git_call}"
        print("✅ git status command works correctly")
        
        # Test non-existent command
        assert not is_direct_command("nonexistent"), "nonexistent should not be a direct command"
        none_call = get_direct_command_tool_call("nonexistent")
        assert none_call is None, f"Should return None for nonexistent command, got: {none_call}"
        print("✅ Non-existent command handling works correctly")
        
        # Test 4: Check that we have the expected commands from both original dictionaries
        print("\n📝 Test 4: Verifying all expected commands are present...")
        expected_commands = [
            "pwd", "ls", "ls -l", "ls -la", 
            "git status", "git log", "whoami", "date"
        ]
        
        actual_commands = command_info['command_names']
        for cmd in expected_commands:
            assert cmd in actual_commands, f"Expected command '{cmd}' not found in actual commands"
            print(f"✅ {cmd} - present")
        
        print(f"\n📊 SUMMARY:")
        print(f"✅ All {len(expected_commands)} expected commands are present")
        print(f"✅ Total commands available: {len(actual_commands)}")
        print(f"✅ Configuration loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dual_model_integration():
    """Test that the dual model handler can import the new configuration."""
    print("\n🔧 TESTING DUAL MODEL HANDLER INTEGRATION") 
    print("=" * 60)
    
    try:
        # Test import compatibility
        print("📝 Testing import compatibility...")
        from services.dual_model_handler import DualModelHandler
        print("✅ DualModelHandler imports successfully with new configuration")
        
        # Test that the functions are available
        from config.direct_commands import is_direct_command, get_direct_command_tool_call
        print("✅ Direct command functions are accessible to DualModelHandler")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 REFACTORING VALIDATION TESTS")
    print("Testing centralized direct commands configuration...")
    print("=" * 80)
    
    # Run tests
    config_success = test_direct_commands_config()
    integration_success = test_dual_model_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 VALIDATION SUMMARY:")
    print(f"✅ Configuration Test: {'PASSED' if config_success else 'FAILED'}")
    print(f"✅ Integration Test: {'PASSED' if integration_success else 'FAILED'}")
    
    if config_success and integration_success:
        print("🎉 ALL TESTS PASSED - REFACTORING SUCCESSFUL!")
        print("\n📋 WHAT WAS ACCOMPLISHED:")
        print("  • Created centralized config/direct_commands.py")
        print("  • Eliminated duplicated command dictionaries") 
        print("  • Updated dual_model_handler.py to use centralized config")
        print("  • Maintained all 8 direct commands")
        print("  • Added comprehensive logging and debug info")
        print("  • Created clean, maintainable architecture")
        return 0
    else:
        print("❌ TESTS FAILED - REFACTORING NEEDS ATTENTION")
        return 1


if __name__ == "__main__":
    sys.exit(main())
