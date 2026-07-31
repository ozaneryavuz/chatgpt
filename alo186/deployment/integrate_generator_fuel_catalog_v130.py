from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HUB = ROOT / "alo186/hesaplama/index.html"
ROUTE = "./jenerator-yakit-tuketimi-calisma-suresi/"
CARD = (
    '<a class="tool-card" href="./jenerator-yakit-tuketimi-calisma-suresi/">'
    '<span class="eyebrow">Gerçek yük % · L/saat · tank · çalışma süresi</span>'
    '<h2>Jeneratör Yakıt Tüketimi ve Çalışma Süresi</h2>'
    '<p>Sürekli kW, gerçek yük, üretici yakıt eğrisi ve kullanılabilir tankla litre/saat, '
    'hedef yakıt ve yaklaşık çalışma süresini hesaplayın; CO ve transfer riski varsa ticari yol kapanır.</p>'
    '<b>Yakıt ve süre planını aç →</b></a>'
)
ANCHOR = (
    '<a class="tool-card" href="./jenerator-gucu-secimi/">'
    '<span class="eyebrow">Sürekli W · kalkış W · kVA</span>'
    '<h2>Jeneratör Gücü Ön Seçimi</h2>'
    '<p>Cihaz yüklerini, en ağır motor kalkışını ve rezervi birlikte hesaplayın; '
    'güvenli ürün veya profesyonel rota görün.</p>'
    '<b>Jeneratör hesabını aç →</b></a>'
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise RuntimeError(f"Hesaplama merkezi entegrasyon ankrajı bulunamadı: {label}")
    return text.replace(old, new, 1)


def integrate() -> bool:
    text = HUB.read_text(encoding="utf-8")
    original = text

    if ROUTE not in text:
        text = replace_once(text, ANCHOR, ANCHOR + "\n" + CARD, "jeneratör güç kartı")

    text = text.replace(
        "USB-C, UPS, jeneratör, inverter, GES ve EV araçlarını ücretsiz kullanın.",
        "USB-C, UPS, jeneratör gücü ve yakıt süresi, inverter, GES ve EV araçlarını ücretsiz kullanın.",
    )
    text = text.replace(
        "yüksek güçlü ev aletleri, EV şarjı",
        "yüksek güçlü ev aletleri, jeneratör yakıtı ve transferi, EV şarjı",
    )
    text = text.replace(
        "USB-C kısa listesine, UPS, jeneratör, inverter",
        "USB-C kısa listesine, UPS, jeneratör gücü ve yakıt çalışma süresine, inverter",
    )
    text = text.replace(
        "Kapalı döngü sonuç takibi, beyaz eşya ve yüksek güçlü ev aleti yedek gücü, ısıtma",
        "Kapalı döngü sonuç takibi, beyaz eşya ve yüksek güçlü ev aleti yedek gücü, jeneratör güç-yakıt-süre planı, ısıtma",
    )
    text = text.replace(
        "kombi, sabit tesisat, beyaz eşya",
        "kombi, jeneratör, sabit tesisat, beyaz eşya",
    )
    text = re.sub(r"\b48 çekirdek araç\b", "49 çekirdek araç", text)

    card_count = text.count('class="tool-card"')
    if card_count != 49:
        raise RuntimeError(f"Beklenen 49 araç kartı yerine {card_count} bulundu")
    if text.count(ROUTE) != 1:
        raise RuntimeError("Jeneratör yakıt aracı hesaplama merkezinde tam bir kez bulunmalıdır")
    if "49 çekirdek araç" not in text:
        raise RuntimeError("49 araç sayacı güncellenmedi")

    if text != original:
        HUB.write_text(text, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    print("changed" if integrate() else "already-integrated")
