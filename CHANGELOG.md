# Changelog

All notable changes to Fractal Music Visualizer will be documented in this file.

## [2.0.0] - 2024-12-19

### Added
- Modern GUI with comprehensive customization options
- Video management system with multiple videos per audio file
- Video thumbnails in horizontal grid layout
- Video deletion functionality
- Video duration display
- Z and C offset sliders for formula customization
- Rotation feature with velocity control
- Custom color palette support
- Dynamic dimension growth feature
- Audio synchronization in generated videos
- Fullscreen video player with controls
- Progress tracking during generation
- Comprehensive setup scripts for all platforms
- Docker support with FFmpeg included
- Detailed documentation (SETUP.md, INSTALL.md, QUICKSTART.md)

### Changed
- Optimized fractal generation with Numba JIT compilation
- Direct MP4 video output (no PNG frames)
- Improved performance with precomputed complex planes
- Better error handling and user feedback
- Enhanced video storage system with metadata

### Fixed
- FFmpeg detection and audio merging
- Video player controls (play, pause, rewind, forward)
- Fullscreen video stretching
- Audio playback synchronization
- Video list initialization order
- Custom color palette application

## [1.0.0] - Initial Release

- Basic fractal generation
- Audio-reactive visualization
- CLI and basic GUI
- PNG frame output

