import pandas as pd
import math


def zemin_tork_katsayisi(zemin_tipi: str) -> float:
    """
    Zemin tipine göre spesifik delme direnci (kPa cinsinden emprik değer).
    Kaynak: Bauer, Soilmec saha referans tabloları + FHWA fore kazık rehberi.
    """
    mapping = {
        "Dolgu": 40,
        "Kil": 60,
        "Silt": 55,
        "Kum": 70,
        "Çakıl": 90,
        "Ayrışmış Kaya": 130,
        "Kumtaşı": 150,
        "Kireçtaşı": 165,
        "Sert Kaya": 190,
    }
    return mapping.get(zemin_tipi, 70)


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
    Fore kazık için gerekli minimum tork hesabı.

    Temel formül (Bauer / FHWA yaklaşımı):
        T = (π/2) * τ * D² * L_etkin * güvenlik

    Burada:
        τ  = zemin kayma direnci (kPa) — SPT ve UCS'den türetilir
        D  = kazık çapı (m)
        L  = ilgili katman kalınlığı (m)

    SPT → τ dönüşümü (Terzaghi & Peck):
        Kil için: τ ≈ SPT * 4 kPa
        Kum için: τ ≈ SPT * 2 kPa

    UCS → τ dönüşümü (kaya için):
        τ ≈ UCS / 10  (emprik, kaya zemin arayüzü için)

    Tork = τ * (π * D² / 4) * 0.5 * D * güvenlik_faktörü
         = τ * π * D³ / 8 * SF
    """
    cap_m = cap_mm / 1000.0
    max_tork = 0.0

    for _, row in df.iterrows():
        zemin = row["Zemin Tipi"]
        kohezyon = row.get("Kohezyon Durumu", "Kohezyonsuz")
        spt = float(row["SPT"]) if pd.notna(row["SPT"]) and float(row["SPT"]) > 0 else 0.0
        ucs = float(row["UCS (MPa)"]) if pd.notna(row["UCS (MPa)"]) and float(row["UCS (MPa)"]) > 0 else 0.0
        rqd = float(row["RQD"]) if pd.notna(row["RQD"]) and float(row["RQD"]) > 0 else 0.0

        # Kayma direnci tahmini (kPa)
        if ucs > 0:
            # Kaya zemin: UCS'den kayma direnci
            # τ = UCS(kPa) / 10 — ISRM emprik yaklaşımı
            tau = (ucs * 1000) / 10.0
        elif kohezyon == "Kohezyonlu":
            # Kil/silt: SPT'den undrained shear strength
            # Su ≈ SPT * 4 kPa (Terzaghi & Peck, 1967)
            tau = spt * 4.0
        else:
            # Kohezyonsuz: SPT'den sürtünme direnci
            # τ ≈ SPT * 2 kPa (emprik, FHWA)
            tau = spt * 2.0

        # Zemin tipi minimum direnci — çok düşük SPT durumunda
        tau = max(tau, zemin_tork_katsayisi(zemin) * 0.5)

        # RQD etkisi: düşük RQD = kırıklı kaya = daha zor
        if rqd > 0:
            if rqd < 25:
                rqd_carpani = 1.4
            elif rqd < 50:
                rqd_carpani = 1.2
            elif rqd < 75:
                rqd_carpani = 1.1
            else:
                rqd_carpani = 1.0
            tau *= rqd_carpani

        # Tork = τ * π * D³ / 8
        # Bu formül Kelly bar üzerindeki tork gereksinimini verir (kNm)
        # τ kPa = kN/m², D metre → T = kN/m² * m³ = kNm
        katman_tork = tau * math.pi * (cap_m ** 3) / 8.0

        # Güvenlik faktörü (saha koşulları, ekipman verimi, kayıplar)
        sf = 1.35
        katman_tork *= sf

        max_tork = max(max_tork, katman_tork)

    return round(max_tork, 1)


def casing_ihtiyaci_detayli(df: pd.DataFrame, yeralti_suyu: float, kazik_boyu: float):
    """
    Delik stabilitesi değerlendirmesi.
    Referans: FHWA Drilled Shaft Manual (FHWA-NHI-10-016)
    """
    gerekce = []
    zorunlu = False
    sartli = False

    for _, row in df.iterrows():
        zemin = row["Zemin Tipi"]
        kohezyon = row["Kohezyon Durumu"]
        spt = float(row["SPT"]) if pd.notna(row["SPT"]) else 0
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]
        kat_basi = row["Başlangıç (m)"]
        kat_sonu = row["Bitiş (m)"]

        # Kum/çakıl her durumda casing gerektirir (FHWA Sec. 5.3)
        if zemin in ["Kum", "Çakıl"] and kalinlik > 0.5:
            zorunlu = True
            gerekce.append(f"{kat_basi}-{kat_sonu}m: {zemin} — casing zorunlu (FHWA)")

        # Kohezyonsuz + yeraltı suyu kombinasyonu
        if kohezyon == "Kohezyonsuz" and yeralti_suyu > 0 and kat_basi >= yeralti_suyu:
            zorunlu = True
            gerekce.append(f"{kat_basi}-{kat_sonu}m: Kohezyonsuz + YAS — casing zorunlu")

        # Çok gevşek zemin (SPT < 10)
        if spt < 10 and kohezyon == "Kohezyonsuz":
            zorunlu = True
            gerekce.append(f"{kat_basi}-{kat_sonu}m: Cok gevşek (SPT={spt}) — casing zorunlu")

        # Kalın dolgu
        if zemin == "Dolgu" and kalinlik > 2.0:
            sartli = True
            gerekce.append(f"{kat_basi}-{kat_sonu}m: Kalin dolgu — casing onerilir")

        # Orta gevşek kohezyonsuz
        if spt < 20 and kohezyon == "Kohezyonsuz" and zemin not in ["Kum", "Çakıl"] and not zorunlu:
            sartli = True
            gerekce.append(f"{kat_basi}-{kat_sonu}m: Gevşek zemin (SPT={spt}) — casing onerilir")

    if not gerekce:
        gerekce.append("Zemin kosullari casing gerektirmiyor")

    if zorunlu:
        return "Muhafaza borusu gerekli", gerekce, True
    if sartli:
        return "Muhafaza borusu sartli onerilir", gerekce, False
    return "Muhafaza borusu gerekmeyebilir", gerekce, False


def casing_oneri_basit(risk_list):
    yuksek = risk_list.count("Yüksek")
    orta = risk_list.count("Orta")
    if yuksek >= 1:
        return "Muhafaza borusu gerekli"
    if orta >= 2:
        return "Muhafaza borusu sartli onerilir"
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
    ROP (Rate of Penetration) — m/saat.
    Kaynak: Saha ölçüm veritabanları (Soilmec, IMT referans değerleri)
    800mm çap, standart makine için baz değerler.
    """
    cap_m = cap_mm / 1000.0

    # Baz ROP değerleri (m/saat) — 800mm çap, orta güç makine için
    baz_rop = {
        "Dolgu": 8.0,
        "Kil": 6.0,
        "Silt": 6.5,
        "Kum": 5.0,
        "Çakıl": 3.5,
        "Ayrışmış Kaya": 2.0,
        "Kumtaşı": 1.2,
        "Kireçtaşı": 0.9,
        "Sert Kaya": 0.5,
    }.get(zemin_tipi, 3.0)

    # UCS etkisi — kaya direnci arttıkça ROP düşer
    # Referans: Teale (1965) specific energy konsepti
    if ucs > 0:
        # Her 10 MPa UCS için ~%15 ROP düşüşü (emprik)
        ucs_faktoru = max(0.25, 1.0 - (ucs / 100.0) * 0.75)
        baz_rop *= ucs_faktoru

    # Çap etkisi — büyük çap daha yavaş
    # Referans: D/D_ref oranına göre lineer düzeltme
    d_ref = 0.8  # referans çap
    cap_faktoru = max(0.45, 1.0 - (cap_m - d_ref) * 0.5)
    baz_rop *= cap_faktoru

    return round(max(baz_rop, 0.25), 2)


