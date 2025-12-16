from audio_features import extract_rms, smooth
from fractals import julia_audio_frames

def main():
    audio_path = "assets/music/song.wav"  # o song.mp3
    fps = 30

    rms, times, sr, duration = extract_rms(audio_path, fps=fps)
    rms_s = smooth(rms, alpha=0.20)

    outdir = julia_audio_frames(
        rms=rms_s,
        width=800,
        height=600,
        max_iter=160,
        output_dir="assets/output/audio_frames",
    )

    print(f"Audio duration: {duration:.2f}s | frames: {len(rms_s)} | fps: {fps}")
    print(f"Frames generados en: {outdir}")

if __name__ == "__main__":
    main()

