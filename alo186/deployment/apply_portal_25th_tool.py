from __future__ import annotations

from pathlib import Path

PORTAL = Path("alo186/index.html")
ROUTE = "/hesaplama/modem-internet-yedekleme/"
CARD = '''      <a class="card" href="/hesaplama/modem-internet-yedekleme/"><span class="tag">12 V · modem · ONT · hedef süre</span><h2>Modem ve ONT Mini UPS Hesabı</h2><p>12 V modem, ONT ve ağ cihazları için toplam W, hedef süre ve gerekli Wh üzerinden uygun mini UPS sınıfını hesaplayın; polarite ve voltajı doğrulamadan satın almayın.</p><b>İnternet yedekleme hesabını aç →</b></a>'''


def main() -> None:
    text = PORTAL.read_text(encoding="utf-8")

    replacements = {
        "24 kişisel veri istemeyen araç": "25 kişisel veri istemeyen araç",
        "24 kişisel veri istemeyen hesaplama ve karar aracı": "25 kişisel veri istemeyen hesaplama ve karar aracı",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    if ROUTE not in text:
        anchor = '''      <a class="card" href="/hesaplama/kesinti-gunlugu/"><span class="tag">Yerel kayıt · 12 saat sinyali · kanıt listesi</span><h2>Kesinti Günlüğü ve Hak Ön Kontrolü</h2><p>Kesintinin tarihini ve süresini cihazınızda tutun; yıllık süre/sayı sinyalini, cihaz hasarında belge listesini ve güvenli yedek güç rotasını görün.</p><b>Kesinti günlüğünü aç →</b></a>'''
        if anchor not in text:
            raise SystemExit("Kesinti Günlüğü kartı bulunamadı; portal yapısı değişmiş olabilir.")
        text = text.replace(anchor, anchor + "\n" + CARD, 1)

    if text.count(ROUTE) != 1:
        raise SystemExit(f"Mini UPS rotası portalda tam bir kez bulunmalı; count={text.count(ROUTE)}")
    if "25 kişisel veri istemeyen araç" not in text:
        raise SystemExit("Portal araç sayısı 25 olarak güncellenemedi.")
    if "24 kişisel veri istemeyen araç" in text:
        raise SystemExit("Portal içinde bayat 24 araç ifadesi kaldı.")

    PORTAL.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
