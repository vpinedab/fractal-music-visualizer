import numpy as np
from PIL import Image
import os

# Try to import numba for JIT compilation, fallback to pure NumPy if not available
try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    # Dummy decorator if numba not available
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range

# Try to import imageio for video output
try:
    import imageio
    # Try to import ffmpeg plugin (imageio-ffmpeg package)
    IMAGEIO_FFMPEG_AVAILABLE = False
    try:
        import imageio_ffmpeg
        IMAGEIO_AVAILABLE = True
        IMAGEIO_FFMPEG_AVAILABLE = True
    except ImportError:
        # imageio-ffmpeg not installed as separate package
        # Try to use built-in plugin (older imageio versions)
        try:
            # Just try to use imageio - it will fail later if ffmpeg not available
            IMAGEIO_AVAILABLE = True
        except Exception:
            IMAGEIO_AVAILABLE = False
            print("Warning: imageio-ffmpeg not found. Install with: pip install imageio-ffmpeg")
except ImportError:
    IMAGEIO_AVAILABLE = False
    IMAGEIO_FFMPEG_AVAILABLE = False
    print("Warning: imageio not installed. Install with: pip install imageio imageio-ffmpeg")

### FRACTAL BASE ###

def mandelbrot( # Fractal configuration
    width=800,  # Number of horizontal pixels
    height=600, # Number of vertical pixels
    max_iter=100,   # Number of iterations for each complex point c
                    # The more iterations, the greater the detail of the fractal
    # Complex plain region
    x_min=-2.0, # Real axis (x)
    x_max=1.0,
    y_min=-1.2, # Imaginary axis (y)
    y_max=1.2,
    output_path="assets/output/mandelbrot.png",
):
    # Crea los ejes del plano complejo
    x = np.linspace(x_min, x_max, width)    # x: width puntos entre x_min y x_max
    y = np.linspace(y_min, y_max, height)   # y: height puntos entre y_min y y_max

    X, Y = np.meshgrid(x, y) # Crea la malla 2D de puntos

    # Construye el plano complejo
    C = X + 1j * Y
    # 1j --> j es la unidad imaginaria, 1j=i

    # Inicializar Z
    Z = np.zeros_like(C)    # Esto crea una matriz del mismo tamaño de C, pero llena de ceros complejos

    # Crear la imagen (matriz de pixeles)
    image = np.zeros(C.shape, dtype=np.uint8)

    # Iteración del fractal
        # Crear la mascara
        mask = np.abs(Z) <= 2
        # Selecciona los puntos que todavía no han escapado
        # Si |z| > el punto diverge
        # Si no, sigue iterando
        # mask es una matriz True/False

        # Actualizar los puntos activos
        Z[mask] = Z[mask] ** 2 + C[mask]
        # Solo se iteran los puntos que no han escapado
        # Hace la fórmula de iteración que usamos anteriormente una ultima vez

        # Colorear los puntos que se acaban de escapar
        image[mask & (np.abs(Z) > 2)] = int(255 * i / max_iter)
        # Encuentra punto que estaban dentro de mask y se escaparon |z|>2
        # Les asigna un color según en que iteración escaparon
        # Más temprano -> Color oscuro
        # Más tarde -> Color claro

    os.makedirs(os.path.dirname(output_path), exist_ok=True)    # Crea la carpeta si no existe

    # Convierte la matriz a imagen real
    img = Image.fromarray(image, mode="L")
    # Convierte la matriz NumPy a imagen
    # "L" = grayscale (0-255)

    img.save(output_path)   # Guarda el archivo

    return output_path

### ZOOM ###

