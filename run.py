# run.py
import sys
import os
import os
import sys
from pathlib import Path

# Change the current working directory to the directory of this script
# This ensures that the .env file is always found.
os.chdir(Path(__file__).parent)

from app import main

if __name__ == "__main__":
    main()