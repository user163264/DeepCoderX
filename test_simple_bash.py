#!/usr/bin/env python3
"""
Simple bash command test - bypassing all the MCP infrastructure
"""

import subprocess
import json
from pathlib import Path

def test_simple_bash():
    """Test bash commands directly like the tool executor does."""
    print("🔧 Testing Simple Bash Commands")
    print("=" * 50)
    
    test_commands = ["pwd", "ls", "whoami", "date"]
    
    for cmd in test_commands:
        print(f"\n📝 Testing: {cmd}")
        try:
            process = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=Path.cwd()
            )
            
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            if process.returncode == 0:
                result = f"✅ Command executed successfully:\n{stdout}" if stdout else "✅ Command executed successfully (no output)"
                print(f"✅ Result: {result}")
            else:
                result = f"❌ Command failed (exit code {process.returncode}):\n{stderr}" if stderr else f"❌ Command failed (exit code {process.returncode})"
                print(f"❌ Error: {result}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ Command '{cmd}' timed out")
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_tool_call_format():
    """Test the exact tool call format that should be generated."""
    print("\n🔍 Testing Tool Call Format")
    print("=" * 50)
    
    # This is what the model should generate
    tool_call_response = 'I need to check the current directory.\n\n<tool_call>run_bash({"command": "pwd"})</tool_call>'
    
    print(f"📝 Raw response: {tool_call_response}")
    
    # Extract tool call using regex (simplified version)
    import re
    pattern = r'<tool_call>(\w+)\(([^)]+)\)</tool_call>'
    matches = re.findall(pattern, tool_call_response)
    
    print(f"🔍 Regex matches: {matches}")
    
    if matches:
        for function_name, args_str in matches:
            print(f"📋 Function: {function_name}")
            print(f"📋 Args string: {args_str}")
            
            try:
                args = json.loads(args_str)
                print(f"✅ Parsed args: {args}")
                
                # Test execution
                if function_name == "run_bash" and "command" in args:
                    cmd = args["command"]
                    print(f"🚀 Executing: {cmd}")
                    
                    process = subprocess.run(
                        cmd, 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        timeout=30
                    )
                    
                    if process.returncode == 0:
                        result = f"✅ Command executed successfully:\n{process.stdout.strip()}"
                        print(f"🎯 Final result: {result}")
                    else:
                        result = f"❌ Command failed: {process.stderr.strip()}"
                        print(f"❌ Error result: {result}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
            except Exception as e:
                print(f"❌ Execution error: {e}")
    else:
        print("❌ No tool calls found in response")

if __name__ == "__main__":
    print("🚀 Simple Bash Test")
    print("=" * 60)
    
    test_simple_bash()
    test_tool_call_format()
    
    print("\n🎉 Simple tests completed!")
    print("\nThis shows us if bash commands work and tool call parsing works.")
