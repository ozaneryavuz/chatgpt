from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "alo186/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/index.html").read_text(encoding="utf-8")
INJECT = (ROOT / "alo186/deployment/inject_growth_run22.py").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "alo186/deployment/routing-overlays/growth-trust-revenue-run22.json").read_text(encoding="utf-8"))

assert OVERLAY["version"] == 73
assert OVERLAY["routes"][0]["canonicalPath"] == "/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/"
for token in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList", "Lümen", "Renk sıcaklığı", "CRI", "Dimmer uyumluluğu"]:
    assert token in HTML, token
assert "ALO186 EDAŞ, kamu kurumu, ürün satıcısı" in HTML
assert "doğrudan mağaza bağlantısı yoktur" in HTML.lower()
assert "affiliateAccepted" in HTML and "Satın alma gerekmez" in HTML
assert "KEY='alo186-lighting-passport-v1'" in HTML
assert "TTL=365*86400000" in HTML and "LIMIT=8" in HTML and "REVIEW_DAYS=180" in HTML
assert "localStorage" in HTML and "JSON indir" in HTML and "text/calendar" in HTML
assert "hazard" in HTML and "Ticari yol kapalı" in HTML
for category in ["e27-led-ampul", "sensorlu-led-ampul", "sensorlu-tavan-armaturu", "dis-mekan-led-projektor", "solar-dis-mekan-lambasi", "ayarlanabilir-calisma-lambasi", "24v-led-serit-seti"]:
    assert category in HTML and category in INJECT
assert not re.search(r"amazon\.com(?:\.tr)?", HTML, re.I)
assert not re.search(r"priceCurrency|availability|aggregateRating|offers", HTML, re.I)
assert not re.search(r'type=["\'](?:email|tel|text)["\']', HTML, re.I)
assert "inject_lighting_deeplink" in INJECT
assert "qualifiedCategoryDeepLink" in INJECT
assert '"directAffiliateLinksAdded": 0' in INJECT
print(json.dumps({"ok": True, "route": OVERLAY["routes"][0]["canonicalPath"], "actions": 3}, ensure_ascii=False))
