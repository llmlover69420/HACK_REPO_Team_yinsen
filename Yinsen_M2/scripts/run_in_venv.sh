#!/bin/bash

echo "Starting Jarvis in virtual environment..."

# Move to project root directory
cd "$(dirname "$0")/.." || exit

# Check if virtual environment exists
if [ ! -d ".venv_jarvis" ]; then
    echo "Error: Virtual environment not found. Please run create_venv.sh first"
    exit 1
fi

# Activate virtual environment and run Jarvis
source ./.venv_jarvis/bin/activate

#pip3 install -r requirements.txt

# Add this line after activating the virtual environment but before running any Python code
export PYTHONPATH=$(pwd):$PYTHONPATH

./scripts/run.sh

# Deactivate virtual environment when done
deactivate 