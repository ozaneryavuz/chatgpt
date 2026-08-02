from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = (ROOT / "amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
APP = (ROOT / "amazon-elektrik-urunleri/appliance-guide.js").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "deployment/routing-overlays/121-appliance-commerce-guides.json").read_text(encoding="utf-8"))

PAGES = {
    "combi": ROOT / "amazon-elektrik-urunleri/kombi-ups-power-station-secimi/index.html",
    "cold_chain": ROOT / "amazon-elektrik-urunleri/buzdolabi-dondurucu-power-station-secimi/index.html",
}

for kind, path in PAGES.items():
    assert path.is_file(), path
    html = path.read_text(encoding="utf-8")
    assert html.count("<h1") == 1
    assert f'data-appliance-guide="{kind}"' in html
    assert "Reklam / satış ortaklığı açıklaması" in html
    assert "kullanıcıya ek maliyet yansımaz" in html.lower()
    assert "Mevcut" in html and "satın alma" in html
    assert 'id="scenario"' in html
    assert 'id="actualNeed"' in html
    assert 'id="technicalCheck"' in html
    assert 'id="affiliateCheck"' in html
    assert 'id="affiliateLink"' in html
    assert 'aria-disabled="true"' in html
    assert 'id="affiliateLink"' in html and not re.search(r'id="affiliateLink"[^>]+href=', html)
    assert 'rel="sponsored nofollow noopener"' in html
    assert 'id="downloadIcs"' in html
    assert "90 günlük" in html
    assert "ALO186" in html and "ürün satıcısı değildir" in html
    assert "Amazon arama sonucu uygunluk onayı değildir" in html
    for forbidden in [
        '"@type":"Product"',
        '"@type":"Offer"',
        "priceCurrency",
        "aggregateRating",
        '"availability"',
        '"review"',
    ]:
        assert forbidden not in html, (kind, forbidden)
    assert not re.search(r'<input[^>]+type="(?:text|email|tel)"', html, re.I)
    assert "<textarea" not in html.lower()

assert "18+ karar rotası" in HUB
assert "Kampanya için değil, kanıtı yenilemek için geri dönün." in HUB
assert "/amazon-elektrik-urunleri/kombi-ups-power-station-secimi" in HUB
assert "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici/" in HUB
assert HUB.count('class="card route-card"') == 12
assert HUB.count('data-commercial-route="priority-card"') == 6
assert HUB.count('data-commercial-route="core-card"') == 6
assert "fiyat, stok, satıcı, teslimat, puan, yorum ve garanti" in HUB.lower()

for token in [
    "scenario.value === 'planning'",
    "checks.every",
    "sponsored nofollow noopener",
    "Aktif kesintide ürün teslimatı anlık çözüm değildir",
    "90 * 86400000",
    "alo186rehber-21",
]:
    assert token in APP, token

for token in ["localStorage", "sessionStorage", "geolocation", "fetch("]:
    assert token not in APP, token

assert OVERLAY["version"] == 121
assert OVERLAY["generatedAt"] == "2026-07-31"
assert len(OVERLAY["routes"]) == 2
assert {route["canonicalPath"] for route in OVERLAY["routes"]} == {
    "/amazon-elektrik-urunleri/kombi-ups-power-station-secimi",
    "/amazon-elektrik-urunleri/buzdolabi-dondurucu-power-station-secimi",
}
assert all(route["type"] == "commerce-guide" for route in OVERLAY["routes"])

subprocess.run(["node", "--check", str(ROOT / "amazon-elektrik-urunleri/appliance-guide.js")], check=True)

print(json.dumps({
    "ok": True,
    "guides": 2,
    "visibleHubDecisionCards": 12,
    "hubDecisionRouteClaim": "18+",
    "affiliateTripleGate": True,
    "activeOutageCommerceClosed": True,
    "noBuyOutcome": True,
    "directProductClaims": 0,
    "personalDataFields": 0,
    "reminderDays": 90,
}, ensure_ascii=False))
