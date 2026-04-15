#!/bin/bash

# Feishu Bot Start Script - SSE Mode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Feishu Bot (SSE Mode)..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $python_version"

# Check if dependencies are installed
if ! python3 -c "import aiohttp" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo ""
echo "✅ Starting bot in SSE mode on http://0.0.0.0:8080"
echo "📊 Health check: http://localhost:8080/health"
echo "📡 Connection mode: Event Subscription (SSE)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 bot_sse.py
