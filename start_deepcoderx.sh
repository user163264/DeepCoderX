#!/bin/bash
"""
DeepCoderX Launcher with Enhanced Logging

This script automatically enables full logging and starts DeepCoderX.
Usage: ./start_deepcoderx.sh
"""

# Set working directory to DeepCoderX project
cd "$(dirname "$0")"

echo "🚀 Starting DeepCoderX with Enhanced Logging"
echo "============================================"

# Enable full enhanced logging
export DEEPCODERX_LOG_MODEL_PROMPTS=true
export DEEPCODERX_LOG_MODEL_RESPONSES=true
export DEEPCODERX_LOG_SEMANTIC_DETAILS=true
export DEEPCODERX_LOG_TOOL_DETAILS=true
export DEEPCODERX_LOG_CONVERSATION_CONTEXT=true
export DEEPCODERX_LOG_INTERACTION_TRACKING=true
export DEEPCODERX_LOG_STRUCTURED_STORAGE=true
export DEEPCODERX_DEBUG_MODE=true

echo "✅ Enhanced logging enabled:"
echo "   - Model prompts: ON"
echo "   - Model responses: ON"
echo "   - Semantic analysis: ON"
echo "   - Tool execution: ON"
echo "   - Conversation context: ON"
echo ""
echo "📁 Logs will be saved to: logs/model_interactions/"
echo ""

# Start DeepCoderX
echo "🚀 Launching DeepCoderX..."
python3 app.py "$@"
