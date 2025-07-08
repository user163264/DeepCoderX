#!/usr/bin/env python3
"""
Debug startup script to identify GGUF implementation issues.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test