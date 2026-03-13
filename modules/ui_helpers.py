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
            "Marka/Model": "Bauer BG",
            "Max Derinlik (m)": 24,
            "Max Çap (mm)": 1000,
            "Tork (kNm)": 180,
            "Casing Yeteneği": "Evet",
            "Dar Alan Uygunluğu": "Hayır",
            "Yakıt Sınıfı": "Orta",
            "Not": "Standart saha makinesi"
        },
        {
            "Makine Adı": "Rig B",
            "Makine Tipi": "Fore Kazık",
            "Marka/Model": "Soilmec SR",
            "Max Derinlik (m)": 36,
            "Max Çap (mm)": 1500,
            "Tork (kNm)": 260,
            "Casing Yeteneği": "Evet",
            "Dar Alan Uygunluğu": "Hayır",
            "Yakıt Sınıfı": "Yüksek",
            "Not": "Yüksek kapasiteli"
        },
        {
            "Makine Adı": "Rig C",
            "Makine Tipi": "Fore Kazık",
            "Marka/Model": "Klemm KR",
            "Max Derinlik (m)": 20,
            "Max Çap (mm)": 800,
            "Tork (kNm)": 130,
            "Casing Yeteneği": "Hayır",
            "Dar Alan Uygunluğu": "Evet",
            "Yakıt Sınıfı": "Düşük",
            "Not": "Dar alan için uygun"
        }
    ])


def machine_library():
    return {
        "Standart Fore Kazık Seti": pd.DataFrame([
            {
                "Makine Adı": "Rig A",
                "Makine Tipi": "Fore Kazık",
                "Marka/Model": "Bauer BG",
                "Max Derinlik (m)": 24,
                "Max Çap (mm)": 1000,
                "Tork (kNm)": 180,
                "Casing Yeteneği": "Evet",
                "Dar Alan Uygunluğu": "Hayır",
                "Yakıt Sınıfı": "Orta",
                "Not": "Standart saha makinesi"
            },
            {
                "Makine Adı": "Rig B",
                "Makine Tipi": "Fore Kazık",
                "Marka/Model": "Soilmec SR",
                "Max Derinlik (m)": 36,
                "Max Çap (mm)": 1500,
                "Tork (kNm)": 260,
                "Casing Yeteneği": "Evet",
                "Dar Alan Uygunluğu": "Hayır",
                "Yakıt Sınıfı": "Yüksek",
                "Not": "Yüksek kapasiteli"
            }
        ]),
        "Dar Alan Seti": pd.DataFrame([
            {
                "Makine Adı": "Rig C",
                "Makine Tipi": "Fore Kazık",
                "Marka/Model": "Klemm KR",
                "Max Derinlik (m)": 20,
                "Max Çap (mm)": 800,
                "Tork (kNm)": 130,
                "Casing Yeteneği": "Hayır",
                "Dar Alan Uygunluğu": "Evet",
                "Yakıt Sınıfı": "Düşük",
                "Not": "Dar alan için uygun"
            },
            {
                "Makine Adı": "Rig D",
                "Makine Tipi": "Fore Kazık",
                "Marka/Model": "Comacchio",
                "Max Derinlik (m)": 22,
                "Max Çap (mm)": 900,
                "Tork (kNm)": 150,
                "Casing Yeteneği": "Şartlı",
                "Dar Alan Uygunluğu": "Evet",
                "Yakıt Sınıfı": "Orta",
                "Not": "Kompakt makine"
            }
        ]),
        "Yüksek Kapasite Seti": pd.DataFrame([
            {
                "Makine Adı": "Rig X",
                "Makine Tipi": "Fore Kazık",
                "Marka/Model": "Casagrande",
                "Max Derinlik (m)": 42,
                "Max Çap (mm)": 1800,
                "Tork (kNm)": 320,
                "Casing Yeteneği": "Evet",
                "Dar Alan Uygunluğu": "Hayır",
                "Yakıt Sınıfı": "Yüksek",
                "Not": "Büyük çap ve zor zemin"
            },
            {
                "Makine Adı": "Rig Y",
                "Makine Tipi": "Fore Kazık",
                "Marka/Model": "Bauer BG XL",
                "Max Derinlik (m)": 50,
                "Max Çap (mm)": 2000,
                "Tork (kNm)": 380,
                "Casing Yeteneği": "Evet",
                "Dar Alan Uygunluğu": "Hayır",
                "Yakıt Sınıfı": "Yüksek",
                "Not": "Çok yüksek kapasite"
            }
        ])
    }


def durum_karti_html(baslik, deger, renk):
    return f"""
    <div style="
        background-color:{renk};
        padding:16px;
        border-radius:14px;
        color:white;
        text-align:center;
        min-height:110px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        box-shadow:0 4px 14px rgba(0,0,0,0.12);
        margin-bottom:8px;
    ">
        <div style="font-size:15px; opacity:0.9;">{baslik}</div>
        <div style="font-size:24px; font-weight:700; margin-top:8px;">{deger}</div>
    </div>
    """
