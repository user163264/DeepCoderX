#!/usr/bin/env python3
"""
Simple Qwen Configuration Test
Verifies basic configuration loading for Qwen optimization.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_config():
    """Test basic configuration loading."""
    print("🔄 Testing basic configuration loading...")
    
    try:
        from config_module import DeepCoderXConfig
        config = DeepCoderXConfig()
        print("✅ Configuration loaded successfully")
        
        # Check model path
        if hasattr(config, 'GGUF_MODEL_PATH') and config.GGUF_MODEL_PATH:
            print(f"✅ Model path: {config.GGUF_MODEL_PATH}")
            if config.GGUF_MODEL_PATH.exists():
                size_mb = config.GGUF_MODEL_PATH.stat().st_size / (1024*1024)
                print(f"✅ Model exists: {size_mb:.1f} MB")
            else:
                print(f"❌ Model file not found: {config.GGUF_MODEL_PATH}")
                return False
        else:
            print("❌ GGUF_MODEL_PATH not configured")
            return False
            
        # Check Qwen optimization
        if hasattr(config, 'QWEN_OPTIMIZATION'):
            opt = config.QWEN_OPTIMIZATION
            print(f"✅ Qwen optimization enabled: {opt.get('code_specialization')}")
            print(f"✅ Progressive intensity: {opt.get('progressive_intensity')}")
        else:
            print("❌ QWEN_OPTIMIZATION not found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_yaml_config():
    """Test YAML configuration."""
    print("\n🔄 Testing YAML configuration...")
    
    try:
        import yaml
        yaml_path = project_root / "gguf_prompts.yaml"
        
        if not yaml_path.exists():
            print(f"❌ YAML file not found: {yaml_path}")
            return False
            
        with open(yaml_path, 'r') as f:
            config = yaml.safe_load(f)
            
        if not config:
            print("❌ YAML file empty or invalid")
            return False
            
        print("✅ YAML file loaded")
        
        # Check key sections
        sections = ['system_instructions', 'progressive_intensity', 'model_overrides']
        for section in sections:
            if section in config:
                print(f"✅ Section found: {section}")
            else:
                print(f"❌ Section missing: {section}")
                return False
                
        # Check Qwen model override
        if 'qwen2.5-coder' in config.get('model_overrides', {}):
            print("✅ Qwen model override found")
        else:
            print("❌ Qwen model override missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ YAML error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 QWEN CONFIGURATION TEST")
    print("=" * 40)
    
    test1 = test_basic_config()
    test2 = test_yaml_config()
    
    print("\n" + "=" * 40)
    if test1 and test2:
        print("🎉 ALL BASIC TESTS PASSED")
        print("\n📋 Next steps:")
        print("1. Run full integration test: python integration_tests/qwen_integration_test.py")
        print("2. Test actual model loading with GGUF handler")
        print("3. Test progressive intensity escalation")
    else:
        print("❌ SOME TESTS FAILED")
        print("Fix configuration issues before proceeding")
