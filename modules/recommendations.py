def uc_oneri(zemin_tipi: str, ucs: float) -> str:
    if zemin_tipi in ["Kumtaşı", "Kireçtaşı", "Sert Kaya"] or ucs >= 25:
        return "Kaya ucu / özel dişli uç önerilir"
    if zemin_tipi == "Ayrışmış Kaya" or 10 <= ucs < 25:
        return "Geçiş tipi uç önerilir"
    return "Standart zemin ucu yeterli"


def casing_oneri(risk_list):
    yuksek = risk_list.count("Yüksek")
    orta = risk_list.count("Orta")
    if yuksek >= 1:
        return "Muhafaza borusu gerekli"
    if orta >= 2:
        return "Muhafaza borusu şartlı önerilir"
    return "Muhafaza borusu gerekmeyebilir"


def casing_oneri_basit(risk_list):
    return casing_oneri(risk_list)
