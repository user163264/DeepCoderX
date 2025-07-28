#!/bin/bash

cd /Users/admin/Documents/DeepCoderX

echo "Running pytest with detailed output..."
echo "======================================"

# Run pytest and capture all output
python -m pytest tests/test_mcp_services.py::test_read_file_success -v --tb=long > test_output.log 2>&1

echo "Pytest command completed. Check test_output.log for results."
echo "Exit code: $?"
