# 🎵 Fractal Music Visualizer

Audio-reactive fractal visualization system that generates beautiful fractal animations synchronized with music.

## ✨ Features

- 🎨 **Audio-Reactive Visualizations**: Fractals that respond to music in real-time
- 🎬 **Video Generation**: Export as MP4 with synchronized audio
- 🎛️ **Full Customization**: Resolution, FPS, colors, iterations, formula parameters
- 🔄 **Rotation & Dynamic Effects**: Rotating fractals with dynamic dimension growth
- 📹 **Video Management**: Multiple videos per audio file with thumbnails and metadata
- 🎨 **Custom Color Palettes**: Create your own color schemes
- 🚀 **Optimized Performance**: Numba JIT compilation for fast generation
- 🖥️ **Modern GUI**: Intuitive interface with real-time preview

## 🚀 Quick Start

### Option 1: One-Command Setup (Easiest)

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

### Option 2: Docker (No Local Setup)

```bash
docker-compose build
docker-run.bat    # Windows
./docker-run.sh   # Linux/Mac
```

## 📋 Requirements

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **FFmpeg** (optional, for video with audio) - Included in Docker

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Complete setup guide
- **[INSTALL.md](INSTALL.md)** - Detailed installation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference

## 🎯 Usage

1. **Add audio files** to `app/assets/music/`
2. **Run the GUI**: `run.bat` (Windows) or `./run.sh` (Linux/Mac)
3. **Select an audio file**
4. **Customize settings** (optional)
5. **Generate video** and enjoy!

## 🎨 Customization Options

- **Resolution**: 800x600 to 4K
- **FPS**: 24-120 fps
- **Iterations**: 50-1000 (affects quality)
- **Color Palettes**: Presets or custom colors
- **Formula Parameters**: Power (z^p), Z offset, C base
- **Rotation**: Enable rotation with adjustable velocity
- **Dynamic Dimensions**: Zoom effect per frame

## 🐳 Docker

Docker includes all dependencies including FFmpeg:

```bash
docker-compose build
docker-run.bat    # Windows
./docker-run.sh   # Linux/Mac
```

## 📁 Project Structure

```
fractal-music-visualizer/
├── app/
│   ├── gui.py              # Main GUI
│   ├── fractals.py          # Fractal algorithms
│   ├── video_manager.py    # Video management
│   └── assets/
│       ├── music/           # Audio files
│       └── output/videos/  # Generated videos
├── setup.py                 # Setup script
├── run.py                   # Entry point
└── Dockerfile               # Docker config
```

## 🔧 Troubleshooting

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## 📝 License

MIT License - See [LICENSE](LICENSE)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Enjoy creating beautiful fractal visualizations! 🎨🎵**

