import pandas as pd


def zemin_tork_katsayisi(zemin_tipi: str) -> int:
    mapping = {
        "Dolgu": 40,
        "Kil": 55,
        "Silt": 50,
        "Kum": 60,
        "Çakıl": 80,
        "Ayrışmış Kaya": 110,
        "Kumtaşı": 130,
        "Kireçtaşı": 145,
        "Sert Kaya": 170
    }
    return mapping.get(zemin_tipi, 60)


def gerekli_tork_hesapla(df: pd.DataFrame, cap_mm: float) -> float:
    max_tork = 0

    for _, row in df.iterrows():
        baz = zemin_tork_katsayisi(row["Zemin Tipi"])
        spt = float(row["SPT"]) if pd.notna(row["SPT"]) else 0
        ucs = float(row["UCS (MPa)"]) if pd.notna(row["UCS (MPa)"]) else 0
        rqd = float(row["RQD"]) if pd.notna(row["RQD"]) else 0

        spt_etki = min(spt, 60) * 0.8
        ucs_etki = ucs * 1.8

        if rqd == 0:
            rqd_etki = 0
        elif rqd < 25:
            rqd_etki = 15
        elif rqd < 50:
            rqd_etki = 10
        else:
            rqd_etki = 5

        katman_tork = baz + spt_etki + ucs_etki + rqd_etki
        max_tork = max(max_tork, katman_tork)

    cap_carpani = cap_mm / 1000.0
    gerekli_tork = max_tork * cap_carpani
    return round(gerekli_tork, 1)


def stabilite_riski(zemin_tipi: str, kohezyon: str, yeralti_suyu: float, spt: float) -> str:
    if zemin_tipi in ["Kum", "Çakıl"] and yeralti_suyu >= 0:
        return "Yüksek"
    if kohezyon == "Kohezyonsuz" and spt <= 15:
        return "Yüksek"
    if kohezyon == "Kohezyonsuz" and spt <= 30:
        return "Orta"
    if zemin_tipi == "Dolgu":
        return "Orta"
    return "Düşük"


def casing_metre_hesapla(df: pd.DataFrame) -> float:
    toplam = 0.0
    for _, row in df.iterrows():
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]
        if row["Stabilite Riski"] == "Yüksek":
            toplam += kalinlik
        elif row["Stabilite Riski"] == "Orta":
            toplam += 0.5 * kalinlik
    return round(toplam, 1)


def tahmini_kazik_suresi(df: pd.DataFrame, cap_mm: float, kazik_boyu: float, casing_m: float) -> float:
    sure = 1.5

    for _, row in df.iterrows():
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]
        zemin = row["Zemin Tipi"]

        if zemin in ["Dolgu", "Kil", "Silt"]:
            hiz = 6.0
        elif zemin in ["Kum", "Çakıl"]:
            hiz = 4.0
        elif zemin == "Ayrışmış Kaya":
            hiz = 2.8
        elif zemin in ["Kumtaşı", "Kireçtaşı"]:
            hiz = 1.8
        else:
            hiz = 1.2

        sure += kalinlik / hiz

        if row.get("Uç Önerisi", "") != "Standart zemin ucu yeterli":
            sure += 0.3

    if cap_mm >= 1000:
        sure += 1.0
    elif cap_mm >= 800:
        sure += 0.6

    sure += casing_m * 0.08

    if kazik_boyu >= 20:
        sure += 0.7

    return round(sure, 1)


def mazot_tahmini(gerekli_tork: float, kazik_boyu: float):
    metre_basi = round(8 + gerekli_tork * 0.08, 1)
    toplam = round(metre_basi * kazik_boyu, 1)
    return metre_basi, toplam


def makina_uygunluk(row, gerekli_tork, kazik_boyu, kazik_capi, casing_gerekli):
    if row["Max Derinlik (m)"] < kazik_boyu:
        return "Uygun Değil", "Derinlik yetersiz"

    if row["Max Çap (mm)"] < kazik_capi:
        return "Uygun Değil", "Çap kapasitesi yetersiz"

    if row["Tork (kNm)"] < gerekli_tork * 0.85:
        return "Uygun Değil", "Tork yetersiz"

    if casing_gerekli and row["Casing Yeteneği"] == "Hayır":
        return "Şartlı Uygun", "Makine yeterli ancak casing yeteneği yok"

    if row["Tork (kNm)"] < gerekli_tork:
        return "Riskli", "Tork sınırda"

    return "Uygun", "Teknik olarak yeterli"