def mandelbrot_zoom(
    frames=120,  # Cuántas imágenes se van a generar

    # Resolución de cada imagen
    width=800,
    height=600,

    max_iter=200, # Nivel de detalle del fractal

    # Punto del plano al que te estás acercando
    x_center=-0.75,
    y_center=-0.00,

    # Qué tan lejos empiezas y qué tan cerca terminas
    zoom_start=1.0,
    zoom_end=0.03,

    output_dir="assets/output/frames", # Carpeta donde se guardan los frames
):

    # Crear carpeta de salida
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Loop de animación
    for i in range(frames): # i representa el tiempo discreto
        t = i / (frames - 1)  # va de 0 a 1
        # t representa el tiempo normalizado
        # Independiza la animación del número de frames

        # Interpolación lineal
        zoom = zoom_start * (1 - t) + zoom_end * t
        # Cuando t=0 --> zoom = zoom_start
        # Cuando t=1 --> zoom = zoom_end

        # Tamaño del campo de visión
        # Mandelbrot clásico ancho=3 y altura=2.4
        span_x = 3.0 * zoom
        span_y = 2.4 * zoom
        # El rectángulo se hace más pequeño, parece que te acercas

        # Límites plano complejo
        # Construye un rectángulo centrado en x_center y y_center
        x_min = x_center - span_x / 2
        x_max = x_center + span_x / 2
        y_min = y_center - span_y / 2
        y_max = y_center + span_y / 2

        output_path = f"{output_dir}/frame_{i:04d}.png" # Nombre del archivo del frame
        # {i:04d} --> i con 4 dígitos

        mandelbrot(
            width=width,
            height=height,
            max_iter=max_iter,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            output_path=output_path,
        )

### JULIA ###

## Paletas de color (RGB)
def _palette_fire(t: np.ndarray) -> np.ndarray:
    """
    t en [0,1] -> RGB. Paleta cálida.
    """
    t = np.clip(t, 0.0, 1.0) # Garantiza que t este dentro de [0,1] para que no se rompa el color si hay valores fuera.
    r = np.clip(3.0 * t, 0, 1)
    g = np.clip(3.0 * t - 1.0, 0, 1)
    b = np.clip(3.0 * t - 2.0, 0, 1)
    return (255 * np.dstack([r, g, b])).astype(np.uint8)

def _palette_ocean(t: np.ndarray) -> np.ndarray:
    """
    Calm / Ocean.
    Azul dominante, suave, no agresiva.
    """
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    stops = np.array([
        [208, 238, 233],   # fondo --> Jagged Ice
        [ 12,  30, 120],   # azul marino
        [ 46, 110, 159],   # azul océano
        [108,  75, 150],   # morado frío sutil
        [ 65, 157, 141],   # bioluminiscencia suave
        [160, 220, 210],   # highlight suave
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops))
    tf = t.ravel()

    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    return np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3).astype(np.uint8)

def _palette_deep_sea(t: np.ndarray) -> np.ndarray:
    """
    Deep Sea.
    Oscura, profunda, sensación de abismo.
    """
    t = np.clip(t, 0.0, 1.0)

    stops = np.array([
        [  3,   8,  20],
        [ 10,  25,  55],
        [ 20,  60,  90],
        [ 40, 100, 120],
        [ 90, 160, 170],
    ])

    x = np.linspace(0, 1, len(stops))
    tf = t.ravel()

    rgb = np.stack([
        np.interp(tf, x, stops[:, 0]),
        np.interp(tf, x, stops[:, 1]),
        np.interp(tf, x, stops[:, 2]),
    ], axis=1)

    return rgb.reshape(t.shape[0], t.shape[1], 3).astype(np.uint8)

def _palette_ethereal(t: np.ndarray) -> np.ndarray:
    """
    Ethereal (center = flower color).
    """
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    FLOWER_RGB = np.array([106, 85, 181], dtype=np.float32)  # <-- reemplaza

    stops = np.array([
        [212, 205, 213],      # fondo --> Gray Suit
        [162, 46,  120],      # degradado alrededor del fractal --> Royal Health
        FLOWER_RGB,           # <-- centro EXACTO (flor) --> Blue Violet
        [157, 141, 215],      # cold purple
        [186, 165, 194],      # london hue
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops), dtype=np.float32)
    tf = t.ravel()

    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    rgb = np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3)
    return rgb.astype(np.uint8)

