#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "alo186/hesaplama/multimetre-pensampermetre-cat-uygunluk/index.html"
APP = PAGE.with_name("app.js")
CSS = PAGE.with_name("styles.css")
TEST = PAGE.with_name("app.test.js")
OVERLAY = ROOT / "alo186/deployment/routing-overlays/098-multimetre-pensampermetre-cat-uygunluk.json"
WORKFLOW = ROOT / ".github/workflows/alo186-multimetre-pensampermetre-cat-v339.yml"
CANONICAL = "/hesaplama/multimetre-pensampermetre-cat-uygunluk/"

for path in (PAGE, APP, CSS, TEST, OVERLAY, WORKFLOW):
    assert path.is_file(), f"missing {path}"

html = PAGE.read_text(encoding="utf-8")
js = APP.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")
overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

assert "https://alo186.com" + CANONICAL in html
assert html.count("<h1>") == 1
assert 'id="meterForm"' in html and 'aria-live="polite"' in html
assert all(token in html for token in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"])
assert all(token in html for token in ["CAT II", "CAT III", "CAT IV", "True RMS", "Inrush"])
assert all(source in html for source in ["IEC 61010-2-033:2023", "IEC 61010-2-032:2023", "IEC 61010-031:2022"])
assert "Amazon Türkiye satış ortaklığı açıklaması" in html
assert "sponsored nofollow noopener" in html
assert html.count('class="confirm"') == 3
assert '"@type":"Product"' not in html and '"@type":"Offer"' not in html
assert all(field not in html.lower() for field in ['name="email"', 'name="phone"', 'name="address"', 'name="location"'])
assert all(token not in js for token in ["localStorage", "sessionStorage", "fetch(", "geolocation"])
assert "baseResult('emergency'" in js
assert "baseResult('no_buy'" in js
assert "Temassız gerilim kalemi tek başına karar aracı değildir" in js
assert "Enerjisizlik doğrulaması multimetre veya temassız kalemle tek başına yapılmaz" in js
assert "alo186rehber-21" in js and "amazon.com.tr" in js
assert "commercialAllowed:false" in js
assert "@media(max-width:820px)" in css and "@media(max-width:560px)" in css
assert "prefers-reduced-motion" in css and ":focus-visible" in css
assert overlay["version"] == 98
assert overlay["routes"] == [{
    "source": "alo186/hesaplama/multimetre-pensampermetre-cat-uygunluk/index.html",
    "canonicalPath": CANONICAL,
    "type": "calculator",
}]

completed = subprocess.run(["node", str(TEST)], cwd=ROOT, check=True, capture_output=True, text=True)
payload = json.loads(completed.stdout.strip())
assert payload["ok"] is True and payload["scenarios"] == 31
subprocess.run(["node", "--check", str(APP)], cwd=ROOT, check=True)

print(json.dumps({
    "ok": True,
    "route": CANONICAL,
    "scenarios": 31,
    "mobileBreakpoints": [820, 560],
    "affiliateTripleGate": True,
    "noBuy": True,
    "emergencyAffiliateBlocked": True,
    "ncvNotSufficient": True,
    "absenceVoltageProfessional": True,
    "personalData": False,
    "storage": False,
    "revisitDays": 180,
}, ensure_ascii=False))
