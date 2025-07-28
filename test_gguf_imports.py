#!/usr/bin/env python3
"""
Test GGUF imports to verify syntax fixes.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing GGUF component imports...")

try:
    print("1. Testing gguf_tool_prompt...")
    from services.gguf_tool_prompt import GGUFToolPromptBuilder
    print("✅ gguf_tool_prompt imported successfully")

    print("2. Testing gguf_tool_parser...")
    from services.gguf_tool_parser import GGUFToolCallParser
    print("✅ gguf_tool_parser imported successfully")

    print("3. Testing gguf_context_manager...")
    from services.gguf_context_manager import GGUFContextManager
    print("✅ gguf_context_manager imported successfully")

    print("4. Testing gguf_handler...")
    from services.gguf_handler import GGUFLocalHandler
    print("✅ gguf_handler imported successfully")

    print("\n🎉 All GGUF components imported successfully!")
    print("The syntax errors have been fixed.")

except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
