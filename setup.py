#!/usr/bin/env python3
"""
Universal setup script for Fractal Music Visualizer.
Works on Windows, Linux, and macOS.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print("✓ pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pip is not available")
        return False

def create_venv():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path(".venv")
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return True

    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✓ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to create virtual environment")
        return False

def get_pip_command():
    """Get the pip command based on platform."""
    if platform.system() == "Windows":
        return Path(".venv") / "Scripts" / "pip.exe"
    else:
        return Path(".venv") / "bin" / "pip"

def get_python_command():
    """Get the Python command based on platform."""
    if platform.system() == "Windows":
        return Path(".venv") / "Scripts" / "python.exe"
    else:
        return Path(".venv") / "bin" / "python"

def install_dependencies():
    """Install Python dependencies."""
    pip_cmd = get_pip_command()
    requirements = Path("app") / "requirements.txt"

    if not requirements.exists():
        print(f"ERROR: {requirements} not found")
        return False

    print("Upgrading pip...")
    try:
        subprocess.run([str(pip_cmd), "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError:
        print("WARNING: Failed to upgrade pip, continuing anyway...")

    print("Installing dependencies...")
    try:
        subprocess.run([str(pip_cmd), "install", "-r", str(requirements)], check=True)
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install dependencies")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"],
                      capture_output=True, check=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ WARNING: FFmpeg not found")
        print("  FFmpeg is required for video generation with audio")
        print("  Install from: https://ffmpeg.org/download.html")
        return False

def create_run_scripts():
    """Create platform-specific run scripts."""
    if platform.system() == "Windows":
        # Create .bat file
        bat_content = """@echo off
call .venv\\Scripts\\activate.bat
python run.py %*
"""
        with open("run.bat", "w") as f:
            f.write(bat_content)
        print("✓ Created run.bat")
    else:
        # Create shell script
        sh_content = """#!/bin/bash
source .venv/bin/activate
python run.py "$@"
"""
        with open("run.sh", "w") as f:
            f.write(sh_content)
        os.chmod("run.sh", 0o755)
        print("✓ Created run.sh")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Fractal Music Visualizer - Setup")
    print("=" * 60)
    print()

    # Check prerequisites
    if not check_python_version():
        sys.exit(1)

    if not check_pip():
        sys.exit(1)

    # Create virtual environment
    if not create_venv():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Check FFmpeg (optional but recommended)
    check_ffmpeg()

    # Create run scripts
    create_run_scripts()

    print()
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print()
    print("To run the application:")
    if platform.system() == "Windows":
        print("  run.bat          # Launch GUI")
        print("  run.bat cli       # Run CLI version")
        print("  run.bat player    # Run player")
    else:
        print("  ./run.sh          # Launch GUI")
        print("  ./run.sh cli      # Run CLI version")
        print("  ./run.sh player   # Run player")
    print()
    print("Or use Python directly:")
    print("  python run.py")
    print()

if __name__ == "__main__":
    main()

