# Quick Start Guide

## 🚀 Fastest Setup

**Windows:**
```powershell
python setup.py
run.bat
```

**Linux/Mac:**
```bash
python3 setup.py
./run.sh
```

**Docker:**
```bash
docker-compose build
docker-run.bat    # Windows
./docker-run.sh   # Linux/Mac
```

## 📝 Quick Reference

## For Windows Users (PowerShell)

### Option 1: Using Docker (Recommended)

1. **Make sure Docker Desktop is installed and running**

2. **Build the Docker image:**
   ```powershell
   docker-compose build
   ```

3. **Run the GUI:**
   ```powershell
   docker-compose run --rm fractal-visualizer python gui.py
   ```

   Or use the helper script:
   ```powershell
   .\docker-run.bat
   ```

### Option 2: Local Setup (Without Docker)

1. **Run the setup script:**
   ```powershell
   .\setup.bat
   ```

2. **Activate virtual environment:**
   ```powershell
   .venv\Scripts\activate
   ```

3. **Run the GUI:**
   ```powershell
   python app\gui.py
   ```

## For Linux/Mac Users

### Option 1: Using Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   docker-compose build
   ```

2. **Run with GUI support:**
   ```bash
   # Enable X11 forwarding (one time)
   xhost +local:docker

   # Run the GUI
   ./docker-run.sh
   ```

### Option 2: Local Setup (Without Docker)

1. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

3. **Run the GUI:**
   ```bash
   python app/gui.py
   ```

## Troubleshooting

### "ModuleNotFoundError: No module named 'PIL'"

**Solution with Docker:**
```powershell
# Rebuild the image
docker-compose build --no-cache
```

**Solution locally:**
```powershell
# Activate venv and reinstall
.venv\Scripts\activate
pip install -r app\requirements.txt
```

### GUI Not Showing (Docker on Linux/Mac)

Make sure X11 forwarding is enabled:
```bash
xhost +local:docker
export DISPLAY=:0
```

### FFmpeg Not Found

**Docker:** FFmpeg is included - no action needed.

**Local:** Install FFmpeg:
- Windows: Download from https://ffmpeg.org/download.html
- Linux: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`

