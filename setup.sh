#!/bin/bash
# Setup script for Google Workspace MCP Server

set -e

echo "🚀 Google Workspace MCP Server Setup"
echo "===================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and install dependencies
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check for OAuth credentials
CRED_PATH="$HOME/google-workspace-mcp/client_secret.json"
if [ ! -f "$CRED_PATH" ]; then
    echo ""
    echo "⚠️  OAuth credentials not found at $CRED_PATH"
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Create a new project (or select existing)"
    echo "3. Enable these APIs:"
    echo "   - Gmail API"
    echo "   - Google Drive API"
    echo "   - Google Calendar API"
    echo "   - Google Docs API"
    echo "   - Google Sheets API"
    echo "   - Google Slides API"
    echo "   - Google Forms API"
    echo "   - Google Tasks API"
    echo "4. Create OAuth 2.0 credentials (Desktop app)"
    echo "5. Download the JSON and save to: $CRED_PATH"
    echo ""
    read -p "Press Enter when you've completed these steps..."
fi

if [ -f "$CRED_PATH" ]; then
    echo "✅ OAuth credentials found"

    # Run authentication
    echo ""
    echo "🔐 Starting authentication..."
    python3 authenticate.py

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "📝 Next steps:"
        echo "1. Add this to your Claude Code/Desktop config:"
        echo ""
        echo '   "google-workspace-full": {'
        echo '     "type": "stdio",'
        echo "     \"command\": \"$HOME/google-drive-shared-mcp/venv/bin/python3\","
        echo "     \"args\": [\"$HOME/google-drive-shared-mcp/server.py\"],"
        echo '     "env": {}'
        echo '   }'
        echo ""
        echo "2. Restart Claude Code/Desktop"
        echo "3. Start using the MCP server!"
    fi
else
    echo ""
    echo "❌ Setup incomplete - OAuth credentials not found"
    echo "Please download credentials from Google Cloud Console"
    exit 1
fi
