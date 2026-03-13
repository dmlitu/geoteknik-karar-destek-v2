import streamlit as st
import pandas as pd

from modules.auth import login_control
from modules.calculations import (
    gerekli_tork_hesapla,
    stabilite_riski,
    casing_metre_hesapla,
    tahmini_kazik_suresi,
    mazot_tahmini,
    makina_uygunluk,
)
from modules.recommendations import uc_oneri, casing_oneri
from modules.ui_helpers import default_zemin_logu, default_makine_parki

st.set_page_config(page_title="Geoteknik Karar Destek Sistemi V2", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "company_name" not in st.session_state:
    st.session_state.company_name = ""

st.title("Geoteknik Karar Destek ve Makine Uygunluk Sistemi V2")
st.caption("Zemin etüdü + proje verileri + makine parkı ile ön karar motoru")

if not st.session_state.logged_in:
    st.subheader("Şirket Giriş Paneli")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        company = st.text_input("Firma Adı", value="Demo Firma")

        if st.button("Giriş Yap", use_container_width=True):
            if login_control(username, password):
                st.session_state.logged_in = True
                st.session_state.company_name = company
                st.success("Giriş başarılı.")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")

    st.stop()

st.success(f"Giriş yapıldı: {st.session_state.company_name}")

if st.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.company_name = ""
    st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Proje Bilgileri",
    "Zemin Logu",
    "Makine Parkı",
    "Analiz Sonucu",
    "Veri Tabloları"
])

with tab1:
    st.subheader("Proje Bilgileri")

    c1, c2, c3 = st.columns(3)

    with c1:
        proje_adi = st.text_input("Proje Adı", value="Örnek Kazık Projesi")
        proje_kodu = st.text_input("Proje Kodu", value="PRJ-001")
        saha_kodu = st.text_input("Saha Kodu", value="SH-01")
        is_tipi = st.selectbox("İş Tipi", ["Fore Kazık", "Ankraj", "Mini Kazık"])

    with c2:
        kazik_boyu = st.number_input("Kazık Boyu (m)", min_value=1.0, value=18.0, step=1.0)
        kazik_capi = st.number_input("Kazık Çapı (mm)", min_value=100, value=800, step=50)
        kazik_adedi = st.number_input("Kazık Adedi", min_value=1, value=30, step=1)
        yeralti_suyu = st.number_input("Yeraltı Suyu Seviyesi (m)", min_value=0.0, value=4.0, step=0.5)

    with c3:
        lokasyon = st.text_input("Lokasyon", value="İstanbul")
        proje_notu = st.text_area("Proje Notu", value="Şantiye koşulları burada tanımlanabilir.")
        teklif_notu = st.text_area("Teklif Notu", value="Teklif açıklamaları burada tutulabilir.")

