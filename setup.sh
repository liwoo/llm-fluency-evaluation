#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it to add your API keys."
fi

echo "Setup complete! To run the script, execute: python multi_llm.py"
