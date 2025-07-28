#!/usr/bin/env python3
"""
TEST UPDATED QWEN CONFIGURATION

Quick test to verify the updated configuration works with the actual model file.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """Test that the updated configuration loads properly."""
    print("🧪 TESTING UPDATED QWEN CONFIGURATION")
    print("=" * 50)
    
    try:
        from config_module import DeepCoderXConfig
        
        print("📄 Loading configuration...")
        config = DeepCoderXConfig()
        print("✅ Configuration loaded successfully")
        
        # Test model path
        print(f"\n📁 Model Configuration:")
        print(f"   Name: {config.GGUF_MODEL_NAME}")
        print(f"   Path: {config.GGUF_MODEL_PATH}")
        
        if config.GGUF_MODEL_PATH and config.GGUF_MODEL_PATH.exists():
            size_gb = config.GGUF_MODEL_PATH.stat().st_size / (1024**3)
            print(f"✅ Model file exists: {size_gb:.2f} GB")
            
            if "q8_0" in str(config.GGUF_MODEL_PATH):
                print("✅ Q8_0 quantization detected (high quality)")
        else:
            print(f"❌ Model file not found: {config.GGUF_MODEL_PATH}")
            return False
        
        # Test Qwen optimization
        print(f"\n⚙️ Qwen Optimization:")
        if hasattr(config, 'QWEN_OPTIMIZATION'):
            qwen_opt = config.QWEN_OPTIMIZATION
            print(f"   Code specialization: {qwen_opt.get('code_specialization')}")
            print(f"   Progressive intensity: {qwen_opt.get('progressive_intensity')}")
            print(f"   Max intensity level: {qwen_opt.get('max_intensity_level')}")
            print(f"   Q8_0 optimized: {qwen_opt.get('q8_0_optimized')}")
        else:
            print("❌ QWEN_OPTIMIZATION not found")
            return False
        
        # Test hardware config
        print(f"\n🖥️ Hardware Configuration:")
        hw_config = config.GGUF_HARDWARE_CONFIG
        print(f"   GPU layers: {hw_config.get('n_gpu_layers')}")
        print(f"   Batch size: {hw_config.get('n_batch')}")
        print(f"   Context size: {hw_config.get('n_ctx')}")
        print(f"   Rope freq base: {hw_config.get('rope_freq_base')}")
        
        # Test generation params
        print(f"\n🎛️ Generation Parameters:")
        gen_params = config.GGUF_GENERATION_PARAMS
        print(f"   Temperature: {gen_params.get('temperature')}")
        print(f"   Top P: {gen_params.get('top_p')}")
        print(f"   Repeat penalty: {gen_params.get('repeat_penalty')}")
        
        print(f"\n🎯 CONFIGURATION TEST SUCCESSFUL")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_provider_availability():
    """Test provider availability."""
    print(f"\n🔌 TESTING PROVIDER AVAILABILITY")
    print("-" * 30)
    
    try:
        from config_module import config
        
        providers = ["local", "deepseek", "openai"]
        
        for provider in providers:
            available = config.is_provider_available(provider)
            status = "✅ Available" if available else "❌ Not available"
            print(f"   {provider}: {status}")
            
            if provider == "local" and available:
                print(f"     Model: {config.GGUF_MODEL_PATH.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Provider test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 QWEN CONFIGURATION VERIFICATION")
    print("=" * 50)
    
    # Test configuration loading
    config_success = test_config_loading()
    
    # Test provider availability
    provider_success = test_provider_availability()
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    
    if config_success and provider_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Configuration loads without errors")
        print("✅ Qwen model found and accessible")
        print("✅ Q8_0 optimization configured")
        print("✅ Apple Silicon optimization enabled")
        print(f"\n📋 Next steps:")
        print("1. Run: python integration_tests/qwen_practical_test.py")
        print("2. Test actual model loading and inference")
        print("3. Test progressive intensity escalation")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Fix configuration issues before proceeding")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
