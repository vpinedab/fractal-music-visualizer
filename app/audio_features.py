import numpy as np
import librosa

def extract_rms(audio_path: str, fps: int = 30):
    """
    Devuelve:
      rms_norm: array en [0,1] con energía por frame
      times: tiempos (segundos) de cada frame
      sr: sample rate
      duration: duración del audio (segundos)
    """
    y, sr = librosa.load(audio_path, sr=None, mono=True)

    hop_length = int(sr / fps)  # 1 valor RMS por frame aprox
    frame_length = 4 * hop_length  # ventana un poco más grande para estabilidad

    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    # Normalización robusta (evita que un pico destruya todo)
    p5, p95 = np.percentile(rms, [5, 95])
    rms_clip = np.clip(rms, p5, p95)
    rms_norm = (rms_clip - rms_clip.min()) / (rms_clip.max() - rms_clip.min() + 1e-12)

    times = librosa.frames_to_time(np.arange(len(rms_norm)), sr=sr, hop_length=hop_length)
    duration = len(y) / sr

    return rms_norm, times, sr, duration

def smooth(x: np.ndarray, alpha: float = 0.25):
    """
    Suavizado exponencial para evitar 'temblores' en el fractal.
    alpha más pequeño = más suave.
    """
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out
