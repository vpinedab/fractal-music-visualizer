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
    Paleta 'sea': azul dominante, con acentos morados y verdes.
    Vibra a mar (deep ocean + bioluminiscencia suave).
    """
    t = np.clip(t, 0.0, 1.0).astype(np.float32)

    stops = np.array([
        [ 10,  18,  40],  # deep navy (muy oscuro)
        [ 12,  30,  80],  # azul marino
        [ 40,  65, 140],  # azul océano (base dominante)
        [ 85,  75, 150],  # morado frío (acentos, no domina)
        [ 65, 105, 155],  # verde/teal (bioluminiscencia)
        [160, 220, 210],  # espuma suave (highlight, no blanco)
    ], dtype=np.float32)

    x = np.linspace(0.0, 1.0, len(stops), dtype=np.float32)

    tf = t.ravel()
    r = np.interp(tf, x, stops[:, 0])
    g = np.interp(tf, x, stops[:, 1])
    b = np.interp(tf, x, stops[:, 2])

    rgb = np.stack([r, g, b], axis=1).reshape(t.shape[0], t.shape[1], 3)
    return rgb.astype(np.uint8)




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
    t = nu / max_iter
    t = np.clip(t, 0.0, 1.0)
    t = t ** gamma

    # Aplicar paleta
    if palette == "ocean":
        rgb = _palette_ocean(t)
        rgb[alive] = (80, 200, 200)
    else:
        rgb = _palette_fire(t)
        rgb[alive] = (0,0,0)

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
        "max_iter": 220,
        "palette": "ocean",
        "gamma": 0.95,
        "view": (-1.2, 1.2, -1.0, 1.0), 
    },
    "energetic": {
        "base_c_real": -0.70,
        "base_c_imag":  0.27015,
        "amp_real": 0.65,
        "amp_imag": 0.55,
        "max_iter": 200,
        "palette": "fire",
        "gamma": 0.85,
        "view": (-1.2, 1.2, -1.0, 1.0),
    },
    "experimental": {
        "base_c_real": -0.40,
        "base_c_imag":  0.60,
        "amp_real": 0.65,
        "amp_imag": 0.55,
        "max_iter": 240,
        "palette": "fire",
        "gamma": 0.80,
        "view": (-1.2, 1.2, -1.0, 1.0),
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

    max_delta = 0.008  # prueba: 0.005, 0.008, 0.012

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