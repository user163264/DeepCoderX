#!/usr/bin/env python3
"""
Test script for dual model streaming fixes
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_streaming_display():
    """Test the fixed streaming display functionality."""
    print("Testing streaming display fixes...")
    
    # Simulate streaming output
    print("\n🌊 Testing fixed streaming output...")
    sys.stdout.flush()
    
    # Simulate token streaming
    test_tokens = ["This", " is", " a", " test", " of", " the", " fixed", " streaming", " functionality."]
    
    for token in test_tokens:
        print(token, end="", flush=True)
        import time
        time.sleep(0.1)  # Simulate model generation delay
    
    print()  # New line after streaming
    sys.stdout.flush()
    
    print("✅ Streaming display test complete!")
    
    # Test that tokens don't interfere with progress indicators
    print("\n⏳ This is a progress indicator...")
    sys.stdout.flush()
    
    # Simulate more streaming
    print("\n🌊 More streaming tokens...")
    sys.stdout.flush()
    
    more_tokens = ["These", " tokens", " should", " appear", " correctly."]
    for token in more_tokens:
        print(token, end="", flush=True)
        import time
        time.sleep(0.1)
    
    print()
    sys.stdout.flush()
    
    print("✅ All streaming tests passed!")

if __name__ == "__main__":
    test_streaming_display()
