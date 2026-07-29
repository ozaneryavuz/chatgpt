from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "alo186/deployment"))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTE = "/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/"
SOURCE = REPO_ROOT / "alo186/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/index.html"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 68
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == "alo186/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/index.html"
    assert routes[0]["type"] == "calculator"

    html = SOURCE.read_text(encoding="utf-8")
    injector = (REPO_ROOT / "alo186/deployment/inject_growth_run20.py").read_text(encoding="utf-8")
    chain = (REPO_ROOT / "alo186/deployment/inject_shortlist_growth.py").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://www.alo186.com/hesaplama/usb-c-guc-ve-goruntu-karar-merkezi/"' in html
    assert "WebApplication" in html and "FAQPage" in html and "BreadcrumbList" in html
    for action in ['data-action="power-chain"', 'data-action="display-diagnosis"', 'data-action="desktop-passport"']:
        assert action in html
    for form_id in ["powerForm", "displayForm", "passportForm"]:
        assert f'id="{form_id}"' in html

    assert "Mevcut zincir yeterliyse satın almama" in html
    assert "Mevcut set yeterli" in html
    assert "directAffiliateLinksAdded" in injector and '"directAffiliateLinksAdded": 0' in injector
    assert "hazardCommerceClosed" in injector and "unknownCapabilityCommerceClosed" in injector
    assert "noBuyOutcomePreserved" in injector
    assert "unverifiedCommercialFieldsUsed" in injector
    assert "passportRecordLimit" in injector and "passportTtlDays" in injector and "passportReviewDays" in injector
    assert "MAX=6" in html and "TTL=365*86400000" in html
    assert "180*86400000" in html

    assert "sponsored" not in html.lower(), "Araç doğrudan affiliate mağaza bağlantısı taşımamalı"
    assert "amazon.com.tr" not in html.lower(), "Araç doğrudan Amazon URL taşımamalı"
    assert "alo186rehber-21" not in html, "Affiliate etiketi karar aracına doğrudan sızmamalı"
    assert "/akilli-urun-secimi?kategori=usb_c_charger" in html
    assert "/akilli-urun-secimi?kategori=usb_c_cable" in html
    assert "/akilli-urun-secimi?kategori=usb_c_hub" in html
    assert "/akilli-urun-secimi?kategori=usb_c_display_cable" in html

    for forbidden in [
        'type="email"', 'type="tel"', 'name="email"', 'name="phone"',
        "priceCurrency", "aggregateRating", "availability", "seller", "warranty",
    ]:
        assert forbidden.lower() not in html.lower(), forbidden
    assert "ALO186 ürün satıcısı, üretici, servis veya resmî kurum değildir" in html
    assert "Fiyat, stok, puan, satıcı, teslimat ve garanti kullanılmaz" in html

    for source in ["https://www.usb.org/usb-charger-pd", "https://www.usb.org/cable_connector", "https://www.displayport.org/faq/"]:
        assert source in html
    assert "DisplayPort Alt Mode" in html
    assert "240 W" in html and "60 W" in html

    assert "from inject_growth_run20 import run as run_growth_run20" in chain
    assert "growth_run20 = run_growth_run20(site, base_path)" in chain
    assert '"growthRun20": growth_run20' in chain
    assert chain.index("growth_run20 = run_growth_run20") > chain.index("growth_run19 = run_growth_run19")

    scripts = re.findall(r'<script(?![^>]+type=["\']application/ld\+json["\'])[^>]*>(.*?)</script>', html, re.I | re.S)
    assert len(scripts) == 1
    assert "localStorage" in scripts[0]
    assert "powerHazard" in scripts[0] and "displayHazard" in scripts[0]
    assert "powerExistingInsufficient" in scripts[0] and "displayExistingInsufficient" in scripts[0]
    assert "powerAffiliate" in scripts[0] and "displayAffiliate" in scripts[0] and "passportAffiliate" in scripts[0]

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "actions": ["power_chain", "display_diagnosis", "desktop_passport"],
        "directAffiliateLinks": 0,
        "passportLimit": 6,
        "passportTtlDays": 365,
        "reviewDays": 180,
        "unverifiedCommercialFieldsUsed": [],
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
