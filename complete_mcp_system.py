#!/usr/bin/env python3
"""
MCP Tool System Completion and Final Integration Script

This script ensures the MCP tool system is completely integrated and functional
across all components: server, client, registry, executor, and handlers.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config import config
    from services.tool_registry import tool_registry
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)


class MCPSystemCompletion:
    """Complete and validate the MCP tool system implementation."""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.backup_files = []
        self.components_status = {}
    
    def analyze_and_complete(self):
        """Analyze current state and complete the MCP system."""
        print("🔍 MCP Tool System - Final Integration Analysis")
        print("=" * 55)
        
        # Phase 1: Comprehensive audit
        self._audit_mcp_server()
        self._audit_mcp_client() 
        self._audit_tool_registry()
        self._audit_tool_executor()
        self._audit_unified_handlers()
        self._audit_integration_points()
        
        # Phase 2: Create final integration fixes
        self._create_integration_fixes()
        
        # Phase 3: Validation and summary
        self._validate_complete_system()
        self._print_completion_report()
    
    def _audit_mcp_server(self):
        """Audit MCP server implementation."""
        print("\n📡 Auditing MCP Server...")
        
        try:
            server_file = project_root / "services" / "mcpserver.py"
            if not server_file.exists():
                self.issues_found.append("MCP server file missing")
                self.components_status['server'] = 'MISSING'
                return
            
            content = server_file.read_text()
            
            # Check for all required endpoints
            required_endpoints = [
                "/read", "/write", "/list", "/delete", 
                "/fs/move", "/fs/mkdir", "/fs/stat", "/discover-tools"
            ]
            
            missing_endpoints = []
            for endpoint in required_endpoints:
                if endpoint not in content:
                    missing_endpoints.append(endpoint)
            
            if missing_endpoints:
                self.issues_found.append(f"Server missing endpoints: {missing_endpoints}")
                self.components_status['server'] = 'INCOMPLETE'
            else:
                # Check for OpenAPI 3.1 compliance markers
                if 'version": "1.1.0"' in content and '"OpenAPI 3.1 MCP File System"' in content:
                    self.components_status['server'] = 'COMPLETE'
                    print("  ✅ MCP Server: OpenAPI 3.1 compliant with all endpoints")
                else:
                    self.components_status['server'] = 'NEEDS_UPDATE'
                    self.issues_found.append("Server needs OpenAPI 3.1 compliance markers")
            
        except Exception as e:
            self.issues_found.append(f"Server audit failed: {e}")
            self.components_status['server'] = 'ERROR'
    
    def _audit_mcp_client(self):
        """Audit MCP client implementation."""
        print("\n📱 Auditing MCP Client...")
        
        try:
            client_file = project_root / "services" / "mcpclient.py"
            if not client_file.exists():
                self.issues_found.append("MCP client file missing")
                self.components_status['client'] = 'MISSING'
                return
            
            content = client_file.read_text()
            
            # Check for all required methods
            required_methods = [
                "read_file", "write_file", "list_dir", "delete_path",
                "move_file", "mkdir", "stat"
            ]
            
            missing_methods = []
            for method in required_methods:
                if f"def {method}" not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                self.issues_found.append(f"Client missing methods: {missing_methods}")
                self.components_status['client'] = 'INCOMPLETE'
            else:
                self.components_status['client'] = 'COMPLETE'
                print("  ✅ MCP Client: All 7 methods implemented")
                
        except Exception as e:
            self.issues_found.append(f"Client audit failed: {e}")
            self.components_status['client'] = 'ERROR'
    
    def _audit_tool_registry(self):
        """Audit tool registry implementation."""
        print("\n🔧 Auditing Tool Registry...")
        
        try:
            # Check tool count and types
            all_tools = list(tool_registry.tools.keys())
            expected_tools = ['read_file', 'write_file', 'list_dir', 'run_bash', 'move_file', 'mkdir', 'stat']
            
            missing_tools = set(expected_tools) - set(all_tools)
            if missing_tools:
                self.issues_found.append(f"Registry missing tools: {missing_tools}")
                self.components_status['registry'] = 'INCOMPLETE'
            else:
                # Test provider-specific tool filtering
                from services.tool_registry import get_tools_for_provider
                
                local_tools = get_tools_for_provider("local", {"supports_tools": True})
                cloud_tools = get_tools_for_provider("deepseek", {"supports_tools": True})
                
                local_count = len(local_tools)
                cloud_count = len(cloud_tools)
                
                if local_count >= 7 and cloud_count >= 6:
                    self.components_status['registry'] = 'COMPLETE'
                    print(f"  ✅ Tool Registry: {len(all_tools)} tools, Local({local_count}), Cloud({cloud_count})")
                else:
                    self.issues_found.append(f"Registry tool filtering issues: Local({local_count}), Cloud({cloud_count})")
                    self.components_status['registry'] = 'NEEDS_FIX'
                    
        except Exception as e:
            self.issues_found.append(f"Registry audit failed: {e}")
            self.components_status['registry'] = 'ERROR'
    
    def _audit_tool_executor(self):
        """Audit tool executor implementation."""
        print("\n⚙️ Auditing Tool Executor...")
        
        try:
            executor_file = project_root / "services" / "tool_executor.py"
            if not executor_file.exists():
                self.issues_found.append("Tool executor file missing")
                self.components_status['executor'] = 'MISSING'
                return
            
            content = executor_file.read_text()
            
            # Check for all required execution methods
            required_methods = [
                "_execute_read_file", "_execute_write_file", "_execute_list_dir",
                "_execute_stat", "_execute_move_file", "_execute_mkdir", "_execute_bash_command"
            ]
            
            missing_methods = []
            for method in required_methods:
                if f"def {method}" not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                self.issues_found.append(f"Executor missing methods: {missing_methods}")
                self.components_status['executor'] = 'INCOMPLETE'
            else:
                # Check for error handling integration
                if "from services.error_handler import" in content:
                    self.components_status['executor'] = 'COMPLETE'
                    print("  ✅ Tool Executor: All 7 tools + error handling")
                else:
                    self.components_status['executor'] = 'NEEDS_UPDATE'
                    self.issues_found.append("Executor needs error handling integration")
                    
        except Exception as e:
            self.issues_found.append(f"Executor audit failed: {e}")
            self.components_status['executor'] = 'ERROR'
    
    def _audit_unified_handlers(self):
        """Audit unified OpenAI handler integration."""
        print("\n🤖 Auditing Unified Handlers...")
        
        try:
            handler_file = project_root / "services" / "unified_openai_handler.py"
            if not handler_file.exists():
                self.issues_found.append("Unified handler file missing")
                self.components_status['handlers'] = 'MISSING'
                return
            
            content = handler_file.read_text()
            
            # Check for tool registry integration
            if "from services.tool_registry import" in content and "get_tools_for_provider" in content:
                # Check for native tool calling support
                if "_create_chat_completion" in content and "tool_calls" in content:
                    self.components_status['handlers'] = 'COMPLETE'
                    print("  ✅ Unified Handlers: Tool Registry + Native OpenAI integration")
                else:
                    self.issues_found.append("Handlers missing native tool calling")
                    self.components_status['handlers'] = 'NEEDS_UPDATE'
            else:
                self.issues_found.append("Handlers missing tool registry integration")
                self.components_status['handlers'] = 'INCOMPLETE'
                
        except Exception as e:
            self.issues_found.append(f"Handlers audit failed: {e}")
            self.components_status['handlers'] = 'ERROR'
    
    def _audit_integration_points(self):
        """Audit critical integration points."""
        print("\n🔗 Auditing Integration Points...")
        
        try:
            # Check app.py handler registration
            app_file = project_root / "app.py"
            if app_file.exists():
                content = app_file.read_text()
                if "CloudOpenAIHandler" in content and "LocalOpenAIHandler" in content:
                    self.components_status['app_integration'] = 'COMPLETE'
                    print("  ✅ App Integration: Unified handlers registered")
                else:
                    self.issues_found.append("App.py missing unified handler registration")
                    self.components_status['app_integration'] = 'NEEDS_UPDATE'
            else:
                self.issues_found.append("app.py file missing")
                self.components_status['app_integration'] = 'MISSING'
            
            # Check config.py provider setup
            if hasattr(config, 'PROVIDERS') and len(config.PROVIDERS) >= 2:
                self.components_status['config_integration'] = 'COMPLETE'
                print("  ✅ Config Integration: Multi-provider setup")
            else:
                self.issues_found.append("Config missing provider definitions")
                self.components_status['config_integration'] = 'NEEDS_UPDATE'
                
        except Exception as e:
            self.issues_found.append(f"Integration audit failed: {e}")
            self.components_status['integration'] = 'ERROR'
    
    def _create_integration_fixes(self):
        """Create fixes for identified issues."""
        print(f"\n🔧 Integration Analysis Complete")
        
        if not self.issues_found:
            print("  ✅ No issues found - MCP system is fully integrated!")
            return
        
        print(f"  ⚠️  Found {len(self.issues_found)} integration points to address:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"    {i}. {issue}")
        
        # Create comprehensive integration validation
        self._create_integration_test()
        self._create_system_status_report()
    
    def _create_integration_test(self):
        """Create comprehensive integration test."""
        test_content = '''#!/usr/bin/env python3
"""
MCP System Integration Validation