def _palette_mathematical(t: np.ndarray) -> np.ndarray:
    """
    Mathematical (blue-black-white).
    Estilo 'chalkboard' / ecuaciones con glow frío.
    """
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    stops = np.array([
        [  2,   4,  10],   # casi negro azulado
        [  6,  12,  79],   # navy
        [ 20,  55, 120],   # azul profundo
        [ 90, 160, 230],   # azul claro tipo brillo
        [235, 245, 255],   # blanco azulado (highlight)
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops), dtype=np.float32)
    tf = t.ravel()

    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    rgb = np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3)
    return rgb.astype(np.uint8)

def _palette_abstract(t: np.ndarray) -> np.ndarray:
    """
    Abstract (kaleidoscope).
    Neón controlado: morado + turquesa + amarillo.
    """
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    stops = np.array([
        [ 14,  32,  28],   # fondo muy oscuro (azul-morado)
        [ 60,  35, 110],   # morado profundo
        [ 40, 140, 160],   # turquesa brillante (contraste frío)
        [180,  90, 210],   # morado luminoso
        [245, 210,  90],   # amarillo cálido (highlight)
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops), dtype=np.float32)
    tf = t.ravel()

    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    rgb = np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3)
    return rgb.astype(np.uint8)

def _palette_warm(t: np.ndarray) -> np.ndarray:
    """
    Warm.
    Paleta cálida basada en rojos, naranjas y ámbar.
    """
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    stops = np.array([
        [ 28,  26,  40],   # #1A2C44  azul petróleo oscuro (inicio)
        [ 89,  51,  78],   # #59334E  morado vino
        [210,  77,  85],   # #D24D55  rojo coral
        [218,  96,  38],   # #DA6026  naranja quemado
        [255, 196,   4],   # #FFC404  amarillo cálido (highlight)
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops), dtype=np.float32)
    tf = t.ravel()

    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    rgb = np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3)
    return rgb.astype(np.uint8)


PALETTES = {
    "fire": _palette_fire,
    "ocean": _palette_ocean,
    "deep_sea": _palette_deep_sea,
    "ethereal": _palette_ethereal,
    "mathematical": _palette_mathematical,
    "abstract": _palette_abstract,
    "warm": _palette_warm,
}

INTERIOR_COLORS = {
    "fire": (0, 0, 0),
    "ocean": (205, 226, 235),
    "deep_sea": (6, 12, 28),
    "ethereal": (20,  11, 66), # --> Violet
    "mathematical": (15, 24, 59),
    "abstract": (6, 8, 22),
    "warm": (18, 26, 40),
}

def _hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def _create_custom_palette(t: np.ndarray, main_color: str, accent_color: str) -> np.ndarray:
    """Create a custom color palette from main and accent colors."""
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    main_rgb = np.array(_hex_to_rgb(main_color), dtype=np.float32)
    accent_rgb = np.array(_hex_to_rgb(accent_color), dtype=np.float32)

    # Create gradient from dark (main) to bright (accent)
    stops = np.array([
        main_rgb * 0.1,  # Very dark main
        main_rgb * 0.5,  # Dark main
        main_rgb,        # Main color
        (main_rgb + accent_rgb) / 2,  # Blend
        accent_rgb,      # Accent color
        accent_rgb * 1.2,  # Bright accent (clipped)
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops), dtype=np.float32)
    tf = t.ravel()

    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    rgb = np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3)
    return np.clip(rgb, 0, 255).astype(np.uint8)

### OPTIMIZED JULIA FUNCTIONS ###

def make_plane(width: int, height: int, view: tuple, dtype=np.float32):
    """
    Precompute the complex plane once.
    Returns a complex64 array that can be reused across frames.
    Shape will be (height, width) to match image dimensions.
    """
    x_min, x_max, y_min, y_max = view
    x = np.linspace(x_min, x_max, width, dtype=dtype)
    y = np.linspace(y_min, y_max, height, dtype=dtype)
    # Use 'xy' indexing (default) to get (height, width) shape
    X, Y = np.meshgrid(x, y, indexing='xy')
    return (X + 1j * Y).astype(np.complex64)


