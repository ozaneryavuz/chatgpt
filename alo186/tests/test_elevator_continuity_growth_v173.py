from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "hesaplama/asansorde-elektrik-kesintisi-mahsur-kalma-guvenligi/index.html",
    ROOT / "hesaplama/asansor-otomatik-kurtarma-alarm-aku-jenerator-uygunluk-kontrolu/index.html",
    ROOT / "sektor-rehberi/apartman-otel-asansor-elektrik-kesintisi-test-merkezi/index.html",
]
ROUTES = ["/hesaplama/asansorde-elektrik-kesintisi-mahsur-kalma-guvenligi/", "/hesaplama/asansor-otomatik-kurtarma-alarm-aku-jenerator-uygunluk-kontrolu/", "/sektor-rehberi/apartman-otel-asansor-elektrik-kesintisi-test-merkezi/"]
OVERLAY = ROOT / "deployment/routing-overlays/173-elevator-continuity-growth.json"
AUDIT = ROOT / "audits/elevator-continuity-growth-v173-2026-08-01.md"

for page, route in zip(PAGES, ROUTES):
    assert page.exists(), page
    text = page.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="https://alo186.com{route}">' in text
    assert "BreadcrumbList" in text and "FAQPage" in text
    assert "ALO186 bağımsız bilgilendirme platformudur" in text
    assert "affiliate bağlantısı yoktur" in text.lower()
    assert '"Product"' not in text and '"Offer"' not in text and "aggregateRating" not in text
    assert "fiyat, stok" not in text.lower() or "yayımlan" in text.lower() or "kullanılmadı" in text.lower()
    assert "resmî kurum değildir" in text or "kamu kurumu değildir" in text
    assert "viewport-fit=cover" in text
    assert "@media(max-width:820px)" in text

p1 = PAGES[0].read_text(encoding="utf-8")
assert "Kapıyı zorlamayın" in p1 or "kapıyı zorlamayın" in p1
assert "112" in p1 and "iki yönlü haberleşme" in p1
assert "kendi kendinize çıkmaya çalışmayın" in p1

p2 = PAGES[1].read_text(encoding="utf-8")
assert "yeni ürün almayın" in p2
assert "TS EN 81-28" in p2
assert "Amazon veya başka mağaza bağlantısı eklenmedi" in p2
assert "Otomatik kurtarma cihazı" in p2

p3 = PAGES[2].read_text(encoding="utf-8")
for token in ["7 günlük", "30 günlük", "90 günlük", "JSON görev planını indir", "ICS"]:
    assert token in p3
assert "personalDataCollected:false" in p3
assert "affiliateLinks:false" in p3
assert "/iletisim/" in p3

overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert overlay["version"] == 173
assert [r["canonicalPath"] for r in overlay["routes"]] == ROUTES
assert len(set(ROUTES)) == 3

assert AUDIT.exists()
audit = AUDIT.read_text(encoding="utf-8")
for token in ["Arama niyeti", "Affiliate ürün kategorileri", "Tekrar ziyaret", "Beklenen gelir / lead etkisi", "Tamamlanamayan"]:
    assert token in audit

for page in PAGES:
    text = page.read_text(encoding="utf-8")
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, flags=re.S)
    assert blocks
    for block in blocks:
        json.loads(block)

print("ALO186 elevator continuity growth v173 contract passed")
