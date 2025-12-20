# Fractal Music Visualizer

Audio-reactive fractal visualization system that generates beautiful fractal animations synchronized with music.

## 🚀 Quick Start

### One-Command Installation

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

**Or use Docker (no local setup needed):**
```bash
docker-compose build
docker-run.bat    # Windows
./docker-run.sh   # Linux/Mac
```

That's it! The setup script will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Set up run scripts
- ✅ Check for FFmpeg

**See [SETUP.md](SETUP.md) for detailed setup instructions.**

## 📋 Prerequisites

- **Python 3.8+** (check with `python --version`)
- **FFmpeg** (optional, for video with audio) - [Download](https://ffmpeg.org/download.html)

## 🎯 Usage

### GUI Mode (Recommended)

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

## 🎨 Features

- **Audio-Reactive Visualization**: Fractals that respond to music in real-time
- **Customizable**: Adjust resolution, FPS, colors, iterations, and more
- **Multiple Presets**: Auto-selects best preset based on audio characteristics
- **Video Generation**: Export as MP4 with synchronized audio
- **Modern GUI**: Intuitive interface with real-time preview

## 📁 Project Structure

```
fractal-music-visualizer/
├── app/
│   ├── gui.py              # GUI interface
│   ├── main.py             # CLI version
│   ├── fractals.py         # Fractal algorithms
│   ├── audio_features.py   # Audio analysis
│   └── assets/
│       ├── music/          # Place audio files here
│       └── output/         # Generated videos
├── run.py                  # Main entry point
├── setup.py                # Installation script
└── Dockerfile              # Docker support
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
docker-compose build
docker-compose run --rm fractal-visualizer python gui.py
```

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Complete setup guide with all methods
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide

## 🛠️ Development

### Setup Development Environment

```bash
# Install dependencies
python setup.py

# Activate virtual environment
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate
```

### Running Tests

```bash
python run.py cli      # Test CLI
python run.py gui      # Test GUI
```

## 🎵 Adding Audio Files

Place your audio files (`.wav`, `.mp3`, `.flac`) in:
```
app/assets/music/
```

## 🎬 Generating Visualizations

1. Launch the GUI: `run.bat` or `./run.sh`
2. Select an audio file
3. Customize settings (optional)
4. Click "Generate Video"
5. Wait for generation to complete
6. Click "Play Visualization" to watch!

## 🔧 Troubleshooting

### "ModuleNotFoundError"
Run the setup script: `python setup.py`

### "FFmpeg not found"
Install FFmpeg or use Docker (FFmpeg included)

### GUI doesn't open
- Ensure you have a display environment
- On Linux, X11 must be running

See [INSTALL.md](INSTALL.md) for more troubleshooting tips.

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⭐ Features in Detail

- **Fractal Types**: Mandelbrot and Julia sets
- **Audio Analysis**: RMS energy and spectral centroid
- **Real-time Sync**: Frame-perfect audio-visual synchronization
- **Custom Palettes**: Choose colors or use presets
- **Dynamic Dimensions**: Zoom effect per frame
- **Quality Presets**: Low to Ultra quality settings
- **Video Export**: MP4 with embedded audio

---

**Enjoy creating beautiful fractal visualizations! 🎨🎵**