if NUMBA_AVAILABLE:
    @njit(parallel=True, fastmath=True, cache=True)
    def julia_escape_smooth(Z0_real: np.ndarray, Z0_imag: np.ndarray,
                            c_real: float, c_imag: float, max_iter: int, power: float = 2.0):
        """
        Numba-accelerated Julia set iteration with smooth coloring.
        Uses squared magnitude to avoid sqrt operations.
        Supports z^p + c formula where p is the power parameter.
        Returns: nu (smooth iteration count), alive (boolean mask as uint8)
        """
        h, w = Z0_real.shape
        nu = np.zeros((h, w), dtype=np.float32)
        alive = np.ones((h, w), dtype=np.uint8)
        p = float(power)

        for y in prange(h):
            for x in range(w):
                zr = float(Z0_real[y, x])
                zi = float(Z0_imag[y, x])
                cr = float(c_real)
                ci = float(c_imag)

                # Iterate until escape or max_iter
                for k in range(max_iter):
                    # Compute z^p + c
                    # For integer powers, use optimized multiplication
                    # For non-integer, use polar form: z^p = |z|^p * exp(i*p*arg(z))
                    mag2 = zr * zr + zi * zi
                    if mag2 < 1e-12:  # Avoid division by zero
                        zr, zi = cr, ci
                    else:
                        # Convert to polar form
                        mag = np.sqrt(mag2)
                        arg = np.arctan2(zi, zr)

                        # Compute z^p in polar form
                        new_mag = mag ** p
                        new_arg = p * arg

                        # Convert back to rectangular
                        zr = new_mag * np.cos(new_arg) + cr
                        zi = new_mag * np.sin(new_arg) + ci

                    # Check escape using squared magnitude
                    mag2 = zr * zr + zi * zi
                    if mag2 > 4.0:
                        # Smooth coloring
                        mag2 = max(mag2, 1e-12)
                        log_mag = 0.5 * np.log(mag2)
                        if log_mag > 1e-12:
                            nu[y, x] = float(k) + 1.0 - np.log(log_mag) / np.log(2.0)
                        else:
                            nu[y, x] = float(k)
                        alive[y, x] = 0
                        break

        return nu, alive
else:
    # Fallback function when numba is not available
    def julia_escape_smooth(Z0_real: np.ndarray, Z0_imag: np.ndarray,
                            c_real: float, c_imag: float, max_iter: int, power: float = 2.0):
        # This won't be called when NUMBA_AVAILABLE is False, but needed for syntax
        raise RuntimeError("Numba not available")

