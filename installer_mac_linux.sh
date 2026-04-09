#!/bin/bash
# Set exit on error mode (optional)
set -e

echo "====================================="
echo " Installing dependencies and setup"
echo "====================================="

# Change to script directory
cd "$(dirname "$0")"

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Error: failed to create virtual environment. Make sure Python 3 is installed."
        exit 1
    fi
    echo "Virtual environment created."
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error installing dependencies."
        exit 1
    fi
    echo "Dependencies installed."
else
    echo "requirements.txt not found. Skipping dependency installation."
fi