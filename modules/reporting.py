from io import BytesIO
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import urllib.request


def _font_kaydet():
    try:
        font_path = "/tmp/DejaVuSans.ttf"
        font_bold_path = "/tmp/DejaVuSans-Bold.ttf"

        if not os.path.exists(font_path):
            urllib.request.urlretrieve(
                "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
                font_path
            )
        if not os.path.exists(font_bold_path):
            urllib.request.urlretrieve(
                "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf",
                font_bold_path
            )

        pdfmetrics.registerFont(TTFont("DejaVu", font_path))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", font_bold_path))
        return "DejaVu", "DejaVu-Bold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


def pdf_olustur(firma_adi, proje_adi, proje_kodu, saha_kodu, is_tipi,
                kazik_boyu, kazik_capi, kazik_adedi, yeralti_suyu,
                gerekli_tork, casing_durum, casing_metre, sure_saat,
                metre_basi_mazot, toplam_mazot, genel_uc, kritik_katman,
                zemin_df=None, makina_sonuclari=None, casing_gerekce=None):

    normal_font, bold_font = _font_kaydet()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    baslik_stil = ParagraphStyle(
        "baslik", fontSize=16, fontName=bold_font,
        textColor=colors.HexColor("#1d4ed8"), spaceAfter=6
    )
    alt_baslik_stil = ParagraphStyle(
        "alt_baslik", fontSize=12, fontName=bold_font,
        textColor=colors.HexColor("#1e293b"), spaceBefore=14, spaceAfter=4
    )
    normal_stil = ParagraphStyle(
        "normal", fontSize=9, fontName=normal_font,
        textColor=colors.HexColor("#334155"), spaceAfter=3
    )
    kucuk_stil = ParagraphStyle(
        "kucuk", fontSize=8, fontName=normal_font,
        textColor=colors.HexColor("#64748b"), spaceAfter=2
    )

    def tablo_stili(header_renk="#1d4ed8"):
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_renk)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), bold_font),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTNAME", (0, 1), (-1, -1), normal_font),
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
        "sub", fontSize=10, fontName=normal_font,
        textColor=colors.HexColor("#64748b"), spaceAfter=4
    )))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor("#1d4ed8"), spaceAfter=10))

    # 1. Proje Bilgileri
    story.append(Paragraph("1. Proje Bilgileri", alt_baslik_stil))
    proje_data = [
        ["Alan", "Deger", "Alan", "Deger"],
        ["Firma", firma_adi, "Proje Adi", proje_adi],
        ["Proje Kodu", proje_kodu, "Saha Kodu", saha_kodu],
        ["Is Tipi", is_tipi, "Tarih", str(date.today())],
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
        ["Muhafaza Borusu", casing_durum, "Tahmini Casing", f"{casing_metre} m"],
        ["Uc Onerisi", genel_uc, "Metre Basi Mazot", f"{metre_basi_mazot} L/m"],
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
        [str(k_formasyon), f"{k_baslangic} - {k_bitis} m",
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
            zemin_data.append([str(row[c]) for c in mevcut_cols])
        col_w = 17*cm / len(mevcut_cols)
        t4 = Table(zemin_data, colWidths=[col_w] * len(mevcut_cols))
        t4.setStyle(tablo_stili("#374151"))
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
            mak_data.append([str(row[c]) for c in mevcut_mak])
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
            story.append(Paragraph(f"- {g}", normal_stil))
        story.append(Spacer(1, 8))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#cbd5e1"), spaceBefore=10))
    story.append(Paragraph(
        f"Bu rapor Geoteknik Karar Destek Sistemi tarafindan olusturulmustur. "
        f"Tarih: {date.today()} | Firma: {firma_adi}",
        kucuk_stil
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
