import random

SILLY_MESSAGES = [
    ("#ab998a", "Having a good time with your mom while you wait..."),
    ("#0d00ff", "Meanwhile....I'm Looking for my teeth..."),
    ("#00FFFF", "Euh...Who has my keys..."),
    ("#0d00ff", "And then...The shadow is compiling itself in reverse..."),
    ("#ff7300", "Why? ...consulting the ancient scrolls..."),
    ("#aae6aa", "And..Is that what she said?..."),
    ("#b152bf", "Going to the library to look for the answer..."),
    ("#ADFF2F", "I'm teaching the AI to peel bananas..."),
    ("#DDA0DD", "Waking up the hamsters..."),
    ("#6A5ACD", "Meanwhile, I'm counting backwards from infinity..."),
    ("#F0E68C", "I hate herding cats..."),
    ("#12e0da", "Just erased your iPhone while are waiting..."),
    ("#ADD8E6", "I'm stealing your Tablet while you wait..."),
    ("#e0163a", "Erasing your children while you wait..."),
]

def get_silly_message() -> tuple[str, str]:
    """Returns a random silly message and its color."""
    return random.choice(SILLY_MESSAGES)