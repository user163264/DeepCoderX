#!/usr/bin/env python3
"""
Test script for Phase 3 dual model integration.

This script tests:
1. Import of dual model handler
2. Configuration validation
3. Model path detection
4. Handler initialization
"""

import sys
from pathlib import Path
import traceback

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_imports():
    """Test if all required modules can be imported."""
    print("🔧 Testing imports...")
    
    try:
        from config_module import config
        print("  ✅ Config module imported successfully")
        
        from models.session import CommandContext
        print("  ✅ CommandContext imported successfully")
        
        from services.dual_model_handler import DualModelHandler
        print("  ✅ DualModelHandler imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test dual model configuration."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config_module import config
        
        # Check if dual provider is configured
        if "dual" in config.PROVIDERS:
            dual_config = config.PROVIDERS["dual"]
            print(f"  ✅ Dual provider configured: {dual_config['name']}")
            print(f"  📊 Enabled: {dual_config['enabled']}")
            print(f"  🧠 Semantic parser: {dual_config['semantic_parser_model']}")
            print(f"  💻 Code specialist: {dual_config['code_specialist_model']}")
            print(f"  💾 Memory usage: {dual_config['memory_usage']}")
        else:
            print("  ❌ Dual provider not found in configuration")
            return False
        
        # Check default provider
        print(f"  🎯 Default provider: {config.DEFAULT_PROVIDER}")
        
        # Check if models exist
        if config.GGUF_MODEL_PATH and config.GGUF_MODEL_PATH.exists():
            print(f"  ✅ Primary model found: {config.GGUF_MODEL_PATH}")
        else:
            print(f"  ❌ Primary model not found: {config.GGUF_MODEL_PATH}")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_model_paths():
    """Test if both required models are available."""
    print("\n🔧 Testing model availability...")
    
    try:
        from services.dual_model_handler import DualModelHandler
        from models.session import CommandContext
        
        # Create test context
        test_ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        test_ctx.user_input = "test"
        
        # Test model path detection
        handler = DualModelHandler(test_ctx, "dual")
        
        print(f"  🧠 Semantic parser: {handler.semantic_parser_path}")
        print(f"  💻 Code specialist: {handler.code_specialist_path}")
        
        if handler.semantic_parser_path.exists():
            print("  ✅ Semantic parser model found")
        else:
            print("  ❌ Semantic parser model missing")
            return False
        
        if handler.code_specialist_path.exists():
            print("  ✅ Code specialist model found")
        else:
            print("  ❌ Code specialist model missing")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Model path test failed: {e}")
        traceback.print_exc()
        return False

def test_handler_initialization():
    """Test handler initialization without loading models."""
    print("\n🔧 Testing handler initialization...")
    
    try:
        from services.dual_model_handler import DualModelHandler
        from models.session import CommandContext
        
        # Create test context
        test_ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        test_ctx.user_input = "hello"
        
        # Initialize handler (this should not load models yet)
        handler = DualModelHandler(test_ctx, "dual")
        print("  ✅ Handler initialized successfully")
        
        # Test can_handle method
        can_handle = handler.can_handle()
        print(f"  🎯 Can handle test input: {can_handle}")
        
        # Test semantic intent parsing (this will load semantic parser)
        print("  🧠 Testing semantic parsing...")
        semantic_intent = handler.semantic_parser.parse_intent("hello")
        print(f"  📝 Semantic intent: {semantic_intent}")
        
        return True
    except Exception as e:
        print(f"  ❌ Handler initialization failed: {e}")
        traceback.print_exc()
        return False

def test_memory_estimation():
    """Test memory usage estimation."""
    print("\n🔧 Testing memory estimation...")
    
    try:
        from services.dual_model_handler import DualModelHandler
        from models.session import CommandContext
        
        test_ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        test_ctx.user_input = "test"
        
        handler = DualModelHandler(test_ctx, "dual")
        model_info = handler.get_model_info()
        
        print("  📊 Model information:")
        for key, value in model_info.items():
            if isinstance(value, dict):
                print(f"    {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"    {key}: {value}")
        
        return True
    except Exception as e:
        print(f"  ❌ Memory estimation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("🚀 Phase 3 Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Model Path Test", test_model_paths),
        ("Handler Initialization Test", test_handler_initialization),
        ("Memory Estimation Test", test_memory_estimation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 3 integration is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
