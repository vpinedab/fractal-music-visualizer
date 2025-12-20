# Fractal Music Visualizer

🎨🎵 Audio-reactive fractal visualization system that generates beautiful fractal animations synchronized with music.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- **Audio-Reactive Visualization**: Fractals that respond to music in real-time
- **Multiple Fractal Types**: Julia Sets and IFS (Iterated Function Systems) fractals
  - Julia Sets: Customizable power, Z offsets, C base parameters, and rotation
  - IFS Fractals: Barnsley Fern, Sierpinski, Dragon, and Spiral presets
- **Customizable**: Adjust resolution, FPS, colors, iterations, rotation, and more
- **Smart Presets**: Auto-selects best preset based on audio characteristics
- **Video Generation**: Export as MP4 with synchronized audio
- **Modern GUI**: Intuitive interface with centered title and organized layout
- **Audio Trimming**: Process specific segments of audio files with fine adjustment buttons
- **Audio Normalization**: Option to normalize audio volume for better visualization
- **Fine Controls**: +/- buttons for precise adjustment of sensitivity, start time, and end time
- **Waveform Following**: Direct audio waveform interpretation for more responsive visuals
- **Video Management**: View all generated videos with thumbnails, duration, and fractal type
- **Stop Generation**: Cancel video generation mid-process if needed

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher** (check with `python --version` or `python3 --version`)
- **pip** (usually included with Python)
- **Internet connection** (for downloading dependencies)

### Installation

**Step 1: Clone or download this repository**

```bash
git clone <repository-url>
cd fractal-music-visualizer
```

**Step 2: Run the setup script**

**Windows:**
```powershell
python setup.py
```

**Linux/Mac:**
```bash
python3 setup.py
```

The setup script will automatically:
- ✅ Check Python version (3.8+ required)
- ✅ Create a virtual environment (`.venv`)
- ✅ Install all Python dependencies from `requirements.txt`
- ✅ Install FFmpeg (bundled via `imageio-ffmpeg` - no system install needed)
- ✅ Create platform-specific run scripts (`run.bat` or `run.sh`)
- ✅ Verify all dependencies are installed correctly

**Step 3: Run the application**

**Windows:**
```powershell
.\run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

That's it! The GUI will launch automatically.

> **Note:** On first run, you may need to add audio files to `app/assets/music/` directory.

## 📖 Usage

### GUI Mode (Recommended)

**After running setup.py, launch the GUI:**

**Windows:**
```powershell
.\run.bat
# or
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

**Or run directly (with venv activated):**

**Windows:**
```powershell
.venv\Scripts\activate
python run.py
```

**Linux/Mac:**
```bash
source .venv/bin/activate
python run.py
```

**Steps:**
1. Click "Refresh" to load audio files from `app/assets/music/`
2. Select an audio file and click "✓ Confirm"
3. Choose fractal type (Julia Sets or IFS) using the buttons at the top
4. Customize settings (optional):
   - **Video Settings**: FPS, resolution, iterations, color palette, dynamic dimensions
   - **Audio Settings**: 
     - Sensitivity (use +/- buttons for fine adjustment)
     - Normalize Audio checkbox (reduces clipping)
     - Enable Trimming with start/end time (use +/- buttons for precise control)
   - **Fractal Formula** (Julia Sets only):
     - Power (z^p + c formula)
     - Z Offset (Real and Imaginary parts)
     - C Base (Real and Imaginary parts)
     - Rotation (enable with rotation velocity)
5. Click "🎬 Generate Video" (use "⏹ Stop" button to cancel if needed)
6. Wait for generation to complete (progress bar shows status)
7. Click "▶ Play" to watch your visualization!
8. Browse generated videos in the "Available Videos" section with thumbnails

### CLI Mode

```bash
# Windows
.\run.bat cli

# Linux/Mac
./run.sh cli

# Or with venv activated
python run.py cli
```

### Player Mode

```bash
# Windows
.\run.bat player

# Linux/Mac
./run.sh player

# Or with venv activated
python run.py player
```

## 🎵 Adding Audio Files

Place your audio files (`.wav`, `.mp3`, `.flac`) in:
```
app/assets/music/
```

The application will automatically detect and list them.

## 🎨 Fractal Types

### Julia Sets
- Classic complex plane fractals
- Customizable power, offsets, and rotation
- Audio-reactive parameter modulation

### IFS Fractals
- Iterated Function Systems with multiple presets:
  - **Barnsley Fern**: Classic fern structure
  - **Sierpinski**: Triangular fractal pattern
  - **Dragon**: Dragon curve fractal (improved visibility with optimized settings)
  - **Spiral**: Spiral patterns (improved visibility with optimized settings)
- Transform-based generation
- Audio-reactive transformation parameters
- Optional rotation control (rotations per second: -1.0 to 1.0)
- Improved point density and brightness for better visibility

Note: IFS preset selection and rotation controls are only visible when "IFS" fractal type is selected.

## ⚙️ Configuration

### Video Settings
- **FPS**: 24, 30, 60, or 120 frames per second
- **Resolution**: Presets from 480p to 4K, or custom
- **Iterations**: Quality presets (Low/Medium/High/Ultra) or custom
- **Color Palette**: Multiple presets or custom colors
- **Dynamic Dimensions**: Optional zoom effect per frame

### Audio Settings
- **Sensitivity**: Control how much audio affects fractals (0.1x to 20x)
  - Use +/- buttons for fine adjustments (0.1x increments)
