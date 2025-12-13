# Fractal Music Visualizer

Audio-reactive fractal visualization system implemented in Python and containerized with Docker.

## Motivation
This project explores the connection between mathematical fractals and music by mapping audio features to visual parameters in real time.

## Technologies
- Python
- NumPy
- Pillow
- Docker

## Project structure
```text
app/        # Core application code
Dockerfile # Container definition

### Fractal generation

The project implements fractal sets using the escape-time algorithm.
Mandelbrot sets are used as an initial baseline to validate rendering and containerization,
while Julia sets are used as the main visual component due to their sensitivity to parameter changes.

## Project status

- [x] Dockerized Python environment
- [x] Static fractal generation (Mandelbrot)
- [x] Animated fractal generation
- [ ] Julia set implementation
- [ ] Audio feature extraction
- [ ] Audio-reactive visualization




