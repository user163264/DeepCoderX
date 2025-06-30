#!/usr/bin/env python3
def count_words(phrase):
    return len(phrase.split())

if __name__ == "__main__":
    print("Word count:", count_words(input("Enter phrase: ")))