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

# Installs pyinstaller
Write-Host "Installing PyInstaller..."
pip install pyinstaller

# Exe creation
Write-Host "Creating exe file..."
pyinstaller --onefile --windowed --icon="ytd-icon.ico" --name="YouTubeDownloader" --add-data "views\main.kv;views" main.py

# Check if exe was created
if (Test-Path ".\dist\YouTubeDownloader.exe") {
    Write-Host "Exe file created in .\dist\YouTubeDownloader.exe"
} else {
    Write-Host "Error while creating exe file"
}

# Deactivates venv
deactivate