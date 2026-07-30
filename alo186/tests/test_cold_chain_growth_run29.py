from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = "/hesaplama/buzdolabi-dondurucu-kesinti-guvenligi/"
HTML_PATH = ROOT / "alo186/hesaplama/buzdolabi-dondurucu-kesinti-guvenligi/index.html"
JS_PATH = HTML_PATH.with_name("app.js")
HUB_PATH = ROOT / "alo186/hesaplama/index.html"
OVERLAY_PATH = ROOT / "alo186/deployment/routing-overlays/cold-chain-growth-run29.json"

html = HTML_PATH.read_text(encoding="utf-8")
js = JS_PATH.read_text(encoding="utf-8")
hub = HUB_PATH.read_text(encoding="utf-8")
overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))

assert overlay["version"] == 81
assert overlay["routes"] == [{
    "source": "alo186/hesaplama/buzdolabi-dondurucu-kesinti-guvenligi/index.html",
    "canonicalPath": ROUTE,
    "type": "calculator",
}]
assert '<link rel="canonical" href="https://alo186.com' + ROUTE + '">' in html
assert html.count("<h1") == 1
assert all(token in html for token in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"])
assert "ALO186 sağlık veya gıda denetim kurumu, EDAŞ, kamu kurumu ya da ürün satıcısı değildir" in html
assert "Amazon satış ortaklığı bağlantılarıdır" in html
assert "fiyat, stok, puan, satıcı, teslimat veya garanti" in html
assert "actualMissing" in html and "futurePreparedness" in html and "affiliateAccepted" in html
assert "Mevcut ekipman yeterli" in js or "Mevcut hazırlığınız" in js
assert "rel=\"sponsored nofollow noopener\"" in js
assert "alo186rehber-21" in js
assert "stage!=='active'" in js
assert "electricalHazard" in js and "floodContact" in js
assert "localStorage" in js and "LIMIT=8" in js and "TTL=365*86400000" in js
assert "RRULE:FREQ=WEEKLY;COUNT=12" in js
assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(", js)
assert not re.search(r'type=["\'](?:email|tel|text|file|password)["\']|<textarea', html, re.I)
assert not re.search(r'"@type"\s*:\s*"Offer"|priceCurrency|aggregateRating|availability', html, re.I)
tool_count = re.search(r"(\d+) çekirdek araç", hub)
assert tool_count and int(tool_count.group(1)) >= 36
assert './buzdolabi-dondurucu-kesinti-guvenligi/' in hub
assert "Buzdolabı ve Dondurucu Kesinti Güvenliği" in hub
assert "https://www.alo186.com" not in hub
for domain in ["www.fda.gov", "www.foodsafety.gov"]:
    assert domain in html
print(json.dumps({"ok": True, "route": ROUTE, "actions": 3, "recordLimit": 8, "ttlDays": 365, "hubToolCount": int(tool_count.group(1))}, ensure_ascii=False))
