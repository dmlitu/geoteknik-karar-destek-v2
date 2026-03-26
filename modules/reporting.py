from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def pdf_olustur(firma_adi, proje_adi, proje_kodu, saha_kodu, is_tipi,
                kazik_boyu, kazik_capi, kazik_adedi, yeralti_suyu,
                gerekli_tork, casing_durum, casing_metre, sure_saat,
                metre_basi_mazot, toplam_mazot, genel_uc, kritik_katman):

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    def satir(text, step=18):
        nonlocal y
        p.drawString(50, y, str(text))
        y -= step

    p.setFont("Helvetica-Bold", 14)
    satir("Geoteknik Karar Destek Sistemi - Yonetici Ozeti", 28)

    p.setFont("Helvetica", 10)
    satir(f"Firma: {firma_adi}")
    satir(f"Proje: {proje_adi}")
    satir(f"Proje Kodu: {proje_kodu}")
    satir(f"Saha Kodu: {saha_kodu}")
    satir(f"Is Tipi: {is_tipi}")
    satir(f"Kazik Boyu: {kazik_boyu} m")
    satir(f"Kazik Capi: {kazik_capi} mm")
    satir(f"Kazik Adedi: {kazik_adedi}")
    satir(f"Yeralti Suyu: {yeralti_suyu} m")

    y -= 8
    p.setFont("Helvetica-Bold", 12)
    satir("Teknik Ozet", 22)
    p.setFont("Helvetica", 10)
    satir(f"Gerekli minimum tork: {gerekli_tork} kNm")
    satir(f"Muhafaza borusu: {casing_durum}")
    satir(f"Tahmini casing metresi: {casing_metre} m")
    satir(f"Tahmini 1 kazik suresi: {sure_saat} saat")
    satir(f"Metre basi tahmini mazot: {metre_basi_mazot} L/m")
    satir(f"Bir kazik tahmini mazot: {toplam_mazot} L")
    satir(f"Uc onerisi: {genel_uc}")

    y -= 8
    p.setFont("Helvetica-Bold", 12)
    satir("Kritik Zemin Katmani", 22)
    p.setFont("Helvetica", 10)
    satir(f"Formasyon: {kritik_katman['Formasyon']}")
    satir(f"Derinlik: {kritik_katman['Başlangıç (m)']} - {kritik_katman['Bitiş (m)']} m")
    satir(f"SPT: {kritik_katman['SPT']}")
    satir(f"UCS: {kritik_katman['UCS (MPa)']} MPa")
    satir(f"RQD: {kritik_katman['RQD']}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
