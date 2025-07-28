#!/usr/bin/env python3
"""
Test script to verify that the config import fix is working.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_import():
    """Test that config can be imported correctly."""
    try:
        from config_module import config
        print("✅ Successfully imported config from config_module")
        print(f"   Config type: {type(config)}")
        print(f"   Config has DEFAULT_PROVIDER: {hasattr(config, 'DEFAULT_PROVIDER')}")
        if hasattr(config, 'DEFAULT_PROVIDER'):
            print(f"   DEFAULT_PROVIDER value: {config.DEFAULT_PROVIDER}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import config from config_module: {e}")
        return False

def test_app_import():
    """Test that app.py can be imported (which uses config)."""
    try:
        import app
        print("✅ Successfully imported app.py")
        return True
    except ImportError as e:
        print(f"❌ Failed to import app.py: {e}")
        return False
    except Exception as e:
        print(f"⚠️  App imported but has other issues: {e}")
        return False

def test_llm_handler_import():
    """Test that llm_handler can be imported."""
    try:
        from services.llm_handler import SecurityMiddleware
        print("✅ Successfully imported SecurityMiddleware from llm_handler")
        return True
    except ImportError as e:
        print(f"❌ Failed to import from llm_handler: {e}")
        return False

def test_mcp_imports():
    """Test that MCP modules can be imported."""
    try:
        from services.mcpclient import MCPClient
        print("✅ Successfully imported MCPClient")
        return True
    except ImportError as e:
        print(f"❌ Failed to import MCPClient: {e}")
        return False

if __name__ == "__main__":
    print("DeepCoderX Import Fix Test")
    print("=" * 40)
    
    all_passed = True
    
    # Test 1: Config import
    if not test_config_import():
        all_passed = False
    
    print()
    
    # Test 2: App import  
    if not test_app_import():
        all_passed = False
    
    print()
    
    # Test 3: LLM Handler import
    if not test_llm_handler_import():
        all_passed = False
    
    print()
    
    # Test 4: MCP imports
    if not test_mcp_imports():
        all_passed = False
    
    print()
    print("=" * 40)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The import fix is working.")
        print("You should now be able to run: deepcoderx")
    else:
        print("❌ Some tests failed. There may be additional import issues.")
    print("=" * 40)
