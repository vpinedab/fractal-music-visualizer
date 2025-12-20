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

def extract_features(audio_path: str, fps: int = 30, start_time: float = None, end_time: float = None, return_waveform: bool = False, normalize: bool = False):
    """
    Extract audio features (RMS and spectral centroid), optionally with waveform data.

    Args:
        audio_path: Path to audio file
        fps: Frames per second for feature extraction
        start_time: Start time in seconds (None = start from beginning)
        end_time: End time in seconds (None = end at file end)
        return_waveform: If True, also return waveform data per frame
        normalize: If True, normalize audio to prevent clipping and improve visualization

    Returns:
        rms_s: Smoothed RMS energy array
        cent_s: Smoothed spectral centroid array
        sr: Sample rate
        duration: Duration of processed audio segment
        waveform (optional): Waveform data per frame (if return_waveform=True)
    """
    # Load full audio first to get duration
    y_full, sr = librosa.load(audio_path, sr=None, mono=True)
    
    # Normalize audio if requested (peak normalization to prevent clipping)
    if normalize:
        max_val = np.abs(y_full).max()
        if max_val > 0:
            # Normalize to 90% of maximum to prevent clipping while maintaining dynamics
            y_full = y_full * (0.9 / max_val)
    full_duration = len(y_full) / sr

    # Apply trimming if specified
    if start_time is not None or end_time is not None:
        start_sample = int(start_time * sr) if start_time is not None else 0
        end_sample = int(end_time * sr) if end_time is not None else len(y_full)

        # Clamp to valid range
        start_sample = max(0, min(start_sample, len(y_full)))
        end_sample = max(start_sample + 1, min(end_sample, len(y_full)))

        y = y_full[start_sample:end_sample]
        duration = len(y) / sr
    else:
        y = y_full
        duration = full_duration

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

    # Extract waveform data per frame if requested
    waveform = None
    if return_waveform:
        n_frames = len(rms_s)
        waveform = np.zeros(n_frames, dtype=np.float32)
        for i in range(n_frames):
            frame_start = i * hop_length
            frame_end = min(frame_start + frame_length, len(y))
            if frame_end > frame_start:
                # Get RMS of this frame's waveform segment
                frame_wave = y[frame_start:frame_end]
                waveform[i] = np.abs(frame_wave).mean()  # Mean absolute amplitude
        # Normalize waveform
        if waveform.max() > 0:
            waveform = waveform / waveform.max()
        return rms_s, cent_s, sr, duration, waveform

    return rms_s, cent_s, sr, duration

def audio_profile(audio_path: str, fps: int = 60, normalize: bool = False) -> dict:
    """
    Devuelve métricas globales del audio para elegir preset.
    - energy_* proviene de RMS
    - bright_* proviene de spectral centroid
    """
    # Reusa tu pipeline existente
    rms, cent, sr, duration = extract_features(audio_path, fps=fps, normalize=normalize)

    # Estadísticos robustos
    e_mean = float(np.mean(rms))
    e_std  = float(np.std(rms))
    e_p90  = float(np.percentile(rms, 90))
    e_p10  = float(np.percentile(rms, 10))
    e_dyn  = float(e_p90 - e_p10)  # rango dinámico robusto
    e_spiky = float(np.mean(rms > np.percentile(rms, 95)))  # proporción de picos

    b_mean = float(np.mean(cent))
    b_std  = float(np.std(cent))
    b_p90  = float(np.percentile(cent, 90))

    # Tempo (opcional, pero útil para "energetic")
    y, _sr = librosa.load(audio_path, sr=sr, mono=True)
    # Apply normalization if requested
    if normalize:
        max_val = np.abs(y).max()
        if max_val > 0:
            y = y * (0.9 / max_val)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo)

    return {
        "duration": float(duration),
        "sr": int(sr),
        "fps": int(fps),

        "energy_mean": e_mean,
        "energy_std": e_std,
        "energy_p90": e_p90,
        "energy_dyn": e_dyn,
        "energy_spiky": e_spiky,

        "bright_mean": b_mean,
        "bright_std": b_std,
        "bright_p90": b_p90,

        "tempo": tempo,
    }
