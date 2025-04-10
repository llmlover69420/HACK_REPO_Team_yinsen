# PowerShell script to create Python virtual environment for Jarvis

Write-Host "Creating Python virtual environment for Jarvis..." -ForegroundColor Green

# Check if python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Create venv directory if it doesn't exist
if (-not (Test-Path -Path ".venv_jarvis")) {
    New-Item -ItemType Directory -Path ".venv_jarvis" -Force | Out-Null
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv_jarvis

# Activate virtual environment and install requirements
Write-Host "Activating virtual environment and installing packages..." -ForegroundColor Yellow
& .\.venv_jarvis\Scripts\Activate.ps1

# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
python -m pip install -r requirements.txt

Write-Host "Virtual environment created and requirements installed!" -ForegroundColor Green
Write-Host "To activate the environment, run: .\.venv_jarvis\Scripts\Activate.ps1" -ForegroundColor Cyan

# Create .env file if it doesn't exist
if (-not (Test-Path -Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
# OpenAI API Key
OPENAI_API_KEY=your_api_key_here
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "Created .env file. Please update it with your OpenAI API key." -ForegroundColor Cyan
}

Write-Host "Setup complete!" -ForegroundColor Green
