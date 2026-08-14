from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "alo186/hesaplama/power-station-gunes-paneli-uygunluk-sarj-suresi"
ROUTE = ROOT / "alo186/deployment/routing-overlays/356-power-station-solar-input.json"
POLICY = ROOT / "alo186/deployment/affiliate-category-decisions/power-station-solar-input-v356.json"

html = (MODULE / "index.html").read_text(encoding="utf-8")
css = (MODULE / "styles.css").read_text(encoding="utf-8")
app = (MODULE / "app.js").read_text(encoding="utf-8")
core = (MODULE / "core.js").read_text(encoding="utf-8")

assert '<link rel="canonical" href="https://alo186.com/hesaplama/power-station-gunes-paneli-uygunluk-sarj-suresi/">' in html
assert all(token in html for token in ("WebApplication", "FAQPage", "BreadcrumbList"))
assert "amazon.com.tr" not in html.lower()
assert "alo186rehber-21" in app
assert "sponsored nofollow noopener" in app
for banned in ("localStorage", "sessionStorage", "geolocation", "XMLHttpRequest", "fetch("):
    assert banned not in html + app + core
for field in ('name="name"', 'name="email"', 'name="phone"', 'name="address"'):
    assert field not in html.lower()
assert "min-height:48px" in css
assert "@media(max-width:620px)" in css
assert "prefers-reduced-motion" in css and "forced-colors" in css
for token in ("arrayColdVocV", "arrayIscA", "currentClippingVerified", "overpanelVerified", "no_buy", "compatible_candidate"):
    assert token in core

route = json.loads(ROUTE.read_text(encoding="utf-8"))
assert route["version"] == 356
assert route["routes"][0]["canonicalPath"] == "/hesaplama/power-station-gunes-paneli-uygunluk-sarj-suresi/"
assert route["routes"][0]["type"] == "calculator"
policy = json.loads(POLICY.read_text(encoding="utf-8"))
assert policy["defaultDecision"] == "closed"
assert policy["affiliateTag"] == "alo186rehber-21"
assert "existing compatible panel already passes real solar test" in policy["alwaysClosedFor"]

subprocess.run(["node", str(MODULE / "test.js")], check=True)
print("ALO186 power-station solar v356 static contract: PASS")
