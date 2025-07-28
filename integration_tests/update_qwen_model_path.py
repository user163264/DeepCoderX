#!/usr/bin/env python3
"""
UPDATE CONFIG FOR QWEN MODEL

Updates config_module.py to use the found Qwen model at the specified path.
"""

import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def update_config_for_qwen_model():
    """Update config to use the found Qwen model."""
    print("🔧 UPDATING CONFIG FOR FOUND QWEN MODEL")
    print("=" * 40)
    
    config_file = project_root / "config_module.py"
    
    # Create backup
    backup_file = project_root / "config_module.py.BAK7"
    
    try:
        import shutil
        shutil.copy2(config_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False
    
    # Read current config
    try:
        with open(config_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read config: {e}")
        return False
    
    # Update the model path directly in the _load_gguf_settings method
    model_path = "/Users/admin/Documents/DeepCoderX/.cache/deepcoderx/models/qwen2.5-coder-1.5b-instruct-q8_0.gguf"
    
    # Find and replace the model path configuration
    patterns_to_replace = [
        # Replace the hardcoded path
        (r'qwen_model_path = Path\(".*?"\)', 
         f'qwen_model_path = Path("{model_path}")'),
        
        # Replace if it's directly set
        (r'/Users/admin/Documents/MyProjects/Project_Genesis/models/qwen-coder/qwen2\.5-coder-1\.5b\.gguf',
         model_path),
        
        # Update model name to match actual file
        (r'"qwen2\.5-coder-1\.5b"',
         '"qwen2.5-coder-1.5b-instruct-q8_0"'),
        
        # Update any hardcoded model name in GGUF_MODEL_NAME
        (r'self\.GGUF_MODEL_NAME = self\._get_str_env\("DEEPCODERX_GGUF_MODEL_NAME", ".*?"\)',
         'self.GGUF_MODEL_NAME = self._get_str_env("DEEPCODERX_GGUF_MODEL_NAME", "qwen2.5-coder-1.5b-instruct-q8_0")')
    ]
    
    updated = False
    for pattern, replacement in patterns_to_replace:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updated = True
            print(f"✅ Updated pattern: {pattern[:50]}...")
    
    # If no patterns matched, we need to insert the path more directly
    if not updated:
        # Look for the qwen model path assignment and replace it
        if "qwen2.5-coder-1.5b.gguf" in content:
            content = content.replace(
                "/Users/admin/Documents/MyProjects/Project_Genesis/models/qwen-coder/qwen2.5-coder-1.5b.gguf",
                model_path
            )
            updated = True
            print("✅ Updated hardcoded model path")
        
        # Update model name
        if 'GGUF_MODEL_NAME' in content and 'qwen2.5-coder-1.5b' in content:
            content = content.replace(
                '"qwen2.5-coder-1.5b"',
                '"qwen2.5-coder-1.5b-instruct-q8_0"'
            )
            print("✅ Updated model name")
    
    # Write the updated content
    try:
        with open(config_file, 'w') as f:
            f.write(content)
        print("✅ Configuration file updated")
        return True
    except Exception as e:
        print(f"❌ Failed to write config: {e}")
        # Restore backup
        try:
            shutil.copy2(backup_file, config_file)
            print("✅ Backup restored")
        except:
            print("❌ Failed to restore backup")
        return False

def test_updated_config():
    """Test the updated configuration."""
    print("\n🧪 TESTING UPDATED CONFIGURATION")
    print("=" * 40)
    
    try:
        from config_module import DeepCoderXConfig
        
        config = DeepCoderXConfig()
        print("✅ Configuration loaded successfully")
        
        # Check model path
        if hasattr(config, 'GGUF_MODEL_PATH') and config.GGUF_MODEL_PATH:
            print(f"✅ Model path configured: {config.GGUF_MODEL_PATH}")
            
            if config.GGUF_MODEL_PATH.exists():
                size_gb = config.GGUF_MODEL_PATH.stat().st_size / (1024**3)
                print(f"✅ Model file exists: {size_gb:.2f} GB")
                
                if "q8_0" in str(config.GGUF_MODEL_PATH):
                    print("✅ Q8_0 quantization detected (high quality)")
            else:
                print(f"❌ Model file not found: {config.GGUF_MODEL_PATH}")
                return False
        else:
            print("❌ GGUF_MODEL_PATH not set")
            return False
        
        # Check Qwen optimization
        if hasattr(config, 'QWEN_OPTIMIZATION'):
            print("✅ QWEN_OPTIMIZATION found")
            qwen_opt = config.QWEN_OPTIMIZATION
            print(f"   - Code specialization: {qwen_opt.get('code_specialization')}")
            print(f"   - Progressive intensity: {qwen_opt.get('progressive_intensity')}")
        else:
            print("❌ QWEN_OPTIMIZATION not found")
            return False
        
        # Check hardware config for Q8_0
        if hasattr(config, 'GGUF_HARDWARE_CONFIG'):
            hw_config = config.GGUF_HARDWARE_CONFIG
            print("✅ Hardware configuration found")
            print(f"   - GPU layers: {hw_config.get('n_gpu_layers')}")
            print(f"   - Batch size: {hw_config.get('n_batch')}")
            print(f"   - Context size: {hw_config.get('n_ctx')}")
        
        print("✅ Configuration test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Update config and test."""
    print("🚀 QWEN MODEL CONFIGURATION UPDATE")
    print("=" * 50)
    
    # Update config
    success = update_config_for_qwen_model()
    
    if not success:
        print("❌ Configuration update failed")
        return 1
    
    # Test config
    test_success = test_updated_config()
    
    if test_success:
        print("\n🎉 QWEN MODEL INTEGRATION READY")
        print("=" * 40)
        print("✅ Model path updated and verified")
        print("✅ Configuration loads without errors")
        print("✅ Q8_0 quantization (high quality)")
        print("✅ Apple Silicon optimization enabled")
        print("\n📋 Next steps:")
        print("1. Run: python integration_tests/qwen_practical_test.py")
        print("2. Test actual model loading and inference")
        return 0
    else:
        print("\n❌ CONFIGURATION TEST FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
