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
            "Açıklama": "Çatlaklı kaya"
        }
    ])


def default_makine_parki():
    return pd.DataFrame([
        {
            "Makine Adı": "Rig A",
            "Makine Tipi": "Fore Kazık",
            "Max Derinlik (m)": 24,
            "Max Çap (mm)": 1000,
            "Tork (kNm)": 180,
            "Casing Yeteneği": "Evet",
            "Not": "Standart saha makinesi"
        },
        {
            "Makine Adı": "Rig B",
            "Makine Tipi": "Fore Kazık",
            "Max Derinlik (m)": 36,
            "Max Çap (mm)": 1500,
            "Tork (kNm)": 260,
            "Casing Yeteneği": "Evet",
            "Not": "Yüksek kapasiteli"
        },
        {
            "Makine Adı": "Rig C",
            "Makine Tipi": "Fore Kazık",
            "Max Derinlik (m)": 20,
            "Max Çap (mm)": 800,
            "Tork (kNm)": 130,
            "Casing Yeteneği": "Hayır",
            "Not": "Dar alan için uygun"
        }
    ])
