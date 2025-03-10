#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from req.txt
pip3 install -r req.txt

# Check if tkinter is installed
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "tkinter is not installed. Installing tkinter..."
    brew install tkinter
else
    echo "tkinter is already installed."
fi

echo "Setup complete."