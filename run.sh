#!/bin/bash

# Mini-Bot TTS System Startup Script
# This script activates the virtual environment and starts the Flask application

echo "================================================"
echo "🤖 Starting Mini-Bot TTS System..."
echo "================================================"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✓ Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if required system packages are installed
echo "✓ Checking system dependencies..."
if ! command -v mpg123 &> /dev/null; then
    echo "⚠ mpg123 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y mpg123
fi

# Create audio directory if it doesn't exist
if [ ! -d "static/audio" ]; then
    echo "✓ Creating audio directory..."
    mkdir -p static/audio
fi

# Start the Flask application
echo "✓ Starting Flask application..."
echo "================================================"
echo "Access the application at:"
echo "  Local: http://localhost:5000"
echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
echo "================================================"
echo ""

python app.py
