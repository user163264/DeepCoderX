"""
Quick Fix: Enhanced DualModelHandler with Direct Bash Execution

This patch adds direct bash command execution to bypass the MCP client dependency
for simple bash commands, which is the main tool being used.
"""

import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List

def patch_dual_model_handler():
    """Apply a quick patch to fix tool execution in dual model handler."""
    
    # Read the current dual model handler
    handler_path = Path("/Users/admin/Documents/DeepCoderX/services/dual_model_handler.py")
    
    with open(handler_path, 'r') as f:
        content = f.read()
    
    # Define the enhanced tool execution method
    enhanced_execute_tool_calls = '''    def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]], original_response: str) -> None:
        """Execute tool calls and update context - Enhanced with direct bash execution."""
        if self.debug_mode:
            log_info("DualModel", f"Executing {len(tool_calls)} tool calls")
        
        # Add original response to context
        self.context_manager.add_assistant_message(original_response)
        
        # Execute tools
        tool_results = []
        for tool_call in tool_calls:
            try:
                # ENHANCED: Direct bash execution for run_bash commands
                if tool_call.get("tool") == "run_bash":
                    result = self._execute_bash_directly(tool_call)
                else:
                    # Use regular tool executor for other tools
                    result = self.tool_executor.execute_tool(tool_call)
                
                tool_results.append(result)
                
                if self.debug_mode:
                    log_debug("DualModel", f"Tool executed: {tool_call.get('tool', 'unknown')} -> {str(result)[:100]}")
            
            except Exception as e:
                error_result = f"Tool execution error: {str(e)}"
                tool_results.append(error_result)
                
                if self.debug_mode:
                    log_error("DualModel", f"Tool execution error for {tool_call.get('tool', 'unknown')}", e)
        
        # Add results to context
        if tool_results:
            combined_results = "\\\\n\\\\n".join([f"Tool result: {result}" for result in tool_results])
            self.context_manager.add_tool_message(combined_results)
            
            # CRITICAL FIX: Set the tool results as the final response for the user
            # For simple commands, the tool output should be the response
            if len(tool_results) == 1:
                # Single tool result - show directly
                self.ctx.response = str(tool_results[0])
            else:
                # Multiple tool results - format nicely
                formatted_results = []
                for i, result in enumerate(tool_results, 1):
                    formatted_results.append(f"Result {i}: {result}")
                self.ctx.response = "\\n".join(formatted_results)
            
            if self.debug_mode:
                log_debug("DualModel", f"Set final response: {self.ctx.response[:100]}...")
    
    def _execute_bash_directly(self, tool_call: Dict[str, Any]) -> str:
        """Execute bash command directly without MCP client dependency."""
        command = tool_call.get("command")
        if not command:
            return "❌ Error: No command specified in bash tool call"
        
        try:
            if self.debug_mode:
                log_debug("DualModel", f"Executing bash command directly: {command}")
            
            process = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,  # 30 second timeout
                cwd=self.ctx.root_path if hasattr(self.ctx, 'root_path') else Path.cwd()
            )
            
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            if process.returncode == 0:
                if stdout:
                    return f"✅ Command executed successfully:\\n{stdout}"
                else:
                    return "✅ Command executed successfully (no output)"
            else:
                if stderr:
                    return f"❌ Command failed (exit code {process.returncode}):\\n{stderr}"
                else:
                    return f"❌ Command failed (exit code {process.returncode})"
                
        except subprocess.TimeoutExpired:
            return f"❌ Command '{command}' timed out after 30 seconds"
        except Exception as e:
            return f"❌ Failed to execute command '{command}': {str(e)}"'''
    
    # Find the current _execute_tool_calls method and replace it
    import re
    
    # Pattern to match the entire _execute_tool_calls method
    pattern = r'    def _execute_tool_calls\(self, tool_calls: List\[Dict\[str, Any\]\], original_response: str\) -> None:.*?(?=\n    def |\n\n    def |\nclass |\n# |$)'
    
    # Replace the method
    new_content = re.sub(pattern, enhanced_execute_tool_calls, content, flags=re.DOTALL)
    
    # Add the direct bash execution method after the enhanced _execute_tool_calls
    new_content = new_content.replace(
        enhanced_execute_tool_calls,
        enhanced_execute_tool_calls + "\n" + '''    def _execute_bash_directly(self, tool_call: Dict[str, Any]) -> str:
        """Execute bash command directly without MCP client dependency."""
        command = tool_call.get("command")
        if not command:
            return "❌ Error: No command specified in bash tool call"
        
        try:
            if self.debug_mode:
                log_debug("DualModel", f"Executing bash command directly: {command}")
            
            process = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,  # 30 second timeout
                cwd=self.ctx.root_path if hasattr(self.ctx, 'root_path') else Path.cwd()
            )
            
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            if process.returncode == 0:
                if stdout:
                    return f"✅ Command executed successfully:\\n{stdout}"
                else:
                    return "✅ Command executed successfully (no output)"
            else:
                if stderr:
                    return f"❌ Command failed (exit code {process.returncode}):\\n{stderr}"
                else:
                    return f"❌ Command failed (exit code {process.returncode})"
                
        except subprocess.TimeoutExpired:
            return f"❌ Command '{command}' timed out after 30 seconds"
        except Exception as e:
            return f"❌ Failed to execute command '{command}': {str(e)}"
'''
    )
    
    # Add subprocess import at the top if not already there
    if "import subprocess" not in new_content:
        new_content = new_content.replace(
            "import json\nimport time",
            "import json\nimport subprocess\nimport time"
        )
    
    return new_content

if __name__ == "__main__":
    print("🔧 Applying Quick Fix for Tool Execution")
    print("=" * 50)
    
    try:
        # Create backup
        handler_path = Path("/Users/admin/Documents/DeepCoderX/services/dual_model_handler.py")
        backup_path = handler_path.with_suffix(".py.backup_tool_fix")
        
        print(f"📄 Creating backup: {backup_path.name}")
        with open(handler_path, 'r') as f:
            backup_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        
        # Apply patch
        print("🔧 Applying enhanced tool execution patch...")
        new_content = patch_dual_model_handler()
        
        # Write the fixed version
        with open(handler_path, 'w') as f:
            f.write(new_content)
        
        print("✅ Quick fix applied successfully!")
        print("\n📋 Changes made:")
        print("1. Added direct bash command execution")
        print("2. Bypasses MCP client dependency for run_bash commands") 
        print("3. Maintains all existing functionality")
        print("4. Proper error handling and timeouts")
        
        print("\n🧪 Test commands now:")
        print("- pwd")
        print("- ls") 
        print("- git status")
        print("- create a Python script")
        
    except Exception as e:
        print(f"❌ Failed to apply quick fix: {e}")
        import traceback
        traceback.print_exc()
