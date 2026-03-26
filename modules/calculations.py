import pandas as pd
import math


def zemin_tork_katsayisi(zemin_tipi: str) -> float:
    mapping = {
        "Dolgu": 40,
        "Kil": 55,
        "Silt": 50,
        "Kum": 65,
        "Çakıl": 85,
        "Ayrışmış Kaya": 120,
        "Kumtaşı": 140,
        "Kireçtaşı": 155,
        "Sert Kaya": 180
    }
    return mapping.get(zemin_tipi, 65)


def stabilite_riski(zemin_tipi: str, kohezyon: str, yeralti_suyu: float, spt: float) -> str:
    if zemin_tipi in ["Kum", "Çakıl"] and yeralti_suyu >= 0:
        return "Yüksek"
    if kohezyon == "Kohezyonsuz" and spt <= 10:
        return "Yüksek"
    if kohezyon == "Kohezyonsuz" and spt <= 30:
        return "Orta"
    if zemin_tipi == "Dolgu":
        return "Orta"
    return "Düşük"


def stabilite_skoru(zemin_tipi: str, kohezyon: str, spt: float, yeralti_suyu: float):
    skor = 0
    if zemin_tipi in ["Kum", "Çakıl", "Dolgu"]:
        skor += 35
    if kohezyon == "Kohezyonsuz":
        skor += 25
    if spt <= 10:
        skor += 25
    elif spt <= 20:
        skor += 15
    elif spt <= 30:
        skor += 8
    if yeralti_suyu > 0:
        skor += 15
    skor = min(skor, 100)
    if skor < 30:
        durum = "Stabil"
    elif skor < 60:
        durum = "Orta Risk"
    else:
        durum = "Yüksek Risk"
    return skor, durum


def gerekli_tork_hesapla(df: pd.DataFrame, cap_mm: float) -> float:
    """
    Tork tahmini:
    - Zemin tipine göre baz katsayı
    - SPT etkisi (kohezyonsuz zemin için)
    - UCS etkisi (kaya için) — emprik: T ≈ k * UCS^0.6 * D^2.5
    - RQD etkisi (kaya kalitesi)
    - Çap etkisi: tork çap^2 ile orantılı artar
    """
    cap_m = cap_mm / 1000.0
    max_tork = 0

    for _, row in df.iterrows():
        baz = zemin_tork_katsayisi(row["Zemin Tipi"])
        spt = float(row["SPT"]) if pd.notna(row["SPT"]) and row["SPT"] > 0 else 0
        ucs = float(row["UCS (MPa)"]) if pd.notna(row["UCS (MPa)"]) and row["UCS (MPa)"] > 0 else 0
        rqd = float(row["RQD"]) if pd.notna(row["RQD"]) and row["RQD"] > 0 else 0

        # SPT katkıs
