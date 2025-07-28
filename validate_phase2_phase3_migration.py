#!/usr/bin/env python3
"""
Comprehensive validation script for Phase 2 and Phase 3 legacy migration.

This script validates:
- Phase 2: structured_tools.py migration to Tool Registry Pattern
- Phase 3: mcpclient.py enhancement with standardized error handling
"""

import sys
import os
import json
import inspect
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging import console

def test_phase2_structured_tools_migration():
    """Test Phase 2: structured_tools.py migration to Tool Registry Pattern."""
    console.print("[bold blue]Testing Phase 2: structured_tools.py Migration[/]")
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "tests": []
    }
    
    # Test 1: Import structured_tools and check migration status
    try:
        from services import structured_tools
        migration_status = structured_tools.get_migration_status()
        
        test_result = {
            "name": "Migration Status Check",
            "passed": migration_status["status"] == "COMPLETED" and migration_status["phase"] == "Phase 2 - Tool Parsing Consolidation",
            "details": f"Status: {migration_status['status']}, Phase: {migration_status['phase']}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Migration Status Check",
            "passed": False,
            "details": f"Import failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 2: Check Tool Registry integration
    try:
        from services.tool_registry import tool_registry
        from services import structured_tools
        
        # Test legacy parser uses Tool Registry
        parser = structured_tools.StructuredToolParser()
        known_tools = parser.KNOWN_TOOLS
        registry_tools = [tool.name for tool in tool_registry.list_tools()]
        
        # Check if parser has updated tool list from registry
        tools_match = len(set(known_tools.keys()).intersection(set(registry_tools))) >= 4  # At least core tools
        
        test_result = {
            "name": "Tool Registry Integration",
            "passed": tools_match,
            "details": f"Parser tools: {list(known_tools.keys())[:5]}..., Registry tools: {len(registry_tools)}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Tool Registry Integration",
            "passed": False,
            "details": f"Integration test failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 3: Deprecation warnings functionality
    try:
        from services import structured_tools
        
        # Test that StructuredToolCall validation uses Tool Registry
        tool_call = structured_tools.StructuredToolCall(
            tool_name="read_file",
            parameters={"path": "test.txt"},
            raw_input='{"tool": "read_file", "path": "test.txt"}'
        )
        
        # This should work without exceptions and use Tool Registry validation
        validation_result = tool_call.validate()
        
        test_result = {
            "name": "Legacy Validation Redirect",
            "passed": validation_result == True,
            "details": "StructuredToolCall validation uses Tool Registry successfully"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Legacy Validation Redirect",
            "passed": False,
            "details": f"Validation redirect failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 4: JSON parsing compatibility
    try:
        from services import structured_tools
        
        parser = structured_tools.StructuredToolParser()
        test_response = 'I need to read a file: {"tool": "read_file", "path": "config.py"}'
        
        tool_calls = parser.parse_tool_calls(test_response)
        
        test_result = {
            "name": "JSON Parsing Compatibility",
            "passed": len(tool_calls) == 1 and tool_calls[0].tool_name == "read_file",
            "details": f"Parsed {len(tool_calls)} tool calls successfully"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "JSON Parsing Compatibility",
            "passed": False,
            "details": f"JSON parsing failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    return results

def test_phase3_mcpclient_enhancement():
    """Test Phase 3: mcpclient.py enhancement with standardized error handling."""
    console.print("[bold blue]Testing Phase 3: MCP Client Enhancement[/]")
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "tests": []
    }
    
    # Test 1: Import enhanced MCP client and check migration status
    try:
        from services import mcpclient
        migration_status = mcpclient.get_migration_status()
        
        test_result = {
            "name": "Enhanced MCP Client Migration Status",
            "passed": migration_status["status"] == "COMPLETED" and migration_status["phase"] == "Phase 3 - MCP Client Enhancement",
            "details": f"Status: {migration_status['status']}, Enhancements: {len(migration_status['enhancements'])}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Enhanced MCP Client Migration Status",
            "passed": False,
            "details": f"Import failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 2: Check standardized error handling integration
    try:
        from services.mcpclient import MCPClient
        from services.error_handler import ErrorHandler
        
        # Test that MCPClient uses ErrorHandler
        client = MCPClient("http://localhost:8000", "test_key")
        
        # Check if ErrorHandler is available in the module
        error_handler_available = hasattr(mcpclient, 'ErrorHandler')
        client_has_error_methods = hasattr(client, '_make_request') and hasattr(client, '_validate_path')
        
        test_result = {
            "name": "Standardized Error Handling Integration",
            "passed": error_handler_available and client_has_error_methods,
            "details": f"ErrorHandler imported: {error_handler_available}, Client methods: {client_has_error_methods}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Standardized Error Handling Integration",
            "passed": False,
            "details": f"Error handling test failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 3: Check new OpenAPI 3.1 methods
    try:
        from services.mcpclient import MCPClient
        
        client = MCPClient("http://localhost:8000", "test_key")
        
        # Check for new methods
        new_methods = ["move_file", "mkdir", "stat"]
        methods_present = all(hasattr(client, method) for method in new_methods)
        
        # Check method signatures
        move_file_sig = inspect.signature(client.move_file)
        mkdir_sig = inspect.signature(client.mkdir)
        stat_sig = inspect.signature(client.stat)
        
        signatures_correct = (
            len(move_file_sig.parameters) >= 2 and  # source, destination
            len(mkdir_sig.parameters) >= 1 and     # path
            len(stat_sig.parameters) >= 1          # path
        )
        
        test_result = {
            "name": "OpenAPI 3.1 Method Implementation",
            "passed": methods_present and signatures_correct,
            "details": f"New methods present: {methods_present}, Signatures correct: {signatures_correct}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "OpenAPI 3.1 Method Implementation",
            "passed": False,
            "details": f"Method implementation test failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 4: Path validation security
    try:
        from services.mcpclient import MCPClient
        
        client = MCPClient("http://localhost:8000", "test_key")
        
        # Test path validation
        valid_path_error = client._validate_path("config.py", "test")
        invalid_absolute_error = client._validate_path("/etc/passwd", "test")
        invalid_parent_error = client._validate_path("../config.py", "test")
        
        security_working = (
            valid_path_error is None and
            invalid_absolute_error is not None and
            invalid_parent_error is not None
        )
        
        test_result = {
            "name": "Path Security Validation",
            "passed": security_working,
            "details": f"Valid path OK, Absolute blocked, Parent dir blocked: {security_working}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Path Security Validation",
            "passed": False,
            "details": f"Security validation test failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    return results

def test_overall_migration_status():
    """Test overall migration status across all phases."""
    console.print("[bold blue]Testing Overall Migration Status[/]")
    
    results = {
        "total_tests": 0,
        "passed_tests": 0,
        "tests": []
    }
    
    # Test 1: Check that both phases are completed
    try:
        from services import structured_tools, mcpclient
        
        phase2_status = structured_tools.get_migration_status()
        phase3_status = mcpclient.get_migration_status()
        
        phases_completed = (
            phase2_status["status"] == "COMPLETED" and
            phase3_status["status"] == "COMPLETED"
        )
        
        test_result = {
            "name": "All Phases Completed",
            "passed": phases_completed,
            "details": f"Phase 2: {phase2_status['status']}, Phase 3: {phase3_status['status']}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "All Phases Completed",
            "passed": False,
            "details": f"Status check failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    # Test 2: Check Tool Registry Pattern is being used
    try:
        from services.tool_registry import tool_registry
        from services.tool_executor import ToolExecutor
        
        # Check Tool Registry has tools
        registry_tools = tool_registry.list_tools()
        has_core_tools = len(registry_tools) >= 7  # Should have all 7 OpenAPI 3.1 tools
        
        # Check Tool Executor exists and has execute_tool method
        tool_executor_ready = hasattr(ToolExecutor, 'execute_tool')
        
        test_result = {
            "name": "Tool Registry Pattern Active",
            "passed": has_core_tools and tool_executor_ready,
            "details": f"Registry tools: {len(registry_tools)}, Executor ready: {tool_executor_ready}"
        }
        results["tests"].append(test_result)
        if test_result["passed"]:
            results["passed_tests"] += 1
        results["total_tests"] += 1
        
    except Exception as e:
        results["tests"].append({
            "name": "Tool Registry Pattern Active",
            "passed": False,
            "details": f"Tool Registry test failed: {str(e)}"
        })
        results["total_tests"] += 1
    
    return results

def main():
    """Run comprehensive migration validation."""
    console.print("[bold cyan]🔍 DeepCoderX Legacy Migration Validation[/]")
    console.print("[cyan]Testing Phase 2 (Tool Parsing Consolidation) and Phase 3 (MCP Enhancement)[/]")
    console.print("")
    
    # Run all test suites
    phase2_results = test_phase2_structured_tools_migration()
    phase3_results = test_phase3_mcpclient_enhancement()
    overall_results = test_overall_migration_status()
    
    # Aggregate results
    total_tests = phase2_results["total_tests"] + phase3_results["total_tests"] + overall_results["total_tests"]
    total_passed = phase2_results["passed_tests"] + phase3_results["passed_tests"] + overall_results["passed_tests"]
    
    # Display results
    console.print("[bold white]📊 Test Results Summary[/]")
    console.print("")
    
    # Phase 2 results
    console.print(f"[bold blue]Phase 2 (structured_tools.py migration):[/] {phase2_results['passed_tests']}/{phase2_results['total_tests']} passed")
    for test in phase2_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        console.print(f"  {status} {test['name']}: {test['details']}")
    console.print("")
    
    # Phase 3 results
    console.print(f"[bold blue]Phase 3 (mcpclient.py enhancement):[/] {phase3_results['passed_tests']}/{phase3_results['total_tests']} passed")
    for test in phase3_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        console.print(f"  {status} {test['name']}: {test['details']}")
    console.print("")
    
    # Overall results
    console.print(f"[bold blue]Overall Migration Status:[/] {overall_results['passed_tests']}/{overall_results['total_tests']} passed")
    for test in overall_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        console.print(f"  {status} {test['name']}: {test['details']}")
    console.print("")
    
    # Final summary
    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    console.print(f"[bold white]🎯 Overall Success Rate: {total_passed}/{total_tests} ({success_rate:.1f}%)[/]")
    
    if success_rate == 100:
        console.print("[bold green]🎉 MIGRATION COMPLETED SUCCESSFULLY![/]")
        console.print("[green]✅ Phase 2: Tool Parsing Consolidation - COMPLETED[/]")
        console.print("[green]✅ Phase 3: MCP Client Enhancement - COMPLETED[/]")
        console.print("[green]🚀 Legacy migration plan fully implemented![/]")
    elif success_rate >= 80:
        console.print("[bold yellow]⚠️  MIGRATION MOSTLY SUCCESSFUL[/]")
        console.print("[yellow]Some minor issues detected - check failed tests above[/]")
    else:
        console.print("[bold red]❌ MIGRATION ISSUES DETECTED[/]")
        console.print("[red]Significant problems found - review failed tests[/]")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
