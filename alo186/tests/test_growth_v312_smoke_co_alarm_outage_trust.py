#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/elektrik-kesilince-duman-karbonmonoksit-alarmi-calisir-mi/index.html"
PLANNER = ROOT / "alo186/hesaplama/duman-karbonmonoksit-alarmi-kesinti-hazirlik-plani/index.html"
AFFILIATE = ROOT / "alo186/amazon-elektrik-urunleri/ev-tipi-duman-karbonmonoksit-alarmi-secimi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/smoke-co-alarm-outage-trust-v312.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v312-smoke-co-alarm-outage-trust.json"
DISCOVERY = ROOT / "alo186/sitemap-growth-v312.xml"
ROBOTS = ROOT / "alo186/robots.txt"
CANONICALS = {
    GUIDE: "https://alo186.com/haberler/elektrik-kesilince-duman-karbonmonoksit-alarmi-calisir-mi/",
    PLANNER: "https://alo186.com/hesaplama/duman-karbonmonoksit-alarmi-kesinti-hazirlik-plani/",
    AFFILIATE: "https://alo186.com/amazon-elektrik-urunleri/ev-tipi-duman-karbonmonoksit-alarmi-secimi/",
}

def read(p: Path) -> str:
    assert p.is_file(), p
    return p.read_text(encoding="utf-8")

def validate(p: Path, canonical: str) -> str:
    html = read(p)
    assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I) == [canonical]
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.I | re.S)
    assert blocks
    for block in blocks:
        json.loads(block)
    folded = html.casefold()
    for forbidden in ('"@type":"aggregaterating"', '"@type":"review"', '"availability":', '"warranty":', '"delivery":', "https://www.alo186.com"):
        assert forbidden.casefold() not in folded, (p, forbidden)
    return html

def visible(html: str, *phrases: str) -> None:
    folded = html.casefold()
    for phrase in phrases:
        assert phrase.casefold() in folded, phrase

def main() -> None:
    guide = validate(GUIDE, CANONICALS[GUIDE])
    planner = validate(PLANNER, CANONICALS[PLANNER])
    affiliate = validate(AFFILIATE, CANONICALS[AFFILIATE])
    visible(guide, "Aktif olay alışveriş fırsatı değildir", "pili çıkarmayın", "112", "professional-only", "yeni ürün almayın", "Test düğmesi", "6 Ağustos 2026")
    assert "amazon.com.tr" not in guide.casefold()
    visible(planner, "form ve ticaret kapalıdır", "Kişisel verisiz", "sunucuya gönderilmez", "kalıcı tarayıcı depolaması", "Mevcut hazırlık yeterli — yeni ürün almayın", "30/90/365", "Blob", "text/calendar")
    for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie", 'type="email"', 'type="tel"', "navigator.geolocation"):
        assert forbidden not in planner, forbidden
    assert "amazon.com.tr" not in planner.casefold()
    visible(affiliate, "Amazon Türkiye satış ortaklığı açıklaması", "nitelikli satın alımlardan komisyon", "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi yayımlanmaz", "yeni ürün almayın", "Professional-only sınıflar", "tek özel konut")
    links = re.findall(r'<a\s+class="merchant"([^>]*)>', affiliate, re.I)
    assert len(links) == 2
    for attrs in links:
        assert "data-merchant-url=" in attrs
        assert 'rel="sponsored noopener"' in attrs
        assert " href=" not in attrs.lower()
        assert 'aria-disabled="true"' in attrs
    assert affiliate.count("amazon.com.tr") == 2
    assert affiliate.count("tag=alo186rehber-21") == 2
    assert affiliate.count('class="gate"') == 8
    decision = json.loads(read(DECISION))
    assert decision["version"] == 312
    assert decision["newMerchantLinks"] == 2
    assert decision["affiliatePolicy"]["consumerAffiliateClasses"] == 2
    assert decision["affiliatePolicy"]["activeAlarmCommerceClosed"] is True
    assert decision["affiliatePolicy"]["buildingSystemCommerceClosed"] is True
    assert decision["affiliatePolicy"]["gateCount"] == 8
    assert decision["privacyPolicy"]["personalDataFields"] == 0
    assert decision["privacyPolicy"]["serverSubmission"] is False
    assert decision["privacyPolicy"]["persistentBrowserStorage"] is False
    assert decision["privacyPolicy"]["localIcsGeneration"] is True
    assert [x["days"] for x in decision["repeatVisitReasons"]] == [30, 90, 365]
    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 312
    assert len(overlay["routes"]) == 3
    assert overlay["updatedExistingRoutes"] == []
    root = ET.fromstring(read(DISCOVERY)); ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [x.text for x in root.findall("s:url/s:loc", ns)]
    assert len(urls) == 5 and len(urls) == len(set(urls))
    for canonical in CANONICALS.values():
        assert canonical in urls
    assert "Sitemap: https://alo186.com/sitemap-growth-v312.xml" in read(ROBOTS)
    print(json.dumps({"ok": True, "version": 312, "newCanonicalRoutes": 3, "newMerchantLinks": 2, "consumerAffiliateClasses": 2, "professionalOnlyClasses": len(decision["professionalOnlyClasses"]), "activeAlarmCommerceClosed": True, "personalDataFields": 0, "repeatVisitDays": [30, 90, 365]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
