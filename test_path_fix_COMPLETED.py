#!/usr/bin/env python3
"""
Quick test to verify the Path object fix for semantic parser loading.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.session import CommandContext
from pathlib import Path

def test_semantic_parser_loading():
    """Test if semantic parser loads without Path object error."""
    print("🧪 Testing semantic parser loading fix...")
    
    try:
        # Create test context
        test_ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        test_ctx.user_input = "hello"
        
        # Import and test dual model handler
        from services.dual_model_handler import DualModelHandler
        
        print("✅ DualModelHandler import successful")
        
        # Create handler (this will initialize the semantic parser)
        handler = DualModelHandler(test_ctx, "dual")
        
        print("✅ DualModelHandler initialization successful")
        
        # Test semantic parser intent parsing (this will load the model)
        print("🧠 Testing semantic parser model loading...")
        
        semantic_intent = handler.semantic_parser.parse_intent("hello")
        
        print(f"✅ Semantic parser loaded successfully!")
        print(f"   Intent: {semantic_intent.intent_type}")
        print(f"   Specialist: {semantic_intent.specialist_needed}")
        print(f"   Confidence: {semantic_intent.confidence:.2f}")
        
        # Get model info
        model_info = handler.get_model_info()
        print(f"📊 Model Info:")
        print(f"   Semantic Parser: {model_info['semantic_parser']['name']}")
        print(f"   Memory Usage: {model_info['semantic_parser']['memory_usage']}")
        
        print("\n🎉 SUCCESS: Path object fix works correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_semantic_parser_loading()
    sys.exit(0 if success else 1)
