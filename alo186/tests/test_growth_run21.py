from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
HTML = (ROOT / "alo186/hesaplama/kesinti-hazirlik-envanteri/index.html").read_text(encoding="utf-8")
INJECT_PATH = DEPLOYMENT / "inject_growth_run21.py"
INJECT = INJECT_PATH.read_text(encoding="utf-8")
OVERLAY = json.loads((DEPLOYMENT / "routing-overlays/growth-trust-revenue-run21.json").read_text(encoding="utf-8"))

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
assert 'CANONICAL = "https://alo186.com" + ROUTE' in INJECT
assert 'entry = f"<url><loc>{CANONICAL}</loc></url>"' in INJECT
assert 'f"<url><loc>{CANONICAL}</loc></urlset>"' not in INJECT
assert "ET.fromstring(updated)" in INJECT

sys.path.insert(0, str(DEPLOYMENT))
spec = importlib.util.spec_from_file_location("inject_growth_run21_test", INJECT_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as temporary:
    site = Path(temporary)
    sitemap = site / "sitemap.xml"
    sitemap.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url><loc>https://alo186.com/</loc></url>\n'
        '</urlset>\n',
        encoding="utf-8",
    )
    module.append_sitemap(site)
    ET.parse(sitemap)
    first = sitemap.read_text(encoding="utf-8")
    assert first.count(module.CANONICAL) == 1
    assert f"<url><loc>{module.CANONICAL}</loc></url>" in first
    module.append_sitemap(site)
    ET.parse(sitemap)
    assert sitemap.read_text(encoding="utf-8").count(module.CANONICAL) == 1

print(json.dumps({
    "ok": True,
    "route": OVERLAY["routes"][0]["canonicalPath"],
    "actions": 3,
    "sitemapWellFormed": True,
    "sitemapIdempotent": True,
    "canonicalHost": "https://alo186.com",
}, ensure_ascii=False))
