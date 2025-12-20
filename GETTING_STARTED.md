# Getting Started - Fractal Music Visualizer

## 🎯 For New Users (GitHub Clone)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd fractal-music-visualizer
```

### Step 2: Run Setup (One Command!)
```bash
# Windows
python setup.py

# Linux/Mac
python3 setup.py
```

### Step 3: Run the Application
```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

**That's it!** The application will launch.

## 📝 What the Setup Does

The `setup.py` script automatically:
1. ✅ Checks Python version (needs 3.8+)
2. ✅ Creates a virtual environment (`.venv`)
3. ✅ Installs all dependencies from `app/requirements.txt`
4. ✅ Creates platform-specific run scripts (`run.bat` or `run.sh`)
5. ✅ Checks for FFmpeg (optional but recommended)

## 🚀 Running the Application

### GUI Mode (Default)
```bash
# Windows
run.bat
# or
python run.py

# Linux/Mac
./run.sh
# or
python3 run.py
```

### CLI Mode
```bash
python run.py cli
```

### Player Mode
```bash
python run.py player
```

## 🎵 Adding Your Music

1. Place audio files (`.wav`, `.mp3`, `.flac`) in:
   ```
   app/assets/music/
   ```

2. Launch the GUI and select your file

3. Click "Generate Video"

4. Wait for generation (progress bar shows status)

5. Click "Play Visualization" to watch!

## ❓ Troubleshooting

### "python: command not found"
- Use `python3` instead
- Or install Python from https://www.python.org/

### "ModuleNotFoundError"
- Run `python setup.py` first
- Make sure you're in the project directory

### "FFmpeg not found"
- Install FFmpeg (optional but recommended)
- Or use Docker (FFmpeg included)

### GUI doesn't open
- Make sure you have a display environment
- On Linux, ensure X11 is running

## 🐳 Alternative: Docker

If you prefer Docker:

```bash
docker-compose build
docker-compose run --rm fractal-visualizer python gui.py
```

## 📚 More Information

- **[README.md](README.md)** - Project overview
- **[INSTALL.md](INSTALL.md)** - Detailed installation guide
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference

---

**Happy visualizing! 🎨🎵**

