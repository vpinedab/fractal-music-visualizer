#!/usr/bin/env python3
"""
Main entry point for Fractal Music Visualizer.
This script handles both GUI and CLI modes, and ensures proper environment setup.
"""

import sys
import os
from pathlib import Path

# Add app directory to Python path
APP_DIR = Path(__file__).parent / "app"
sys.path.insert(0, str(APP_DIR))

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    required = [
        'numpy', 'PIL', 'librosa', 'soundfile',
        'pygame', 'numba', 'imageio', 'cv2'
    ]

    for module in required:
        try:
            if module == 'PIL':
                __import__('PIL')
            elif module == 'cv2':
                __import__('cv2')
            else:
                __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print("ERROR: Missing required dependencies:")
        for m in missing:
            print(f"  - {m}")
        print("\nPlease run the setup script first:")
        print("  python setup.py")
        print("\nOr install manually:")
        print("  pip install -r requirements.txt")
        return False
    return True

def main():
    """Main entry point."""
    # Change to app directory for relative imports
    original_dir = os.getcwd()
    app_dir = Path(__file__).parent / "app"

    try:
        # Change to app directory
        os.chdir(app_dir)

        # Check dependencies
        if not check_dependencies():
            sys.exit(1)

        # Parse command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
        else:
            mode = 'gui'  # Default to GUI

        if mode == 'gui':
            # Run GUI
            try:
                from gui import FractalMusicGUI
                import tkinter as tk

                root = tk.Tk()
                app = FractalMusicGUI(root)
                root.mainloop()
            except ImportError as e:
                print(f"Import error: {e}")
                print("Make sure all dependencies are installed:")
                print("  python setup.py")
                sys.exit(1)

        elif mode == 'cli' or mode == 'main':
            # Run CLI version
            try:
                from main import main as cli_main
                cli_main()
            except ImportError as e:
                print(f"Import error: {e}")
                sys.exit(1)

        elif mode == 'player':
            # Run player
            try:
                from pygame_player import main as player_main
                player_main()
            except ImportError as e:
                print(f"Import error: {e}")
                sys.exit(1)

        elif mode == 'help' or mode == '--help' or mode == '-h':
            print("Fractal Music Visualizer")
            print("\nUsage:")
            print("  python run.py [mode]")
            print("\nModes:")
            print("  gui     - Launch GUI interface (default)")
            print("  cli     - Run command-line version")
            print("  player  - Run visualization player")
            print("  help    - Show this help message")
            print("\nExamples:")
            print("  python run.py          # Launch GUI")
            print("  python run.py gui      # Launch GUI")
            print("  python run.py cli      # Run CLI version")

        else:
            print(f"Unknown mode: {mode}")
            print("Run 'python run.py help' for usage information")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()

