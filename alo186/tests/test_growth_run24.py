from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "alo186/hesaplama/home-office-internet-sureklilik-plani/index.html").read_text(encoding="utf-8")
INJECT = (ROOT / "alo186/deployment/inject_growth_run24.py").read_text(encoding="utf-8")
CHAIN = (ROOT / "alo186/deployment/inject_growth_run22.py").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "alo186/deployment/routing-overlays/growth-trust-revenue-run24.json").read_text(encoding="utf-8"))

assert OVERLAY["version"] == 76
assert OVERLAY["routes"][0]["canonicalPath"] == "/hesaplama/home-office-internet-sureklilik-plani/"
assert "WebApplication" in HTML and "DefinedTermSet" in HTML and "FAQPage" in HTML and "BreadcrumbList" in HTML
for token in ["Yerel güç mü, upstream ağ mı?", "Kritik yük ve enerji hedefi", "Karşılaştırılabilir kesinti günlüğü"]:
    assert token in HTML
assert "ALO186 EDAŞ, internet servis sağlayıcısı, ürün satıcısı veya kamu kurumu değildir" in HTML
assert "affiliateAccepted" in HTML and "Amazon satış ortaklığı" in HTML
assert "Satın alma gerekli değildir" in HTML
assert "repeatedUpstream" in HTML and ">=2" in HTML and "upstream açığı" in HTML
assert "TTL=365*86400000" in HTML and "LIMIT=12" in HTML and "REVIEW_DAYS=30" in HTML
assert "localStorage" in HTML and "JSON indir" in HTML and "text/calendar" in HTML
assert "requiredWh" in HTML and "1.25" in HTML
assert not re.search(r"amazon\.com(?:\.tr)?", HTML, re.I)
assert not re.search(r"priceCurrency|availability|aggregateRating|offers", HTML, re.I)
assert not re.search(r'type=["\'](?:email|tel|text)["\']', HTML, re.I)
assert "run_growth_run24" in CHAIN and "homeOfficeContinuity" in CHAIN
assert "upstreamFailureSuppressesCommerce" in INJECT and "directAffiliateLinksAdded\": 0" in INJECT
assert len(re.findall(r"Path\(", INJECT)) >= 5
print(json.dumps({"ok": True, "route": OVERLAY["routes"][0]["canonicalPath"], "actions": 3}, ensure_ascii=False))