def tahmini_kazik_suresi(df: pd.DataFrame, cap_mm: float, kazik_boyu: float, casing_m: float) -> float:
    """
    Kazık tamamlama süresi tahmini (saat).
    Bileşenler:
    1. Delgi süresi: her katman için ROP bazlı
    2. Uç değiştirme: zemin geçişlerinde
    3. Casing kurulum: ~6 dk/m
    4. Beton dökme: hacme göre ~20 dk/m³
    5. Mobilizasyon/temizleme: sabit süre
    Kaynak: Soilmec üretim tabloları, saha gözlemleri
    """
    sure = 0.75  # mobilizasyon + kurulum (saat)

    uc_degistirme_sayisi = 0
    onceki_zemin = None

    for _, row in df.iterrows():
        kalinlik = row["Bitiş (m)"] - row["Başlangıç (m)"]
        ucs = float(row["UCS (MPa)"]) if pd.notna(row["UCS (MPa)"]) else 0
        rop = rop_hesapla(row["Zemin Tipi"], ucs, cap_mm)
        sure += kalinlik / rop

        # Zemin geçişinde uç değiştirme ihtimali
        uc_val = row.get("Uç Önerisi", "")
        if uc_val != "Standart zemin ucu yeterli" and onceki_zemin != row["Zemin Tipi"]:
            uc_degistirme_sayisi += 1

        onceki_zemin = row["Zemin Tipi"]

    # Uç değiştirme süresi: ortalama 30-45 dakika
    sure += uc_degistirme_sayisi * 0.6

    # Casing kurulum: ~6 dk/m (çekme + sürme)
    sure += casing_m * 0.1

    # Beton dökme süresi
    cap_m = cap_mm / 1000.0
    hacim = math.pi * (cap_m / 2) ** 2 * kazik_boyu  # m³
    # ~20 dk/m³ beton dökme + temizleme
    sure += hacim * (20 / 60)

    # Derin kazık ek süresi (rod ekleme, rod çıkarma)
    if kazik_boyu >= 30:
        sure += 1.5
    elif kazik_boyu >= 20:
        sure += 0.8

    # Dewater/stabilizasyon — su varsa
    return round(sure, 1)


