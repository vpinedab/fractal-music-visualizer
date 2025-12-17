from audio_features import extract_features
from fractals import JULIA_PRESETS, julia_audio_frames_2d

def main():
    rms, cent, sr, duration = extract_features(
        "assets/music/song.wav",
        fps=60
    )

    preset = JULIA_PRESETS["abstract"]  # o el nombre que estés usando

    julia_audio_frames_2d(
        rms=rms,
        cent=cent,
        preset=preset,
        width=800,
        height=600,
        output_dir="assets/output/audio_frames",
    )

    print("Frames:", len(rms), "Duration:", duration)

if __name__ == "__main__":
    main()


