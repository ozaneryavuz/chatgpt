from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = "/hesaplama/kombi-kesinti-yedek-guc-uygunluk/"
HTML = (ROOT / "alo186/hesaplama/kombi-kesinti-yedek-guc-uygunluk/index.html").read_text(encoding="utf-8")
JS = (ROOT / "alo186/hesaplama/kombi-kesinti-yedek-guc-uygunluk/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "alo186/hesaplama/kombi-kesinti-yedek-guc-uygunluk/styles.css").read_text(encoding="utf-8")
INJECT = (ROOT / "alo186/deployment/inject_boiler_continuity_growth.py").read_text(encoding="utf-8")
CHAIN = (ROOT / "alo186/deployment/inject_growth_run21.py").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "alo186/deployment/routing-overlays/boiler-continuity-growth-run30.json").read_text(encoding="utf-8"))

assert OVERLAY["version"] == 82
assert OVERLAY["routes"][0]["canonicalPath"] == ROUTE
assert OVERLAY["routes"][0]["source"].endswith("kombi-kesinti-yedek-guc-uygunluk/index.html")
assert HTML.count("<h1") == 1
assert "Kombi Kesinti Yedek Güç ve UPS Uygunluğu" in HTML
assert 'rel="canonical" href="https://alo186.com/hesaplama/kombi-kesinti-yedek-guc-uygunluk/"' in HTML
for schema_type in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
    assert schema_type in HTML
for phrase in [
    "Mevcut çözüm yeterliyse satın alma önerilmez",
    "doğrudan mağaza bağlantısı vermez",
    "Amazon satış ortaklığı ilişkisi ayrıca",
    "Elektrikli kombi ve ısı pompası",
    "nötr-toprak",
    "ALO186 EDAŞ, doğalgaz dağıtım şirketi",
]:
    assert phrase in HTML
assert "RRULE:FREQ=MONTHLY;COUNT=12" in JS
assert "localStorage" in JS and "LIMIT=10" in JS and "TTL=365*86400000" in JS
assert "state:'no_buy'" in JS and "state:'emergency'" in JS and "state:'qualified'" in JS
assert "insert_hub_card" in INJECT and "insert_entry_panels" in INJECT
assert "data-alo186-boiler-hub-card" in INJECT and "37 çekirdek araç" in INJECT
assert 'Path("elektrik-portali/index.html")' in INJECT
assert 'Path("akilli-urun-secimi/index.html")' in INJECT
assert 'Path("amazon-elektrik-urunleri/index.html")' in INJECT
assert 'CANONICAL = "https://alo186.com" + ROUTE' in INJECT
assert 'entry = f"<url><loc>{CANONICAL}</loc></url>"' in INJECT
assert 'f"<url><loc>{CANONICAL}</loc></urlset>"' not in INJECT
assert "ET.fromstring(updated)" in INJECT
assert "run_boiler_continuity" in CHAIN and "boilerContinuity" in CHAIN
assert 'ET.parse(site / "sitemap.xml")' in CHAIN
assert "min-inline-size:0" in CSS and "@media(max-width:640px)" in CSS
assert not re.search(r"amazon\.(?:com|com\.tr)|amzn\.", HTML + JS, re.I)
assert not re.search(r'"@type"\s*:\s*"(?:Product|Offer)"|priceCurrency|aggregateRating|availability', HTML, re.I)
assert not re.search(r'type=["\'](?:email|tel|text|file)["\']|<textarea', HTML, re.I)
print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "actions": 3,
    "artifactToolCount": 37,
    "sitemapWriterWellFormed": True,
    "finalChainParseRequired": True,
}, ensure_ascii=False))