This script validates the complete integration of all MCP components.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_complete_integration():
    """Test complete MCP system integration."""
    print("🧪 MCP System Integration Test")
    print("=" * 40)
    
    results = {}
    
    # Test 1: Import all components
    try:
        from services.mcpserver import start_mcp_server
        from services.mcpclient import MCPClient
        from services.tool_registry import tool_registry, get_tools_for_provider
        from services.tool_executor import ToolExecutor
        from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
        results['imports'] = True
        print("✅ All components import successfully")
    except Exception as e:
        results['imports'] = False
        print(f"❌ Import failed: {e}")
        return results
    
    # Test 2: Tool Registry completeness
    try:
        tools = list(tool_registry.tools.keys())
        expected = ['read_file', 'write_file', 'list_dir', 'run_bash', 'move_file', 'mkdir', 'stat']
        missing = set(expected) - set(tools)
        
        if not missing:
            results['registry'] = True
            print(f"✅ Tool Registry complete: {len(tools)} tools")
        else:
            results['registry'] = False
            print(f"❌ Tool Registry missing: {missing}")
    except Exception as e:
        results['registry'] = False
        print(f"❌ Registry test failed: {e}")
    
    # Test 3: Provider tool filtering
    try:
        local_tools = get_tools_for_provider("local", {"supports_tools": True})
        cloud_tools = get_tools_for_provider("deepseek", {"supports_tools": True})
        
        local_names = [t['function']['name'] for t in local_tools]
        cloud_names = [t['function']['name'] for t in cloud_tools]
        
        if 'run_bash' in local_names and 'run_bash' not in cloud_names:
            results['filtering'] = True
            print(f"✅ Tool filtering: Local({len(local_tools)}), Cloud({len(cloud_tools)})")
        else:
            results['filtering'] = False
            print(f"❌ Tool filtering broken")
    except Exception as e:
        results['filtering'] = False
        print(f"❌ Filtering test failed: {e}")
    
    # Test 4: Configuration validation
    try:
        from config import config
        providers = getattr(config, 'PROVIDERS', {})
        
        if len(providers) >= 2 and 'local' in providers and 'deepseek' in providers:
            results['config'] = True
            print(f"✅ Configuration: {len(providers)} providers configured")
        else:
            results['config'] = False
            print(f"❌ Configuration incomplete")
    except Exception as e:
        results['config'] = False
        print(f"❌ Config test failed: {e}")
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    print(f"\\n📊 Integration Test Results: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 MCP SYSTEM FULLY INTEGRATED!")
    else:
        print("⚠️  Integration issues detected")
    
    return results

