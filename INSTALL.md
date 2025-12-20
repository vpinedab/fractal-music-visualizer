# Installation Guide

Complete installation instructions for Fractal Music Visualizer.

## Prerequisites

### Required
- **Python 3.8 or higher**
  - Check version: `python --version` or `python3 --version`
  - Download: [python.org](https://www.python.org/downloads/)
- **pip** (usually included with Python)
  - Check: `pip --version`

### Optional (but recommended)
- **FFmpeg** - For adding audio to generated videos
  - Windows: [Download](https://ffmpeg.org/download.html)
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`
  - **Note:** Docker includes FFmpeg automatically

## Installation Methods

### Method 1: Automated Setup (Recommended)

This is the easiest method and works on all platforms.

**Windows:**
```powershell
python setup.py
```

**Linux/Mac:**
```bash
python3 setup.py
```

The script will:
1. Check Python version
2. Create virtual environment (`.venv`)
3. Install all dependencies
4. Create platform-specific run scripts
5. Check for FFmpeg

**Then run:**
- Windows: `run.bat` or `python run.py`
- Linux/Mac: `./run.sh` or `python3 run.py`

### Method 2: Docker

Best for users who want to avoid local Python setup.

**Prerequisites:** Docker and Docker Compose

**Build and run:**
```bash
# Build the image
docker-compose build

# Run (Windows)
docker-run.bat

# Run (Linux/Mac)
./docker-run.sh
```

**Benefits:**
- No local Python installation needed
- All dependencies pre-installed
- FFmpeg included
- Consistent environment

### Method 3: Manual Installation

For advanced users who prefer manual control.

1. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

3. **Install dependencies:**
   ```bash
   pip install -r app/requirements.txt
   ```

4. **Run:**
   ```bash
   python run.py
   ```

## Verification

After installation, verify everything works:

```bash
# Check help
python run.py help

# Test GUI
python run.py gui
```

## Adding Audio Files

Place your audio files in:
```
app/assets/music/
```

Supported formats: `.wav`, `.mp3`, `.flac`, `.ogg`

## Troubleshooting

### Python Not Found
- Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Add Python to PATH during installation
- Restart terminal after installation

### ModuleNotFoundError
- Run `python setup.py` to install dependencies
- Or manually: `pip install -r app/requirements.txt`
- Make sure virtual environment is activated

### FFmpeg Not Found
- Install FFmpeg (see Prerequisites)
- Or use Docker (FFmpeg included)
- Videos will generate without audio if FFmpeg is missing

### GUI Doesn't Open (Linux)
- Ensure X11 is running
- For Docker: Use `./docker-run.sh` for X11 forwarding
- Check DISPLAY variable: `echo $DISPLAY`

### Permission Errors (Linux/Mac)
```bash
chmod +x setup.sh
chmod +x run.sh
chmod +x docker-run.sh
```

### Virtual Environment Issues
- Delete `.venv` folder and run `python setup.py` again
- Make sure you're using the correct Python version

## Next Steps

1. **Add audio files** to `app/assets/music/`
2. **Run the GUI:** `run.bat` (Windows) or `./run.sh` (Linux/Mac)
3. **Select an audio file** from the list
4. **Customize settings** (optional)
5. **Generate video** and enjoy!

For more information, see:
- [README.md](README.md) - Main documentation
- [SETUP.md](SETUP.md) - Detailed setup guide
- [QUICKSTART.md](QUICKSTART.md) - Quick reference