def julia(
    c_real: float,
    c_imag: float,
    width: int = 800,
    height: int = 600,
    max_iter: int = 200,
    x_min: float = -1.5,
    x_max: float = 1.5,
    y_min: float = -1.5,
    y_max: float = 1.5,
    output_path: str = "assets/output/julia.png",
    palette: str = "fire",
    gamma: float = 0.85,
    Z0: np.ndarray = None,  # Optional precomputed plane
    nu_buf: np.ndarray = None,  # Optional buffer for reuse
    t_buf: np.ndarray = None,  # Optional buffer for reuse
    return_rgb: bool = False,  # If True, return RGB array instead of saving
    power: float = 2.0,  # Power for z^p + c formula
    custom_palette: str = None,  # Custom main color (hex)
    custom_accent: str = None,  # Custom accent color (hex)
) -> str:
    """
    Generate a Julia set fractal.

    If Z0, nu_buf, and t_buf are provided, they will be reused (faster for animations).
    Otherwise, they will be allocated fresh.
    """
    # Use precomputed plane if provided, otherwise create it
    if Z0 is None:
        x = np.linspace(x_min, x_max, width, dtype=np.float32)
        y = np.linspace(y_min, y_max, height, dtype=np.float32)
        X, Y = np.meshgrid(x, y, indexing='xy')  # 'xy' gives (height, width) shape
        Z0 = (X + 1j * Y).astype(np.complex64)
    else:
        # Ensure correct shape
        if Z0.shape != (height, width):
            raise ValueError(f"Z0 shape {Z0.shape} doesn't match {height}x{width}")

    # Compute escape iterations using optimized Numba function
    if NUMBA_AVAILABLE:
        nu, alive_uint8 = julia_escape_smooth(
            Z0.real, Z0.imag,
            float(c_real), float(c_imag),
            max_iter,
            float(power)
        )
        alive = alive_uint8.astype(bool)
    else:
        # Fallback to original method if numba not available
        Z = Z0.copy()
        C = complex(c_real, c_imag)
        it = np.zeros(Z.shape, dtype=np.int32)
        z_escape = np.zeros(Z.shape, dtype=np.complex64)
        alive = np.ones(Z.shape, dtype=bool)

        for i in range(max_iter):
            # Compute z^p + c
            if abs(power - 2.0) < 1e-6:
                # Optimized for power=2
                Z[alive] = Z[alive] * Z[alive] + C
            else:
                # General power: z^p = |z|^p * exp(i*p*arg(z))
                mag = np.abs(Z[alive])
                arg = np.angle(Z[alive])
                new_mag = np.power(mag, power)
                new_arg = power * arg
                Z[alive] = new_mag * np.exp(1j * new_arg) + C

            # Use squared magnitude instead of abs
            mag2 = (Z.real * Z.real + Z.imag * Z.imag)
            escaped = alive & (mag2 > 4.0)
            it[escaped] = i
            z_escape[escaped] = Z[escaped]
            alive[escaped] = False
            if not alive.any():
                break

        esc = ~alive
        nu = np.zeros(Z.shape, dtype=np.float32)
        z_abs = np.abs(z_escape[esc])
        z_abs = np.maximum(z_abs, 1e-12)
        nu[esc] = it[esc] + 1.0 - np.log(np.log(z_abs)) / np.log(2.0)

    # Normalization
    esc = ~alive
    if t_buf is None:
        t = np.zeros_like(nu, dtype=np.float32)
    else:
        t = t_buf
        t.fill(0.0)

    if esc.any():
        nu_esc = nu[esc]
        # Estiramiento de contraste robusto
        p_lo, p_hi = np.percentile(nu_esc, [2, 98])
        if p_hi - p_lo < 1e-6:
            p_lo, p_hi = nu_esc.min(), nu_esc.max() + 1e-6
        t[esc] = (nu_esc - p_lo) / (p_hi - p_lo)

    t = np.clip(t, 0.0, 1.0)
    # Contraste adicional
    contrast = 1.25
    t = np.clip((t - 0.5) * contrast + 0.5, 0.0, 1.0)
    t = t ** gamma

    # Aplicar paleta
    # Use custom palette if colors are provided, otherwise use preset palette
    if palette == "custom" and custom_palette and custom_accent:
        # Create custom palette from colors
        rgb = _create_custom_palette(t, custom_palette, custom_accent)
    elif palette in PALETTES:
        # Use preset palette
        pal_fn = PALETTES[palette]
        rgb = pal_fn(t)
    else:
        # Fallback to fire palette
        rgb = _palette_fire(t)

    # Interior / fondo
    if palette == "custom":
        # Use darker version of main color for interior
        interior = _hex_to_rgb(custom_palette) if custom_palette else (0, 0, 0)
        # Darken it
        interior = tuple(max(0, c - 30) for c in interior)
    else:
        interior = INTERIOR_COLORS.get(palette, (0, 0, 0))
    rgb[alive] = interior

    # Return RGB array or save to file
    if return_rgb:
        return rgb

    # Guardar con compresión optimizada
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img = Image.fromarray(rgb, mode="RGB")
        # Use compress_level=1 for faster PNG writing (0-9, lower = faster)
        img.save(output_path, compress_level=1, optimize=False)
        return output_path

    return rgb  # Fallback: return RGB if no output_path and not return_rgb

