#!/usr/bin/env python3
"""
Test the GGUF post-processor to verify it can extract tool calls from user intent.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_post_processor():
    """Test the post-processor with the failing scenario."""
    try:
        from services.gguf_response_postprocessor import GGUFResponsePostProcessor
        
        processor = GGUFResponsePostProcessor()
        
        print("🧪 Testing GGUF Post-Processor")
        print("=" * 50)
        
        # Test the exact failing case
        user_input = "what is the current directory"
        model_response = "The current working directory is /path/to/your/project"
        
        print(f"User Input: '{user_input}'")
        print(f"Model Response: '{model_response}'")
        print()
        
        # Test post-processing
        tool_calls, clean_response = processor.process_response(user_input, model_response)
        
        if tool_calls:
            print("✅ POST-PROCESSOR SUCCESS!")
            print(f"Generated Tool Calls: {tool_calls}")
            
            # Show the corrected format
            corrected = processor.create_corrected_response(tool_calls)
            print(f"Corrected Format: {corrected}")
            
        else:
            print("❌ Post-processor failed to generate tool calls")
        
        # Test diagnosis
        diagnosis = processor.diagnose_response(user_input, model_response)
        print(f"\nDiagnosis:")
        print(f"  Should Process: {diagnosis['should_process']}")
        print(f"  Matched Intent: {diagnosis['matched_intent']}")
        print(f"  Suggested Tool Call: {diagnosis['suggested_tool_call']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_post_processor()
