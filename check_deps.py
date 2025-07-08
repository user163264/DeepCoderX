#!/usr/bin/env python3
"""
Quick dependency check for DeepCoderX GGUF configuration
"""

print("Checking dependencies...")

# Test PyYAML
try:
    import yaml
    print("✅ PyYAML available")
except ImportError:
    print("❌ PyYAML not installed")
    print("Run: pip install pyyaml>=6.0.1")
    exit(1)

# Test config package
try:
    import config
    print("✅ Config package importable")
except ImportError as e:
    print(f"❌ Config package not importable: {e}")
    exit(1)

# Test GGUF config specifically
try:
    from config.gguf_prompting_config import get_gguf_prompting_config
    print("✅ GGUF prompting config importable")
except ImportError as e:
    print(f"❌ GGUF prompting config not importable: {e}")
    exit(1)

print("✅ All dependencies OK for GGUF configuration!")