JULIA_PRESETS = {
    "calm": {
        "base_c_real": -0.62,
        "base_c_imag":  0.43,
        "amp_real": 0.12,
        "amp_imag": 0.06,
        "max_iter": 400,
        "palette": "ocean",
        "gamma": 0.95,
        "view": (-1.2, 1.2, -1.0, 1.0),
    },
    "deep_sea": {
        "base_c_real": -0.75,
        "base_c_imag":  0.12,
        "amp_real": 0.08,
        "amp_imag": 0.05,
        "max_iter": 400,
        "palette": "deep_sea",
        "gamma": 1.05,
        "view": (-1.4, 1.4, -1.2, 1.2),
    },
    "ethereal": {
        "base_c_real": -0.55,
        "base_c_imag":  0.48,
        "amp_real": 0.18,
        "amp_imag": 0.12,
        "max_iter": 400,
        "palette": "ethereal",
        "gamma": 1.00,
        "view": (-1.3, 1.3, -1.1, 1.1),
    },
    "energetic": {
        "base_c_real": -0.70,
        "base_c_imag":  0.27015,
        "amp_real": 0.65,
        "amp_imag": 0.55,
        "max_iter": 400,
        "palette": "fire",
        "gamma": 0.85,
        "view": (-1.2, 1.2, -1.0, 1.0),
    },
    "mathematical": {
        "base_c_real": -0.40,
        "base_c_imag":  0.60,
        "amp_real": 0.05,
        "amp_imag": 0.05,
        "max_iter": 400,
        "palette": "mathematical",
        "gamma": 1.10,
        "view": (-1.35, 1.35, -1.35, 1.35),
    },
    "abstract": {
        "base_c_real": -0.40,      # antes -0.30  -> un poco menos caótico
        "base_c_imag":  0.64,      # casi igual
        "amp_real": 0.25,          # antes 0.55   -> baja para que no “rompa” el patrón
        "amp_imag": 0.30,          # antes 0.65   -> baja para estabilidad visual
        "max_iter": 400,           # antes 220    -> más detalle, más “filigrana”
        "palette": "abstract",
        "gamma": 0.78,             # antes 0.90   -> más vivo (levanta tonos medios)
        "view": (-1.35, 1.35, -1.05, 1.05),  # antes más grande -> un poco de zoom
    },
    "warm": {
        "base_c_real": -0.68,
        "base_c_imag":  0.22,
        "amp_real": 0.25,
        "amp_imag": 0.18,
        "max_iter": 400,
        "palette": "warm",
        "gamma": 0.95,
        "view": (-1.3, 1.3, -1.1, 1.1),
    },
}

### ANIMACIÓN CON JULIA ###

