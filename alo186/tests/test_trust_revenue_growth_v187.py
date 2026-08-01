#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CO2 = ROOT / "alo186/hesaplama/oda-co2-havalandirma-sicaklik-nem-izleme/index.html"
LOW = ROOT / "alo186/amazon-elektrik-urunleri/usb-ethernet-dusuk-gerilim-test-urun-secici/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/187-trust-revenue-growth.json"
AUDIT = ROOT / "alo186/audits/trust-revenue-growth-v187-2026-08-02.md"

expected = {
    "/hesaplama/oda-co2-havalandirma-sicaklik-nem-izleme/": CO2,
    "/amazon-elektrik-urunleri/usb-ethernet-dusuk-gerilim-test-urun-secici/": LOW,
}

def check_page(path: Path, canonical: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="https://alo186.com{canonical}">' in text
    assert 'alo186rehber-21' in text
    assert 'sponsored nofollow noopener' in text
    assert text.count('class="gate"') == 3
    assert 'Amazon satış ortaklığı bağlantısı' in text
    assert 'Yeni ürün almayın' in text or 'yeni ürün almayın' in text
    assert 'kamu kurumu' in text or 'resmî kurum' in text
    assert 'Fiyat, stok' in text
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    assert 'AggregateRating' not in text
    assert 'availability' not in text
    assert not re.search(r'href=["\']https://www\.amazon\.com\.tr/', text, re.I)
    assert 'pointer-events:none' in text
    assert 'removeAttribute(\'href\')' in text or 'removeAttribute("href")' in text

for canonical, path in expected.items():
    assert path.is_file(), path
    check_page(path, canonical)

co2 = CO2.read_text(encoding="utf-8")
assert 'CO₂ ölçer karbonmonoksit alarmının yerini tutmaz' in co2
assert 'Ticari yol kapalı' in co2
assert 'Profesyonel ölçüm planı gerekir' in co2
assert 'NDIR CO₂ monitörü' in co2
assert 'US EPA' in co2

low = LOW.read_text(encoding="utf-8")
for token in ('USB-C güç ölçer', 'RJ45 kablo test cihazı', 'Kablo etiketleme seti'):
    assert token in low
assert 'yalnız tüketici tipi düşük gerilimli USB ve enerjisiz veri kabloları içindir' in low
assert 'Şebeke, pano veya sabit tesisat için yetkili elektrikçi gerekir' in low
assert 'USB-IF' in low

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 187
routes = {item["canonicalPath"]: ROOT / item["source"] for item in overlay["routes"]}
assert set(routes) == set(expected)
for canonical, source in routes.items():
    assert source.resolve() == expected[canonical].resolve()

assert AUDIT.is_file()
audit = AUDIT.read_text(encoding="utf-8")
for token in ('Arama niyeti', 'Kullanıcı yolculuğu', 'Affiliate kategorileri', 'Dönüşüm', 'Tekrar ziyaret', 'Beklenen etki'):
    assert token.lower() in audit.lower()

print(json.dumps({
    "ok": True,
    "version": 187,
    "routes": sorted(expected),
    "affiliateCategories": 6,
    "tripleGate": True,
    "noBuy": True,
    "activeHazardCommerceClosed": True,
    "noProductOfferSchema": True,
}, ensure_ascii=False))
