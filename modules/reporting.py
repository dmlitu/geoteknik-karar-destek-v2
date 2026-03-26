from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def pdf_olustur(firma_adi, proje_adi, proje_kodu, saha_kodu, is_tipi,
                kazik_boyu, kazik_capi, kazik_adedi, yeralti_suyu,
                gerekli_tork, casing_durum, casing_metre, sure_saat,
                metre_basi_mazot, toplam_mazot, genel_uc, kritik_katman,
                zemin_df=None, makina_sonuclari=None, casing_gerekce=None):

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    baslik_stil = ParagraphStyle(
        "baslik", fontSize=16, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1d4ed8"), spaceAfter=6, alignment=TA_LEFT
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

    # ── BAŞLIK ──
    story.append(Paragraph("Geoteknik Karar Destek Sistemi", baslik_stil))
    story.append(Paragraph("Ön Yeterlilik ve Makine Uygunluk Raporu", ParagraphStyle(
        "sub", fontSize=10, fontName="Helvetica", textColor=colors.HexColor("#64748b"), spaceAfter=4
    )))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1d4ed8"), spaceAfter=10))

    # ── PROJE BİLGİLERİ ──
    story.append(Paragraph("1. Proje Bilgileri", alt_baslik_stil))

    proje_data = [
        ["Alan", "Değer", "Alan", "Değer"],
        ["Firma", firma_adi, "Proje Adı", proje_adi],
        ["Proje Kodu", proje_kodu, "Saha Kodu", saha_kodu],
        ["İş Tipi", is_tipi, "Tarih", str(date.today())],
        ["Kazık Boyu", f"{kazik_boyu} m", "Kazık Çapı", f"{kazik_capi} mm"],
        ["Kazık Adedi", str(int(kazik_adedi)), "Yeraltı Suyu", f"{yeralti_suyu} m"],
    ]
    t = Table(proje_data, colWidths=[3.5*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    t.setStyle(tablo_stili("#1e3a5f"))
    story.append(t)
    story.append(Spacer(1, 10))

    # ── TEKNİK ÖZET ──
    story.append(Paragraph("2. Teknik Özet", alt_baslik_stil))

    ozet_data = [
        ["Parametre", "Değer", "Parametre", "Değer"],
        ["Gerekli Min. Tork", f"{gerekli_tork} kNm", "1 Kazık Süresi", f"{sure_saat} saat"],
        ["Muhafaza Borusu", casing_durum, "Tahmini Casing", f"{casing_metre} m"],
        ["Uç Önerisi", genel_uc, "Metre Başı Mazot", f"{metre_basi_mazot} L/m"],
        ["Toplam Mazot/Kazık", f"{toplam_mazot} L", "Toplam Mazot", f"{round(toplam_mazot * kazik_adedi, 0)} L"],
    ]
    t2 = Table(ozet_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    t2.setStyle(tablo_stili("#0f766e"))
    story.append(t2)
    story.append(Spacer(1, 10))

    # ── KRİTİK ZEMİN KATMANI ──
    story.append(Paragraph("3. Kritik Zemin Katmanı", alt_baslik_stil))

    kritik_data = [
        ["Formasyon", "Derinlik", "SPT", "UCS (MPa)", "RQD"],
        [
            str(kritik_katman["Formasyon"]),
            f"{kritik_katman['Başlangıç (m)']} – {kritik_katman['Bitiş (m)']} m",
            str(kritik_katman["SPT"]),
            str(kritik_katman["UCS (MPa)"]),
            str(kritik_katman["RQD"]),
        ]
    ]
    t3 = Table(kritik_data, colWidths=[3.5*cm, 4*cm, 2.5*cm, 3*cm, 3*cm])
    t3.setStyle(tablo_stili("#b45309"))
    story.append(t3)
    story.append(Spacer(1, 10))

    # ── ZEMİN LOGU ──
    if zemin_df is not None and not zemin_df.empty:
        story.append(Paragraph("4. Zemin Logu", alt_baslik_stil))

        zemin_cols = ["Başlangıç (m)", "Bitiş (m)", "Formasyon", "Zemin Tipi",
                      "SPT", "UCS (MPa)", "RQD", "Stabilite Riski"]
        mevcut_cols = [c for c in zemin_cols if c in zemin_df.columns]
        zemin_data = [mevcut_cols]
        for _, row in zemin_df.iterrows():
            zemin_data.append([str(row[c]) for c in mevcut_cols])

        col_w = 18*cm / len(mevcut_cols)
        t4 = Table(zemin_data, colWidths=[col_w] * len(mevcut_cols))
        stil4 = tablo_stili("#374151")
        # Stabilite Riski renklendir
        if "Stabilite Riski" in mevcut_cols:
            idx = mevcut_cols.index("Stabilite Riski")
            for i, row in enumerate(zemin_df.itertuples(), start=1):
                risk = getattr(row, "Stabilite_Riski", "") if hasattr(row, "Stabilite_Riski") else ""
                if zemin_df.iloc[i-1].get("Stabilite Riski", "") == "Yüksek":
                    stil4.add("BACKGROUND", (idx, i), (idx, i), colors.HexColor("#fee2e2"))
                elif zemin_df.iloc[i-1].get("Stabilite Riski", "") == "Orta":
                    stil4.add("BACKGROUND", (idx, i), (idx, i), colors.HexColor("#fef9c3"))
        t4.setStyle(stil4)
        story.append(t4)
        story.append(Spacer(1, 10))

    # ── MAKİNE UYGUNLUK ──
    if makina_sonuclari is not None and not makina_sonuclari.empty:
        story.append(Paragraph("5. Makine Uygunluk Sonuçları", alt_baslik_stil))

        mak_cols = ["Makine Adı", "Marka/Model", "Tork (kNm)", "Max Derinlik (m)", "Karar", "Gerekçe"]
        mevcut_mak = [c for c in mak_cols if c in makina_sonuclari.columns]
        mak_data = [mevcut_mak]
        for _, row in makina_sonuclari.iterrows():
            mak_data.append([str(row[c]) for c in mevcut_mak])

        col_w2 = 18*cm / len(mevcut_mak)
        t5 = Table(mak_data, colWidths=[col_w2] * len(mevcut_mak))
        stil5 = tablo_stili("#1e3a5f")
        if "Karar" in mevcut_mak:
            idx2 = mevcut_mak.index("Karar")
            for i, row in enumerate(makina_sonuclari.itertuples(), start=1):
                karar = makina_sonuclari.iloc[i-1].get("Karar", "")
                if karar == "Uygun":
                    stil5.add("BACKGROUND", (idx2, i), (idx2, i), colors.HexColor("#dcfce7"))
                    stil5.add("TEXTCOLOR", (idx2, i), (idx2, i), colors.HexColor("#15803d"))
                elif karar in ["Şartlı Uygun", "Riskli"]:
                    stil5.add("BACKGROUND", (idx2, i), (idx2, i), colors.HexColor("#fef9c3"))
                    stil5.add("TEXTCOLOR", (idx2, i), (idx2, i), colors.HexColor("#b45309"))
                elif karar == "Uygun Değil":
                    stil5.add("BACKGROUND", (idx2, i), (idx2, i), colors.HexColor("#fee2e2"))
                    stil5.add("TEXTCOLOR", (idx2, i), (idx2, i), colors.HexColor("#dc2626"))
        t5.setStyle(stil5)
        story.append(t5)
        story.append(Spacer(1, 10))

    # ── CASING GEREKÇESİ ──
    if casing_gerekce:
        story.append(Paragraph("6. Muhafaza Borusu Değerlendirmesi", alt_baslik_stil))
        for g in casing_gerekce:
            story.append(Paragraph(f"• {g}", normal_stil))
        story.append(Spacer(1, 8))

    # ── FOOTER ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=10))
    story.append(Paragraph(
        f"Bu rapor Geoteknik Karar Destek Sistemi tarafından otomatik oluşturulmuştur. "
        f"Tarih: {date.today()}  |  Firma: {firma_adi}",
        kucuk_stil
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
