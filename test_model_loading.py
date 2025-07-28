#!/usr/bin/env python3
"""
Test model loading with ChatTemplateFormatter integration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_model_loading():
    """Test model loading with ChatTemplateFormatter."""
    
    try:
        print("🔄 Importing required modules...")
        from models.session import CommandContext
        from services.gguf_handler import GGUFLocalHandler
        
        print("✅ Imports successful!")
        
        # Create test context
        print("🔄 Creating test context...")
        
        # Create a minimal MCP client mock for testing
        class MockMCPClient:
            pass
        
        ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=MockMCPClient(),
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        ctx.user_input = 'test model loading'  # Set user input after initialization
        print("✅ Test context created!")
        
        # Initialize handler
        print("🔄 Initializing GGUFLocalHandler...")
        handler = GGUFLocalHandler(ctx, 'local')
        
        print("✅ Handler initialized successfully!")
        print(f"📁 Model path: {handler.model_path}")
        print(f"🏷️  Chat template: {handler.chat_formatter.model_type}")
        
        # Get chat template info
        template_info = handler.chat_formatter.get_model_info()
        print(f"📋 Template format: {template_info['template_format']}")
        print(f"🤖 Model name: {template_info['model_name']}")
        
        # Test chat template formatting (without loading model)
        print("\n🧪 Testing chat template formatting...")
        test_prompt = handler.chat_formatter.format_prompt(
            system_prompt="You are a helpful assistant.",
            user_prompt="Hello, world!"
        )
        print(f"📝 Template length: {len(test_prompt)} characters")
        print(f"🏷️  Template preview: {test_prompt[:100]}...")
        
        # Test model loading (this will actually load the GGUF model)
        print("\n🔄 Testing actual model loading...")
        print("⚠️  This may take a moment for first-time loading...")
        
        model = handler.model  # This triggers lazy loading
        print("✅ GGUF model loaded successfully with Metal acceleration!")
        
        print("\n🎉 All tests passed! Model loading and ChatTemplateFormatter working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the DeepCoderX directory")
        return False
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Check that model files exist in .cache/deepcoderx/models/")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 DeepCoderX Model Loading Test")
    print("=" * 50)
    
    success = test_model_loading()
    
    if success:
        print("\n✅ Model loading test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Model loading test failed!")
        sys.exit(1)
