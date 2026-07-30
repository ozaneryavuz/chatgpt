#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "alo186/hesaplama/arac-aku-sarj-cihazi-takviye-uygunluk/index.html"
APP = PAGE.with_name("app.js")
CSS = PAGE.with_name("styles.css")
TEST = PAGE.with_name("app.test.js")
OVERLAY = ROOT / "alo186/deployment/routing-overlays/094-arac-aku-sarj-takviye-uygunluk.json"
WORKFLOW = ROOT / ".github/workflows/alo186-arac-aku-sarj-takviye-v333.yml"
CANONICAL = "/hesaplama/arac-aku-sarj-cihazi-takviye-uygunluk/"

for path in (PAGE, APP, CSS, TEST, OVERLAY, WORKFLOW):
    assert path.is_file(), f"missing {path}"

html = PAGE.read_text(encoding="utf-8")
js = APP.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")
overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

assert "https://alo186.com" + CANONICAL in html
assert 'id="batteryForm"' in html and 'aria-live="polite"' in html
assert "WebApplication" in html and "DefinedTermSet" in html and "FAQPage" in html and "BreadcrumbList" in html
assert '"@type":"Product"' not in html and '"@type":"Offer"' not in html
assert "Amazon Türkiye satış ortaklığı açıklaması" in html
assert "sponsored nofollow noopener" in html
assert all(token not in html.lower() for token in ['name="email"', 'name="phone"', 'name="address"', 'name="location"', 'name="vin"', 'name="plate"'])
assert all(token not in js for token in ["localStorage", "sessionStorage", "fetch(", "geolocation"])
assert "alo186rehber-21" in js and "amazon.com.tr" in js
assert "commercialAllowed:false" in js
assert "result('no_buy'" not in js
assert "baseResult('no_buy'" in js
assert "baseResult('emergency'" in js and "baseResult('stop_use'" in js
assert "Donmuş olabilecek aküyü şarj etmeyin" in js
assert "LiFePO₄" in js and "recondition" in js
assert "@media(max-width:820px)" in css and "@media(max-width:560px)" in css
assert "prefers-reduced-motion" in css and ":focus-visible" in css
assert overlay["version"] == 94
assert overlay["routes"] == [{
    "source": "alo186/hesaplama/arac-aku-sarj-cihazi-takviye-uygunluk/index.html",
    "canonicalPath": CANONICAL,
    "type": "calculator",
}]

subprocess.run(["node", str(TEST)], cwd=ROOT, check=True)
subprocess.run(["node", "--check", str(APP)], cwd=ROOT, check=True)

print(json.dumps({
    "ok": True,
    "route": CANONICAL,
    "scenarios": 22,
    "mobileBreakpoints": [820, 560],
    "affiliateTripleGate": True,
    "noBuy": True,
    "emergencyAffiliateBlocked": True,
    "personalData": False,
    "storage": False,
}, ensure_ascii=False))
