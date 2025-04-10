# PowerShell script to run Jarvis in virtual environment

Write-Host "Starting Jarvis in virtual environment..." -ForegroundColor Green

# Move to project root directory (already handled by PowerShell's working directory)
# The current script's directory is $PSScriptRoot
Set-Location (Split-Path -Parent $PSScriptRoot)

# Check if virtual environment exists
if (-not (Test-Path -Path ".venv_jarvis")) {
    Write-Host "Error: Virtual environment not found. Please run create_venv.ps1 first" -ForegroundColor Red
    exit 1
}

# Activate virtual environment and run Jarvis
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv_jarvis\Scripts\Activate.ps1

# Add the current directory to Python path
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# Run the main script
Write-Host "Running Jarvis..." -ForegroundColor Green
& .\scripts\run.ps1

# Deactivate virtual environment when done
deactivate
