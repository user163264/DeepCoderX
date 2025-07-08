#!/usr/bin/env python3
"""
Simple import test to verify what's working in DeepCoderX.
Following Assessment Protocol - test actual functionality before making claims.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_step_by_step():
    """Test imports step by step to identify specific failures."""
    
    print("=== ASSESSMENT PROTOCOL: STEP-BY-STEP IMPORT TESTING ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {Path.cwd()}")
    print(f"Project root: {project_root}")
    print()
    
    results = []
    
    # Test 1: Basic config import
    print("Test 1: Basic config import")
    try:
        from config_module import config
        print("✅ config_module import: SUCCESS")
        print(f"   - Default provider: {config.DEFAULT_PROVIDER}")
        results.append(("config_module", True, None))
    except Exception as e:
        print(f"❌ config_module import: FAILED - {e}")
        results.append(("config_module", False, str(e)))
    
    # Test 2: Tool registry import
    print("\nTest 2: Tool registry import")
    try:
        from services.tool_registry import tool_registry
        print("✅ tool_registry import: SUCCESS")
        tools = list(tool_registry.tools.keys())
        print(f"   - Available tools: {len(tools)} tools")
        results.append(("tool_registry", True, None))
    except Exception as e:
        print(f"❌ tool_registry import: FAILED - {e}")
        results.append(("tool_registry", False, str(e)))
    
    # Test 3: GGUF prompt builder
    print("\nTest 3: GGUF prompt builder import")
    try:
        from services.gguf_tool_prompt import GGUFToolPromptBuilder
        print("✅ GGUFToolPromptBuilder import: SUCCESS")
        builder = GGUFToolPromptBuilder()
        print("   - Builder instantiation: SUCCESS")
        results.append(("gguf_tool_prompt", True, None))
    except Exception as e:
        print(f"❌ GGUFToolPromptBuilder import: FAILED - {e}")
        results.append(("gguf_tool_prompt", False, str(e)))
    
    # Test 4: GGUF parser
    print("\nTest 4: GGUF parser import")
    try:
        from services.gguf_tool_parser import GGUFToolCallParser
        print("✅ GGUFToolCallParser import: SUCCESS")
        parser = GGUFToolCallParser()
        print("   - Parser instantiation: SUCCESS")
        results.append(("gguf_tool_parser", True, None))
    except Exception as e:
        print(f"❌ GGUFToolCallParser import: FAILED - {e}")
        results.append(("gguf_tool_parser", False, str(e)))
    
    # Test 5: GGUF handler
    print("\nTest 5: GGUF handler import")
    try:
        from services.gguf_handler import GGUFLocalHandler
        print("✅ GGUFLocalHandler import: SUCCESS")
        results.append(("gguf_handler", True, None))
    except Exception as e:
        print(f"❌ GGUFLocalHandler import: FAILED - {e}")
        results.append(("gguf_handler", False, str(e)))
    
    # Test 6: Enhanced GGUF handler
    print("\nTest 6: Enhanced GGUF handler import")
    try:
        from services.enhanced_gguf_handler import EnhancedGGUFHandler
        print("✅ EnhancedGGUFHandler import: SUCCESS")
        results.append(("enhanced_gguf_handler", True, None))
    except Exception as e:
        print(f"❌ EnhancedGGUFHandler import: FAILED - {e}")
        results.append(("enhanced_gguf_handler", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("IMPORT TEST SUMMARY")
    print("=" * 20)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for component, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{component:25} {status}")
        if not success and error:
            print(f"{'':25} Error: {error}")
    
    print(f"\nResults: {passed}/{total} imports successful")
    
    if passed == total:
        print("\n🎉 ALL IMPORTS SUCCESSFUL - Can proceed to functional testing")
        return True
    else:
        print(f"\n⚠️ {total - passed} imports failed - Must fix before functional testing")
        return False

if __name__ == "__main__":
    success = test_step_by_step()
    print(f"\nIMPORT TEST RESULT: {'SUCCESS' if success else 'BLOCKED'}")
    sys.exit(0 if success else 1)
