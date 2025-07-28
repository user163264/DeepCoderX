import random

# Professional and appropriate loading messages for DeepCoderX
SILLY_MESSAGES = [
    ("#9c9c9c", "Analyzing your request..."),
    ("#9c9c9c", "Consulting the code libraries..."),
    ("#9c9c9c", "Optimizing the response..."),
    ("#9c9c9c", "Loading semantic parser..."),
    ("#9c9c9c", "Initializing code specialist..."),
    ("#9c9c9c", "Processing with AI models..."),
    ("#9c9c9c", "Running intelligent analysis..."),
    ("#9c9c9c", "Coordinating multi-agent system..."),
    ("#9c9c9c", "Generating optimal solution..."),
    ("#9c9c9c", "Thinking through the problem..."),
    ("#9c9c9c", "Compiling the perfect response..."),
    ("#9c9c9c", "Fine-tuning the output..."),
    ("#9c9c9c", "Almost ready with your answer..."),
    ("#9c9c9c", "Putting the finishing touches..."),
]

def get_silly_message() -> tuple[str, str]:
    """Returns a random appropriate loading message and its color."""
    return random.choice(SILLY_MESSAGES)
