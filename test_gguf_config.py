#!/usr/bin/env python3
"""
Test script to verify GGUF configuration dependencies and imports
"""

import sys
import traceback

def test_pyyaml():
    """Test if PyYAML is installed"""
    try:
        import yaml
        print("✅ PyYAML is installed")
        return True
    except ImportError as e:
        print(f"❌ PyYAML not installed: {e}")
        print("Run: pip install pyyaml>=6.0.1")
        return False

def test_config_import():
    """Test if config package can be imported"""
    try:
        from config.gguf_prompting_config import get_gguf_prompting_config
        print("✅ Config package import successful")
        return True
    except ImportError as e:
        print(f"❌ Config package import failed: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Test if GGUF config can be loaded"""
    try:
        from config.gguf_prompting_config import get_gguf_prompting_config
        config = get_gguf_prompting_config()
        print("✅ GGUF config loaded successfully")
        print(f"   Config file: {config.config_path}")
        print(f"   Post-processing enabled: {config.is_post_processing_enabled()}")
        return True
    except Exception as e:
        print(f"❌ GGUF config loading failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("DeepCoderX GGUF Configuration Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test PyYAML
    if not test_pyyaml():
        all_tests_passed = False
    
    print()
    
    # Test config import
    if not test_config_import():
        all_tests_passed = False
    
    print()
    
    # Test config loading
    if not test_config_loading():
        all_tests_passed = False
    
    print()
    print("=" * 50)
    
    if all_tests_passed:
        print("✅ All tests passed! GGUF configuration system is ready.")
    else:
        print("❌ Some tests failed. See errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
