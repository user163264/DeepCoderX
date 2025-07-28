#!/usr/bin/env python3
"""
Word Counter Script
A simple script that asks for user input and counts the number of words.
"""

def count_words(phrase):
    """
    Count the number of words in a given phrase.
    
    Args:
        phrase (str): The input phrase to count words in
        
    Returns:
        int: The number of words in the phrase
    """
    # Split the phrase by whitespace and filter out empty strings
    words = phrase.strip().split()
    return len(words)

def main():
    """Main function to run the word counter."""
    print("=== Word Counter ===")
    print("This script will count the number of words in your input phrase.")
    print()
    
    # Get user input
    user_phrase = input("Please enter a phrase: ")
    
    # Count words
    word_count = count_words(user_phrase)
    
    # Display result
    print(f"\nInput phrase: '{user_phrase}'")
    print(f"Number of words: {word_count}")
    
    # Handle edge cases
    if word_count == 0:
        print("Note: No words detected (empty input or only whitespace)")
    elif word_count == 1:
        print("Note: Single word detected")
    else:
        print(f"Note: Multiple words detected")

if __name__ == "__main__":
    main()
