from fractals import mandelbrot_zoom

def main():
    path = mandelbrot_zoom(frames=120)
    print(f"Fractal generados")

if __name__ == "__main__":
    main()

