#!/usr/bin/env python3
"""
API Automation Example for DeepCoderX
Direct handler access for automated testing
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models.session import CommandContext
from services.dual_model_handler import DualModelHandler
from config_module import config


class DeepCoderXAPI:
    """
    Simple API wrapper for DeepCoderX automation.
    Provides programmatic access to all handlers.
    """
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.session_results = []
    
    def execute_command(self, command: str, provider: str = "dual", 
                       timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a command and return structured result.
        
        Args:
            command: Command to execute (e.g., "pwd", "create script")
            provider: Provider to use (dual, local, deepseek, openai)
            timeout: Maximum execution time in seconds
            
        Returns:
            Dict with response, timing, and metadata
        """
        start_time = time.time()
        
        try:
            # Create command context
            ctx = CommandContext(
                user_input=command,
                root_path=Path.cwd(),
                debug_mode=self.debug_mode
            )
            
            # Select handler based on provider
            if provider == "dual":
                handler = DualModelHandler(ctx, "dual")
            elif provider == "local":
                from services.gguf_handler import GGUFHandler
                handler = GGUFHandler(ctx, "local")
            elif provider in ["deepseek", "openai"]:
                from services.unified_openai_handler import UnifiedOpenAIHandler
                handler = UnifiedOpenAIHandler(ctx, provider)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            # Execute command
            if handler.can_handle():
                handler.handle()
                response = ctx.response or "No response generated"
                success = True
                error = None
            else:
                response = f"Handler cannot process command with provider {provider}"
                success = False
                error = "Handler rejection"
                
        except Exception as e:
            response = f"Error: {str(e)}"
            success = False
            error = str(e)
        
        execution_time = time.time() - start_time
        
        result = {
            "command": command,
            "provider": provider,
            "success": success,
            "response": response,
            "execution_time": execution_time,
            "error": error,
            "timestamp": time.time()
        }
        
        self.session_results.append(result)
        return result
    
    def batch_execute(self, commands: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Execute multiple commands in sequence.
        
        Args:
            commands: List of {"command": "...", "provider": "..."}
            
        Returns:
            List of execution results
        """
        results = []
        for cmd_info in commands:
            command = cmd_info["command"]
            provider = cmd_info.get("provider", "dual")
            result = self.execute_command(command, provider)
            results.append(result)
        
        return results
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all commands executed in this session."""
        if not self.session_results:
            return {"total": 0, "success_rate": 0, "avg_time": 0}
        
        total = len(self.session_results)
        successful = sum(1 for r in self.session_results if r["success"])
        total_time = sum(r["execution_time"] for r in self.session_results)
        
        return {
            "total_commands": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total,
            "average_execution_time": total_time / total,
            "total_time": total_time
        }
    
    def export_results(self, filename: str = None) -> str:
        """Export session results to JSON file."""
        if filename is None:
            filename = f"deepcoderx_test_results_{int(time.time())}.json"
        
        export_data = {
            "session_summary": self.get_session_summary(),
            "results": self.session_results,
            "config": {
                "debug_mode": self.debug_mode,
                "default_provider": config.DEFAULT_PROVIDER
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename


def run_test_suite():
    """Example automated test suite."""
    print("🚀 DeepCoderX API Automation Test Suite")
    print("=" * 50)
    
    api = DeepCoderXAPI(debug_mode=True)
    
    # Test commands
    test_commands = [
        {"command": "pwd", "provider": "dual"},
        {"command": "ls", "provider": "dual"},
        {"command": "hello", "provider": "dual"},
        {"command": "git status", "provider": "dual"},
        {"command": "whoami", "provider": "dual"}
    ]
    
    print("📝 Executing test commands...")
    results = api.batch_execute(test_commands)
    
    # Display results
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        time_str = f"{result['execution_time']:.3f}s"
        print(f"{status} Test {i}: '{result['command']}' -> {time_str}")
        if not result["success"]:
            print(f"   Error: {result['error']}")
    
    # Summary
    summary = api.get_session_summary()
    print(f"\n📊 Test Summary:")
    print(f"   Total: {summary['total_commands']}")
    print(f"   Success Rate: {summary['success_rate']:.1%}")
    print(f"   Average Time: {summary['average_execution_time']:.3f}s")
    
    # Export results
    filename = api.export_results()
    print(f"📁 Results exported to: {filename}")
    
    return summary


if __name__ == "__main__":
    # Run the test suite
    run_test_suite()
    
    # Example individual command
    print("\n🔧 Example individual command:")
    api = DeepCoderXAPI()
    result = api.execute_command("explain Python functions", "dual")
    print(f"Response: {result['response'][:100]}...")
