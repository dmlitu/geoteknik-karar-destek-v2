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

        # SPT katkısı
        spt_etki = min(spt, 60) * 0.9

        # UCS katkısı — kaya için emprik tork tahmini
        if ucs > 0:
            ucs_etki = 2.2 * (ucs ** 0.6) * (cap_m ** 0.5) * 10
        else:
            ucs_etki = 0

        # RQD katkısı — düşük RQD = bloklu/kırıklı kaya = daha zor
        if rqd > 0:
            if rqd < 25:
                rqd_etki = 20
            elif rqd < 50:
                rqd_etki = 12
            elif rqd < 75:
                rqd_etki = 6
            else:
                rqd_etki = 2
        else:
            rqd_etki = 0

        katman_tork = baz + spt_etki + ucs_etki + rqd_etki
        max_tork = max(max_tork, katman_tork)

    # Çap etkisi: fore kazıkta tork çap^2 ile orantılı
    cap_carpani = (cap_m ** 2) * 3.5
    gerekli_tork = max_tork * cap_carpani
    return round(gerekli_tork, 1)


def casing_ihtiyaci_detayli(df: pd.DataFrame, yeralti_suyu: float, kazik_boyu: float):
    """
    Casing ihtiyacı için detaylı geoteknik değerlendirme.
    Döndürür: (durum_metni, gerekce_listesi, zorunlu_mu)
    """
    gerekce = []
    zorunlu = False
    sartli = False

    for _, row in df.iterrows():
        zemin = row["Zemin Tipi"]
        kohezyon = row["Kohezyon Durumu"]
        spt = float(row["SPT"]) if pd.notna(row["SPT"]) else 0
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]

        # Kohezyonsuz + su → kesin casing
        if kohezyon == "Kohezyonsuz" and yeralti_suyu > 0 and row["Başlangıç (m)"] >= yeralti_suyu:
            zorunlu = True
            gerekce.append(f"{row['Başlangıç (m)']}-{row['Bitiş (m)']}m: Kohezyonsuz zemin + yeraltı suyu")

        # Çok gevşek zemin → kesin casing
        if spt < 8 and kohezyon == "Kohezyonsuz":
            zorunlu = True
            gerekce.append(f"{row['Başlangıç (m)']}-{row['Bitiş (m)']}m: Çok gevşek zemin (SPT={spt})")

        # Kum/çakıl → kesin casing
        if zemin in ["Kum", "Çakıl"] and kalinlik > 1.0:
            zorunlu = True
            gerekce.append(f"{row['Başlangıç (m)']}-{row['Bitiş (m)']}m: {zemin} tabakası")

        # Dolgu → şartlı
        if zemin == "Dolgu" and kalinlik > 2.0:
            sartli = True
            gerekce.append(f"{row['Başlangıç (m)']}-{row['Bitiş (m)']}m: Kalın dolgu tabakası")

        # Orta gevşek kohezyonsuz → şartlı
        if spt < 15 and kohezyon == "Kohezyonsuz" and not zorunlu:
            sartli = True
            gerekce.append(f"{row['Başlangıç (m)']}-{row['Bitiş (m)']}m: Gevşek zemin (SPT={spt})")

    if not gerekce:
        gerekce.append("Zemin koşulları casing gerektirmiyor")

    if zorunlu:
        return "Muhafaza borusu gerekli", gerekce, True
    if sartli:
        return "Muhafaza borusu şartlı önerilir", gerekce, False
    return "Muhafaza borusu gerekmeyebilir", gerekce, False


def casing_oneri_basit(risk_list):
    yuksek = risk_list.count("Yüksek")
    orta = risk_list.count("Orta")
    if yuksek >= 1:
        return "Muhafaza borusu gerekli"
    if orta >= 2:
        return "Muhafaza borusu şartlı önerilir"
    return "Muhafaza borusu gerekmeyebilir"


def casing_metre_hesapla(df: pd.DataFrame) -> float:
    toplam = 0.0
    for _, row in df.iterrows():
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]
        if row["Stabilite Riski"] == "Yüksek":
            toplam += kalinlik
        elif row["Stabilite Riski"] == "Orta":
            toplam += 0.5 * kalinlik
    return round(toplam, 1)


