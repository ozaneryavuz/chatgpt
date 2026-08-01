#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALC = ROOT / "alo186/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/index.html"
TRACKER = ROOT / "alo186/sektor-rehberi/akvaryum-kesinti-30-90-gun-test-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/189-aquarium-outage-growth.json"
AUDIT = ROOT / "alo186/audits/aquarium-outage-growth-v189-2026-08-02.md"

expected = {
    "/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/": CALC,
    "/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/": SELECTOR,
    "/sektor-rehberi/akvaryum-kesinti-30-90-gun-test-merkezi/": TRACKER,
}

for canonical, path in expected.items():
    assert path.is_file(), path
    text = path.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="https://alo186.com{canonical}">' in text
    assert 'kamu kurumu' in text
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    assert 'AggregateRating' not in text
    assert 'availability' not in text

calc = CALC.read_text(encoding="utf-8")
for token in (
    'Acil havalandırma ve uzman desteği',
    'Mevcut düzeni kullanın — yeni ürün almayın',
    'Kesinti sırasında yemlemeyi durdurun',
    'Fluval',
    'Aqueon',
):
    assert token in calc
assert 'tek bir “güvenli saat” yayınlanmaz' in calc
assert '/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/' in calc

selector = SELECTOR.read_text(encoding="utf-8")
for token in (
    'Pilli akvaryum hava motoru',
    'USB düşük gerilimli akvaryum hava pompası',
    'Dijital akvaryum termometresi',
    'Akvaryum hava hortumu ve çek valf seti',
    'Amazon Gelir Ortağı açıklaması',
    'Mevcut düzen yeterli — yeni ürün almayın',
):
    assert token in selector
assert 'alo186rehber-21' in selector
assert 'sponsored nofollow noopener' in selector
assert selector.count('class="gate"') == 3
assert 'pointer-events:none' in selector
assert "removeAttribute('href')" in selector
assert not re.search(r'href=["\']https://www\.amazon\.com\.tr/', selector, re.I)
assert 'Fiyat, stok, satıcı, puan, yorum, teslimat veya garanti bilgisi yayımlanmaz' in selector

tracker = TRACKER.read_text(encoding="utf-8")
for token in (
    'JSON indir',
    '30/90 gün ICS indir',
    'Test başarılı',
    'Mevcut ekipmanı kullanın; yeni ürün almayın',
    'Kişisel veri istemez',
):
    assert token in tracker
assert 'localStorage' not in tracker
assert 'document.cookie' not in tracker
assert '30 ve 90 gün resmî bakım periyodu mudur?' in tracker

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 189
routes = {item["canonicalPath"]: ROOT / item["source"] for item in overlay["routes"]}
assert set(routes) == set(expected)
for canonical, source in routes.items():
    assert source.resolve() == expected[canonical].resolve()

assert AUDIT.is_file()
audit = AUDIT.read_text(encoding="utf-8")
for token in (
    'Arama niyeti',
    'İçerik boşluğu',
    'Kullanıcı yolculuğu',
    'Affiliate ürün kategorileri',
    'Dönüşüm noktaları',
    'Tekrar ziyaret nedenleri',
    'Beklenen etki',
):
    assert token.lower() in audit.lower()

print(json.dumps({
    "ok": True,
    "version": 189,
    "routes": sorted(expected),
    "affiliateCategories": 4,
    "tripleGate": True,
    "noBuy": True,
    "activeHazardCommerceClosed": True,
    "personalDataRequested": False,
    "noProductOfferSchema": True,
}, ensure_ascii=False))
