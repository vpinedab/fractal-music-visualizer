# Setup Guide - Fractal Music Visualizer

This guide provides multiple ways to set up and run the Fractal Music Visualizer.

## 🚀 Quick Setup (Recommended)

### Option 1: One-Command Setup (Easiest)

**Windows:**
```powershell
python setup.py
```

**Linux/Mac:**
```bash
python3 setup.py
```

This will:
- ✅ Check Python version (3.8+ required)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create run scripts (`run.bat` or `run.sh`)
- ✅ Check for FFmpeg

Then run:
- **Windows:** `run.bat` or `python run.py`
- **Linux/Mac:** `./run.sh` or `python3 run.py`

### Option 2: Docker (No Local Setup Required)

**Prerequisites:** Docker and Docker Compose installed

**Windows:**
```powershell
docker-compose build
docker-run.bat
```

**Linux/Mac:**
```bash
docker-compose build
./docker-run.sh
```

Docker includes all dependencies including FFmpeg!

### Option 3: Manual Setup

1. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

## 📋 System Requirements

### Required
- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
- **pip** (usually comes with Python)

### Optional (but recommended)
- **FFmpeg** - Required for adding audio to videos
  - Windows: [Download](https://ffmpeg.org/download.html) or use Docker
  - Linux: `sudo apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`

## 🎯 Running the Application

### GUI Mode (Default)
```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# Or directly
python run.py
```

### CLI Mode
```bash
python run.py cli
```

### Player Mode
```bash
python run.py player
```

## 🐳 Docker Setup (Detailed)

### Building the Image
```bash
docker-compose build
```

### Running with Docker

**Windows:**
```powershell
docker-run.bat
```

**Linux/Mac (with X11 forwarding for GUI):**
```bash
./docker-run.sh
```

**Or manually:**
```bash
docker-compose run --rm fractal-visualizer python gui.py
```

### Docker Benefits
- ✅ All dependencies pre-installed
- ✅ FFmpeg included
- ✅ Consistent environment across platforms
- ✅ No local Python setup required

## 🔧 Troubleshooting

### "Python not found"
- Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Make sure Python is in your PATH

### "ModuleNotFoundError"
- Run `python setup.py` to install dependencies
- Or manually: `pip install -r app/requirements.txt`

### "FFmpeg not found"
- Install FFmpeg or use Docker (FFmpeg included)
- Videos will generate without audio if FFmpeg is missing

### GUI doesn't open (Linux)
- Ensure X11 is running
- For Docker: Use `./docker-run.sh` which handles X11 forwarding

### Permission errors (Linux/Mac)
- Make scripts executable: `chmod +x setup.sh run.sh docker-run.sh`

## 📁 Project Structure

```
fractal-music-visualizer/
├── app/
│   ├── gui.py              # Main GUI application
│   ├── main.py             # CLI version
│   ├── fractals.py         # Fractal generation algorithms
│   ├── audio_features.py   # Audio analysis
│   ├── video_manager.py    # Video management system
│   ├── requirements.txt    # Python dependencies
│   └── assets/
│       ├── music/          # Place your audio files here
│       └── output/
│           ├── frames/     # Temporary frame storage
│           └── videos/     # Generated videos
├── setup.py                # Universal setup script
├── run.py                  # Main entry point
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose config
├── setup.bat / setup.sh    # Platform-specific setup
├── docker-run.bat / .sh    # Docker run scripts
└── README.md               # Main documentation
```

## ✅ Verification

After setup, verify everything works:

1. **Check dependencies:**
   ```bash
   python run.py help
   ```

2. **Test GUI:**
   ```bash
   python run.py gui
   ```

3. **Add audio files:**
   - Place `.wav`, `.mp3`, or `.flac` files in `app/assets/music/`

4. **Generate a video:**
   - Open GUI
   - Select an audio file
   - Click "Generate Video"
   - Wait for completion
   - Click "Play Visualization"

## 🆘 Getting Help

If you encounter issues:
1. Check this guide's troubleshooting section
2. Verify Python version: `python --version` (should be 3.8+)
3. Check dependencies: `pip list`
4. Try Docker if local setup fails
5. Check the [README.md](README.md) for more information

## 📝 Notes

- Generated videos are stored in `app/assets/output/videos/`
- Each video has metadata stored in `app/assets/output/videos/metadata.json`
- The virtual environment (`.venv`) is created locally and should not be committed to Git
- Run scripts (`run.bat`, `run.sh`) are generated by `setup.py` and can be regenerated

