import numpy as np
import librosa

def _norm01_robust(x: np.ndarray) -> np.ndarray:
    p5, p95 = np.percentile(x, [5, 95])
    x = np.clip(x, p5, p95)
    return (x - x.min()) / (x.max() - x.min() + 1e-12)

def smooth_ar(x: np.ndarray, alpha_up: float, alpha_down: float) -> np.ndarray:
    """
    Attack/Release smoothing:
    - Si x sube: usa alpha_up (reacciona más rápido)
    - Si x baja: usa alpha_down (baja más lento)
    """
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        a = alpha_up if x[i] > out[i-1] else alpha_down
        out[i] = a * x[i] + (1 - a) * out[i-1]
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

    rms_s  = smooth_ar(rms_n,  alpha_up=0.10, alpha_down=0.04)
    cent_s = smooth_ar(cent_n, alpha_up=0.06, alpha_down=0.02)

    duration = len(y) / sr
    return rms_s, cent_s, sr, duration
