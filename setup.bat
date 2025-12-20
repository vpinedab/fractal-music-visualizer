@echo off
REM Windows setup script for local development (without Docker)

echo Setting up Fractal Music Visualizer...

REM Check Python version
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.12 or later.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check for ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo WARNING: ffmpeg not found. Please install ffmpeg for video generation.
    echo Download from https://ffmpeg.org/download.html
)

echo Setup complete!
echo To run the GUI: python run.py

