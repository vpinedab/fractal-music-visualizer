from fractals import julia_animation

def main():
    outdir = julia_animation(frames=120)
    print(f"Frames Julia generado en: {outdir}")

if __name__ == "__main__":
    main()

