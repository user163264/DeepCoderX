#!/bin/bash
# This script starts the DeepCoderX application.

# Change to the DeepCoderX project directory.
cd /Users/admin/Documents/DeepCoderX || exit

# Activate the virtual environment
source VENV/bin/activate

# Run the application, passing along any command-line arguments
python run.py "$@"