#!/bin/bash
# Script to run the main agent

# Add these lines at the beginning of the script, before any Python code is executed
export PYTHONPATH=$(pwd):$PYTHONPATH

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    # Use a while loop to read each line in the .env file
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        if [[ ! -z "$line" && ! "$line" =~ ^# ]]; then
            # Export the environment variable
            export "$line"
            # Print variable name without showing its value for security
            var_name=$(echo "$line" | cut -d= -f1)
            echo "Loaded: $var_name"
        fi
    done < .env
else
    echo "No .env file found. Please create one with OPENAI_API_KEY=your-api-key"
fi

# Set environment variables
export CONFIG_PATH="${PWD}/config/config.yaml"
echo "CONFIG_PATH: $CONFIG_PATH"

# Check if required directories exist
required_dirs=("data/sounds" "models" "logs")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "Created directory: $dir"
    fi
done

# Check if config file exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Error: Config file not found at $CONFIG_PATH"
    exit 1
fi

# Start the main application
echo "Starting Jarvis..."
python3 ./main.py
