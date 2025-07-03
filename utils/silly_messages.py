import random

SILLY_MESSAGES = [
    ("#9c9c9c", "Having a good time with your mom while you wait..."),
    ("#9c9c9c", "Meanwhile....I'm Looking for my teeth..."),
    ("#9c9c9c", "Euh...Who has my keys..."),
    ("#9c9c9c", "And then...The shadow is compiling itself in reverse..."),
    ("#9c9c9c", "Why? ...consulting the ancient scrolls..."),
    ("#9c9c9c", "And..Is that what she said?..."),
    ("#9c9c9c", "Going to the library to look for the answer..."),
    ("#9c9c9c", "I'm teaching the AI to peel bananas..."),
    ("#9c9c9c", "Waking up the hamsters..."),
    ("#9c9c9c", "Meanwhile, I'm counting backwards from infinity..."),
    ("#9c9c9c", "I hate herding cats..."),
    ("#9c9c9c", "Just erased your iPhone..."),
    ("#9c9c9c", "I'm stealing your Tablet while you wait..."),
    ("#9c9c9c", "Erasing your children while you wait..."),
]

def get_silly_message() -> tuple[str, str]:
    """Returns a random silly message and its color."""
    return random.choice(SILLY_MESSAGES)