def mazot_tahmini(gerekli_tork: float, kazik_boyu: float):
    """
    Yakıt tüketimi tahmini.
    Referans: Casagrande/Soilmec teknik bültenler
    Ortalama rotary rig: 15-25 L/saat bekleme, 40-80 L/saat delgi
    Basitleştirilmiş: metre başı tüketim = f(tork gereksinimi)

    Düşük tork (<100 kNm): ~8-12 L/m
    Orta tork (100-200 kNm): ~12-20 L/m
    Yüksek tork (>200 kNm): ~20-35 L/m
    """
    if gerekli_tork < 100:
        metre_basi = round(8 + gerekli_tork * 0.04, 1)
    elif gerekli_tork < 200:
        metre_basi = round(12 + (gerekli_tork - 100) * 0.08, 1)
    else:
        metre_basi = round(20 + (gerekli_tork - 200) * 0.075, 1)

    toplam = round(metre_basi * kazik_boyu, 1)
    return metre_basi, toplam


def makina_uygunluk(row, gerekli_tork, kazik_boyu, kazik_capi, casing_gerekli):
    max_derinlik = float(row.get("Max Derinlik (m)", 0))
    max_cap = float(row.get("Max Çap (mm)", 0))
    tork = float(row.get("Tork (kNm)", 0))
    casing_yeteneği = row.get("Casing Yeteneği", "Hayır")

    if max_derinlik < kazik_boyu:
        return "Uygun Değil", f"Derinlik yetersiz ({max_derinlik}m < {kazik_boyu}m)"
    if max_cap < kazik_capi:
        return "Uygun Değil", f"Cap yetersiz ({max_cap}mm < {kazik_capi}mm)"
    if tork < gerekli_tork * 0.80:
        return "Uygun Değil", f"Tork yetersiz ({tork} kNm, gerekli {gerekli_tork} kNm)"
    if casing_gerekli and casing_yeteneği == "Hayır":
        return "Şartlı Uygun", "Casing yeteneği yok, ek ekipman gerekli"
    if tork < gerekli_tork:
        return "Riskli", f"Tork sinirda ({tork} / {gerekli_tork} kNm)"
    if tork >= gerekli_tork * 1.25:
        return "Uygun", f"Yeterli kapasite ({tork} kNm)"
    return "Uygun", "Teknik olarak yeterli"
