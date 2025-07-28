#!/usr/bin/env python3
"""
EMERGENCY TEST: Semantic Parser JSON Fix Validation
Test the emergency fixes for semantic parser JSON output format.
"""

import sys
import os
sys.path.append('/Users/admin/Documents/DeepCoderX')

from services.dual_model_handler import LlamaSemanticParser
from pathlib import Path

def test_semantic_parser_fixes():
    """Test the emergency fixes for semantic parser."""
    print("=== EMERGENCY SEMANTIC PARSER TEST ===")
    
    try:
        # Find the model path
        cache_dir = Path("/Users/admin/Documents/DeepCoderX/.cache/deepcoderx/models")
        model_path = cache_dir / "Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf"
        
        if not model_path.exists():
            print(f"❌ Model not found: {model_path}")
            return False
        
        print(f"✅ Model found: {model_path.name}")
        
        # Create semantic parser with debug mode
        parser = LlamaSemanticParser(str(model_path), debug_mode=True)
        
        # Test cases
        test_cases = [
            "hello",
            "pwd", 
            "create a script",
            "why do cats have fur?"
        ]
        
        print("\n=== TESTING SIMPLIFIED PROMPT ===")
        print("New prompt:")
        print(parser.semantic_system_prompt)
        
        print("\n=== TESTING INTENT PARSING ===")
        for test_input in test_cases:
            try:
                print(f"\nTesting: '{test_input}'")
                intent = parser.parse_intent(test_input)
                print(f"✅ SUCCESS: {intent}")
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                return False
        
        print("\n=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_semantic_parser_fixes()
    exit(0 if success else 1)
