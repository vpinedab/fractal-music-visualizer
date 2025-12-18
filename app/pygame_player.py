import os
import sys
import time
from pathlib import Path
import pygame


# =========================
# 1) Configuración general
# =========================

APP_ROOT = Path(__file__).resolve().parent   # .../fractal-music-visualizer/app
MUSIC_DIR = APP_ROOT / "assets" / "music"
FRAMES_ROOT = APP_ROOT / "assets" / "output" / "frames"

WINDOW_W, WINDOW_H = 800, 600
TARGET_FPS = 60  # Debe coincidir con fps usado para generar frames


# ==========================================
# 2) Utilidades: listar audios y frames
# ==========================================

def list_audio_files(music_dir: Path) -> list[Path]:
    """
    Regresa una lista de archivos de audio disponibles.
    Recomendación: usa WAV para evitar sorpresas de codecs.
    """
    if not music_dir.exists():
        return []

    exts = {".wav", ".mp3"}  # puedes limitar a {".wav"} si quieres
    files = [p for p in music_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.name.lower())
    return files


def count_frames(frames_dir: Path) -> int:
    """
    Cuenta cuántos frames existen con el patrón frame_XXXX.png
    """
    if not frames_dir.exists():
        return 0
    return len(list(frames_dir.glob("frame_*.png")))


def frame_path(frames_dir: Path, idx: int) -> Path:
    """
    Construye la ruta a un frame por índice: frame_0000.png, frame_0001.png, ...
    """
    return frames_dir / f"frame_{idx:04d}.png"


# ==========================================
# 3) Selector de audio (consola)
# ==========================================

def choose_audio_interactive(audio_files: list[Path]) -> Path:
    """
    Selector por consola: el usuario elige el índice.
    """
    if not audio_files:
        raise FileNotFoundError(
            f"No encontré audios en {MUSIC_DIR}. "
            "Copia un .wav a assets/music/ y vuelve a intentar."
        )

    print("APP_ROOT:", APP_ROOT)
    print("MUSIC_DIR:", MUSIC_DIR)
    print("Exists:", MUSIC_DIR.exists())


    print("\nAudios disponibles:")
    for i, p in enumerate(audio_files, start=1):
        print(f"  {i}) {p.name}")

    while True:
        choice = input("\nElige un número y presiona Enter: ").strip()
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(audio_files):
                return audio_files[n - 1]
        print("Entrada inválida. Intenta de nuevo.")


# ==========================================
# 4) Player Pygame: audio + frames sync
# ==========================================

def run_player(audio_path: Path, frames_dir: Path, fps: int = TARGET_FPS) -> None:
    """
    Player offline:
    - reproduce audio (pygame.mixer)
    - calcula frame_idx = floor(audio_time * fps)
    - carga y muestra el frame correspondiente
    """

    # --- Validaciones básicas ---
    n_frames = count_frames(frames_dir)
    if n_frames == 0:
        raise FileNotFoundError(
            f"No encontré frames en {frames_dir}. "
            "Genera frames primero (tu pipeline de Julia) y vuelve a intentar."
        )

    # --- Inicializar pygame ---
    pygame.init()

    # Mixer: audio
    # Nota: si tu audio es WAV, normalmente esto funciona sin problemas.
    pygame.mixer.init()

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Fractal Music Visualizer - Pygame Player")

    clock = pygame.time.Clock()

    # --- Cargar audio y empezar ---
    pygame.mixer.music.load(str(audio_path))
    pygame.mixer.music.play()

    # Para sincronización, usaremos "tiempo desde que le dimos play".
    # Esto evita depender demasiado de get_pos() (que puede variar por backend).
    start_time = time.perf_counter()

    paused = False
    pause_accum = 0.0  # total de tiempo pausado
    pause_start = None

    # Cache simple del último frame (evita recargar si no cambió)
    last_idx = -1
    last_surface = None

    running = True
    while running:
        # =========================
        # 4.1) Eventos (teclado/UI)
        # =========================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Space = pausa / reanuda
                if event.key == pygame.K_SPACE:
                    if not paused:
                        pygame.mixer.music.pause()
                        paused = True
                        pause_start = time.perf_counter()
                    else:
                        pygame.mixer.music.unpause()
                        paused = False
                        if pause_start is not None:
                            pause_accum += time.perf_counter() - pause_start
                            pause_start = None

                # R = reiniciar
                if event.key == pygame.K_r:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                    start_time = time.perf_counter()
                    paused = False
                    pause_accum = 0.0
                    pause_start = None
                    last_idx = -1
                    last_surface = None

        # =========================
        # 4.2) Calcular tiempo audio
        # =========================
        if paused:
            # Si está pausado, congelamos el tiempo "lógico"
            audio_time = (pause_start - start_time - pause_accum) if pause_start else 0.0
        else:
            audio_time = time.perf_counter() - start_time - pause_accum

        # Convertimos a índice de frame
        idx = int(audio_time * fps)

        # Terminar cuando ya no hay frames
        if idx >= n_frames:
            running = False
            continue

        # =========================
        # 4.3) Cargar y dibujar frame
        # =========================
        if idx != last_idx:
            fp = frame_path(frames_dir, idx)
            if fp.exists():
                img = pygame.image.load(str(fp))
                # Convert para blit rápido y asegurar formato display
                img = img.convert()
                # Escalar si hace falta (si tu frame ya es 800x600, esto es 1:1)
                if img.get_width() != WINDOW_W or img.get_height() != WINDOW_H:
                    img = pygame.transform.smoothscale(img, (WINDOW_W, WINDOW_H))
                last_surface = img
                last_idx = idx

        if last_surface is not None:
            screen.blit(last_surface, (0, 0))

        # (Opcional) Overlay mínimo: frame y tiempo
        # Para no introducir fuentes aún, lo dejamos para el siguiente paso.

        pygame.display.flip()

        # =========================
        # 4.4) Control FPS
        # =========================
        clock.tick(fps)

    # --- Limpieza ---
    pygame.mixer.music.stop()
    pygame.quit()


def main():
    audio_files = list_audio_files(MUSIC_DIR)
    audio_path = choose_audio_interactive(audio_files)

    frames_dir = FRAMES_ROOT / audio_path.stem

    print(f"\nReproduciendo: {audio_path.name}")
    print(f"Frames dir: {frames_dir}")
    print(f"FPS: {TARGET_FPS}\n")

    run_player(audio_path=audio_path, frames_dir=frames_dir, fps=TARGET_FPS)



if __name__ == "__main__":
    main()
