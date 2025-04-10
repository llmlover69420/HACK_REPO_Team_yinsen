#!/bin/bash

echo "Creating Python virtual environment for Jarvis..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# Install system dependencies based on OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing Linux system dependencies..."
    if ! command -v mpg321 &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y mpg321
    else
        echo "mpg321 is already installed"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Windows detected"
fi

# Create venv directory if it doesn't exist
mkdir -p .venv_jarvis

# Create virtual environment
python3 -m venv .venv_jarvis

# Activate virtual environment and install requirements
source .venv_jarvis/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install PyTorch (CPU version)
#echo "Installing CPU version of PyTorch..."
#pip install torch torchvision torchaudio

# Install all other requirements
pip install -r requirements.txt


echo "Virtual environment created and requirements installed!"
echo "To activate the environment, run: source .venv_jarvis/bin/activate"

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat <<EOL > .env
# OpenAI API Key
OPENAI_API_KEY=your_api_key_here
EOL
    echo "Created .env file. Please update it with your OpenAI API key."
fi

# Make script executable
chmod +x "$(dirname "$0")/download_models.sh"
echo "You can learn more about Whisper models by running: ./scripts/download_models.sh" 

sudo chmod +x ./*
sudo chmod -R 755 ./*