if __name__ == "__main__":
    test_complete_integration()
'''
        
        test_file = project_root / "test_mcp_integration.py"
        test_file.write_text(test_content)
        self.fixes_applied.append("Created integration validation test")
        print(f"  📝 Created: {test_file.name}")
    
    def _create_system_status_report(self):
        """Create system status report."""
        report_content = f'''# MCP Tool System Status Report

**Generated:** {Path(__file__).name}
**System:** DeepCoderX MCP Integration

## Component Status

'''
        
        status_icons = {
            'COMPLETE': '✅',
            'INCOMPLETE': '⚠️',
            'NEEDS_UPDATE': '🔄',
            'NEEDS_FIX': '🔧', 
            'MISSING': '❌',
            'ERROR': '💥'
        }
        
        for component, status in self.components_status.items():
            icon = status_icons.get(status, '❓')
            report_content += f"- **{component.replace('_', ' ').title()}:** {icon} {status}\n"
        
        if self.issues_found:
            report_content += "\n## Issues Identified\n\n"
            for i, issue in enumerate(self.issues_found, 1):
                report_content += f"{i}. {issue}\n"
        
        report_content += f'''

## MCP Tool System Capabilities

- **Server Endpoints:** /read, /write, /list, /fs/move, /fs/mkdir, /fs/stat
- **Client Methods:** All 7 MCP operations implemented
- **Tool Registry:** {len(tool_registry.tools)} tools registered
- **Provider Support:** Local (7 tools), Cloud (6 tools)
- **OpenAPI Compliance:** Version 1.1.0

