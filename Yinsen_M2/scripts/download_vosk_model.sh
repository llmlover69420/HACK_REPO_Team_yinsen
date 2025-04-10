#!/bin/bash

# Download and prepare the Vosk model
mkdir -p models
cd models

echo "Downloading Vosk small English model..."
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.22.zip

echo "Extracting model..."
unzip vosk-model-small-en-us-0.22.zip

echo "Clean up..."
rm vosk-model-small-en-us-0.22.zip

echo "Vosk model downloaded and prepared."
echo "Model is available at: models/vosk-model-small-en-us-0.22" 