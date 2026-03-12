import pandas as pd


def default_zemin_logu():
    return pd.DataFrame([
        {
            "Başlangıç (m)": 0.0,
            "Bitiş (m)": 3.0,
            "Formasyon": "Dolgu",
            "Zemin Tipi": "Dolgu",
            "Kohezyon Durumu": "Kohezyonsuz",
            "SPT": 10,
            "UCS (MPa)": 0.0,
            "RQD": 0,
            "Ayrışma Derecesi": "Yok",
            "Yeraltı Suyu Etkisi": "Orta",
            "Açıklama": "Gevşek dolgu"
        },
        {
            "Başlangıç (m)": 3.0,
            "Bitiş (m)": 8.0,
            "Formasyon": "Kil",
            "Zemin Tipi": "Kil",
            "Kohezyon Durumu": "Kohezyonlu",
            "SPT": 18,
            "UCS (MPa)": 0.0,
            "RQD": 0,
            "Ayrışma Derecesi": "Yok",
            "Yeraltı Suyu Etkisi": "Düşük",
            "Açıklama": "Orta katı"
        },
        {
            "Başlangıç (m)": 8.0,
            "Bitiş (m)": 18.0,
            "Formasyon": "Kumtaşı",
            "Zemin Tipi": "Kumtaşı",
            "Kohezyon Durumu": "Kaya",
            "SPT": 50,
            "UCS (MPa)": 22.0,
            "RQD": 45,
            "Ayrışma Derecesi": "Orta",
            "Yeraltı Suyu Etkisi": "Düşük",
            "Açıklama": "Çatlaklı kaya"
        }
    ])


def default_makine_parki():
    return pd.DataFrame([
        {
            "Makine Adı": "Rig A",
            "Marka/Model": "Model A",
            "Makine Tipi": "Fore Kazık",
            "Max Derinlik (m)": 24,
            "Max Çap (mm)": 1000,
            "Tork (kNm)": 180,
            "Casing Yeteneği": "Evet",
            "Kaya Delgi": "Orta",
            "Dar Alan Uygunluğu": "Evet",
            "Mast Yüksekliği (m)": 11,
            "Yakıt Sınıfı": "Orta",
            "Not": "Standart saha makinesi"
        },
        {
            "Makine Adı": "Rig B",
            "Marka/Model": "Model B",
            "Makine Tipi": "Fore Kazık",
            "Max Derinlik (m)": 36,
            "Max Çap (mm)": 1500,
            "Tork (kNm)": 260,
            "Casing Yeteneği": "Evet",
            "Kaya Delgi": "Yüksek",
            "Dar Alan Uygunluğu": "Hayır",
            "Mast Yüksekliği (m)": 14,
            "Yakıt Sınıfı": "Yüksek",
            "Not": "Yüksek kapasiteli"
        },
        {
            "Makine Adı": "Rig C",
            "Marka/Model": "Model C",
            "Makine Tipi": "Fore Kazık",
            "Max Derinlik (m)": 20,
            "Max Çap (mm)": 800,
            "Tork (kNm)": 130,
            "Casing Yeteneği": "Hayır",
            "Kaya Delgi": "Düşük",
            "Dar Alan Uygunluğu": "Evet",
            "Mast Yüksekliği (m)": 9,
            "Yakıt Sınıfı": "Düşük",
            "Not": "Dar alan için uygun"
        }
    ])


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]
    return df
