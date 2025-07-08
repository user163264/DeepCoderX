#!/bin/bash
# Clear Python cache files and restart

echo "Clearing Python cache files..."
find /Users/admin/Documents/DeepCoderX -name "*.pyc" -delete
find /Users/admin/Documents/DeepCoderX -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "Cache cleared. Try running deepcoderx again."
