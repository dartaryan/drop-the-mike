# ============================================================
# DROP THE MIKE - Local Build Script (Windows)
# Creates a ready-to-share ZIP with the app + FFmpeg bundled
#
# Usage:   .\build_local.ps1
# Output:  release\DropTheMike-Windows.zip
#          release\DropTheMike-Setup.exe  (if Inno Setup installed)
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  DROP THE MIKE - Local Build" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# --- 1. Check prerequisites ---
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python not found. Install from Microsoft Store or python.org" -ForegroundColor Red
    exit 1
}

# --- 2. Install build dependencies ---
Write-Host "[2/6] Installing build dependencies..." -ForegroundColor Cyan
Write-Host "  Upgrading pip..." -ForegroundColor Gray
python -m pip install --upgrade pip --quiet 2>$null
Write-Host "  Installing packages (using source builds to bypass network restrictions)..." -ForegroundColor Gray
python -m pip install pyinstaller pillow customtkinter --no-cache-dir --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Retrying with source-only builds..." -ForegroundColor Yellow
    python -m pip install pyinstaller pillow customtkinter --no-binary :all: --no-cache-dir --quiet
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Could not install dependencies. Your network may be blocking PyPI downloads." -ForegroundColor Red
    Write-Host "Try running this first: python -m pip install pyinstaller pillow customtkinter" -ForegroundColor Yellow
    exit 1
}

# --- 3. Convert icon ---
Write-Host "[3/6] Converting app icon..." -ForegroundColor Cyan

$iconScript = @'
from PIL import Image
img = Image.open("android-chrome-512x512.png")
sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
img.save("icon.ico", format="ICO", sizes=sizes)
print("  Created icon.ico")
'@

$iconScript | python

# --- 4. Build with PyInstaller ---
Write-Host "[4/6] Building with PyInstaller (about 30 seconds)..." -ForegroundColor Cyan
python -m PyInstaller drop_the_mike.spec --noconfirm 2>&1 | Out-Null
if (-not (Test-Path "dist\DropTheMike\DropTheMike.exe")) {
    Write-Host "ERROR: PyInstaller build failed" -ForegroundColor Red
    exit 1
}
Write-Host "  Build complete" -ForegroundColor Green

# --- 5. Download FFmpeg ---
Write-Host "[5/6] Downloading FFmpeg LGPL..." -ForegroundColor Cyan

$ffmpegDir = "dist\DropTheMike\ffmpeg"
if (-not (Test-Path $ffmpegDir)) { New-Item -ItemType Directory -Path $ffmpegDir | Out-Null }

if (-not (Test-Path "$ffmpegDir\ffmpeg.exe")) {
    $ffmpegUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip"
    Write-Host "  Downloading from BtbN/FFmpeg-Builds..."
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile "ffmpeg_download.zip" -UseBasicParsing
    Expand-Archive -Path "ffmpeg_download.zip" -DestinationPath "ffmpeg_temp" -Force
    Copy-Item "ffmpeg_temp\ffmpeg-master-latest-win64-lgpl\bin\ffmpeg.exe" "$ffmpegDir\"
    Copy-Item "ffmpeg_temp\ffmpeg-master-latest-win64-lgpl\bin\ffprobe.exe" "$ffmpegDir\"
    Remove-Item "ffmpeg_download.zip" -Force
    Remove-Item "ffmpeg_temp" -Recurse -Force
    Write-Host "  FFmpeg downloaded" -ForegroundColor Green
} else {
    Write-Host "  FFmpeg already present, skipping download" -ForegroundColor Yellow
}

# --- 6. Create output ---
Write-Host "[6/6] Creating distributable packages..." -ForegroundColor Cyan

$releaseDir = "release"
if (-not (Test-Path $releaseDir)) { New-Item -ItemType Directory -Path $releaseDir | Out-Null }

# Create ZIP (portable, always works)
$zipPath = "$releaseDir\DropTheMike-Windows.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "dist\DropTheMike\*" -DestinationPath $zipPath
Write-Host "  Created: $zipPath" -ForegroundColor Green

# Create installer (only if Inno Setup is installed)
$iscc = "C:\Program Files (x86)\Inno Setup 6\iscc.exe"
if (Test-Path $iscc) {
    & $iscc /DMyAppVersion=1.0.0 /DSourceDir=dist\DropTheMike installer.iss /Q
    if (Test-Path "Output\DropTheMike-Setup.exe") {
        Move-Item "Output\DropTheMike-Setup.exe" "$releaseDir\DropTheMike-Setup.exe" -Force
        Remove-Item "Output" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Created: $releaseDir\DropTheMike-Setup.exe" -ForegroundColor Green
    }
} else {
    Write-Host "  Inno Setup not found - skipping installer (ZIP is still available)" -ForegroundColor Yellow
    Write-Host "  Install from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
}

# --- Done ---
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  BUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ready to share:" -ForegroundColor White
Get-ChildItem $releaseDir | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 1)
    Write-Host ("  {0}  ({1} MB)" -f $_.Name, $sizeMB) -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Send the ZIP to anyone - they extract and double-click DropTheMike.exe" -ForegroundColor Yellow
Write-Host ""
