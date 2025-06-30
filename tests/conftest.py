import pytest
import sys
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent.parent  # Go up one level from tests/ to project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
