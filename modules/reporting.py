from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle


def _tr(metin) -> str:
    """Türkçe karakterleri ASCII'ye çevirir — PDF uyumluluğu için."""
    tablo = str.maketrans(
        "çğıöşüÇĞİÖŞÜ",
        "cgiosuCGIOSU"
    )
    return str(metin).translate(tablo)


def pdf_olustur(firma_adi, proje_adi, proje_kodu, saha_kodu, is_tipi,
                kazik_boyu, kazik_capi, kazik_adedi, yeralti_suyu,
                gerekli_tork, casing_durum, casing_metre, sure_saat,
                metre_basi_mazot, toplam_mazot, genel_uc, kritik_katman,
                zemin_df=None, makina_sonuclari=None, casing_gerekce=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    baslik_stil = ParagraphStyle(
        "baslik", fontSize=16, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1d4ed8"), spaceAfter=6
    )
    alt_baslik_stil = ParagraphStyle(
        "alt_baslik", fontSize=12, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e293b"), spaceBefore=14, spaceAfter=4
    )
    normal_stil = ParagraphStyle(
        "normal", fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#334155"), spaceAfter=3
    )
    kucuk_stil = ParagraphStyle(
        "kucuk", fontSize=8, fontName="Helvetica",
        textColor=colors.HexColor("#64748b"), spaceAfter=2
    )

    def tablo_stili(header_renk="#1d4ed8"):
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_renk)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ])

    story = []

    # Başlık
    story.append(Paragraph("Geoteknik Karar Destek Sistemi", baslik_stil))
    story.append(Paragraph("On Yeterlilik ve Makine Uygunluk Raporu", ParagraphStyle(
        "sub", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#64748b"), spaceAfter=4
    )))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#1d4ed8"), spaceAfter=10))

    # 1. Proje Bilgileri
    story.append(Paragraph("1. Proje Bilgileri", alt_baslik_stil))
    proje_data = [
        ["Alan", "Deger", "Alan", "Deger"],
        ["Firma", _tr(firma_adi), "Proje Adi", _tr(proje_adi)],
        ["Proje Kodu", _tr(proje_kodu), "Saha Kodu", _tr(saha_kodu)],
        ["Is Tipi", _tr(is_tipi), "Tarih", str(date.today())],
        ["Kazik Boyu", f"{kazik_boyu} m", "Kazik Capi", f"{kazik_capi} mm"],
        ["Kazik Adedi", str(int(kazik_adedi)), "Yeralti Suyu", f"{yeralti_suyu} m"],
    ]
    t = Table(proje_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    t.setStyle(tablo_stili("#1e3a5f"))
    story.append(t)
    story.append(Spacer(1, 10))

    # 2. Teknik Ozet
    story.append(Paragraph("2. Teknik Ozet", alt_baslik_stil))
    ozet_data = [
        ["Parametre", "Deger", "Parametre", "Deger"],
        ["Gerekli Min. Tork", f"{gerekli_tork} kNm", "1 Kazik Suresi", f"{sure_saat} saat"],
        ["Muhafaza Borusu", _tr(casing_durum), "Tahmini Casing", f"{casing_metre} m"],
        ["Uc Onerisi", _tr(genel_uc), "Metre Basi Mazot", f"{metre_basi_mazot} L/m"],
        ["Toplam Mazot/Kazik", f"{toplam_mazot} L", "Toplam Mazot",
         f"{round(toplam_mazot * kazik_adedi, 0)} L"],
    ]
    t2 = Table(ozet_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    t2.setStyle(tablo_stili("#0f766e"))
    story.append(t2)
    story.append(Spacer(1, 10))

    # 3. Kritik Zemin Katmani
    story.append(Paragraph("3. Kritik Zemin Katmani", alt_baslik_stil))

    def safe_get(d, *keys):
        for k in keys:
            try:
                return d[k]
            except (KeyError, TypeError):
                continue
        return "?"

    k_formasyon = safe_get(kritik_katman, "Formasyon")
    k_baslangic = safe_get(kritik_katman, "Başlangıç (m)", "Baslangic (m)")
    k_bitis = safe_get(kritik_katman, "Bitiş (m)", "Bitis (m)")
    k_spt = safe_get(kritik_katman, "SPT")
    k_ucs = safe_get(kritik_katman, "UCS (MPa)")
    k_rqd = safe_get(kritik_katman, "RQD")

    kritik_data = [
        ["Formasyon", "Derinlik", "SPT", "UCS (MPa)", "RQD"],
        [_tr(k_formasyon), f"{k_baslangic} - {k_bitis} m",
         str(k_spt), str(k_ucs), str(k_rqd)]
    ]
    t3 = Table(kritik_data, colWidths=[3.5*cm, 4*cm, 2.5*cm, 3*cm, 3*cm])
    t3.setStyle(tablo_stili("#b45309"))
    story.append(t3)
    story.append(Spacer(1, 10))

    # 4. Zemin Logu
    if zemin_df is not None and not zemin_df.empty:
        story.append(Paragraph("4. Zemin Logu", alt_baslik_stil))
        zemin_cols = ["Başlangıç (m)", "Bitiş (m)", "Formasyon", "Zemin Tipi",
                      "SPT", "UCS (MPa)", "RQD", "Stabilite Riski"]
        mevcut_cols = [c for c in zemin_cols if c in zemin_df.columns]
        baslik_row = ["Baslangic(m)", "Bitis(m)", "Formasyon", "Zemin Tipi",
                      "SPT", "UCS(MPa)", "RQD", "Stabilite"][:len(mevcut_cols)]
        zemin_data = [baslik_row]
        for _, row in zemin_df.iterrows():
            zemin_data.append([_tr(row[c]) for c in mevcut_cols])
        col_w = 17*cm / len(mevcut_cols)
        t4 = Table(zemin_data, colWidths=[col_w] * len(mevcut_cols))
        stil4 = tablo_stili("#374151")
        # Stabilite renklendir
        if "Stabilite Riski" in mevcut_cols:
            idx = mevcut_cols.index("Stabilite Riski")
            for i in range(len(zemin_df)):
                stab = zemin_df.iloc[i].get("Stabilite Riski", "")
                if stab == "Yüksek":
                    stil4.add("BACKGROUND", (idx, i+1), (idx, i+1), colors.HexColor("#fee2e2"))
                elif stab == "Orta":
                    stil4.add("BACKGROUND", (idx, i+1), (idx, i+1), colors.HexColor("#fef9c3"))
        t4.setStyle(stil4)
        story.append(t4)
        story.append(Spacer(1, 10))

    # 5. Makine Uygunluk
    if makina_sonuclari is not None and not makina_sonuclari.empty:
        story.append(Paragraph("5. Makine Uygunluk Sonuclari", alt_baslik_stil))
        mak_cols = ["Makine Adı", "Marka/Model", "Tork (kNm)",
                    "Max Derinlik (m)", "Karar", "Gerekçe"]
        mevcut_mak = [c for c in mak_cols if c in makina_sonuclari.columns]
        baslik_mak = ["Makine", "Marka/Model", "Tork(kNm)",
                      "Max Derinlik(m)", "Karar", "Gerekce"][:len(mevcut_mak)]
        mak_data = [baslik_mak]
        for _, row in makina_sonuclari.iterrows():
            mak_data.append([_tr(row[c]) for c in mevcut_mak])
        col_w2 = 17*cm / len(mevcut_mak)
        t5 = Table(mak_data, colWidths=[col_w2] * len(mevcut_mak))
        stil5 = tablo_stili("#1e3a5f")
        if "Karar" in mevcut_mak:
            idx2 = mevcut_mak.index("Karar")
            for i in range(len(makina_sonuclari)):
                karar = makina_sonuclari.iloc[i].get("Karar", "")
                if karar == "Uygun":
                    stil5.add("BACKGROUND", (idx2, i+1), (idx2, i+1), colors.HexColor("#dcfce7"))
                    stil5.add("TEXTCOLOR", (idx2, i+1), (idx2, i+1), colors.HexColor("#15803d"))
                elif karar in ["Şartlı Uygun", "Riskli"]:
                    stil5.add("BACKGROUND", (idx2, i+1), (idx2, i+1), colors.HexColor("#fef9c3"))
                    stil5.add("TEXTCOLOR", (idx2, i+1), (idx2, i+1), colors.HexColor("#b45309"))
                else:
                    stil5.add("BACKGROUND", (idx2, i+1), (idx2, i+1), colors.HexColor("#fee2e2"))
                    stil5.add("TEXTCOLOR", (idx2, i+1), (idx2, i+1), colors.HexColor("#dc2626"))
        t5.setStyle(stil5)
        story.append(t5)
        story.append(Spacer(1, 10))

    # 6. Casing Gerekçesi
    if casing_gerekce:
        story.append(Paragraph("6. Muhafaza Borusu Degerlendirmesi", alt_baslik_stil))
        for g in casing_gerekce:
            story.append(Paragraph(f"- {_tr(g)}", normal_stil))
        story.append(Spacer(1, 8))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#cbd5e1"), spaceBefore=10))
    story.append(Paragraph(
        f"Bu rapor Geoteknik Karar Destek Sistemi tarafindan olusturulmustur. "
        f"Tarih: {date.today()} | Firma: {_tr(firma_adi)}",
        kucuk_stil
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