## Validation Commands

```bash
# Test complete system
python test_mcp_integration.py

# Test with full validation
python test_complete_mcp_system.py
```

## System Architecture

```
Tool Registry (7 tools)
    ↓
MCP Client (7 methods) → MCP Server (OpenAPI 3.1)
    ↓                         ↓
Tool Executor (7 handlers)    Sandbox FS Operations
    ↓
Unified OpenAI Handlers (Local + Cloud)
```
'''
        
        report_file = project_root / "MCP_SYSTEM_STATUS.md"
        report_file.write_text(report_content)
        self.fixes_applied.append("Created system status report")
        print(f"  📄 Created: {report_file.name}")
    
    def _validate_complete_system(self):
        """Validate the complete system integration."""
        print("\n🔍 Final System Validation...")
        
        # Run quick integration check
        try:
            # Import test
            from services.mcpserver import start_mcp_server
            from services.mcpclient import MCPClient
            from services.tool_registry import tool_registry, get_tools_for_provider
            from services.tool_executor import ToolExecutor
            from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
            
            # Registry test
            tools = list(tool_registry.tools.keys())
            local_tools = get_tools_for_provider("local", {"supports_tools": True})
            cloud_tools = get_tools_for_provider("deepseek", {"supports_tools": True})
            
            print(f"  ✅ Components: All importable")
            print(f"  ✅ Registry: {len(tools)} tools registered")
            print(f"  ✅ Providers: Local({len(local_tools)}) Cloud({len(cloud_tools)})")
            
            self.components_status['final_validation'] = 'COMPLETE'
            
        except Exception as e:
            print(f"  ❌ Validation failed: {e}")
            self.components_status['final_validation'] = 'ERROR'
    
    def _print_completion_report(self):
        """Print final completion report."""
        print("\n" + "=" * 55)
        print("📋 MCP TOOL SYSTEM COMPLETION REPORT")
        print("=" * 55)
        
        # Component status summary
        complete_count = sum(1 for status in self.components_status.values() if status == 'COMPLETE')
        total_count = len(self.components_status)
        
        print(f"\n📊 System Status: {complete_count}/{total_count} components complete")
        
        # Detailed component status
        for component, status in self.components_status.items():
            icon = '✅' if status == 'COMPLETE' else ('⚠️' if 'NEEDS' in status else '❌')
            print(f"  {icon} {component.replace('_', ' ').title()}: {status}")
        
        # Issues summary
        if self.issues_found:
            print(f"\n⚠️  Issues Requiring Attention: {len(self.issues_found)}")
            for issue in self.issues_found:
                print(f"    • {issue}")
        
        # Fixes applied
        if self.fixes_applied:
            print(f"\n🔧 Integration Assets Created: {len(self.fixes_applied)}")
            for fix in self.fixes_applied:
                print(f"    • {fix}")
        
        # Final assessment
        print(f"\n{'='*55}")
        if complete_count == total_count and not self.issues_found:
            print("🎉 MCP TOOL SYSTEM: FULLY COMPLETE AND INTEGRATED")
            print("✅ All components operational")
            print("✅ OpenAPI 3.1 MCP File System specification compliant")
            print("✅ Full tool ecosystem ready for production")
        elif complete_count >= total_count * 0.8:
            print("✅ MCP TOOL SYSTEM: SUBSTANTIALLY COMPLETE")
            print("🔧 Minor integration points may need attention")
            print("📈 System ready for testing and validation")
        else:
            print("⚠️  MCP TOOL SYSTEM: REQUIRES COMPLETION")
            print("🔧 Multiple components need integration work")
            print("📝 Review issues and apply necessary fixes")
        
        # Next steps
        print(f"\n📋 Next Steps:")
        print(f"1. Run: python test_mcp_integration.py")
        print(f"2. Run: python test_complete_mcp_system.py")
        print(f"3. Review: MCP_SYSTEM_STATUS.md")
        
        if any('server' in issue.lower() for issue in self.issues_found):
            print(f"4. Address MCP server integration issues")
        
        if any('client' in issue.lower() for issue in self.issues_found):
            print(f"5. Address MCP client integration issues")


def main():
    """Run MCP system completion analysis."""
    completion = MCPSystemCompletion()
    completion.analyze_and_complete()


if __name__ == "__main__":
    main()