with tab2:
    st.subheader("Zemin Logu")

    uploaded_file = st.file_uploader(
        "Zemin logu yükle (CSV veya Excel)",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            zemin_df = pd.read_csv(uploaded_file)
        else:
            zemin_df = pd.read_excel(uploaded_file)

        st.success("Zemin logu başarıyla yüklendi")
    else:
        zemin_df = default_zemin_logu()

    zemin_df = st.data_editor(
        zemin_df,
        num_rows="dynamic",
        use_container_width=True,
        key="zemin_editor"
    )

    if not zemin_df.empty:
        zemin_df["Stabilite Riski"] = zemin_df.apply(
            lambda row: stabilite_riski(
                row["Zemin Tipi"],
                row["Kohezyon Durumu"],
                yeralti_suyu,
                row["SPT"]
            ),
            axis=1
        )

        zemin_df["Uç Önerisi"] = zemin_df.apply(
            lambda row: uc_oneri(row["Zemin Tipi"], row["UCS (MPa)"]),
            axis=1
        )

with tab3:
    st.subheader("Makine Parkı")

    makina_df = st.data_editor(
        default_makine_parki(),
        num_rows="dynamic",
        use_container_width=True,
        key="makina_editor"
    )

with tab4:
    st.subheader("Analiz Sonucu")

    if zemin_df.empty or makina_df.empty:
        st.warning("Lütfen zemin logu ve makine parkı verilerini doldurun.")
    else:
        # Kritik zemin katmanı analizi
        zemin_df["Zorluk Skoru"] = (
            zemin_df["SPT"] * 0.5 +
            zemin_df["UCS (MPa)"] * 2 +
            (100 - zemin_df["RQD"]) * 0.3
        )

        kritik_katman = zemin_df.sort_values(
            by="Zorluk Skoru",
            ascending=False
        ).iloc[0]

        gerekli_tork = gerekli_tork_hesapla(zemin_df, kazik_capi)
        casing_durum = casing_oneri(list(zemin_df["Stabilite Riski"]))
        casing_gerekli = casing_durum == "Muhafaza borusu gerekli"
        casing_metre = casing_metre_hesapla(zemin_df)
        sure_saat = tahmini_kazik_suresi(zemin_df, kazik_capi, kazik_boyu, casing_metre)
        metre_basi_mazot, toplam_mazot = mazot_tahmini(gerekli_tork, kazik_boyu)

        uc_listesi = list(zemin_df["Uç Önerisi"].unique())
        if "Kaya ucu / özel dişli uç önerilir" in uc_listesi:
            genel_uc = "Kaya ucu / özel dişli uç gerekli olabilir"
        elif "Geçiş tipi uç önerilir" in uc_listesi:
            genel_uc = "Geçiş tipi uç önerilir"
        else:
            genel_uc = "Standart uç yeterli"

        makina_sonuclari = makina_df.copy()
        makina_sonuclari[["Karar", "Gerekçe"]] = makina_sonuclari.apply(
            lambda row: pd.Series(
                makina_uygunluk(
                    row,
                    gerekli_tork,
                    kazik_boyu,
                    kazik_capi,
                    casing_gerekli
                )
            ),
            axis=1
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gerekli Min. Tork", f"{gerekli_tork} kNm")
        m2.metric("Muhafaza Borusu", casing_durum)
        m3.metric("1 Kazık Süresi", f"{sure_saat} saat")
        m4.metric("Tahmini Casing", f"{casing_metre} m")

        st.markdown("---")

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("### Proje Özeti")
            st.write(f"**Firma:** {st.session_state.company_name}")
            st.write(f"**Proje:** {proje_adi}")
            st.write(f"**Proje Kodu:** {proje_kodu}")
            st.write(f"**Saha Kodu:** {saha_kodu}")
            st.write(f"**İş Tipi:** {is_tipi}")
            st.write(f"**Kazık Boyu:** {kazik_boyu} m")
            st.write(f"**Kazık Çapı:** {kazik_capi} mm")
            st.write(f"**Kazık Adedi:** {kazik_adedi}")
            st.write(f"**Yeraltı Suyu:** {yeralti_suyu} m")

            st.markdown("### Teknik Öneriler")
            st.write(f"**Uç önerisi:** {genel_uc}")
            st.write(f"**Metre başı tahmini mazot:** {metre_basi_mazot} L/m")
            st.write(f"**Bir kazık tahmini mazot:** {toplam_mazot} L")

            gunluk = max(1, int(10 / max(sure_saat, 1)))
            st.write(f"**Tahmini günlük üretim:** {gunluk} kazık/gün")

            toplam_sure_gun = round((sure_saat * kazik_adedi) / 10, 1)
            st.write(f"**Toplam iş süresi:** {toplam_sure_gun} gün")

        with right:
            st.markdown("### Kritik Zemin Katmanı")
            st.write(
                f"""
Formasyon: **{kritik_katman["Formasyon"]}**

Derinlik: **{kritik_katman["Başlangıç (m)"]} - {kritik_katman["Bitiş (m)"]} m**

SPT: **{kritik_katman["SPT"]}**

UCS: **{kritik_katman["UCS (MPa)"]} MPa**

RQD: **{kritik_katman["RQD"]}**
"""
            )

        st.markdown("### Makine Uygunluk Sonuçları")
        st.dataframe(
            makina_sonuclari[[
                "Makine Adı",
                "Makine Tipi",
                "Max Derinlik (m)",
                "Max Çap (mm)",
                "Tork (kNm)",
                "Casing Yeteneği",
                "Karar",
                "Gerekçe"
            ]],
            use_container_width=True
        )

with tab5:
    st.subheader("Veri Tabloları")

    st.markdown("### Zemin Logu")
    st.dataframe(zemin_df, use_container_width=True)

    st.markdown("### Makine Parkı")
    st.dataframe(makina_df, use_container_width=True)
