# PowerShell script to run the main agent

# Add the current directory to Python path
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# Load environment variables from .env file if it exists
if (Test-Path -Path ".env") {
    Write-Host "Loading environment variables from .env file" -ForegroundColor Green
    Get-Content -Path ".env" | ForEach-Object {
        # Skip empty lines and comments
        if ($_ -match "^[^#]" -and $_ -ne "") {
            # Split the line into name and value
            $name, $value = $_ -split '=', 2
            # Set environment variable
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            # Print variable name without showing its value for security
            Write-Host "Loaded: $name" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "No .env file found. Please create one with OPENAI_API_KEY=your-api-key" -ForegroundColor Red
}

# Set environment variables
$env:CONFIG_PATH = "$PWD\config\config.yaml"
Write-Host "CONFIG_PATH: $env:CONFIG_PATH" -ForegroundColor Yellow

# Check if required directories exist
$requiredDirs = @("data\sounds", "models", "logs")
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Yellow
    }
}

# Check if config file exists
if (-not (Test-Path -Path $env:CONFIG_PATH)) {
    Write-Host "Error: Config file not found at $env:CONFIG_PATH" -ForegroundColor Red
    exit 1
}

# Start the main application
Write-Host "Starting Jarvis..." -ForegroundColor Green
python .\main.py
