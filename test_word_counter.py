#!/usr/bin/env python3
"""
Test script for word_counter.py
"""

import sys
import os

# Add the current directory to the Python path so we can import word_counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from word_counter import count_words

def test_word_counter():
    """Test the word counter function with various inputs."""
    test_cases = [
        ("", 0),  # Empty string
        ("   ", 0),  # Only whitespace
        ("hello", 1),  # Single word
        ("hello world", 2),  # Two words
        ("  hello   world  ", 2),  # Words with extra whitespace
        ("The quick brown fox jumps", 5),  # Multiple words
        ("Python is awesome!", 3),  # Words with punctuation
        ("word1 word2 word3 word4 word5 word6", 6),  # Six words
    ]
    
    print("Testing word_counter function:")
    print("=" * 40)
    
    all_passed = True
    for i, (input_phrase, expected) in enumerate(test_cases, 1):
        result = count_words(input_phrase)
        status = "PASS" if result == expected else "FAIL"
        
        if result != expected:
            all_passed = False
            
        print(f"Test {i}: '{input_phrase}' -> {result} words (expected {expected}) [{status}]")
    
    print("=" * 40)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    test_word_counter()
