from pathlib import Path
from audio_features import extract_features, audio_profile
from fractals import JULIA_PRESETS, julia_audio_frames_2d
from preset_selector import choose_preset_name

def main():
    audio_path = Path("assets/music/lofi.wav")
    fps = 60

    # Frames (lo que ya usas para animar)
    rms, cent, sr, duration = extract_features(audio_path, fps=fps)

    # Perfil global (para escoger preset)
    prof = audio_profile(str(audio_path), fps=fps)
    preset_name = choose_preset_name(prof)
    preset = JULIA_PRESETS[preset_name]

    # NUEVO: carpeta por canción
    frames_root = Path("assets/output/frames")
    frames_dir = frames_root / audio_path.stem   # "song.wav" -> "song"

    print("Auto preset:", preset_name, "| tempo:", prof["tempo"])
    print("Frames:", len(rms), "Duration:", duration)
    print("Frames dir:", frames_dir)

    julia_audio_frames_2d(
        rms=rms,
        cent=cent,
        preset=preset,
        width=800,
        height=600,
        output_dir=str(frames_dir),
    )

if __name__ == "__main__":
    main()
