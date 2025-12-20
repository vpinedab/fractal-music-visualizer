#!/bin/bash
# Setup script for local development (without Docker)

echo "Setting up Fractal Music Visualizer..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for system dependencies
echo "Checking system dependencies..."
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: ffmpeg not found. Please install ffmpeg for video generation."
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
fi

echo "Setup complete!"
echo "To run the GUI: python run.py"

