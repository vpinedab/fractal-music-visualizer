import numpy as np
import librosa

def _norm01_robust(x: np.ndarray) -> np.ndarray:
    p5, p95 = np.percentile(x, [5, 95])
    x = np.clip(x, p5, p95)
    return (x - x.min()) / (x.max() - x.min() + 1e-12)

def smooth(x: np.ndarray, alpha: float = 0.15) -> np.ndarray:
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out

def extract_features(audio_path: str, fps: int = 30):
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    hop_length = max(1, int(sr / fps))
    frame_length = 4 * hop_length

    rms = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]

    cent = librosa.feature.spectral_centroid(
        y=y,
        sr=sr,
        hop_length=hop_length
    )[0]

    rms_n = _norm01_robust(rms)
    cent_n = _norm01_robust(cent)

    # ✅ Más suave / lento:
    rms_s  = smooth(rms_n,  alpha=0.08)  # antes 0.12
    cent_s = smooth(cent_n, alpha=0.03)  # antes 0.06 (cent es más nervioso)

    duration = len(y) / sr
    return rms_s, cent_s, sr, duration
