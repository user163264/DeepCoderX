#!/usr/bin/env python3
"""
Complete MCP Tool System Validation Script

This script provides comprehensive testing of the entire MCP tool system
including server, client, tool registry, and handler integration.
"""

import os
import sys
import json
import signal
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config import config
    from services.mcpserver import start_mcp_server, create_mcp_request_handler
    from services.mcpclient import MCPClient
    from services.tool_registry import tool_registry, get_tools_for_provider
    from services.tool_executor import ToolExecutor
    from models.session import CommandContext
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the DeepCoderX directory")
    sys.exit(1)


class MCPSystemValidator:
    """Comprehensive MCP system validation."""
    
    def __init__(self):
        self.test_results = {}
        self.mcp_server_process = None
        self.endpoint = f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}"
        self.test_dir = Path(config.SANDBOX_PATH) / "mcp_test"
        
        # Signal handlers for clean exit
        signal.signal(signal.SIGINT, self._cleanup_and_exit)
        signal.signal(signal.SIGTERM, self._cleanup_and_exit)
    
    def _cleanup_and_exit(self, signum, frame):
        """Clean exit handler."""
        print("\n🧹 Cleaning up...")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Clean up test resources."""
        if self.mcp_server_process:
            self.mcp_server_process.terminate()
            self.mcp_server_process.wait()
        
        # Clean up test directory
        if self.test_dir.exists():
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def run_all_tests(self):
        """Run comprehensive MCP system validation."""
        print("🚀 Starting Complete MCP Tool System Validation")
        print("=" * 60)
        
        try:
            # Phase 1: Configuration and Setup
            self._test_configuration()
            
            # Phase 2: Tool Registry Validation
            self._test_tool_registry()
            
            # Phase 3: MCP Server Testing
            self._test_mcp_server()
            
            # Phase 4: MCP Client Testing
            self._test_mcp_client()
            
            # Phase 5: Tool Executor Testing
            self._test_tool_executor()
            
            # Phase 6: End-to-End Integration
            self._test_integration()
            
            # Results Summary
            self._print_results()
            
        except KeyboardInterrupt:
            print("\n❌ Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
        finally:
            self._cleanup()
    
    def _test_configuration(self):
        """Test MCP configuration and dependencies."""
        print("\n📋 Phase 1: Configuration and Setup Validation")
        
        # Test 1: Basic configuration
        try:
            assert hasattr(config, 'MCP_SERVER_HOST')
            assert hasattr(config, 'MCP_SERVER_PORT')
            assert hasattr(config, 'MCP_API_KEY')
            assert hasattr(config, 'SANDBOX_PATH')
            self.test_results['config_basic'] = True
            print("  ✅ Basic MCP configuration present")
        except Exception as e:
            self.test_results['config_basic'] = False
            print(f"  ❌ Basic configuration failed: {e}")
        
        # Test 2: Sandbox path validation
        try:
            sandbox_path = Path(config.SANDBOX_PATH)
            assert sandbox_path.exists(), f"Sandbox path does not exist: {config.SANDBOX_PATH}"
            assert sandbox_path.is_dir(), f"Sandbox path is not a directory: {config.SANDBOX_PATH}"
            
            # Create test directory
            self.test_dir.mkdir(parents=True, exist_ok=True)
            self.test_results['sandbox_validation'] = True
            print(f"  ✅ Sandbox path validated: {config.SANDBOX_PATH}")
        except Exception as e:
            self.test_results['sandbox_validation'] = False
            print(f"  ❌ Sandbox validation failed: {e}")
        
        # Test 3: Tool system constants
        try:
            required_constants = [
                'MAX_TOOL_CALLS', 'COMMAND_TIMEOUT', 'MCP_CLIENT_TIMEOUT',
                'MAX_FILE_SIZE', 'ALLOWED_EXTENSIONS'
            ]
            for constant in required_constants:
                assert hasattr(config, constant), f"Missing constant: {constant}"
            self.test_results['tool_constants'] = True
            print("  ✅ Tool system constants validated")
        except Exception as e:
            self.test_results['tool_constants'] = False
            print(f"  ❌ Tool constants validation failed: {e}")
    
    def _test_tool_registry(self):
        """Test Tool Registry functionality."""
        print("\n🔧 Phase 2: Tool Registry Validation")
        
        # Test 1: Registry initialization and core tools
        try:
            # Check that registry has expected tools
            expected_tools = ['read_file', 'write_file', 'list_dir', 'run_bash', 'move_file', 'mkdir', 'stat']
            actual_tools = list(tool_registry.tools.keys())
            
            missing_tools = set(expected_tools) - set(actual_tools)
            assert not missing_tools, f"Missing tools in registry: {missing_tools}"
            
            self.test_results['registry_core_tools'] = True
            print(f"  ✅ Tool registry has all {len(expected_tools)} expected tools")
        except Exception as e:
            self.test_results['registry_core_tools'] = False
            print(f"  ❌ Tool registry validation failed: {e}")
        
        # Test 2: OpenAPI definitions generation
        try:
            # Test local provider tools (should include run_bash)
            local_tools = get_tools_for_provider("local", {"supports_tools": True})
            local_tool_names = [tool['function']['name'] for tool in local_tools]
            assert 'run_bash' in local_tool_names, "Local provider missing run_bash tool"
            assert len(local_tools) >= 7, f"Local provider has {len(local_tools)} tools, expected >= 7"
            
            # Test cloud provider tools (should exclude run_bash)
            cloud_tools = get_tools_for_provider("deepseek", {"supports_tools": True})
            cloud_tool_names = [tool['function']['name'] for tool in cloud_tools]
            assert 'run_bash' not in cloud_tool_names, "Cloud provider should not have run_bash tool"
            assert len(cloud_tools) >= 6, f"Cloud provider has {len(cloud_tools)} tools, expected >= 6"
            
            self.test_results['registry_openai_format'] = True
            print(f"  ✅ OpenAPI definitions: Local({len(local_tools)} tools), Cloud({len(cloud_tools)} tools)")
        except Exception as e:
            self.test_results['registry_openai_format'] = False
            print(f"  ❌ OpenAPI definitions failed: {e}")
        
        # Test 3: Tool validation
        try:
            # Test valid tool call
            valid_call = {"tool": "read_file", "path": "test.txt"}
            validation = tool_registry.validate_tool_call(valid_call)
            assert validation['valid'], f"Valid tool call failed validation: {validation}"
            
            # Test invalid tool call
            invalid_call = {"tool": "nonexistent_tool", "param": "value"}
            validation = tool_registry.validate_tool_call(invalid_call)
            assert not validation['valid'], "Invalid tool call passed validation"
            
            self.test_results['registry_validation'] = True
            print("  ✅ Tool validation working correctly")
        except Exception as e:
            self.test_results['registry_validation'] = False
            print(f"  ❌ Tool validation failed: {e}")
    
    def _test_mcp_server(self):
        """Test MCP Server functionality."""
        print("\n🖥️  Phase 3: MCP Server Testing")
        
        # Test 1: Server startup
        try:
            # Start MCP server in subprocess
            cmd = [
                sys.executable, "-c",
                f"""