def rop_hesapla(zemin_tipi: str, ucs: float, cap_mm: float) -> float:
    """
    ROP (Rate of Penetration) tahmini — m/saat
    Gerçek saha değerlerine dayalı emprik tahmin.
    """
    cap_m = cap_mm / 1000.0

    baz_rop = {
        "Dolgu": 7.0,
        "Kil": 5.5,
        "Silt": 6.0,
        "Kum": 4.5,
        "Çakıl": 3.5,
        "Ayrışmış Kaya": 2.2,
        "Kumtaşı": 1.4,
        "Kireçtaşı": 1.1,
        "Sert Kaya": 0.7,
    }.get(zemin_tipi, 3.0)

    # UCS etkisi
    if ucs > 0:
        ucs_faktoru = max(0.3, 1.0 - (ucs / 100.0) * 0.7)
        baz_rop *= ucs_faktoru

    # Çap etkisi — büyük çap daha yavaş
    cap_faktoru = max(0.5, 1.0 - (cap_m - 0.6) * 0.4)
    baz_rop *= cap_faktoru

    return round(max(baz_rop, 0.3), 2)


def tahmini_kazik_suresi(df: pd.DataFrame, cap_mm: float, kazik_boyu: float, casing_m: float) -> float:
    """
    Gerçekçi kazık tamamlama süresi tahmini (saat)
    - Her katman için ROP bazlı hesap
    - Uç değiştirme süresi
    - Casing kurulum süresi
    - Başlangıç/bitiş mobilizasyonu
    - Çap bazlı ek süre
    """
    sure = 1.0  # mobilizasyon

    uc_degistirme_sayisi = 0

    for _, row in df.iterrows():
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]
        ucs = float(row["UCS (MPa)"]) if pd.notna(row["UCS (MPa)"]) else 0
        rop = rop_hesapla(row["Zemin Tipi"], ucs, cap_mm)
        sure += kalinlik / rop

        # Uç değiştirme ihtimali
        uc_oneri = row.get("Uç Önerisi", "")
        if uc_oneri != "Standart zemin ucu yeterli":
            uc_degistirme_sayisi += 1

    # Uç değiştirme süresi (ortalama 45 dk)
    sure += uc_degistirme_sayisi * 0.75

    # Casing kurulum süresi (her metre ~6 dk)
    sure += casing_m * 0.1

    # Beton dökme ve temizleme
    cap_m = cap_mm / 1000.0
    beton_sure = (math.pi * (cap_m / 2) ** 2 * kazik_boyu) / 3.0
    sure += beton_sure

    # Derin kazık ek süresi
    if kazik_boyu >= 25:
        sure += 1.2
    elif kazik_boyu >= 20:
        sure += 0.7

    return round(sure, 1)


def mazot_tahmini(gerekli_tork: float, kazik_boyu: float):
    """
    Emprik mazot tahmini.
    Ağır rig makinelerinde ortalama tüketim tork ve delgi süresine bağlı.
    """
    metre_basi = round(6 + gerekli_tork * 0.06, 1)
    toplam = round(metre_basi * kazik_boyu, 1)
    return metre_basi, toplam


def makina_uygunluk(row, gerekli_tork, kazik_boyu, kazik_capi, casing_gerekli):
    max_derinlik = float(row.get("Max Derinlik (m)", 0))
    max_cap = float(row.get("Max Çap (mm)", 0))
    tork = float(row.get("Tork (kNm)", 0))
    casing_yeteneği = row.get("Casing Yeteneği", "Hayır")

    if max_derinlik < kazik_boyu:
        return "Uygun Değil", "Derinlik yetersiz"
    if max_cap < kazik_capi:
        return "Uygun Değil", "Çap kapasitesi yetersiz"
    if tork < gerekli_tork * 0.80:
        return "Uygun Değil", "Tork yetersiz"
    if casing_gerekli and casing_yeteneği == "Hayır":
        return "Şartlı Uygun", "Makine yeterli ancak casing yeteneği yok"
    if tork < gerekli_tork:
        return "Riskli", f"Tork sınırda ({tork} / {gerekli_tork} kNm)"
    if tork >= gerekli_tork * 1.3:
        return "Uygun", f"Tork yeterli ve güvenli ({tork} kNm)"
    return "Uygun", "Teknik olarak yeterli"
