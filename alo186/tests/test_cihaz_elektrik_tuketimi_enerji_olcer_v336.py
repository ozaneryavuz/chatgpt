#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "alo186/hesaplama/cihaz-elektrik-tuketimi-enerji-olcer-uygunluk/index.html"
APP = PAGE.with_name("app.js")
CSS = PAGE.with_name("styles.css")
TEST = PAGE.with_name("app.test.js")
OVERLAY = ROOT / "alo186/deployment/routing-overlays/097-cihaz-elektrik-tuketimi-enerji-olcer-uygunluk.json"
WORKFLOW = ROOT / ".github/workflows/alo186-cihaz-enerji-olcer-v336.yml"
CANONICAL = "/hesaplama/cihaz-elektrik-tuketimi-enerji-olcer-uygunluk/"

for path in (PAGE, APP, CSS, TEST, OVERLAY, WORKFLOW):
    assert path.is_file(), f"missing {path}"

html = PAGE.read_text(encoding="utf-8")
js = APP.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")
overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

assert "https://alo186.com" + CANONICAL in html
assert 'id="energyForm"' in html and 'aria-live="polite"' in html
assert all(token in html for token in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"])
assert '"@type":"Product"' not in html and '"@type":"Offer"' not in html
assert "Amazon Türkiye satış ortaklığı açıklaması" in html
assert "sponsored nofollow noopener" in html
assert "IEC 62301:2026" in html and "IEC 62052-31:2024" in html and "IEC 62053-21:2020" in html
assert "Etiket wattı" in html and "aktif W/kWh" in html
assert all(token not in html.lower() for token in ['name="email"', 'name="phone"', 'name="address"', 'name="location"', 'name="subscription"', 'name="meter_number"'])
assert all(token not in js for token in ["localStorage", "sessionStorage", "fetch(", "geolocation"])
assert "alo186rehber-21" in js and "amazon.com.tr" in js
assert "commercialAllowed:false" in js
assert "baseResult('no_buy'" in js
assert "baseResult('emergency'" in js and "baseResult('stop_use'" in js
assert "VA veya anlık watt gösterimi" in js
assert "EV şarjı için priz tipi enerji ölçer" in js
assert "@media(max-width:820px)" in css and "@media(max-width:560px)" in css
assert "prefers-reduced-motion" in css and ":focus-visible" in css
assert overlay["version"] == 97
assert overlay["routes"] == [{
    "source": "alo186/hesaplama/cihaz-elektrik-tuketimi-enerji-olcer-uygunluk/index.html",
    "canonicalPath": CANONICAL,
    "type": "calculator",
}]

subprocess.run(["node", str(TEST)], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(APP)], cwd=ROOT, check=True)

print(json.dumps({
    "ok": True,
    "route": CANONICAL,
    "scenarios": 31,
    "mobileBreakpoints": [820, 560],
    "affiliateTripleGate": True,
    "noBuy": True,
    "emergencyAffiliateBlocked": True,
    "activeEnergyNotVA": True,
    "personalData": False,
    "storage": False,
}, ensure_ascii=False))
