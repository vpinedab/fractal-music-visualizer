#!/bin/bash
# Helper script to run the Docker container with proper X11 forwarding for GUI

# Check if running on Linux/Mac
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    # Allow X11 connections
    xhost +local:docker 2>/dev/null || true

    # Run with X11 forwarding
    docker-compose run --rm \
        -e DISPLAY=$DISPLAY \
        -v /tmp/.X11-unix:/tmp/.X11-unix \
        fractal-visualizer python run.py

    # Revoke X11 access
    xhost -local:docker 2>/dev/null || true
else
    # Windows - use docker-compose directly
    docker-compose run --rm fractal-visualizer python run.py
fi

