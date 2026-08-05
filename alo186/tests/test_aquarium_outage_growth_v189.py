#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALC = ROOT / "alo186/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/index.html"
TRACKER = ROOT / "alo186/sektor-rehberi/akvaryum-kesinti-30-90-gun-test-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/189-aquarium-outage-growth.json"
AUDIT = ROOT / "alo186/audits/aquarium-outage-growth-v189-2026-08-02.md"
EXPECTED = {
    "/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/": CALC,
    "/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/": SELECTOR,
    "/sektor-rehberi/akvaryum-kesinti-30-90-gun-test-merkezi/": TRACKER,
}


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == "a":
            self.anchors.append({key.casefold(): value or "" for key, value in attrs})


texts: dict[Path, str] = {}
for canonical, path in EXPECTED.items():
    assert path.is_file(), path
    text = path.read_text(encoding="utf-8")
    texts[path] = text
    assert f'<link rel="canonical" href="https://alo186.com{canonical}">' in text
    assert "Bağımsız" in text or "bağımsız" in text
    assert '"@type":"Offer"' not in text
    assert "AggregateRating" not in text
    assert '"availability"' not in text

assert "kamu kurumu" in texts[SELECTOR]
assert "kamu kurumu" in texts[TRACKER]

calc = texts[CALC]
for token in (
    "Canlı stresi veya su-elektrik tehlikesinde ticari yol kapalı",
    "Mevcut plan yeterli — yeni ürün almayın",
    "Aktif kesintide önce gerçek havalandırmayı sağlayın",
    "30 gün: pil, hortum ve termometre",
    "90 gün: gözetimli kesinti provası",
    "180 gün: sıcaklık, stok ve filtre planı",
    "/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/",
):
    assert token in calc, token
for forbidden in (
    "fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.",
    "document.cookie", 'type="email"', 'type="tel"',
):
    assert forbidden not in calc, forbidden

selector = texts[SELECTOR]
for token in (
    "Pilli hava motoru",
    "Açıkça 5 V USB hava pompası",
    "Basit akvaryum termometresi",
    "Satış ortaklığı açıklaması",
    "Satın almama geçerli sonuçtur",
    "Mevcut plan yeterli. Yeni ürün almayın.",
    "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz",
):
    assert token in selector, token
assert "alo186rehber-21" in selector
assert "sponsored nofollow noopener" in selector
assert "pointer-events:none" in selector
assert "removeAttribute('href')" in selector
assert not re.search(r'href=["\']https://www\.amazon\.com\.tr/', selector, re.I)

parser = AnchorParser()
parser.feed(selector)
product_ids = {"batteryLink", "usbLink", "tempLink"}
product_anchors = [anchor for anchor in parser.anchors if anchor.get("id") in product_ids]
assert len(product_anchors) == 3
for anchor in product_anchors:
    assert not anchor.get("href")
    assert anchor.get("aria-disabled") == "true"
    assert {"sponsored", "nofollow", "noopener"}.issubset(set(anchor.get("rel", "").split()))

tracker = texts[TRACKER]
for token in (
    "JSON indir", "30/90 gün ICS indir", "Test başarılı",
    "Mevcut ekipmanı kullanın; yeni ürün almayın", "Kişisel veri istemez",
):
    assert token in tracker
assert "localStorage" not in tracker
assert "document.cookie" not in tracker
assert "30 ve 90 gün resmî bakım periyodu mudur?" in tracker

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 189
routes = {item["canonicalPath"]: ROOT / item["source"] for item in overlay["routes"]}
assert set(routes) == set(EXPECTED)
for canonical, source in routes.items():
    assert source.resolve() == EXPECTED[canonical].resolve()

assert AUDIT.is_file()
audit = AUDIT.read_text(encoding="utf-8")
for token in (
    "Arama niyeti", "İçerik boşluğu", "Kullanıcı yolculuğu",
    "Affiliate ürün kategorileri", "Dönüşüm noktaları",
    "Tekrar ziyaret nedenleri", "Beklenen etki",
):
    assert token.casefold() in audit.casefold()

print(json.dumps({
    "ok": True,
    "legacyVersion": 189,
    "migratedToCurrentTrustContract": True,
    "routes": sorted(EXPECTED),
    "guardedProductClasses": 3,
    "noBuy": True,
    "activeHazardCommerceClosed": True,
    "personalDataRequested": False,
    "noOfferSchema": True,
}, ensure_ascii=False))
