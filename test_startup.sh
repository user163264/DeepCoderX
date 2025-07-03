#!/bin/bash
cd /Users/admin/Documents/DeepCoderX
echo "⏱️  Testing startup performance..."
echo "Before: 5-15 second model loading delay"
echo "After: Should start almost instantly"
echo ""
echo "Starting DeepCoderX..."
time python app.py --debug
