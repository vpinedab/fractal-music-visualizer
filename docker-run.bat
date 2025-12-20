@echo off
REM Windows batch script to run the Docker container

docker-compose run --rm fractal-visualizer python gui.py