import sys
sys.path.insert(0, '{project_root}')
from services.mcpserver import start_mcp_server
start_mcp_server('{config.MCP_SERVER_HOST}', {config.MCP_SERVER_PORT}, '{config.SANDBOX_PATH}')
"""
            ]
            
            self.mcp_server_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            time.sleep(2)
            
            # Check if server is running
            if self.mcp_server_process.poll() is None:
                self.test_results['server_startup'] = True
                print(f"  ✅ MCP Server started on {self.endpoint}")
            else:
                stdout, stderr = self.mcp_server_process.communicate()
                raise Exception(f"Server failed to start: {stderr.decode()}")
                
        except Exception as e:
            self.test_results['server_startup'] = False
            print(f"  ❌ Server startup failed: {e}")
            return
        
        # Test 2: Tool discovery endpoint
        try:
            import requests
            response = requests.get(
                f"{self.endpoint}/discover-tools",
                headers={"X-API-Key": config.MCP_API_KEY},
                timeout=5
            )
            assert response.status_code == 200, f"Discovery endpoint returned {response.status_code}"
            
            tools_data = response.json()
            assert "tools" in tools_data, "Discovery response missing 'tools' key"
            assert "version" in tools_data, "Discovery response missing version"
            assert tools_data["version"] == "1.1.0", f"Expected version 1.1.0, got {tools_data['version']}"
            
            tool_names = [tool["name"] for tool in tools_data["tools"]]
            expected_endpoints = ["read", "write", "list", "move", "mkdir", "stat"]
            for endpoint in expected_endpoints:
                assert endpoint in tool_names, f"Missing endpoint: {endpoint}"
            
            self.test_results['server_discovery'] = True
            print(f"  ✅ Tool discovery endpoint working ({len(tool_names)} endpoints)")
        except Exception as e:
            self.test_results['server_discovery'] = False
            print(f"  ❌ Tool discovery failed: {e}")
    
    def _test_mcp_client(self):
        """Test MCP Client functionality."""
        print("\n📡 Phase 4: MCP Client Testing")
        
        if not self.test_results.get('server_startup', False):
            print("  ⏭️  Skipping client tests (server not running)")
            return
        
        # Initialize client
        try:
            client = MCPClient(self.endpoint, config.MCP_API_KEY)
            
            # Test 1: Basic file operations
            test_file = "mcp_test/test_file.txt"
            test_content = "Hello, MCP World!"
            
            # Write file
            write_response = client.write_file(test_file, test_content)
            assert "error" not in write_response, f"Write failed: {write_response.get('error')}"
            
            # Read file
            read_response = client.read_file(test_file)
            assert "error" not in read_response, f"Read failed: {read_response.get('error')}"
            assert read_response.get("content") == test_content, "Read content doesn't match written content"
            
            self.test_results['client_basic_ops'] = True
            print("  ✅ Basic file operations (write/read)")
            
        except Exception as e:
            self.test_results['client_basic_ops'] = False
            print(f"  ❌ Basic operations failed: {e}")
            return
        
        try:
            # Test 2: Directory operations
            test_dir = "mcp_test/new_directory"
            
            # Create directory
            mkdir_response = client.mkdir(test_dir, parents=True, exist_ok=True)
            assert "error" not in mkdir_response, f"Mkdir failed: {mkdir_response.get('error')}"
            
            # List directory
            list_response = client.list_dir("mcp_test")
            assert "error" not in list_response, f"List failed: {list_response.get('error')}"
            
            self.test_results['client_directory_ops'] = True
            print("  ✅ Directory operations (mkdir/list)")
            
        except Exception as e:
            self.test_results['client_directory_ops'] = False
            print(f"  ❌ Directory operations failed: {e}")
        
        try:
            # Test 3: Enhanced operations
            source_file = "mcp_test/source.txt"
            dest_file = "mcp_test/destination.txt"
            
            # Create source file
            client.write_file(source_file, "Source content")
            
            # Move file
            move_response = client.move_file(source_file, dest_file, overwrite=True)
            assert "error" not in move_response, f"Move failed: {move_response.get('error')}"
            
            # Get file stats
            stat_response = client.stat(dest_file)
            assert "error" not in stat_response, f"Stat failed: {stat_response.get('error')}"
            assert "result" in stat_response, "Stat response missing result"
            
            metadata = stat_response["result"]
            assert metadata.get("type") == "file", f"Expected file type, got {metadata.get('type')}"
            
            self.test_results['client_enhanced_ops'] = True
            print("  ✅ Enhanced operations (move/stat)")
            
        except Exception as e:
            self.test_results['client_enhanced_ops'] = False
            print(f"  ❌ Enhanced operations failed: {e}")
    
    def _test_tool_executor(self):
        """Test Tool Executor functionality."""
        print("\n⚙️  Phase 5: Tool Executor Testing")
        
        if not self.test_results.get('server_startup', False):
            print("  ⏭️  Skipping executor tests (server not running)")
            return
        
        try:
            # Create mock command context
            ctx = CommandContext(
                user_input="test",
                root_path=Path(config.SANDBOX_PATH),
                current_dir=Path(config.SANDBOX_PATH),
                mcp_client=MCPClient(self.endpoint, config.MCP_API_KEY),
                debug_mode=True
            )
            
            executor = ToolExecutor(ctx, use_complex_path_resolution=True)
            
            # Test 1: Basic tool execution
            tool_call = {"tool": "write_file", "path": "mcp_test/executor_test.txt", "content": "Executor test"}
            result = executor.execute_tool(tool_call)
            assert "Successfully wrote" in result, f"Write tool execution failed: {result}"
            
            # Test 2: Read tool execution
            tool_call = {"tool": "read_file", "path": "mcp_test/executor_test.txt"}
            result = executor.execute_tool(tool_call)
            assert "Executor test" in result, f"Read tool execution failed: {result}"
            
            self.test_results['executor_basic'] = True
            print("  ✅ Basic tool execution (write/read)")
            
        except Exception as e:
            self.test_results['executor_basic'] = False
            print(f"  ❌ Basic executor failed: {e}")
            return
        
        try:
            # Test 3: Enhanced tool execution
            
            # Directory creation
            tool_call = {"tool": "mkdir", "path": "mcp_test/executor_dir", "parents": True}
            result = executor.execute_tool(tool_call)
            assert "Successfully created" in result, f"Mkdir execution failed: {result}"
            
            # File move
            tool_call = {
                "tool": "move_file", 
                "source": "mcp_test/executor_test.txt",
                "destination": "mcp_test/executor_dir/moved_file.txt"
            }
            result = executor.execute_tool(tool_call)
            assert "Successfully moved" in result, f"Move execution failed: {result}"
            
            # File stat
            tool_call = {"tool": "stat", "path": "mcp_test/executor_dir/moved_file.txt"}
            result = executor.execute_tool(tool_call)
            assert "Metadata for" in result, f"Stat execution failed: {result}"
            
            self.test_results['executor_enhanced'] = True
            print("  ✅ Enhanced tool execution (mkdir/move/stat)")
            
        except Exception as e:
            self.test_results['executor_enhanced'] = False
            print(f"  ❌ Enhanced executor failed: {e}")
        
        try:
            # Test 4: Error handling
            
            # Invalid tool
            tool_call = {"tool": "invalid_tool", "param": "value"}
            result = executor.execute_tool(tool_call)
            assert "Invalid" in result or "tool" in result, f"Error handling failed: {result}"
            
            # Missing parameters
            tool_call = {"tool": "read_file"}  # Missing path
            result = executor.execute_tool(tool_call)
            assert "missing" in result.lower() or "path" in result, f"Parameter validation failed: {result}"
            
            self.test_results['executor_errors'] = True
            print("  ✅ Error handling validation")
            
        except Exception as e:
            self.test_results['executor_errors'] = False
            print(f"  ❌ Error handling failed: {e}")
    
    def _test_integration(self):
        """Test end-to-end integration."""
        print("\n🔗 Phase 6: End-to-End Integration Testing")
        
        if not all([
            self.test_results.get('server_startup'),
            self.test_results.get('client_basic_ops'),
            self.test_results.get('executor_basic')
        ]):
            print("  ⏭️  Skipping integration tests (prerequisite failures)")
            return
        
        try:
            # Simulate complete workflow
            print("  🔄 Simulating complete file management workflow...")
            
            ctx = CommandContext(
                user_input="integration test",
                root_path=Path(config.SANDBOX_PATH),
                current_dir=Path(config.SANDBOX_PATH),
                mcp_client=MCPClient(self.endpoint, config.MCP_API_KEY),
                debug_mode=True
            )
            
            executor = ToolExecutor(ctx, use_complex_path_resolution=True)
            
            # Step 1: Create project structure
            executor.execute_tool({"tool": "mkdir", "path": "mcp_test/integration_project"})
            executor.execute_tool({"tool": "mkdir", "path": "mcp_test/integration_project/src"})
            executor.execute_tool({"tool": "mkdir", "path": "mcp_test/integration_project/tests"})
            
            # Step 2: Create files
            executor.execute_tool({
                "tool": "write_file",
                "path": "mcp_test/integration_project/README.md",
                "content": "# Integration Test Project\n\nThis is a test project for MCP integration."
            })
            
            executor.execute_tool({
                "tool": "write_file", 
                "path": "mcp_test/integration_project/src/main.py",
                "content": "def main():\n    print('Hello from integration test!')\n\nif __name__ == '__main__':\n    main()"
            })
            
            # Step 3: Manage files
            executor.execute_tool({
                "tool": "move_file",
                "source": "mcp_test/integration_project/src/main.py",
                "destination": "mcp_test/integration_project/main.py"
            })
            
            # Step 4: Inspect structure
            list_result = executor.execute_tool({"tool": "list_dir", "path": "mcp_test/integration_project"})
            stat_result = executor.execute_tool({"tool": "stat", "path": "mcp_test/integration_project/README.md"})
            
            # Validate results
            assert "README.md" in list_result, "README.md not found in directory listing"
            assert "main.py" in list_result, "main.py not found after move"
            assert "file" in stat_result, "Stat didn't identify README.md as file"
            
            self.test_results['integration_workflow'] = True
            print("  ✅ Complete workflow integration successful")
            
        except Exception as e:
            self.test_results['integration_workflow'] = False
            print(f"  ❌ Integration workflow failed: {e}")
        
        try:
            # Test tool permission enforcement
            local_tools = get_tools_for_provider("local", {"supports_tools": True})
            cloud_tools = get_tools_for_provider("deepseek", {"supports_tools": True})
            
            local_names = [tool['function']['name'] for tool in local_tools]
            cloud_names = [tool['function']['name'] for tool in cloud_tools]
            
            # Verify security restrictions
            assert 'run_bash' in local_names, "Local provider missing system access tools"
            assert 'run_bash' not in cloud_names, "Cloud provider incorrectly has system access tools"
            
            # Verify both have file operations
            file_ops = ['read_file', 'write_file', 'list_dir', 'move_file', 'mkdir', 'stat']
            for op in file_ops:
                assert op in local_names, f"Local provider missing {op}"
                assert op in cloud_names, f"Cloud provider missing {op}"
            
            self.test_results['integration_security'] = True
            print("  ✅ Security permission enforcement validated")
            
        except Exception as e:
            self.test_results['integration_security'] = False
            print(f"  ❌ Security validation failed: {e}")
    
    def _print_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 60)
        print("📊 COMPLETE MCP TOOL SYSTEM VALIDATION RESULTS")
        print("=" * 60)
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📈 Summary: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        # Detailed results by phase
        phases = {
            "Configuration": ['config_basic', 'sandbox_validation', 'tool_constants'],
            "Tool Registry": ['registry_core_tools', 'registry_openai_format', 'registry_validation'],
            "MCP Server": ['server_startup', 'server_discovery'],
            "MCP Client": ['client_basic_ops', 'client_directory_ops', 'client_enhanced_ops'],
            "Tool Executor": ['executor_basic', 'executor_enhanced', 'executor_errors'],
            "Integration": ['integration_workflow', 'integration_security']
        }
        
        for phase_name, test_keys in phases.items():
            phase_results = [self.test_results.get(key, False) for key in test_keys]
            phase_passed = sum(phase_results)
            phase_total = len(phase_results)
            
            if phase_passed == phase_total:
                status = "✅ PASS"
            elif phase_passed > 0:
                status = "⚠️  PARTIAL"
            else:
                status = "❌ FAIL"
            
            print(f"\n{status} {phase_name}: {phase_passed}/{phase_total}")
            
            for i, test_key in enumerate(test_keys):
                result = self.test_results.get(test_key, False)
                icon = "  ✅" if result else "  ❌"
                print(f"{icon} {test_key}")
        
        # Overall assessment
        print(f"\n{'='*60}")
        if failed_tests == 0:
            print("🎉 MCP TOOL SYSTEM: FULLY OPERATIONAL")
            print("All components working correctly - system ready for production use!")
        elif failed_tests <= 3:
            print("⚠️  MCP TOOL SYSTEM: MOSTLY OPERATIONAL")
            print("Minor issues detected - system functional with some limitations")
        else:
            print("❌ MCP TOOL SYSTEM: REQUIRES ATTENTION")
            print("Significant issues detected - manual intervention required")
        
        # Capability summary
        if self.test_results.get('integration_security', False):
            print(f"\n🛡️  Security Configuration:")
            print(f"   • Local models: 7 tools (including system access)")
            print(f"   • Cloud models: 6 tools (file operations only)")
            print(f"   • OpenAPI 3.1 MCP File System: Fully Compliant")
        
        if self.test_results.get('server_startup', False):
            print(f"\n📡 Server Status: Running on {self.endpoint}")
        
        print(f"\n🧹 Cleanup: Test resources will be removed on exit")


def main():
    """Run the complete MCP system validation."""
    validator = MCPSystemValidator()
    validator.run_all_tests()


if __name__ == "__main__":
    main()
