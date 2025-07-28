#!/usr/bin/env python3
"""
Phase 2 & Phase 3 Completion Verification Script

This script verifies that both Phase 2 (Tool Parsing Consolidation) and 
Phase 3 (MCP Client Enhancement) are fully implemented and functional.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from utils.logging import console
except ImportError:
    # Fallback console
    class MockConsole:
        def print(self, text, **kwargs):
            print(text.replace('[', '').replace(']', '').replace('/', ''))
    console = MockConsole()

def verify_phase2_structured_tools():
    """Verify Phase 2: Tool Parsing Consolidation."""
    console.print("[bold blue]🔍 Phase 2: Tool Parsing Consolidation Verification[/]")
    
    results = {"phase": "Phase 2", "status": "UNKNOWN", "issues": [], "details": []}
    
    try:
        # Check structured_tools.py migration
        from services import structured_tools
        
        # Verify it's a deprecation wrapper
        if hasattr(structured_tools, 'get_migration_status'):
            migration_status = structured_tools.get_migration_status()
            if migration_status.get("status") == "COMPLETED":
                results["details"].append("✅ structured_tools.py successfully migrated to deprecation wrapper")
                
                # Test legacy compatibility
                parser = structured_tools.StructuredToolParser()
                if hasattr(parser, 'KNOWN_TOOLS') and len(parser.KNOWN_TOOLS) > 0:
                    results["details"].append(f"✅ Legacy compatibility maintained with {len(parser.KNOWN_TOOLS)} tools")
                else:
                    results["issues"].append("❌ Legacy compatibility broken - no tools in KNOWN_TOOLS")
                
                results["status"] = "COMPLETED"
            else:
                results["issues"].append("❌ structured_tools.py migration status not completed")
        else:
            results["issues"].append("❌ structured_tools.py missing migration status method")
            
    except ImportError as e:
        results["issues"].append(f"❌ Cannot import structured_tools: {e}")
    except Exception as e:
        results["issues"].append(f"❌ Error checking structured_tools: {e}")
    
    # Verify Tool Registry is active
    try:
        from services.tool_registry import tool_registry
        
        tools = tool_registry.list_tools()
        if len(tools) >= 7:  # Should have all 7 OpenAPI 3.1 tools
            tool_names = [tool.name for tool in tools]
            expected_tools = ["read_file", "write_file", "list_dir", "move_file", "mkdir", "stat", "run_bash"]
            missing_tools = set(expected_tools) - set(tool_names)
            
            if not missing_tools:
                results["details"].append(f"✅ Tool Registry active with all {len(tools)} OpenAPI 3.1 tools")
            else:
                results["issues"].append(f"❌ Tool Registry missing tools: {', '.join(missing_tools)}")
        else:
            results["issues"].append(f"❌ Tool Registry has only {len(tools)} tools, expected 7")
            
    except Exception as e:
        results["issues"].append(f"❌ Tool Registry error: {e}")
    
    return results

def verify_phase3_mcp_client():
    """Verify Phase 3: MCP Client Enhancement."""
    console.print("[bold blue]🔍 Phase 3: MCP Client Enhancement Verification[/]")
    
    results = {"phase": "Phase 3", "status": "UNKNOWN", "issues": [], "details": []}
    
    try:
        # Check MCP Client enhancement
        from services import mcpclient
        from services.mcpclient import MCPClient
        
        # Verify migration status
        if hasattr(mcpclient, 'get_migration_status'):
            migration_status = mcpclient.get_migration_status()
            if migration_status.get("status") == "COMPLETED":
                results["details"].append("✅ MCP Client migration completed")
                
                # Check enhancements count
                enhancements = migration_status.get("enhancements", [])
                results["details"].append(f"✅ {len(enhancements)} enhancements implemented")
            else:
                results["issues"].append("❌ MCP Client migration status not completed")
        else:
            results["issues"].append("❌ MCP Client missing migration status method")
        
        # Verify error handling integration
        if hasattr(mcpclient, 'ErrorHandler'):
            results["details"].append("✅ Standardized error handling integrated")
        else:
            results["issues"].append("❌ ErrorHandler not imported in mcpclient")
        
        # Verify OpenAPI 3.1 methods
        client = MCPClient("http://test", "test_key")
        openapi_methods = ["move_file", "mkdir", "stat"]
        available_methods = []
        
        for method in openapi_methods:
            if hasattr(client, method):
                available_methods.append(method)
        
        if len(available_methods) == 3:
            results["details"].append(f"✅ All OpenAPI 3.1 methods available: {', '.join(available_methods)}")
        else:
            missing = set(openapi_methods) - set(available_methods)
            results["issues"].append(f"❌ Missing OpenAPI methods: {', '.join(missing)}")
        
        # Verify security validation
        if hasattr(client, '_validate_path'):
            results["details"].append("✅ Path security validation implemented")
        else:
            results["issues"].append("❌ Path security validation missing")
        
        if not results["issues"]:
            results["status"] = "COMPLETED"
            
    except Exception as e:
        results["issues"].append(f"❌ Error checking MCP Client: {e}")
    
    return results

def verify_tool_system_integration():
    """Verify overall tool system integration."""
    console.print("[bold blue]🔍 Tool System Integration Verification[/]")
    
    results = {"phase": "Integration", "status": "UNKNOWN", "issues": [], "details": []}
    
    try:
        # Verify Tool Executor has all execute methods
        from services.tool_executor import ToolExecutor
        
        expected_methods = ["_execute_read_file", "_execute_write_file", "_execute_list_dir", 
                          "_execute_stat", "_execute_move_file", "_execute_mkdir", "_execute_bash_command"]
        
        missing_methods = []
        for method in expected_methods:
            if not hasattr(ToolExecutor, method):
                missing_methods.append(method)
        
        if not missing_methods:
            results["details"].append(f"✅ Tool Executor has all {len(expected_methods)} execute methods")
        else:
            results["issues"].append(f"❌ Tool Executor missing methods: {', '.join(missing_methods)}")
        
        # Verify unified handlers exist
        from services.unified_openai_handler import CloudOpenAIHandler, LocalOpenAIHandler
        results["details"].append("✅ Unified OpenAI handlers available")
        
        # Check if app.py uses unified architecture
        app_file = project_root / "app.py"
        if app_file.exists():
            app_content = app_file.read_text()
            if "CloudOpenAIHandler" in app_content and "LocalOpenAIHandler" in app_content:
                results["details"].append("✅ app.py uses unified handler architecture")
            else:
                results["issues"].append("❌ app.py not using unified handlers")
        
        if not results["issues"]:
            results["status"] = "COMPLETED"
            
    except Exception as e:
        results["issues"].append(f"❌ Integration verification error: {e}")
    
    return results

def generate_completion_report(phase2_results, phase3_results, integration_results):
    """Generate final completion report."""
    console.print("[bold white]📊 Phase 2 & Phase 3 Completion Report[/]")
    console.print("")
    
    all_results = [phase2_results, phase3_results, integration_results]
    
    for result in all_results:
        phase_name = result["phase"]
        status = result["status"]
        
        if status == "COMPLETED":
            console.print(f"[bold green]✅ {phase_name}: COMPLETED[/]")
        else:
            console.print(f"[bold red]❌ {phase_name}: INCOMPLETE[/]")
        
        # Show details
        for detail in result["details"]:
            console.print(f"   {detail}")
        
        # Show issues
        for issue in result["issues"]:
            console.print(f"   {issue}")
        
        console.print("")
    
    # Overall status
    all_completed = all(r["status"] == "COMPLETED" for r in all_results)
    total_issues = sum(len(r["issues"]) for r in all_results)
    
    if all_completed and total_issues == 0:
        console.print("[bold green]🎉 SUCCESS: All Phase 2 & 3 implementations are COMPLETE![/]")
        console.print("[green]✅ Phase 2: Tool Parsing Consolidation - COMPLETED[/]")
        console.print("[green]✅ Phase 3: MCP Client Enhancement - COMPLETED[/]")
        console.print("[green]✅ Integration: Tool System Integration - COMPLETED[/]")
        console.print("")
        console.print("[bold cyan]🚀 DeepCoderX Legacy Migration Status:[/]")
        console.print("[cyan]✅ Phase 1: Legacy Handler Migration - COMPLETED (previous session)[/]")
        console.print("[cyan]✅ Phase 2: Tool Parsing Consolidation - COMPLETED[/]")
        console.print("[cyan]✅ Phase 3: MCP Client Enhancement - COMPLETED[/]")
        console.print("")
        console.print("[bold cyan]🏆 LEGACY MIGRATION PLAN FULLY IMPLEMENTED![/]")
        return True
    else:
        console.print(f"[bold yellow]⚠️  PARTIAL COMPLETION: {total_issues} issues found[/]")
        return False

def main():
    """Run comprehensive Phase 2 & 3 completion verification."""
    console.print("[bold cyan]🔍 DeepCoderX Phase 2 & Phase 3 Completion Verification[/]")
    console.print("[cyan]Verifying Tool Parsing Consolidation and MCP Client Enhancement[/]")
    console.print("")
    
    # Run verifications
    phase2_results = verify_phase2_structured_tools()
    console.print("")
    
    phase3_results = verify_phase3_mcp_client()
    console.print("")
    
    integration_results = verify_tool_system_integration()
    console.print("")
    
    # Generate completion report
    success = generate_completion_report(phase2_results, phase3_results, integration_results)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
