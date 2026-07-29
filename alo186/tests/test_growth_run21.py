from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "alo186/hesaplama/kesinti-hazirlik-envanteri/index.html").read_text(encoding="utf-8")
INJECT = (ROOT / "alo186/deployment/inject_growth_run21.py").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "alo186/deployment/routing-overlays/growth-trust-revenue-run21.json").read_text(encoding="utf-8"))

assert OVERLAY["version"] == 72
assert OVERLAY["routes"][0]["canonicalPath"] == "/hesaplama/kesinti-hazirlik-envanteri/"
assert "WebApplication" in HTML and "FAQPage" in HTML and "BreadcrumbList" in HTML
assert "ALO186 EDAŞ, kamu kurumu, ürün satıcısı veya servis değildir" in HTML
assert "doğrudan mağaza bağlantısı yoktur" in HTML.lower()
assert "affiliateAccepted" in HTML and "yeniden satın almayın" in HTML.lower()
assert "TTL=365*86400000" in HTML and "LIMIT=12" in HTML and "90 günlük" in HTML
assert "localStorage" in HTML and "JSON indir" in HTML and "text/calendar" in HTML
assert not re.search(r"amazon\.com(?:\.tr)?", HTML, re.I)
assert not re.search(r"priceCurrency|availability|aggregateRating|offers", HTML, re.I)
assert not re.search(r'type=["\'](?:email|tel|text)["\']', HTML, re.I)
assert "inject_risk_gate" in INJECT
for token in ["pano", "rccb", "rcbo", "jeneratör", "inverter", "mppt", "ev şarj"]:
    assert token in INJECT.lower()
assert "Önce teknik uygunluğu doğrula" in INJECT
assert "directAffiliateLinksAdded\": 0" in INJECT
print(json.dumps({"ok": True, "route": OVERLAY["routes"][0]["canonicalPath"], "actions": 3}, ensure_ascii=False))
