#!/bin/bash
"""
DeepCoderX Enhanced Logging Auto-Setup

This script will help you permanently enable enhanced logging.
"""

echo "🔧 DeepCoderX Enhanced Logging Auto-Setup"
echo "========================================"

# Detect current shell
CURRENT_SHELL=$(basename "$SHELL")
echo "Detected shell: $CURRENT_SHELL"

# Determine config file
case $CURRENT_SHELL in
    "zsh")
        CONFIG_FILE="$HOME/.zshrc"
        ;;
    "bash")
        CONFIG_FILE="$HOME/.bashrc"
        if [ ! -f "$CONFIG_FILE" ]; then
            CONFIG_FILE="$HOME/.bash_profile"
        fi
        ;;
    *)
        CONFIG_FILE="$HOME/.profile"
        ;;
esac

echo "Configuration file: $CONFIG_FILE"

# Enhanced logging environment variables
LOGGING_VARS="
# DeepCoderX Enhanced Logging Configuration
export DEEPCODERX_LOG_MODEL_PROMPTS=true
export DEEPCODERX_LOG_MODEL_RESPONSES=true
export DEEPCODERX_LOG_SEMANTIC_DETAILS=true
export DEEPCODERX_LOG_TOOL_DETAILS=true
export DEEPCODERX_LOG_CONVERSATION_CONTEXT=true
export DEEPCODERX_LOG_INTERACTION_TRACKING=true
export DEEPCODERX_LOG_STRUCTURED_STORAGE=true"

# Check if already configured
if grep -q "DEEPCODERX_LOG_MODEL_PROMPTS" "$CONFIG_FILE" 2>/dev/null; then
    echo ""
    echo "⚠️  DeepCoderX logging variables already exist in $CONFIG_FILE"
    echo "Do you want to update them? (y/n)"
    read -r response
    if [[ "$response" != "y" && "$response" != "Y" ]]; then
        echo "Skipping update."
        exit 0
    fi
    
    # Remove existing DeepCoderX logging configuration
    echo "Removing existing configuration..."
    sed -i.backup '/# DeepCoderX Enhanced Logging Configuration/,/export DEEPCODERX_LOG_STRUCTURED_STORAGE=true/d' "$CONFIG_FILE"
fi

# Add configuration
echo ""
echo "Adding enhanced logging configuration to $CONFIG_FILE..."

# Backup existing file
cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

# Add the configuration
echo "$LOGGING_VARS" >> "$CONFIG_FILE"

echo ""
echo "✅ Configuration added successfully!"
echo ""
echo "📋 Added variables:"
echo "   - DEEPCODERX_LOG_MODEL_PROMPTS=true"
echo "   - DEEPCODERX_LOG_MODEL_RESPONSES=true"  
echo "   - DEEPCODERX_LOG_SEMANTIC_DETAILS=true"
echo "   - DEEPCODERX_LOG_TOOL_DETAILS=true"
echo "   - DEEPCODERX_LOG_CONVERSATION_CONTEXT=true"
echo "   - DEEPCODERX_LOG_INTERACTION_TRACKING=true"
echo "   - DEEPCODERX_LOG_STRUCTURED_STORAGE=true"
echo ""
echo "🔄 To apply immediately, run:"
echo "   source $CONFIG_FILE"
echo ""
echo "Or open a new terminal window."
echo ""
echo "🎯 Enhanced logging will now be enabled automatically every time you start DeepCoderX!"
