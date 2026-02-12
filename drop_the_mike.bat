@echo off
title DROP THE MIKE
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo =====================================================
    echo   PYTHON NOT FOUND
    echo =====================================================
    echo.
    echo Please install Python from Microsoft Store:
    echo.
    echo   1. Click Start menu
    echo   2. Type "Microsoft Store" and open it
    echo   3. Search for "Python 3.11"
    echo   4. Click "Get" to install
    echo   5. After installation, run this file again
    echo.
    echo =====================================================
    echo.
    pause
    exit /b 1
)

REM Check for customtkinter
python -c "import customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo =====================================================
        echo   INSTALLATION FAILED
        echo =====================================================
        echo.
        echo Could not install the required packages.
        echo Try running: pip install customtkinter
        echo.
        pause
        exit /b 1
    )
)

REM Run the application
start "" pythonw drop_the_mike.py
