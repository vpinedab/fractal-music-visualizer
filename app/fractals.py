import numpy as np
from PIL import Image
import os

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
    for i in range(max_iter):
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
    gamma: float = 0.85, # Controla contraste del gradiente
) -> str:
    
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    C = complex(c_real, c_imag)

    it = np.zeros(Z.shape, dtype=np.int32) # Guarda en que iteración escaó cada punto
    z_escape = np.zeros(Z.shape, dtype=np.complex64)
    alive = np.ones(Z.shape, dtype=bool) # Máscara booleana: True si aún no escapa

    for i in range(max_iter):
        Z[alive] = Z[alive] * Z[alive] + C
        
        escaped = alive & (np.abs(Z) > 2.0)
        it[escaped] = i
        z_escape[escaped] = Z[escaped]
        alive[escaped] = False

        if not alive.any():
            break

    esc = ~alive # Máscara de los que escaparon
    nu = np.zeros(Z.shape, dtype=np.float32)

    z_abs = np.abs(z_escape[esc])  # |z| en el punto de escape
    z_abs = np.maximum(z_abs, 1e-12) # evita log(0) con maximum

    nu[esc] = it[esc] + 1.0 - np.log(np.log(z_abs)) / np.log(2.0)
    # En vez de colorear solo por i, usa una corrección con 
    # log⁡(log⁡∣z∣)
    # log(log∣z∣) para interpolar el escape “entre iteraciones”.

    # Normalización
    t = np.zeros_like(nu, dtype=np.float32)

    if esc.any():
        nu_esc = nu[esc]

        # Estiramiento de contraste robusto
        p_lo, p_hi = np.percentile(nu_esc, [2, 98])
        if p_hi - p_lo < 1e-6:
            p_lo, p_hi = nu_esc.min(), nu_esc.max() + 1e-6

        t[esc] = (nu_esc - p_lo) / (p_hi - p_lo)

    t = np.clip(t, 0.0, 1.0)
    # Contraste adicional (realza estructura fina)
    contrast = 1.25  # prueba: 1.1, 1.25, 1.4
    t = np.clip((t - 0.5) * contrast + 0.5, 0.0, 1.0)

    t = t ** gamma


    # Aplicar paleta (selector genérico)
    pal_fn = PALETTES.get(palette, _palette_fire)
    rgb = pal_fn(t)

    # Interior / fondo (selector genérico)
    interior = INTERIOR_COLORS.get(palette, (0, 0, 0))
    rgb[alive] = interior


    # Guardar
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    Image.fromarray(rgb, mode="RGB").save(output_path)
    return output_path

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
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    x_min, x_max, y_min, y_max = preset["view"]

    max_delta = 0.006 # prueba: 0.005, 0.008, 0.012

    prev_real = None
    prev_imag = None

    for i, (a, b) in enumerate(zip(rms, cent)):
        c_real = preset["base_c_real"] + preset["amp_real"] * (a - 0.5)
        c_imag = preset["base_c_imag"] + preset["amp_imag"] * (b - 0.5)

        if prev_real is not None:
            c_real = prev_real + np.clip(c_real - prev_real, -max_delta, max_delta)
            c_imag = prev_imag + np.clip(c_imag - prev_imag, -max_delta, max_delta)

        prev_real, prev_imag = c_real, c_imag
       
        out = os.path.join(output_dir, f"frame_{i:04d}.png")
        julia(
            c_real=c_real,
            c_imag=c_imag,
            width=width,
            height=height,
            max_iter=preset["max_iter"],
            x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,
            output_path=out,
            palette=preset["palette"],
            gamma=preset["gamma"],
        )

    return output_dir