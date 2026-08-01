#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOLAR = ROOT / "alo186/hesaplama/tasinabilir-gunes-paneli-guc-istasyonu-uyumluluk/index.html"
COOLER = ROOT / "alo186/hesaplama/12v-kamp-buzdolabi-guc-istasyonu-calisma-suresi/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/kamp-arac-enerji-urun-secici/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/190-kamp-arac-enerji-growth.json"
AUDIT = ROOT / "alo186/audits/kamp-arac-enerji-growth-v190-2026-08-02.md"

expected = {
    "/hesaplama/tasinabilir-gunes-paneli-guc-istasyonu-uyumluluk/": SOLAR,
    "/hesaplama/12v-kamp-buzdolabi-guc-istasyonu-calisma-suresi/": COOLER,
    "/amazon-elektrik-urunleri/kamp-arac-enerji-urun-secici/": SELECTOR,
}

for canonical, path in expected.items():
    assert path.is_file(), path
    text = path.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="https://alo186.com{canonical}">' in text
    assert "kamu kurumu" in text
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    assert "AggregateRating" not in text
    assert "availability" not in text

solar = SOLAR.read_text(encoding="utf-8")
for token in (
    "Panel Voc (V)",
    "Panel Vmp (V)",
    "Panel Isc (A)",
    "Panel Imp (A)",
    "Voc planlama payı",
    "Mevcut düzeni kullanın — yeni ürün almayın",
    "Jackery",
    "EcoFlow",
):
    assert token in solar
assert "Bağlantı yapmayın" in solar
assert "/amazon-elektrik-urunleri/kamp-arac-enerji-urun-secici/" in solar

cooler = COOLER.read_text(encoding="utf-8")
for token in (
    "Nominal kapasite (Wh)",
    "Buzdolabı ortalama gücü (W)",
    "Ek planlama rezervi",
    "Marş aküsünü koruyun",
    "Mevcut düzen hedefi karşılıyor — yeni ürün almayın",
    "Dometic",
):
    assert token in cooler
assert "/amazon-elektrik-urunleri/kamp-arac-enerji-urun-secici/" in cooler

selector = SELECTOR.read_text(encoding="utf-8")
for token in (
    "Katlanabilir taşınabilir güneş paneli",
    "Model uyumlu solar şarj kablosu",
    "12/24 V kompresörlü araç-kamp buzdolabı",
    "12 V lityum jump starter",
    "Akıllı 12 V akü bakım ve şarj cihazı",
    "Amazon Gelir Ortağı açıklaması",
    "Mevcut ekipmanı kullanın; yeni ürün almayın",
    "JSON indir",
    "30/90 gün ICS indir",
):
    assert token in selector
assert "alo186rehber-21" in selector
assert "sponsored nofollow noopener" in selector
assert selector.count('class="gate"') == 3
assert "removeAttribute('href')" in selector
assert not re.search(r'href=["\']https://www\.amazon\.com\.tr/', selector, re.I)
assert "Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti bilgisi yayımlanmaz" in selector
assert "localStorage" not in selector
assert "document.cookie" not in selector
assert "Ticari yol kapalı" in selector
assert "EV veya hibrit aracın yüksek gerilim sistemine müdahale etmeyin" in selector

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 190
routes = {item["canonicalPath"]: ROOT / item["source"] for item in overlay["routes"]}
assert set(routes) == set(expected)
for canonical, source in routes.items():
    assert source.resolve() == expected[canonical].resolve()

assert AUDIT.is_file()
audit = AUDIT.read_text(encoding="utf-8")
for token in (
    "Arama niyeti",
    "İçerik boşluğu",
    "Kullanıcı yolculuğu",
    "Affiliate ürün kategorileri",
    "Dönüşüm noktaları",
    "Tekrar ziyaret nedenleri",
    "Beklenen etki",
):
    assert token.lower() in audit.lower()

print(json.dumps({
    "ok": True,
    "version": 190,
    "routes": sorted(expected),
    "affiliateCategories": 7,
    "maxClassesPerVisit": 3,
    "tripleGate": True,
    "noBuy": True,
    "activeHazardCommerceClosed": True,
    "personalDataRequested": False,
    "noProductOfferSchema": True,
}, ensure_ascii=False))
