#!/bin/bash

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies from req.txt
pip install -r req.txt

# Run the PeopleCounter.py file
python PeopleCounter.py