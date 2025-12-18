def choose_preset_name(p: dict) -> str:
    """
    Heurística simple (explicable) -> un preset.
    Todos los thresholds asumen features normalizados [0,1].
    Ajusta con 2-3 audios reales y listo.
    """
    e = p["energy_mean"]
    e_dyn = p["energy_dyn"]
    e_spiky = p["energy_spiky"]
    b = p["bright_mean"]
    b_std = p["bright_std"]
    tempo = p["tempo"]

    # 1) Energetic: por TEMPO alto o energía alta + picos
    #    (esto garantiza que electronic caiga en energetic)
    if (tempo >= 138) or (tempo >= 128 and e >= 0.50) or (e > 0.62 and (e_spiky > 0.08 or tempo > 120)):
        return "energetic"

    # 2) Brillante + cambiante = abstract (más “neón”, más movimiento visual)
    if (b > 0.57 and (b_std > 0.18 or e_dyn > 0.28)):
        return "abstract"

    # 3) Oscuro + estable = deep_sea (sensación “abismo”)
    if (b < 0.38 and e < 0.52):
        return "deep_sea"

    # 4) Calm vs Ethereal: aquí es donde decidimos tu "acoustic"
    #    Calm si NO es spiky y NO es muy dinámico; si no, ethereal.
    #    (relajamos e_dyn, porque en tus audios está muy alto)
    if (0.40 <= b <= 0.62) and (e_spiky < 0.055) and (e_dyn < 0.55):
        return "calm"

    # 5) Armónico / “glow matemático”: brillo medio-bajo, poca varianza
    if (b < 0.55 and b_std < 0.14 and e_dyn < 0.22):
        return "mathematical"

    # 6) Caso general “bonito” cuando no cae en lo demás
    return "ethereal"
