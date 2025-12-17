import numpy as np
import librosa

# Normalización
def _norm01_robust(x: np.ndarray) -> np.ndarray:
    p5, p95 = np.percentile(x, [5, 95]) # Calcula los percentiles 5 y 95
    x = np.clip(x, p5, p95) # Todo <p5 -> p5 y todo >p95 -> p95
    return (x - x.min()) / (x.max() - x.min() + 1e-12) # Escala el arreglo entre 0 y 1

def smooth(x: np.ndarray, alpha: float = 0.15) -> np.ndarray:
    out = np.empty_like(x)
    out[0] = x[0]

    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    # Si alpha es pequeño, hay cambios lentos y fluidos
    # Si alpha es grande, responde rápido pero tiembla

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

    rms_s = smooth(rms_n, alpha=0.12)
    cent_s = smooth(cent_n, alpha=0.06)

    duration = len(y) / sr

    return rms_s, cent_s, sr, duration
