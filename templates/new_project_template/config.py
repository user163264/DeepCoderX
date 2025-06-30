import os

class Config:
    """
    Main configuration class for the project.
    """
    # Example setting
    API_KEY = os.getenv("API_KEY", "default_key")

config = Config()
