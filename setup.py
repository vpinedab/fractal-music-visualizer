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
    python_cmd = get_python_command()
    requirements = Path("requirements.txt")

    if not requirements.exists():
        print(f"ERROR: {requirements} not found")
        print(f"Current directory: {os.getcwd()}")
        return False

    print("Upgrading pip...")
    try:
        subprocess.run([str(python_cmd), "-m", "pip", "install", "--upgrade", "pip"],
                      check=True, capture_output=True)
        print("✓ pip upgraded")
    except subprocess.CalledProcessError as e:
        print("WARNING: Failed to upgrade pip, continuing anyway...")
        print(f"  Error: {e}")

    print("Installing dependencies from requirements.txt...")
    print("  This may take a few minutes...")
    try:
        result = subprocess.run(
            [str(pip_cmd), "install", "-r", str(requirements)],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ All dependencies installed successfully")

        # Verify critical dependencies
        print("\nVerifying critical dependencies...")
        critical_deps = ['numpy', 'PIL', 'librosa', 'imageio', 'imageio_ffmpeg']
        for dep in critical_deps:
            try:
                if dep == 'PIL':
                    __import__('PIL')
                elif dep == 'imageio_ffmpeg':
                    __import__('imageio_ffmpeg')
                else:
                    __import__(dep)
                print(f"  ✓ {dep}")
            except ImportError:
                print(f"  ✗ {dep} - WARNING: Failed to import")

        return True
    except subprocess.CalledProcessError as e:
        print("ERROR: Failed to install dependencies")
        print(f"  Error output: {e.stderr if hasattr(e, 'stderr') else 'Unknown error'}")
        print("\nTry installing manually:")
        print(f"  {pip_cmd} install -r {requirements}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is available (bundled or system)."""
    # First check if imageio-ffmpeg is available (bundled FFmpeg)
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_exe and os.path.exists(ffmpeg_exe):
            print("✓ FFmpeg available (via imageio-ffmpeg)")
            return True
    except (ImportError, Exception):
        pass

    # Fallback: check for system FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"],
                      capture_output=True, check=True)
        print("✓ FFmpeg is installed (system)")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Only warn if imageio-ffmpeg is not installed yet
        # (it will be installed by install_dependencies)
        try:
            import imageio_ffmpeg
            # If we can import it, FFmpeg should be available after install
            print("ℹ FFmpeg will be available via imageio-ffmpeg (installed with dependencies)")
            return True
        except ImportError:
            # This shouldn't happen if dependencies are installed, but just in case
            print("ℹ Note: FFmpeg is optional (for adding audio to videos)")
            print("  The imageio-ffmpeg package (installed with dependencies) includes FFmpeg")
            print("  System FFmpeg not found, but bundled version should work")
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

    # Check FFmpeg (optional but recommended) - after dependencies are installed
    # Use venv Python to check for imageio-ffmpeg
    python_cmd = get_python_command()
    try:
        result = subprocess.run(
            [str(python_cmd), "-c", "import imageio_ffmpeg; import os; exe = imageio_ffmpeg.get_ffmpeg_exe(); print('OK' if exe and os.path.exists(exe) else 'NOT_FOUND')"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout.strip() == "OK":
            print("✓ FFmpeg available (via imageio-ffmpeg)")
        else:
            # Check system FFmpeg
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
                print("✓ FFmpeg is installed (system)")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("ℹ Note: FFmpeg is optional (for adding audio to videos)")
                print("  The imageio-ffmpeg package (installed with dependencies) includes FFmpeg")
    except Exception:
        # Fallback to simple check
        check_ffmpeg()

    # Create run scripts
    create_run_scripts()

    print()
    print("=" * 60)
    print("Setup complete! ✓")
    print("=" * 60)
    print()
    print("📌 IMPORTANT: All dependencies are now installed.")
    print("   The virtual environment is ready to use.")
    print()
    print("To run the application:")
    print()
    if platform.system() == "Windows":
        print("  Option 1: Use the run script (recommended)")
        print("    .\\run.bat         # Launch GUI")
        print("    .\\run.bat cli     # Run CLI version")
        print("    .\\run.bat player # Run player")
        print()
        print("  Option 2: Activate venv and run directly")
        print("    .venv\\Scripts\\activate")
        print("    python run.py")
    else:
        print("  Option 1: Use the run script (recommended)")
        print("    ./run.sh          # Launch GUI")
        print("    ./run.sh cli      # Run CLI version")
        print("    ./run.sh player   # Run player")
        print()
        print("  Option 2: Activate venv and run directly")
        print("    source .venv/bin/activate")
        print("    python run.py")
    print()
    print("📝 Note: Make sure to place audio files in:")
    print("    app/assets/music/")
    print()

if __name__ == "__main__":
    main()

