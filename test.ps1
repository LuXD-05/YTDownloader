# Checks python installation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found (make sure it's installed and in PATH)"
    exit 1
}

# Creates venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating venv..."
    python -m venv venv
}

# Activates venv
Write-Host "Activating venv..."
. .\venv\Scripts\Activate.ps1

# Installs dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Exec tests
Write-Host "Executing tests..."
pytest --maxfail=5 --disable-warnings -v

# Deactivates venv
deactivate