#!/bin/bash

echo "Starting Jarvis using Docker..."

# Move to project root directory
cd "$(dirname "$0")/.." || exit

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat <<EOL > .env
# OpenAI API Key
OPENAI_API_KEY=your_api_key_here
EOL
    echo "Created .env file. Please update it with your OpenAI API key."
fi

# Create Dockerfile if it doesn't exist
if [ ! -f "Dockerfile" ]; then
    echo "Creating Dockerfile..."
    cat <<EOL > Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    mpg321 \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \\
    && pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Make scripts executable
RUN chmod +x ./scripts/*.sh

# Set Python path
ENV PYTHONPATH=/app:\$PYTHONPATH

# Expose port for API
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--reload"]
EOL
    echo "Created Dockerfile."
fi

'''
# Build Docker image
echo "Building Docker image..."
docker build -t jarvis-app .

# Run Docker container
echo "Running Jarvis in Docker container..."
docker run -it --rm \
    -p 8000:8000 \
    -v "$(pwd):/app" \
    --env-file .env \
    --name jarvis-container \
    jarvis-app

echo "Docker container stopped."
'''