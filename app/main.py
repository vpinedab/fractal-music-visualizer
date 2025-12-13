from fractals import julia

def main():
    path = julia(c_real=-0.285, c_imag=0.01)
    print(f"Julia generado en {path}")

if __name__ == "__main__":
    main()

