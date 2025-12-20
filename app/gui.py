"""
Modern GUI interface for the Fractal Music Visualizer.
Provides file selection, frame generation, and playback controls with customization options.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
import threading
import queue
import os
import sys
from PIL import Image, ImageTk
import librosa

# Import project modules
from audio_features import extract_features, audio_profile
from fractals import JULIA_PRESETS, julia_audio_frames_2d, PALETTES
from preset_selector import choose_preset_name
from pygame_player import run_player, list_audio_files, count_frames
from video_manager import (
    VIDEOS_ROOT, ensure_video_directories, register_video,
    get_videos_for_audio, get_all_videos, delete_video, get_video_filename
)

# Constants
APP_ROOT = Path(__file__).resolve().parent
MUSIC_DIR = APP_ROOT / "assets" / "music"
FRAMES_ROOT = APP_ROOT / "assets" / "output" / "frames"
DEFAULT_FPS = 60

# Ensure video directories exist
ensure_video_directories()


class FractalMusicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractal Music Visualizer")
        self.root.geometry("1200x1000")
        self.root.resizable(True, True)

        # Configure style
        self.setup_style()

        # State
        self.current_audio_path = None
        self.audio_info = {}
        self.generation_thread = None
        self.is_generating = False
        self.message_queue = queue.Queue()

        # Customization settings
        self.settings = {
            'fps': tk.IntVar(value=60),
            'palette': tk.StringVar(value='auto'),
            'intensity': tk.DoubleVar(value=1.0),
            'power': tk.DoubleVar(value=2.0),
            'width': tk.IntVar(value=800),
            'height': tk.IntVar(value=600),
            'resolution_preset': tk.StringVar(value='800x600'),
            'dynamic_dimensions': tk.BooleanVar(value=False),
            'dimension_factor': tk.DoubleVar(value=1.001),
            'custom_main_color': tk.StringVar(value='#FF0000'),
            'custom_accent_color': tk.StringVar(value='#0000FF'),
            'use_custom_palette': tk.BooleanVar(value=False),
            'quality_preset': tk.StringVar(value='high'),
            'max_iterations': tk.IntVar(value=400),  # Default iterations
            'use_custom_iterations': tk.BooleanVar(value=False),  # Custom iterations checkbox
            'z_real': tk.DoubleVar(value=0.0),  # Z offset (real part)
            'z_imag': tk.DoubleVar(value=0.0),  # Z offset (imaginary part)
            'c_base_real': tk.DoubleVar(value=0.0),  # C base offset (real part)
            'c_base_imag': tk.DoubleVar(value=0.0),  # C base offset (imaginary part)
            'rotation_enabled': tk.BooleanVar(value=False),  # Enable rotation
            'rotation_velocity': tk.DoubleVar(value=0.1),  # Rotation velocity (radians per frame)
        }

        # Resolution presets (standard video resolutions supported by imageio/ffmpeg)
        self.resolution_presets = {
            '320x240': (320, 240),    # QVGA
            '640x480': (640, 480),    # VGA
            '800x600': (800, 600),    # SVGA
            '1280x720': (1280, 720),  # HD (720p)
            '1920x1080': (1920, 1080), # Full HD (1080p)
            '2560x1440': (2560, 1440), # 2K/QHD
            '3840x2160': (3840, 2160), # 4K/UHD
        }

        # Check for messages from background threads
        self.root.after(100, self.check_queue)

        self.setup_ui()
        self.refresh_audio_list()
        # refresh_video_list will be called after UI setup is complete

        # Set initial resolution
        self.on_resolution_preset_change()

        # Set initial iterations based on quality preset
        quality = self.settings['quality_preset'].get()
        quality_iterations = {
            'low': 200,
            'medium': 300,
            'high': 400,
            'ultra': 500,
        }
        if quality in quality_iterations:
            self.settings['max_iterations'].set(quality_iterations[quality])

    def setup_style(self):
        """Configure modern styling."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure('Title.TLabel', font=('Segoe UI', 20, 'bold'), foreground='#2c3e50')
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 9), foreground='#7f8c8d')
        style.configure('Custom.TButton', font=('Segoe UI', 10))

    def setup_ui(self):
        """Create the main UI layout."""
        # Main container
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_container,
            text="🎵 Fractal Music Visualizer 🎨",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Left column: File selection and info
        left_frame = ttk.Frame(main_container)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Right column: Customization options
        right_frame = ttk.Frame(main_container)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)

        self.setup_file_section(left_frame)
        self.setup_customization_section(right_frame)
        self.setup_controls_section(main_container)
        self.setup_video_preview_section(main_container)  # Video preview at bottom

        # Load videos after UI is fully set up
        self.refresh_video_list()

    def setup_file_section(self, parent):
        """Setup file selection and info display."""
        # Audio Selection
        audio_frame = ttk.LabelFrame(parent, text="Audio Selection", padding="12")
        audio_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        audio_frame.columnconfigure(1, weight=1)

        ttk.Label(audio_frame, text="File:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.audio_path_var = tk.StringVar()
        audio_entry = ttk.Entry(audio_frame, textvariable=self.audio_path_var, state="readonly")
        audio_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        browse_btn = ttk.Button(audio_frame, text="Browse...", command=self.browse_audio, style='Custom.TButton')
        browse_btn.grid(row=0, column=2)

        # Audio List
        list_frame = ttk.LabelFrame(parent, text="Available Files", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.audio_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10, font=('Segoe UI', 9))
        self.audio_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.audio_listbox.bind('<<ListboxSelect>>', self.on_audio_select)
        scrollbar.config(command=self.audio_listbox.yview)

        refresh_btn = ttk.Button(list_frame, text="🔄 Refresh", command=self.refresh_audio_list)
        refresh_btn.grid(row=1, column=0, pady=(8, 0))

        # File Info Panel
        info_frame = ttk.LabelFrame(parent, text="File Information", padding="12")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        self.info_labels = {}
        info_fields = [
            ('name', 'Name:'),
            ('duration', 'Duration:'),
            ('sample_rate', 'Sample Rate:'),
            ('tempo', 'Tempo:'),
            ('energy', 'Energy:'),
            ('brightness', 'Brightness:'),
        ]

        for i, (key, label) in enumerate(info_fields):
            ttk.Label(info_frame, text=label, style='Heading.TLabel').grid(row=i, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            value_label = ttk.Label(info_frame, text="—", style='Info.TLabel')
            value_label.grid(row=i, column=1, sticky=tk.W, pady=2)
            self.info_labels[key] = value_label


    def setup_customization_section(self, parent):
        """Setup customization controls."""
        # Video Settings
        video_frame = ttk.LabelFrame(parent, text="Video Settings", padding="12")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        video_frame.columnconfigure(1, weight=1)

        # FPS with dropdown
        ttk.Label(video_frame, text="Frames per Second:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        fps_frame = ttk.Frame(video_frame)
        fps_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        fps_presets = ['24', '30', '60', '120']
        fps_combo = ttk.Combobox(fps_frame, values=fps_presets, state='readonly', width=8)
        fps_combo.set('60')
        fps_combo.grid(row=0, column=0, padx=(0, 5))

        def on_fps_preset_change(event=None):
            if fps_combo.get():
                self.settings['fps'].set(int(fps_combo.get()))

        fps_combo.bind('<<ComboboxSelected>>', on_fps_preset_change)

        # Also allow custom input via spinbox
        fps_spin = ttk.Spinbox(fps_frame, from_=24, to=120, textvariable=self.settings['fps'], width=8,
                              command=lambda: fps_combo.set('') if str(self.settings['fps'].get()) not in fps_presets else None)
        fps_spin.grid(row=0, column=1, padx=(0, 5))
        ttk.Label(fps_frame, text="(24-120)", style='Info.TLabel').grid(row=0, column=2, padx=(5, 0))

        # Resolution with dropdown only (no custom option)
        ttk.Label(video_frame, text="Resolution:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        res_combo = ttk.Combobox(video_frame, textvariable=self.settings['resolution_preset'],
                                 values=list(self.resolution_presets.keys()), state='readonly', width=18)
        res_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        res_combo.bind('<<ComboboxSelected>>', self.on_resolution_preset_change)

        # Dynamic dimensions
        dynamic_frame = ttk.Frame(video_frame)
        dynamic_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        dynamic_check = ttk.Checkbutton(dynamic_frame, text="Dynamic Dimensions (zoom per frame)",
                                       variable=self.settings['dynamic_dimensions'])
        dynamic_check.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        factor_frame = ttk.Frame(dynamic_frame)
        factor_frame.grid(row=0, column=1, sticky=tk.W)
        ttk.Label(factor_frame, text="Factor:", style='Info.TLabel').grid(row=0, column=0, padx=(0, 5))
        factor_spin = ttk.Spinbox(factor_frame, from_=1.0001, to=1.01, textvariable=self.settings['dimension_factor'],
                                 width=8, increment=0.0001, format="%.4f")
        factor_spin.grid(row=0, column=1)

        # Iterations (combined quality and iterations)
        ttk.Label(video_frame, text="Iterations:", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        iter_frame = ttk.Frame(video_frame)
        iter_frame.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Iterations dropdown with preset names showing iteration counts
        iter_presets = ['Low (200)', 'Medium (300)', 'High (400)', 'Ultra (500)']
        iter_combo = ttk.Combobox(iter_frame, values=iter_presets, state='readonly', width=14)
        iter_combo.set('High (400)')
        iter_combo.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)

        # Custom iterations checkbox
        custom_iter_check = ttk.Checkbutton(iter_frame, text="Custom",
                                           variable=self.settings['use_custom_iterations'],
                                           command=lambda: self.toggle_custom_iterations(iter_combo))
        custom_iter_check.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        # Custom iterations input (initially disabled)
        self.custom_iter_spin = ttk.Spinbox(iter_frame, from_=50, to=1000,
                                            textvariable=self.settings['max_iterations'],
                                            width=10, increment=50, state='disabled')
        self.custom_iter_spin.grid(row=0, column=2, sticky=tk.W)

        # Iterations change handler
        def on_iter_preset_change(event=None):
            if not self.settings['use_custom_iterations'].get():
                preset = iter_combo.get()
                if preset == 'Low (200)':
                    self.settings['max_iterations'].set(200)
                    self.settings['quality_preset'].set('low')
                elif preset == 'Medium (300)':
                    self.settings['max_iterations'].set(300)
                    self.settings['quality_preset'].set('medium')
                elif preset == 'High (400)':
                    self.settings['max_iterations'].set(400)
                    self.settings['quality_preset'].set('high')
                elif preset == 'Ultra (500)':
                    self.settings['max_iterations'].set(500)
                    self.settings['quality_preset'].set('ultra')
        iter_combo.bind('<<ComboboxSelected>>', on_iter_preset_change)

        # Color Palette
        color_frame = ttk.LabelFrame(parent, text="Visual Style", padding="12")
        color_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        color_frame.columnconfigure(1, weight=1)

        ttk.Label(color_frame, text="Color Palette:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        # Palette selection row
        palette_row = ttk.Frame(color_frame)
        palette_row.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        palette_combo = ttk.Combobox(palette_row, textvariable=self.settings['palette'],
                                     values=['auto'] + list(PALETTES.keys()), state='readonly', width=18)
        palette_combo.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        palette_combo.set('auto')

        # Custom Colors button - make it more visible
        custom_palette_btn = ttk.Button(palette_row, text="Custom Colors...",
                                       command=self.show_custom_palette_dialog, width=16)
        custom_palette_btn.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)

        # Color previews (show when custom colors are selected)
        preview_row = ttk.Frame(color_frame)
        preview_row.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        self.main_color_canvas = tk.Canvas(preview_row, width=32, height=24, highlightthickness=1, relief=tk.SUNKEN, bg='white')
        self.main_color_canvas.pack(side=tk.LEFT, padx=(0, 5))
        self.main_color_canvas.create_rectangle(1, 1, 31, 23, fill='#FF0000', outline='gray', width=1)

        self.accent_color_canvas = tk.Canvas(preview_row, width=32, height=24, highlightthickness=1, relief=tk.SUNKEN, bg='white')
        self.accent_color_canvas.pack(side=tk.LEFT)
        self.accent_color_canvas.create_rectangle(1, 1, 31, 23, fill='#0000FF', outline='gray', width=1)

        # Hide initially, show when custom colors are selected
        preview_row.grid_remove()
        self.preview_row = preview_row  # Store reference for showing/hiding

        # Audio Intensity
        ttk.Label(color_frame, text="Audio Sensitivity:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        intensity_frame = ttk.Frame(color_frame)
        intensity_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        intensity_frame.columnconfigure(1, weight=1)
        intensity_scale = ttk.Scale(intensity_frame, from_=0.1, to=2.0, variable=self.settings['intensity'],
                                    orient=tk.HORIZONTAL, length=200)
        intensity_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.intensity_label = ttk.Label(intensity_frame, text="1.0x", style='Info.TLabel', width=5)
        self.intensity_label.grid(row=0, column=1, padx=(10, 0))
        intensity_scale.configure(command=lambda v: self.intensity_label.config(text=f"{float(v):.1f}x"))

        # Fractal Formula
        formula_frame = ttk.LabelFrame(parent, text="Fractal Formula", padding="12")
        formula_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        formula_frame.columnconfigure(1, weight=1)

        ttk.Label(formula_frame, text="Power (z^p + c):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        power_frame = ttk.Frame(formula_frame)
        power_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        power_scale = ttk.Scale(power_frame, from_=1.0, to=10.0, variable=self.settings['power'],
                                orient=tk.HORIZONTAL, length=200)
        power_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.power_label = ttk.Label(power_frame, text="2.0", style='Info.TLabel', width=5)
        self.power_label.grid(row=0, column=1, padx=(10, 0))
        power_scale.configure(command=lambda v: self.power_label.config(text=f"{float(v):.1f}"))

        # Z offset sliders
        ttk.Label(formula_frame, text="Z Offset (Real):", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        z_real_frame = ttk.Frame(formula_frame)
        z_real_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        z_real_scale = ttk.Scale(z_real_frame, from_=-2.0, to=2.0, variable=self.settings['z_real'],
                                 orient=tk.HORIZONTAL, length=200)
        z_real_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.z_real_label = ttk.Label(z_real_frame, text="0.0", style='Info.TLabel', width=5)
        self.z_real_label.grid(row=0, column=1, padx=(10, 0))
        z_real_scale.configure(command=lambda v: self.z_real_label.config(text=f"{float(v):.2f}"))

        ttk.Label(formula_frame, text="Z Offset (Imag):", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        z_imag_frame = ttk.Frame(formula_frame)
        z_imag_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        z_imag_scale = ttk.Scale(z_imag_frame, from_=-2.0, to=2.0, variable=self.settings['z_imag'],
                                 orient=tk.HORIZONTAL, length=200)
        z_imag_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.z_imag_label = ttk.Label(z_imag_frame, text="0.0", style='Info.TLabel', width=5)
        self.z_imag_label.grid(row=0, column=1, padx=(10, 0))
        z_imag_scale.configure(command=lambda v: self.z_imag_label.config(text=f"{float(v):.2f}"))

        # C base offset sliders
        ttk.Label(formula_frame, text="C Base (Real):", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        c_real_frame = ttk.Frame(formula_frame)
        c_real_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        c_real_scale = ttk.Scale(c_real_frame, from_=-2.0, to=2.0, variable=self.settings['c_base_real'],
                                  orient=tk.HORIZONTAL, length=200)
        c_real_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.c_real_label = ttk.Label(c_real_frame, text="0.0", style='Info.TLabel', width=5)
        self.c_real_label.grid(row=0, column=1, padx=(10, 0))
        c_real_scale.configure(command=lambda v: self.c_real_label.config(text=f"{float(v):.2f}"))

        ttk.Label(formula_frame, text="C Base (Imag):", style='Heading.TLabel').grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        c_imag_frame = ttk.Frame(formula_frame)
        c_imag_frame.grid(row=4, column=1, sticky=tk.W, pady=5)
        c_imag_scale = ttk.Scale(c_imag_frame, from_=-2.0, to=2.0, variable=self.settings['c_base_imag'],
                                 orient=tk.HORIZONTAL, length=200)
        c_imag_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.c_imag_label = ttk.Label(c_imag_frame, text="0.0", style='Info.TLabel', width=5)
        self.c_imag_label.grid(row=0, column=1, padx=(10, 0))
        c_imag_scale.configure(command=lambda v: self.c_imag_label.config(text=f"{float(v):.2f}"))

        # Rotation controls
        rotation_check = ttk.Checkbutton(formula_frame, text="Enable Rotation",
                                        variable=self.settings['rotation_enabled'])
        rotation_check.grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=5)

        rotation_frame = ttk.Frame(formula_frame)
        rotation_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        ttk.Label(rotation_frame, text="Velocity:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        rotation_scale = ttk.Scale(rotation_frame, from_=0.0, to=1.0, variable=self.settings['rotation_velocity'],
                                  orient=tk.HORIZONTAL, length=150)
        rotation_scale.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.rotation_label = ttk.Label(rotation_frame, text="0.1", style='Info.TLabel', width=5)
        self.rotation_label.grid(row=0, column=2, padx=(10, 0))
        rotation_scale.configure(command=lambda v: self.rotation_label.config(text=f"{float(v):.3f}"))

    def toggle_custom_iterations(self, iter_combo):
        """Enable/disable custom iterations input based on checkbox."""
        if self.settings['use_custom_iterations'].get():
            self.custom_iter_spin.config(state='normal')
            iter_combo.config(state='disabled')
        else:
            self.custom_iter_spin.config(state='disabled')
            iter_combo.config(state='readonly')
            # Reset to current preset value
            current_iter = self.settings['max_iterations'].get()
            if current_iter == 200:
                iter_combo.set('Low (200)')
            elif current_iter == 300:
                iter_combo.set('Medium (300)')
            elif current_iter == 400:
                iter_combo.set('High (400)')
            elif current_iter == 500:
                iter_combo.set('Ultra (500)')
            else:
                iter_combo.set('High (400)')
                self.settings['max_iterations'].set(400)

    def setup_video_preview_section(self, parent):
        """Setup video list section showing all available videos."""
        # Video List Frame
        preview_frame = ttk.LabelFrame(parent, text="Available Videos", padding="12")
        preview_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)  # Allow preview to expand

        # Create canvas with scrollbar for thumbnail display
        list_frame = ttk.Frame(preview_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Use Canvas for custom thumbnail display
        self.video_canvas = tk.Canvas(list_frame, bg='#f0f0f0', highlightthickness=0)
        self.video_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.video_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.video_canvas.yview)

        # Content frame for video items
        self.video_content = ttk.Frame(self.video_canvas)
        self.video_canvas_window = self.video_canvas.create_window((0, 0), window=self.video_content, anchor=tk.NW)

        # Configure scrolling
        def configure_video_scroll(event):
            self.video_canvas.configure(scrollregion=self.video_canvas.bbox("all"))
            canvas_width = event.width
            self.video_canvas.itemconfig(self.video_canvas_window, width=canvas_width)

        self.video_content.bind('<Configure>', configure_video_scroll)
        self.video_canvas.bind('<Configure>', lambda e: self.video_canvas.itemconfig(self.video_canvas_window, width=e.width))

        # Mouse wheel scrolling
        def on_video_wheel(event):
            self.video_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.video_canvas.bind_all("<MouseWheel>", on_video_wheel)

        # Keep listbox for selection tracking (hidden)
        self.video_listbox = tk.Listbox(list_frame, height=0, width=0)
        self.video_listbox.grid_remove()  # Hide it

        # Video info display
        info_frame = ttk.Frame(preview_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Title:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.video_title_label = ttk.Label(info_frame, text="—", style='Info.TLabel')
        self.video_title_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(info_frame, text="Created:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.video_date_label = ttk.Label(info_frame, text="—", style='Info.TLabel')
        self.video_date_label.grid(row=1, column=1, sticky=tk.W)

        # Store video data
        self.video_list_data = []  # List of video info dicts
        self.selected_video = None
        self.video_thumbnails = []  # Store thumbnail references

    def setup_controls_section(self, parent):
        """Setup generation and playback controls."""
        controls_frame = ttk.Frame(parent, padding="10")
        controls_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        controls_frame.columnconfigure(1, weight=1)

        # Generate button
        self.generate_btn = ttk.Button(
            controls_frame,
            text="🎬 Generate Video",
            command=self.start_generation,
            style='Custom.TButton',
            width=20
        )
        self.generate_btn.grid(row=0, column=0, padx=(0, 10))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            controls_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Play button
        self.play_btn = ttk.Button(
            controls_frame,
            text="▶ Play",
            command=self.play_visualization,
            style='Custom.TButton',
            state="disabled",
            width=15
        )
        self.play_btn.grid(row=0, column=2)

        # Status
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Info.TLabel')
        status_label.grid(row=0, column=0, sticky=tk.W)

        self.preset_var = tk.StringVar(value="")
        preset_label = ttk.Label(status_frame, textvariable=self.preset_var, style='Info.TLabel')
        preset_label.grid(row=0, column=1, sticky=tk.E)

    def browse_audio(self):
        """Open file dialog to select audio file."""
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.ogg"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ],
            initialdir=str(MUSIC_DIR) if MUSIC_DIR.exists() else "."
        )

        if file_path:
            self.current_audio_path = Path(file_path)
            self.audio_path_var.set(str(self.current_audio_path))
            self.load_audio_info()
            self.update_ui_state()

    def refresh_audio_list(self):
        """Refresh the list of available audio files."""
        self.audio_listbox.delete(0, tk.END)

        try:
            if MUSIC_DIR.exists():
                audio_files = list_audio_files(MUSIC_DIR)
                if audio_files:
                    for audio_file in audio_files:
                        self.audio_listbox.insert(tk.END, audio_file.name)
                else:
                    self.audio_listbox.insert(tk.END, "No audio files found in assets/music/")
            else:
                self.audio_listbox.insert(tk.END, f"Directory not found: {MUSIC_DIR}")
        except Exception as e:
            self.audio_listbox.insert(tk.END, f"Error: {str(e)}")

    def refresh_video_list(self):
        """Refresh the list of available videos with thumbnails."""
        # Check if video_content exists (UI might not be fully initialized)
        if not hasattr(self, 'video_content'):
            return

        # Clear existing widgets
        for widget in self.video_content.winfo_children():
            widget.destroy()
        self.video_list_data = []
        self.video_thumbnails = []  # Store thumbnail references

        try:
            all_videos = get_all_videos()
            if all_videos:
                # Calculate number of columns based on available width (3 videos per row)
                videos_per_row = 3

                for idx, video_info in enumerate(all_videos):
                    row = idx // videos_per_row
                    col = idx % videos_per_row

                    # Create frame for video item
                    item_frame = ttk.Frame(self.video_content, relief=tk.RAISED, borderwidth=1)
                    item_frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
                    item_frame.columnconfigure(0, weight=1)

                    # Main container for thumbnail and info
                    content_container = ttk.Frame(item_frame)
                    content_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

                    # Try to load thumbnail and get duration
                    video_path = Path(video_info['path'])
                    thumbnail = None
                    duration_str = "Unknown"

                    if video_path.exists():
                        try:
                            import imageio
                            reader = imageio.get_reader(str(video_path))
                            frame = reader.get_data(0)

                            # Get video duration
                            try:
                                fps = reader.get_meta_data().get('fps', 30)
                                frame_count = reader.count_frames()
                                duration_seconds = frame_count / fps if fps > 0 else 0
                                minutes = int(duration_seconds // 60)
                                seconds = int(duration_seconds % 60)
                                duration_str = f"{minutes}:{seconds:02d}"
                            except:
                                # Fallback: try opencv
                                try:
                                    import cv2
                                    cap = cv2.VideoCapture(str(video_path))
                                    fps = cap.get(cv2.CAP_PROP_FPS)
                                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                                    cap.release()
                                    if fps > 0:
                                        duration_seconds = frame_count / fps
                                        minutes = int(duration_seconds // 60)
                                        seconds = int(duration_seconds % 60)
                                        duration_str = f"{minutes}:{seconds:02d}"
                                except:
                                    pass

                            reader.close()

                            img = Image.fromarray(frame)
                            img.thumbnail((150, 112), Image.Resampling.LANCZOS)  # Slightly larger for horizontal layout
                            thumbnail = ImageTk.PhotoImage(img)
                            self.video_thumbnails.append(thumbnail)  # Keep reference
                        except Exception as e:
                            print(f"Error loading thumbnail: {e}")

                    # Thumbnail label
                    thumb_container = ttk.Frame(content_container)
                    thumb_container.grid(row=0, column=0, pady=(0, 5))

                    if thumbnail:
                        thumb_label = ttk.Label(thumb_container, image=thumbnail, text="")
                        thumb_label.image = thumbnail  # Keep reference
                        thumb_label.pack()
                    else:
                        thumb_label = ttk.Label(thumb_container, text="[No Preview]", width=20, anchor=tk.CENTER)
                        thumb_label.pack()

                    # Video info
                    from datetime import datetime
                    created = video_info.get('created', '')
                    try:
                        dt = datetime.fromisoformat(created)
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = created[:16] if len(created) > 16 else created

                    audio_name = Path(video_info.get('audio_file', '')).stem
                    title = video_info.get('title', 'Untitled')

                    info_frame = ttk.Frame(content_container)
                    info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

                    title_label = ttk.Label(info_frame, text=title, font=('Segoe UI', 9, 'bold'), wraplength=150)
                    title_label.grid(row=0, column=0, sticky=tk.W)

                    duration_label = ttk.Label(info_frame, text=f"Duration: {duration_str}", font=('Segoe UI', 8))
                    duration_label.grid(row=1, column=0, sticky=tk.W)

                    audio_label = ttk.Label(info_frame, text=f"Audio: {audio_name[:20]}...", font=('Segoe UI', 7))
                    audio_label.grid(row=2, column=0, sticky=tk.W)

                    date_label = ttk.Label(info_frame, text=f"{date_str}", font=('Segoe UI', 7))
                    date_label.grid(row=3, column=0, sticky=tk.W)

                    # Delete button
                    delete_btn = ttk.Button(item_frame, text="🗑", width=3,
                                           command=lambda vid=video_info: self.delete_video_confirm(vid))
                    delete_btn.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)

                    # Bind click events to item frame
                    def make_select_handler(vid_info):
                        def handler(event):
                            self.selected_video = vid_info
                            self.on_video_select_from_thumb(vid_info)
                        return handler

                    def make_double_click_handler(vid_info):
                        def handler(event):
                            self.selected_video = vid_info
                            self.play_selected_video()
                        return handler

                    content_container.bind('<Button-1>', make_select_handler(video_info))
                    content_container.bind('<Double-Button-1>', make_double_click_handler(video_info))
                    thumb_label.bind('<Button-1>', make_select_handler(video_info))
                    thumb_label.bind('<Double-Button-1>', make_double_click_handler(video_info))
                    for child in info_frame.winfo_children():
                        child.bind('<Button-1>', make_select_handler(video_info))
                        child.bind('<Double-Button-1>', make_double_click_handler(video_info))

                    self.video_list_data.append(video_info)

                # Configure column weights for equal spacing
                for col in range(videos_per_row):
                    self.video_content.columnconfigure(col, weight=1, uniform="video_cols")

                # Update scroll region
                self.video_content.update_idletasks()
                self.video_canvas.configure(scrollregion=self.video_canvas.bbox("all"))
            else:
                no_videos_label = ttk.Label(self.video_content, text="No videos available. Generate a video to get started!",
                                           font=('Segoe UI', 10))
                no_videos_label.grid(row=0, column=0, padx=20, pady=20)
        except Exception as e:
            error_label = ttk.Label(self.video_content, text=f"Error loading videos: {str(e)}",
                                   font=('Segoe UI', 9), foreground='red')
            error_label.grid(row=0, column=0, padx=20, pady=20)
            print(f"Error in refresh_video_list: {e}")

    def on_video_select_from_thumb(self, video_info):
        """Handle video selection from thumbnail."""
        self.selected_video = video_info
        # Update info labels
        self.video_title_label.config(text=video_info.get('title', 'Untitled'))
        created = video_info.get('created', '')
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(created)
            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            date_str = created
        self.video_date_label.config(text=date_str)
        self.update_ui_state()

    def delete_video_confirm(self, video_info):
        """Show confirmation dialog and delete video if confirmed."""
        title = video_info.get('title', 'Untitled')
        result = messagebox.askyesno(
            "Delete Video",
            f"Are you sure you want to delete '{title}'?\n\nThis action cannot be undone.",
            icon='warning'
        )

        if result:
            if delete_video(video_info):
                messagebox.showinfo("Success", f"Video '{title}' has been deleted.")
                # Refresh the list
                self.refresh_video_list()
                # Clear selection if deleted video was selected
                if self.selected_video == video_info:
                    self.selected_video = None
                    self.video_title_label.config(text="—")
                    self.video_date_label.config(text="—")
                    self.update_ui_state()
            else:
                messagebox.showerror("Error", f"Failed to delete video '{title}'.")

    def on_video_select(self, event):
        """Handle video selection from listbox."""
        selection = self.video_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.video_list_data):
                self.selected_video = self.video_list_data[index]
                # Update info labels
                self.video_title_label.config(text=self.selected_video.get('title', 'Untitled'))
                created = self.selected_video.get('created', '')
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created)
                    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date_str = created
                self.video_date_label.config(text=date_str)
                self.update_ui_state()

    def play_selected_video(self):
        """Play the selected video."""
        if self.selected_video:
            video_path = Path(self.selected_video['path'])
            audio_path = Path(self.selected_video.get('audio_file', ''))
            if video_path.exists():
                self.open_video_player(video_path, audio_path if audio_path.exists() else None)
            else:
                messagebox.showerror("Error", f"Video file not found: {video_path}")
                self.refresh_video_list()  # Refresh to remove missing videos

    def get_video_title(self):
        """Show dialog to get video title from user."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Video Title")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Enter video title:", style='Heading.TLabel').pack(pady=(0, 10))

        title_var = tk.StringVar()
        title_entry = ttk.Entry(main_frame, textvariable=title_var, width=40, font=('Segoe UI', 10))
        title_entry.pack(pady=(0, 15))
        title_entry.focus()

        result = {'title': None}

        def apply_title():
            title = title_var.get().strip()
            if title:
                result['title'] = title
            else:
                result['title'] = ""  # Empty string for default naming
            dialog.destroy()

        def cancel():
            result['title'] = None
            dialog.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack()

        ttk.Button(button_frame, text="Generate", command=apply_title, style='Custom.TButton', width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel, width=12).pack(side=tk.LEFT, padx=5)

        # Handle Enter key
        title_entry.bind('<Return>', lambda e: apply_title())
        dialog.bind('<Escape>', lambda e: cancel())

        dialog.wait_window()
        return result['title']

    def on_audio_select(self, event):
        """Handle audio file selection from listbox."""
        selection = self.audio_listbox.curselection()
        if selection:
            index = selection[0]
            try:
                audio_files = list_audio_files(MUSIC_DIR)
                if index < len(audio_files):
                    self.current_audio_path = audio_files[index]
                    self.audio_path_var.set(str(self.current_audio_path))
                    self.load_audio_info()
                    self.update_ui_state()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to select audio file:\n{e}")

    def load_audio_info(self):
        """Load and display audio file information."""
        if not self.current_audio_path or not self.current_audio_path.exists():
            return

        try:
            # Load audio file
            y, sr = librosa.load(str(self.current_audio_path), sr=None, mono=True)
            duration = len(y) / sr

            # Get audio profile
            prof = audio_profile(str(self.current_audio_path), fps=self.settings['fps'].get())

            # Update info labels
            self.info_labels['name'].config(text=self.current_audio_path.name)
            self.info_labels['duration'].config(text=f"{duration:.2f} seconds")
            self.info_labels['sample_rate'].config(text=f"{sr:,} Hz")
            self.info_labels['tempo'].config(text=f"{prof['tempo']:.1f} BPM")
            self.info_labels['energy'].config(text=f"{prof['energy_mean']:.2f}")
            self.info_labels['brightness'].config(text=f"{prof['bright_mean']:.2f}")

            self.audio_info = prof

            # Refresh video list to show videos for this audio file
            self.refresh_video_list()

        except Exception as e:
            # Reset labels on error
            for label in self.info_labels.values():
                label.config(text="—")
            print(f"Error loading audio info: {e}")

    def load_video_thumbnail(self):
        """Load and display video thumbnail in scrollable preview."""
        if not self.current_audio_path:
            return

        frames_dir = FRAMES_ROOT / self.current_audio_path.stem
        video_path = frames_dir / "visualization.mp4"

        # Clear existing thumbnail
        for widget in self.preview_content.winfo_children():
            widget.destroy()

        # Try to load thumbnail from video
        if video_path.exists():
            try:
                import imageio
                reader = imageio.get_reader(str(video_path))
                # Get first frame as thumbnail
                frame = reader.get_data(0)
                reader.close()

                # Resize to reasonable preview size
                img = Image.fromarray(frame)
                # Keep aspect ratio, max width 300px
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)

                # Convert to PhotoImage
                self.thumbnail_image = ImageTk.PhotoImage(img)
                self.thumbnail_label = ttk.Label(self.preview_content, image=self.thumbnail_image, text="")
                self.thumbnail_label.pack(pady=10)

                # Add video info
                video_size = video_path.stat().st_size / (1024 * 1024)  # Size in MB
                info_text = f"Video: {video_path.name}\nSize: {video_size:.1f} MB"
                info_label = ttk.Label(self.preview_content, text=info_text, style='Info.TLabel')
                info_label.pack(pady=5)

                # Update scroll region
                self.preview_canvas.update_idletasks()
                self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            except Exception as e:
                self.thumbnail_label = ttk.Label(self.preview_content, text=f"Video available\n(Error loading preview: {e})",
                                                style='Info.TLabel')
                self.thumbnail_label.pack(pady=10)
                self.thumbnail_image = None
                self.preview_canvas.update_idletasks()
                self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        else:
            self.thumbnail_label = ttk.Label(self.preview_content, text="No video available", style='Info.TLabel')
            self.thumbnail_label.pack(pady=10)
            self.thumbnail_image = None
            self.preview_canvas.update_idletasks()
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def update_ui_state(self):
        """Update UI button states based on current selection."""
        has_audio = self.current_audio_path is not None and self.current_audio_path.exists()
        has_video = False

        has_video = self.selected_video is not None

        self.generate_btn.config(state="normal" if has_audio and not self.is_generating else "disabled")
        self.play_btn.config(state="normal" if has_video else "disabled")

    def start_generation(self):
        """Start video generation in a background thread."""
        if not self.current_audio_path or not self.current_audio_path.exists():
            messagebox.showerror("Error", "Please select a valid audio file.")
            return

        if self.is_generating:
            messagebox.showwarning("Warning", "Generation already in progress.")
            return

        # Ask for video title
        video_title = self.get_video_title()
        if video_title is None:  # User cancelled
            return

        self.is_generating = True
        self.generate_btn.config(state="disabled")
        self.play_btn.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Analyzing audio...")

        # Start generation in background thread
        self.generation_thread = threading.Thread(
            target=self.generate_video_worker,
            args=(self.current_audio_path, video_title),
            daemon=True
        )
        self.generation_thread.start()

    def generate_video_worker(self, audio_path: Path, video_title: str = None):
        """Worker function that runs in background thread to generate video."""
        try:
            self.message_queue.put(("status", "Extracting audio features..."))

            # Get settings
            fps = self.settings['fps'].get()
            width = self.settings['width'].get()
            height = self.settings['height'].get()
            intensity = self.settings['intensity'].get()
            palette_choice = self.settings['palette'].get()
            power = self.settings['power'].get()
            dynamic_dims = self.settings['dynamic_dimensions'].get()
            dim_factor = self.settings['dimension_factor'].get()
            use_custom_palette = self.settings['use_custom_palette'].get()
            quality = self.settings['quality_preset'].get()
            max_iterations = self.settings['max_iterations'].get()
            z_real = self.settings['z_real'].get()
            z_imag = self.settings['z_imag'].get()
            c_base_real = self.settings['c_base_real'].get()
            c_base_imag = self.settings['c_base_imag'].get()
            rotation_enabled = self.settings['rotation_enabled'].get()
            rotation_velocity = self.settings['rotation_velocity'].get()

            # Extract features
            rms, cent, sr, duration = extract_features(str(audio_path), fps=fps)

            self.message_queue.put(("status", "Analyzing audio profile..."))

            # Get audio profile and select preset
            prof = audio_profile(str(audio_path), fps=fps)
            preset_name = choose_preset_name(prof) if palette_choice == 'auto' else palette_choice
            preset = JULIA_PRESETS.get(preset_name, JULIA_PRESETS['ethereal']).copy()

            # Apply custom palette if selected
            if use_custom_palette:
                # Always set custom colors when custom palette is enabled
                preset['palette'] = 'custom'
                preset['custom_main_color'] = self.settings['custom_main_color'].get()
                preset['custom_accent_color'] = self.settings['custom_accent_color'].get()
                # Clear any other palette settings
                if 'palette' in preset and preset['palette'] != 'custom':
                    pass  # Will be overridden
            elif palette_choice != 'auto' and palette_choice in PALETTES:
                preset['palette'] = palette_choice
                # Clear custom colors when using preset palette
                preset.pop('custom_main_color', None)
                preset.pop('custom_accent_color', None)

            # Apply intensity multiplier to amplitudes
            preset['amp_real'] *= intensity
            preset['amp_imag'] *= intensity

            # Apply quality settings (affects video quality)
            # Use max_iterations from GUI setting (can be overridden by user)
            quality_settings = {
                'low': {'video_quality': 5},
                'medium': {'video_quality': 6},
                'high': {'video_quality': 8},
                'ultra': {'video_quality': 10},
            }
            quality_config = quality_settings.get(quality, quality_settings['high'])
            preset['video_quality'] = quality_config['video_quality']

            # Use max_iterations from GUI (user can override quality preset)
            max_iterations = self.settings['max_iterations'].get()
            preset['max_iter'] = max_iterations

            self.message_queue.put(("preset", f"Preset: {preset_name} | Tempo: {prof['tempo']:.1f} BPM"))

            total_frames = len(rms)
            self.message_queue.put(("status", f"Generating {total_frames} frames..."))

            # Create output directories
            audio_stem = audio_path.stem
            video_dir = VIDEOS_ROOT / audio_stem
            video_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            video_filename = get_video_filename(audio_stem, video_title)
            video_path = video_dir / video_filename

            # Temporary directory for generation
            temp_dir = FRAMES_ROOT / audio_stem
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Progress callback
            def progress_callback(current, total):
                progress_pct = int((current / total) * 100)
                self.message_queue.put(("progress", progress_pct))
                self.message_queue.put(("status", f"Generating frame {current}/{total}..."))

            # Generate video to temporary location first
            output_path = julia_audio_frames_2d(
                rms=rms,
                cent=cent,
                preset=preset,
                width=width,
                height=height,
                output_dir=str(temp_dir),
                progress_callback=progress_callback,
                power=power,  # Pass power parameter
                fps=fps,  # Pass FPS for video
                dynamic_dimensions=dynamic_dims,  # Dynamic dimension feature
                dimension_factor=dim_factor,  # Dimension growth factor
                audio_path=str(audio_path),  # Pass audio path to add to video
                z_offset_real=z_real,  # Z offset real part
                z_offset_imag=z_imag,  # Z offset imaginary part
                c_base_offset_real=c_base_real,  # C base offset real part
                c_base_offset_imag=c_base_imag,  # C base offset imaginary part
                rotation_enabled=rotation_enabled,  # Enable rotation
                rotation_velocity=rotation_velocity,  # Rotation velocity
            )

            # Move video to final location
            if output_path and Path(output_path).exists():
                import shutil
                shutil.move(output_path, video_path)
                output_path = str(video_path)

                # Register video in metadata
                settings_dict = {
                    'fps': fps,
                    'width': width,
                    'height': height,
                    'power': power,
                    'intensity': intensity,
                    'palette': palette_choice,
                    'max_iterations': max_iterations,
                }
                video_info = register_video(audio_path, video_path, video_title, settings_dict)

                self.message_queue.put(("status", f"Complete! Generated: {video_info['title']}"))
            else:
                self.message_queue.put(("status", f"Complete! Generated {total_frames} frames."))

            # Generation complete
            self.message_queue.put(("progress", 100))
            self.message_queue.put(("done", None))
            self.message_queue.put(("refresh_videos", None))  # Trigger video list refresh

        except Exception as e:
            self.message_queue.put(("error", str(e)))
            self.message_queue.put(("done", None))

    def check_queue(self):
        """Check for messages from background threads and update UI."""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()

                if msg_type == "status":
                    self.status_var.set(data)
                elif msg_type == "preset":
                    self.preset_var.set(data)
                elif msg_type == "progress":
                    self.progress_var.set(data)
                elif msg_type == "error":
                    messagebox.showerror("Generation Error", f"An error occurred:\n{data}")
                    self.status_var.set("Error occurred")
                elif msg_type == "done":
                    self.is_generating = False
                    self.update_ui_state()
                elif msg_type == "refresh_videos":
                    self.refresh_video_list()

        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)

    def on_resolution_preset_change(self, event=None):
        """Update width/height when resolution preset changes."""
        preset = self.settings['resolution_preset'].get()
        if preset in self.resolution_presets:
            width, height = self.resolution_presets[preset]
            self.settings['width'].set(width)
            self.settings['height'].set(height)


    def show_custom_palette_dialog(self):
        """Show dialog for custom color palette."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Color Palette")
        dialog.geometry("450x220")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Style the dialog to match main GUI
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        def choose_color(var, label, canvas_widget):
            color = colorchooser.askcolor(title=f"Choose {label} Color", color=var.get())
            if color[1]:
                var.set(color[1])
                # Update dialog canvas
                canvas_widget.create_rectangle(0, 0, 50, 30, fill=color[1], outline='black')
                # Update main GUI preview
                self.update_color_previews()
                return color[1]
            return None

        ttk.Label(main_frame, text="Main Color:", style='Heading.TLabel').grid(row=0, column=0, padx=10, pady=15, sticky=tk.W)
        main_color_frame = ttk.Frame(main_frame)
        main_color_frame.grid(row=0, column=1, padx=10, pady=15, sticky=tk.W)
        main_canvas = tk.Canvas(main_color_frame, width=50, height=30, highlightthickness=1, relief=tk.SUNKEN)
        main_canvas.pack(side=tk.LEFT, padx=5)
        main_canvas.create_rectangle(0, 0, 50, 30, fill=self.settings['custom_main_color'].get(), outline='black')
        ttk.Button(main_color_frame, text="Choose...", style='Custom.TButton',
                  command=lambda: choose_color(self.settings['custom_main_color'], "Main", main_canvas)).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="Accent Color:", style='Heading.TLabel').grid(row=1, column=0, padx=10, pady=15, sticky=tk.W)
        accent_color_frame = ttk.Frame(main_frame)
        accent_color_frame.grid(row=1, column=1, padx=10, pady=15, sticky=tk.W)
        accent_canvas = tk.Canvas(accent_color_frame, width=50, height=30, highlightthickness=1, relief=tk.SUNKEN)
        accent_canvas.pack(side=tk.LEFT, padx=5)
        accent_canvas.create_rectangle(0, 0, 50, 30, fill=self.settings['custom_accent_color'].get(), outline='black')
        ttk.Button(accent_color_frame, text="Choose...", style='Custom.TButton',
                  command=lambda: choose_color(self.settings['custom_accent_color'], "Accent", accent_canvas)).pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        def apply_palette():
            self.settings['use_custom_palette'].set(True)
            self.settings['palette'].set('custom')
            self.update_color_previews()
            dialog.destroy()

        ttk.Button(button_frame, text="Apply", command=apply_palette, style='Custom.TButton', width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.LEFT, padx=5)

    def update_color_previews(self):
        """Update the color preview canvases in the main GUI."""
        if self.settings['use_custom_palette'].get():
            main_color = self.settings['custom_main_color'].get()
            accent_color = self.settings['custom_accent_color'].get()
            # Clear and redraw with new colors (using correct dimensions)
            self.main_color_canvas.delete("all")
            self.main_color_canvas.create_rectangle(1, 1, 31, 23, fill=main_color, outline='gray', width=1)
            self.accent_color_canvas.delete("all")
            self.accent_color_canvas.create_rectangle(1, 1, 31, 23, fill=accent_color, outline='gray', width=1)
            self.preview_row.grid()  # Show preview row
        else:
            self.preview_row.grid_remove()  # Hide preview row

    def play_visualization(self):
        """Launch the embedded video player with controls."""
        if self.selected_video:
            self.play_selected_video()
        elif self.current_audio_path:
            # Try to find any video for this audio file
            videos = get_videos_for_audio(self.current_audio_path)
            if videos:
                # Play the most recent video
                self.selected_video = videos[-1]  # Last one is newest
                self.play_selected_video()
            else:
                messagebox.showinfo("No Video", "No videos found for this audio file. Generate a video first.")

    def open_video_player(self, video_path, audio_path=None):
        """Open embedded video player with controls."""
        try:
            import cv2
        except ImportError:
            # Fallback to system player if opencv not available
            import subprocess
            import platform
            try:
                if platform.system() == 'Windows':
                    os.startfile(str(video_path))
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', str(video_path)])
                else:
                    subprocess.run(['xdg-open', str(video_path)])
            except Exception as e:
                messagebox.showerror("Playback Error", f"Could not open video:\n{e}")
            return

        player_window = tk.Toplevel(self.root)
        player_window.title("Video Player")
        player_window.geometry("900x600")

        # Video display - use Canvas for better fullscreen support
        video_canvas = tk.Canvas(player_window, bg='black', highlightthickness=0)
        video_canvas.pack(fill=tk.BOTH, expand=True)

        video_label = ttk.Label(video_canvas, text="Loading video...", background='black', foreground='white')
        video_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Controls
        controls_frame = ttk.Frame(player_window, padding="10")
        controls_frame.pack(fill=tk.X)

        self.player_state = {
            'playing': False,
            'position': 0,
            'total_frames': 0,
            'cap': None,
            'fps': 30,
            'current_frame': None,
            'fullscreen': False,
            'audio_path': None,
        }

        # Initialize pygame mixer for audio
        try:
            import pygame
            pygame.mixer.init()
            self.player_state['pygame_available'] = True
            # Use provided audio path or try to find audio file
            if audio_path and Path(audio_path).exists():
                self.player_state['audio_path'] = str(audio_path)
            else:
                # Try to find audio file
                audio_file = video_path.parent.parent.parent / "music" / video_path.stem
                # Check common audio extensions
                for ext in ['.wav', '.mp3', '.flac', '.m4a']:
                    potential_audio = audio_file.with_suffix(ext)
                    if potential_audio.exists():
                        self.player_state['audio_path'] = str(potential_audio)
                        break
        except ImportError:
            self.player_state['pygame_available'] = False

        def load_video():
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open video file")
                player_window.destroy()
                return

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            self.player_state['cap'] = cap
            self.player_state['fps'] = fps
            self.player_state['total_frames'] = total_frames

            # Update window size to video size
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            player_window.geometry(f"{min(width+100, 1200)}x{min(height+150, 800)}")

            # Start playing automatically
            self.player_state['playing'] = True
            self.play_pause_btn.config(text="⏸ Pause")
            # Start audio playback
            if self.player_state.get('pygame_available') and self.player_state.get('audio_path'):
                try:
                    import pygame
                    pygame.mixer.music.load(self.player_state['audio_path'])
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Audio playback error: {e}")
            update_frame()

        def play_video():
            if not self.player_state['playing']:
                self.player_state['playing'] = True
                self.play_pause_btn.config(text="⏸ Pause")
                # Play audio if available
                if self.player_state.get('pygame_available') and self.player_state.get('audio_path'):
                    try:
                        import pygame
                        pygame.mixer.music.load(self.player_state['audio_path'])
                        # Calculate audio position based on video position
                        audio_pos = self.player_state['position'] / self.player_state['fps']
                        pygame.mixer.music.play(start=audio_pos)
                    except Exception as e:
                        print(f"Audio playback error: {e}")
                update_frame()

        def pause_video():
            if self.player_state['playing']:
                self.player_state['playing'] = False
                self.play_pause_btn.config(text="▶ Play")
                # Pause audio if available
                if self.player_state.get('pygame_available'):
                    try:
                        import pygame
                        pygame.mixer.music.pause()
                    except Exception:
                        pass

        def rewind_video():
            if self.player_state['cap']:
                new_pos = max(0, self.player_state['position'] - int(self.player_state['fps'] * 5))  # 5 seconds
                self.player_state['cap'].set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                self.player_state['position'] = new_pos
                # Update audio position
                if self.player_state.get('pygame_available') and self.player_state.get('audio_path'):
                    try:
                        import pygame
                        audio_pos = new_pos / self.player_state['fps']
                        if self.player_state['playing']:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(self.player_state['audio_path'])
                            pygame.mixer.music.play(start=audio_pos)
                    except Exception:
                        pass
                # Force frame update
                ret, frame = self.player_state['cap'].read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    update_video_display(img)

        def forward_video():
            if self.player_state['cap']:
                new_pos = min(self.player_state['total_frames'] - 1,
                            self.player_state['position'] + int(self.player_state['fps'] * 5))  # 5 seconds
                self.player_state['cap'].set(cv2.CAP_PROP_POS_FRAMES, new_pos)
                self.player_state['position'] = new_pos
                # Update audio position
                if self.player_state.get('pygame_available') and self.player_state.get('audio_path'):
                    try:
                        import pygame
                        audio_pos = new_pos / self.player_state['fps']
                        if self.player_state['playing']:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(self.player_state['audio_path'])
                            pygame.mixer.music.play(start=audio_pos)
                    except Exception:
                        pass
                # Force frame update
                ret, frame = self.player_state['cap'].read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    update_video_display(img)

        def toggle_fullscreen():
            is_fullscreen = player_window.attributes('-fullscreen')
            self.player_state['fullscreen'] = not is_fullscreen
            player_window.attributes('-fullscreen', self.player_state['fullscreen'])

            # Force update of video display after fullscreen toggle
            if self.player_state['cap'] and self.player_state.get('current_frame') is not None:
                # Re-display current frame with new sizing
                update_video_display(self.player_state['current_frame'])

        def update_video_display(img):
            """Update video display with proper sizing for fullscreen/normal mode."""
            # Store current frame for fullscreen toggle
            self.player_state['current_frame'] = img.copy()

            if self.player_state['fullscreen']:
                # Fullscreen: stretch to fill entire screen
                screen_width = player_window.winfo_screenwidth()
                screen_height = player_window.winfo_screenheight()
                # Account for controls height (approximately 60px)
                available_height = screen_height - 60
                img = img.resize((screen_width, available_height), Image.Resampling.LANCZOS)
            else:
                # Normal mode: fit to window
                display_width = video_canvas.winfo_width() or 800
                display_height = video_canvas.winfo_height() or 600
                if display_width > 1 and display_height > 1:
                    img.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image=img)
            video_label.config(image=photo, text="", background='black')
            video_label.image = photo
            # Center the image
            video_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        def update_frame():
            if not self.player_state['cap']:
                return

            # Always update frame position
            self.player_state['position'] = int(self.player_state['cap'].get(cv2.CAP_PROP_POS_FRAMES))

            # Check if we've reached the end
            if self.player_state['position'] >= self.player_state['total_frames']:
                self.player_state['playing'] = False
                self.play_pause_btn.config(text="▶ Play")
                # Stop audio
                if self.player_state.get('pygame_available'):
                    try:
                        import pygame
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                return

            ret, frame = self.player_state['cap'].read()
            if not ret:
                self.player_state['playing'] = False
                self.play_pause_btn.config(text="▶ Play")
                # Stop audio
                if self.player_state.get('pygame_available'):
                    try:
                        import pygame
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
                return

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            # Update display with proper sizing
            update_video_display(img)

            # Continue playing if state is playing
            if self.player_state['playing']:
                player_window.after(int(1000 / self.player_state['fps']), update_frame)

        # Control buttons
        ttk.Button(controls_frame, text="⏮ Rewind", command=rewind_video).pack(side=tk.LEFT, padx=5)
        self.play_pause_btn = ttk.Button(controls_frame, text="⏸ Pause", command=lambda: pause_video() if self.player_state['playing'] else play_video())
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⏭ Forward", command=forward_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⛶ Fullscreen", command=toggle_fullscreen).pack(side=tk.LEFT, padx=5)

        def on_close():
            # Stop audio
            if self.player_state.get('pygame_available'):
                try:
                    import pygame
                    pygame.mixer.music.stop()
                except Exception:
                    pass
            # Release video capture
            if self.player_state['cap']:
                self.player_state['cap'].release()
            player_window.destroy()

        player_window.protocol("WM_DELETE_WINDOW", on_close)
        load_video()


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = FractalMusicGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
