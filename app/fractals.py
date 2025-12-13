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

def julia(
    c_real: float,
    c_imag: float,
    width: int=800,
    height: int=600,
    max_iter: int=150,
    x_min: float=-1.5,
    x_max: float=1.5,
    y_min: float=-1.5,
    y_max: float=1.5,
    output_path: str = "assets/output/julia.png"
) -> str:
    x = np.linspace(x_min,x_max,width)
    y = np.linspace(y_min,y_max,height)
    X, Y = np.meshgrid(x,y)
    Z = X + 1j * Y

    # Parámetro fijo c
    C = complex(c_real, c_imag)

    img = np.zeros(Z.shape, dtype=np.uint8)

    for i in range(max_iter):
        mask = np.abs(Z)<=2
        Z[mask] = Z[mask] ** 2 + C
        escaped = mask & (np.abs(Z)>2)
        img[escaped] = int( 255*i / max_iter)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    Image.fromarray(img, mode="L").save(output_path)
    return output_path