- **Normalize Audio**: Checkbox to normalize audio volume, preventing clipping for clearer visualizations
- **Trimming**: Process specific time segments (e.g., 20-30 seconds)
  - Enable trimming checkbox to activate
  - Use +/- buttons for precise start/end time adjustments (0.1s increments)

### Fractal Formula (Julia Sets)
- **Power**: Exponent for z^p + c formula (1.0 to 10.0) - adjustable slider
- **Z Offset**: Real and imaginary offsets (-2.0 to 2.0) - separate sliders for each
- **C Base**: Base complex parameter (-2.0 to 2.0) - separate sliders for real and imaginary parts
- **Rotation**: Enable constant rotation (rotations per second: -1.0 to 1.0)

Note: These controls are only visible when "Julia Sets" fractal type is selected.

## 🐳 Docker Alternative

If you prefer Docker (no local Python setup needed):

```bash
docker-compose build
docker-run.bat    # Windows
./docker-run.sh   # Linux/Mac
```

## 📁 Project Structure

```
fractal-music-visualizer/
├── app/
│   ├── gui.py              # Main GUI interface
│   ├── main.py             # CLI version
│   ├── fractals.py         # Fractal algorithms (Julia & IFS)
│   ├── audio_features.py   # Audio analysis and waveform extraction
│   ├── preset_selector.py  # Auto preset selection
│   ├── video_manager.py    # Video metadata management
│   ├── pygame_player.py    # Video player
│   └── assets/
│       ├── music/          # Place audio files here
│       └── output/
│           ├── frames/     # Generated frames (gitignored)
│           └── videos/     # Generated videos (gitignored)
├── run.py                  # Main entry point
├── setup.py                # Installation script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Troubleshooting

### "ModuleNotFoundError"
Run the setup script: `python setup.py`

### "FFmpeg not found"
FFmpeg is included via `imageio-ffmpeg` package. If you still get errors:
- The setup script installs it automatically
- Or install manually: `pip install imageio-ffmpeg`

### GUI doesn't open
- Ensure you have a display environment
- On Linux, X11 must be running
- Try running from terminal to see error messages

### Audio trimming not working
- Make sure start time < end time
- The trimmed segment will be processed correctly

### Performance issues
- Reduce resolution or FPS
- Lower iteration count
- Disable dynamic dimensions

### Video paths or metadata issues
- All paths are stored as relative paths for portability
- If you see path-related errors, the metadata will automatically migrate on first run
- Generated videos are stored in `app/assets/output/videos/` (gitignored)

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
python run.py player   # Test player
```

## 📝 Dependencies

All dependencies are **automatically installed** by `setup.py`. No manual installation needed!

### Python Packages (installed via `requirements.txt`)

- **numpy** (≥1.24.0): Numerical computing and array operations
- **Pillow** (≥10.0.0): Image processing and manipulation
- **librosa** (≥0.10.0): Audio analysis, feature extraction, and waveform processing
- **soundfile** (≥0.12.0): Audio file I/O (reads WAV, MP3, FLAC, etc.)
- **pygame** (≥2.5.0): Audio playback and synchronization
- **numba** (≥0.58.0): JIT compilation for fast fractal computation
- **imageio** (≥2.31.0): Video generation and frame writing
- **imageio-ffmpeg** (≥0.4.9): FFmpeg integration (includes bundled FFmpeg binary)
- **opencv-python** (≥4.8.0): Video player and frame reading

### System Dependencies

**None required!** All dependencies are Python packages:
- FFmpeg is bundled via `imageio-ffmpeg` (no system install needed)
- Tkinter (for GUI) is included with most Python installations
- All other functionality is pure Python with compiled extensions

### Installation Verification

After running `setup.py`, you can verify installation:
```bash
# Activate venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# Check installed packages
pip list

# Test imports
python -c "import numpy, PIL, librosa, imageio, pygame, numba, cv2; print('All dependencies OK!')"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⭐ Features in Detail

- **Audio Analysis**: RMS energy, spectral centroid, and waveform extraction
- **Real-time Sync**: Frame-perfect audio-visual synchronization
- **Custom Palettes**: Choose colors or use presets
- **Dynamic Dimensions**: Optional zoom effect per frame
- **Quality Presets**: Low to Ultra quality settings
- **Video Export**: MP4 with embedded audio
- **Multiple Fractals**: Julia Sets and IFS fractals
- **Rotation Control**: Constant rotation speed for Julia Sets and IFS
- **Audio Trimming**: Process specific segments with fine time controls
- **Audio Normalization**: Prevent clipping and improve visualization clarity
- **Waveform Following**: Direct audio waveform interpretation
- **Julia Sets Controls**: Full parameter control (power, offsets, rotation)
- **IFS Presets**: Multiple fractal types with improved visibility
- **Fine Adjustment Buttons**: Precise controls for sensitivity and trimming times
- **Video List Display**: Browse all videos with thumbnails, duration, and fractal type
- **Generation Cancellation**: Stop video generation at any time

---

## 📦 Installation Summary

**For new users:**
1. Clone/download this repository
2. Run `python setup.py` (or `python3 setup.py` on Linux/Mac)
3. Run `.\run.bat` (Windows) or `./run.sh` (Linux/Mac)
4. Add audio files to `app/assets/music/`
5. Start creating!

**That's it!** Everything is automated. No manual dependency installation needed.

---

**Enjoy creating beautiful fractal visualizations! 🎨🎵**
