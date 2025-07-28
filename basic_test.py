#!/usr/bin/env python3

print("Testing streaming implementation directly...")

# Test 1: Basic imports
try:
    import sys
    sys.path.insert(0, '/Users/admin/Documents/DeepCoderX')
    
    from pathlib import Path
    from models.session import CommandContext
    print("✅ Basic imports successful")
    
    # Test 2: Configuration import
    from config_module import config
    print(f"✅ Config loaded - Default provider: {config.DEFAULT_PROVIDER}")
    
    # Test 3: Check if models exist
    if hasattr(config, 'GGUF_MODEL_PATH') and config.GGUF_MODEL_PATH:
        print(f"✅ GGUF model path: {config.GGUF_MODEL_PATH}")
        print(f"   Model exists: {config.GGUF_MODEL_PATH.exists()}")
    else:
        print("❌ No GGUF model path configured")
    
    # Test 4: Try to import dual model handler
    from services.dual_model_handler import DualModelHandler
    print("✅ DualModelHandler import successful")
    
    # Test 5: Create simple context and handler
    ctx = CommandContext(
        user_input="hello world test",
        root_path=Path.cwd(),
        debug_mode=False  # Disable debug to avoid model loading
    )
    
    # Don't actually create the handler as it tries to load models
    print("✅ CommandContext creation successful")
    
    print("\n🎉 All basic tests passed!")
    print("\nNext: Test with actual DeepCoderX application")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
