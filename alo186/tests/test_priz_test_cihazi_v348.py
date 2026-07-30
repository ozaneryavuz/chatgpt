from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "hesaplama" / "priz-test-cihazi-topraklama-on-kontrol"
HTML = (PAGE / "index.html").read_text(encoding="utf-8")
JS = (PAGE / "app.js").read_text(encoding="utf-8")
CSS = (PAGE / "styles.css").read_text(encoding="utf-8")
OVERLAY = ROOT / "deployment" / "routing-overlays" / "102-priz-test-cihazi-topraklama-on-kontrol.json"
ROUTE = "/hesaplama/priz-test-cihazi-topraklama-on-kontrol/"

assert HTML.lower().count("<h1>") == 1
assert 'rel="canonical" href="https://alo186.com' + ROUTE + '"' in HTML
for schema in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
    assert f'"@type":"{schema}"' in HTML
for token in [
    "Priz test cihazını", "Priz test cihazı topraklamanın iyi olduğunu kanıtlar mı?",
    "IEC 60364-6:2026", "IEC 61557-4:2019", "IEC 61557-6:2019", "IEC 61010-2-030:2023",
    "Amazon Türkiye satış ortaklığı açıklaması", 'rel="sponsored nofollow noopener"',
    "Mevcut test cihazı yeterli; yeni ürün almayın"
]:
    assert token in HTML + JS
for forbidden in [
    '"@type":"Product"', '"@type":"Offer"', "aggregateRating", "reviewCount",
    "localStorage", "sessionStorage", "geolocation", "navigator.geolocation",
    "fetch(", "XMLHttpRequest", 'type="email"', 'type="tel"', 'name="address"'
]:
    assert forbidden not in HTML + JS
for element_id in [
    "outletForm", "emergency", "condition", "issue", "outageScope", "role",
    "installation", "plugStandard", "commonFaults", "voltageDisplay", "rcdFunctional",
    "earthQuality", "loopImpedance", "rcdTripTime", "measuredVoltage", "ownership",
    "testerType", "plugCompatibility", "voltageRating", "safetyEvidence", "recall",
    "knownGood", "result", "commerce", "affiliate", "downloadJson", "downloadIcs", "printResult"
]:
    assert f'id="{element_id}"' in HTML
assert "@media(max-width:560px)" in CSS
assert "@media(max-width:900px)" in CSS
assert "prefers-reduced-motion" in CSS
assert ":focus-visible" in CSS
assert "aria-live" in HTML and "skip-link" in HTML
assert "alo186rehber-21" in JS
assert "personalData: false" in JS
assert "confirmations.every" in JS
assert "reviewDays: 180" in JS
assert "threephase" in JS and "loopImpedance" in JS and "rcdTripTime" in JS
assert OVERLAY.exists()
data = json.loads(OVERLAY.read_text(encoding="utf-8"))
assert data["version"] == 102
assert data["generatedAt"] == "2026-07-30"
entry = data["routes"][0]
assert entry["canonicalPath"] == ROUTE
assert entry["type"] == "calculator"
assert entry["source"] == "alo186/hesaplama/priz-test-cihazi-topraklama-on-kontrol/index.html"
subprocess.run(["node", "--check", str(PAGE / "app.js")], check=True)
completed = subprocess.run(["node", str(PAGE / "app.test.js")], check=True, capture_output=True, text=True)
payload = json.loads(completed.stdout)
assert payload["ok"] is True
assert payload["scenarios"] >= 55
print(json.dumps({
    "ok": True,
    "route": ROUTE,
    "decision_scenarios": payload["scenarios"],
    "mobile_breakpoints": [900, 560],
    "personal_data": False,
    "affiliate_gate": 3,
    "no_buy": True,
    "professional_measurements_blocked": True,
    "outage_186_route": True
}, ensure_ascii=False))