def julia_audio_frames_2d(
    rms: np.ndarray, # energía por frame
    cent: np.ndarray, # brillo por frame
    preset: dict,
    width: int = 800,
    height: int = 600,
    output_dir: str = "assets/output/audio_frames",
    progress_callback=None,  # Callback function(current, total) for progress updates
    power: float = 2.0,  # Power for z^p + c formula
    fps: int = 60,  # FPS for video output
    dynamic_dimensions: bool = False,  # Enable dynamic dimension growth
    dimension_factor: float = 1.001,  # Growth factor per frame
    audio_path: str = None,  # Path to audio file to add to video
    z_offset_real: float = 0.0,  # Z offset (real part)
    z_offset_imag: float = 0.0,  # Z offset (imaginary part)
    c_base_offset_real: float = 0.0,  # C base offset (real part)
    c_base_offset_imag: float = 0.0,  # C base offset (imaginary part)
    rotation_enabled: bool = False,  # Enable rotation
    rotation_velocity: float = 0.1,  # Rotation velocity (radians per frame)
) -> str:
    """
    Optimized version: precomputes complex plane and reuses buffers.
    Writes directly to video file instead of individual PNG frames.
    """
    os.makedirs(output_dir, exist_ok=True)

    x_min, x_max, y_min, y_max = preset["view"]

    # Initial dimensions
    current_width = width
    current_height = height

    # OPTIMIZATION: Precompute complex plane (only if not using dynamic dimensions)
    Z0 = None if dynamic_dimensions else make_plane(width, height, preset["view"])

    # OPTIMIZATION: Preallocate buffers for reuse (use max size for dynamic)
    max_width = int(width * (dimension_factor ** len(rms))) if dynamic_dimensions else width
    max_height = int(height * (dimension_factor ** len(rms))) if dynamic_dimensions else height
    nu_buf = np.zeros((max_height, max_width), dtype=np.float32)
    t_buf = np.zeros((max_height, max_width), dtype=np.float32)

    alpha_c = 0.12   # prueba: 0.08 – 0.18
    drift = 0.0006

    prev_real = None
    prev_imag = None

    total_frames = len(rms)

    # Always use video format - require imageio
    if not IMAGEIO_AVAILABLE:
        raise RuntimeError(
            "imageio or imageio-ffmpeg is not available. "
            "Please install with: pip install imageio imageio-ffmpeg"
        )

    # Use output_dir as the final video path (will be set by caller)
    video_path = os.path.join(output_dir, "visualization.mp4")
    # Use imageio to write video directly (much faster than PNG)
    # Quality from preset (5-10, lower = faster encoding)
    video_quality = preset.get('video_quality', 8)

    try:
        writer = imageio.get_writer(video_path, fps=fps, codec='libx264',
                                   quality=video_quality, pixelformat='yuv420p',
                                   ffmpeg_params=['-preset', 'fast'])  # Fast encoding preset
    except Exception as e:
        raise RuntimeError(
            f"Failed to create video writer. Make sure ffmpeg is installed. Error: {e}"
        )

    # Rotation angle accumulator
    rotation_angle = 0.0

    try:
        for i, (a, b) in enumerate(zip(rms, cent)):
            # Dynamic dimensions: grow per frame
            if dynamic_dimensions:
                current_width = int(width * (dimension_factor ** i))
                current_height = int(height * (dimension_factor ** i))
                # Recompute plane for new dimensions
                Z0 = make_plane(current_width, current_height, preset["view"])

            # Apply rotation to the complex plane if enabled
            if rotation_enabled:
                rotation_angle += rotation_velocity
                # Rotate the view coordinates
                x_min, x_max, y_min, y_max = preset["view"]
                center_x = (x_min + x_max) / 2.0
                center_y = (y_min + y_max) / 2.0

                # Create rotated plane
                if dynamic_dimensions:
                    Z0_rotated = make_plane(current_width, current_height, preset["view"])
                else:
                    Z0_rotated = Z0.copy()

                # Apply rotation: rotate each point around center
                Z0_centered = Z0_rotated - (center_x + 1j * center_y)
                Z0_rotated = Z0_centered * np.exp(1j * rotation_angle) + (center_x + 1j * center_y)
                Z0 = Z0_rotated.astype(np.complex64)

            # Apply Z offset to the complex plane
            if z_offset_real != 0.0 or z_offset_imag != 0.0:
                Z0 = Z0 + (z_offset_real + 1j * z_offset_imag)

            # Calculate C with base offset
            c_real = preset["base_c_real"] + c_base_offset_real + preset["amp_real"] * (a - 0.5)
            c_imag = preset["base_c_imag"] + c_base_offset_imag + preset["amp_imag"] * (b - 0.5)

            # --- INERCIA (movimiento continuo) ---
            if prev_real is None:
                c_real_s, c_imag_s = c_real, c_imag
            else:
                c_real_s = prev_real + alpha_c * (c_real - prev_real)
                c_imag_s = prev_imag + alpha_c * (c_imag - prev_imag)

            # --- MICRO DRIFT (vida constante) ---
            drift = 0.0006
            c_real_s += drift * np.sin(2 * np.pi * i / 240.0)
            c_imag_s += drift * np.cos(2 * np.pi * i / 240.0)

            prev_real, prev_imag = c_real_s, c_imag_s

            # Get palette settings - ensure custom colors are always passed when available
            palette_name = preset.get("palette", "fire")
            custom_main = preset.get("custom_main_color")
            custom_accent = preset.get("custom_accent_color")

            # Use custom palette if colors are provided, regardless of palette name
            if custom_main and custom_accent:
                palette_name = "custom"

            # Generate frame (return RGB array, don't save)
            rgb_frame = julia(
                c_real=c_real_s,
                c_imag=c_imag_s,
                width=current_width,
                height=current_height,
                max_iter=preset["max_iter"],
                x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
                output_path=None,  # Don't save to file
                palette=palette_name,
                gamma=preset["gamma"],
                Z0=Z0,  # Reuse precomputed plane (or new one for dynamic)
                nu_buf=nu_buf[:current_height, :current_width] if dynamic_dimensions else nu_buf,
                t_buf=t_buf[:current_height, :current_width] if dynamic_dimensions else t_buf,
                return_rgb=True,  # Return RGB array
                power=power,  # Pass power parameter
                custom_palette=custom_main if palette_name == "custom" else None,
                custom_accent=custom_accent if palette_name == "custom" else None,
            )

            # Resize frame to initial dimensions if using dynamic (for consistent video size)
            if dynamic_dimensions and (current_width != width or current_height != height):
                img = Image.fromarray(rgb_frame)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                rgb_frame = np.array(img)

            # Write frame to video (always video format)
            writer.append_data(rgb_frame)

            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total_frames)

    finally:
        if writer:
            writer.close()

    # Add audio track to video if audio_path is provided
    if audio_path and os.path.exists(audio_path):
        try:
            import subprocess
            import shutil

            # Find ffmpeg executable
            ffmpeg_exe = None
            if IMAGEIO_FFMPEG_AVAILABLE:
                try:
                    import imageio_ffmpeg
                    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                except:
                    pass

            # Fallback to system ffmpeg
            if not ffmpeg_exe:
                ffmpeg_exe = shutil.which('ffmpeg')

            if not ffmpeg_exe:
                print("Warning: ffmpeg not found. Video generated without audio. Install ffmpeg to add audio.")
                return video_path

            # Create temporary video path
            temp_video_path = video_path.replace('.mp4', '_temp.mp4')
            if os.path.exists(video_path):
                os.rename(video_path, temp_video_path)
            else:
                print(f"Warning: Video file not found: {video_path}")
                return video_path

            # Use ffmpeg to combine video and audio
            ffmpeg_cmd = [
                ffmpeg_exe,
                '-i', temp_video_path,
                '-i', str(audio_path),
                '-c:v', 'copy',  # Copy video codec (no re-encoding)
                '-c:a', 'aac',   # Encode audio as AAC
                '-shortest',     # Use shortest stream duration
                '-y',            # Overwrite output file
                str(video_path)
            ]

            # Run ffmpeg command
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Remove temporary video
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
            else:
                # If ffmpeg fails, restore original video
                if os.path.exists(temp_video_path):
                    os.rename(temp_video_path, video_path)
                print(f"Warning: Failed to add audio to video: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Warning: ffmpeg timed out while adding audio")
            temp_video_path = video_path.replace('.mp4', '_temp.mp4')
            if os.path.exists(temp_video_path):
                os.rename(temp_video_path, video_path)
        except Exception as e:
            # If anything fails, restore original video
            temp_video_path = video_path.replace('.mp4', '_temp.mp4')
            if os.path.exists(temp_video_path):
                os.rename(temp_video_path, video_path)
            print(f"Warning: Failed to add audio to video: {e}")

    return video_path
