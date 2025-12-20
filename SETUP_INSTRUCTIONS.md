# Setup Instructions for GitHub Users

## 🎯 Quick Setup (3 Steps)

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd fractal-music-visualizer
```

### 2. Run Setup Script
```bash
# Windows
python setup.py

# Linux/Mac
python3 setup.py
```

### 3. Run the Application
```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

## ✅ What You Get

After running `setup.py`, you'll have:
- ✅ Virtual environment with all dependencies installed
- ✅ Platform-specific run scripts (`run.bat` or `run.sh`)
- ✅ Everything ready to use!

## 📋 Requirements

- **Python 3.8+** (check with `python --version`)
- **FFmpeg** (optional, for video with audio)

## 🚀 Usage Examples

### Launch GUI
```bash
run.bat          # Windows
./run.sh         # Linux/Mac
python run.py    # Any platform
```

### Run CLI Version
```bash
python run.py cli
```

### Run Player
```bash
python run.py player
```

## 🔧 If Something Goes Wrong

### "ModuleNotFoundError"
**Solution:** Run `python setup.py` to install dependencies

### "python: command not found"
**Solution:** Use `python3` instead, or install Python

### "FFmpeg not found"
**Solution:** Install FFmpeg (optional) or use Docker

## 🐳 Docker Alternative

If you prefer Docker:
```bash
docker-compose build
docker-compose run --rm fractal-visualizer python gui.py
```

## 📁 Project Files Explained

- `setup.py` - **Run this first!** Sets up everything
- `run.py` - Main entry point (handles GUI/CLI/Player)
- `run.bat` / `run.sh` - Convenience scripts (created by setup.py)
- `app/requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration

## 🎵 Next Steps

1. Add audio files to `app/assets/music/`
2. Run `run.bat` (Windows) or `./run.sh` (Linux/Mac)
3. Select audio file and generate visualization!

---

**That's all you need to know!** The setup script handles everything automatically.

