#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/elektrik-kesilince-guvenlik-alarmi-calisir-mi/index.html"
PLANNER = ROOT / "alo186/hesaplama/guvenlik-alarmi-elektrik-kesintisi-hazirlik-plani/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/apartman-otel-guvenlik-alarmi-kesinti-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/security-alarm-outage-continuity-v313.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v313-security-alarm-outage-continuity.json"
DISCOVERY = ROOT / "alo186/sitemap-growth-v313.xml"
ROBOTS = ROOT / "alo186/robots.txt"
CANONICALS = {
    GUIDE: "https://alo186.com/haberler/elektrik-kesilince-guvenlik-alarmi-calisir-mi/",
    PLANNER: "https://alo186.com/hesaplama/guvenlik-alarmi-elektrik-kesintisi-hazirlik-plani/",
    SECTOR: "https://alo186.com/sektor-rehberi/apartman-otel-guvenlik-alarmi-kesinti-surekliligi/",
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
    sector = validate(SECTOR, CANONICALS[SECTOR])
    visible(guide, "Aktif güvenlik olayı alışveriş fırsatı değildir", "112", "bataryayı çıkarmayın", "tamper devresini köprülemeyin", "yeni ürün almayın", "Yerel alarm ile telefona bildirim", "6 Ağustos 2026")
    visible(planner, "Aktif olayda form ve ticaret kapalıdır", "Kişisel verisiz", "sunucuya gönderilmez", "kalıcı tarayıcı depolaması", "Mevcut hazırlık yeterli — yeni ürün almayın", "30/90/365", "Blob", "text/calendar", "professional-only")
    for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie", 'type="email"', 'type="tel"', "navigator.geolocation"):
        assert forbidden not in planner, forbidden
    visible(sector, "professional-only", "Amazon veya başka mağaza bağlantısı yoktur", "Batarya kapasite ve yaşam döngüsü", "Çift iletişim", "yeni ürün almayın", "112")
    for html in (guide, planner, sector):
        folded = html.casefold()
        assert "amazon.com.tr" not in folded
        assert 'class="merchant"' not in folded
        for forbidden in ("fiyat:", "stok:", "puan:", "garanti:"):
            assert forbidden not in folded
    decision = json.loads(read(DECISION))
    assert decision["version"] == 313
    assert decision["newMerchantLinks"] == 0
    assert decision["affiliatePolicy"]["consumerAffiliateClasses"] == 0
    assert decision["affiliatePolicy"]["activeSecurityEventCommerceClosed"] is True
    assert decision["affiliatePolicy"]["sharedCommercialSystemCommerceClosed"] is True
    assert decision["privacyPolicy"]["personalDataFields"] == 0
    assert decision["privacyPolicy"]["serverSubmission"] is False
    assert decision["privacyPolicy"]["persistentBrowserStorage"] is False
    assert decision["privacyPolicy"]["localIcsGeneration"] is True
    assert [x["days"] for x in decision["repeatVisitReasons"]] == [30, 90, 365]
    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 313
    assert len(overlay["routes"]) == 3
    assert overlay["updatedExistingRoutes"] == []
    root = ET.fromstring(read(DISCOVERY)); ns = {"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [x.text for x in root.findall("s:url/s:loc", ns)]
    assert len(urls) == 5 and len(urls) == len(set(urls))
    for canonical in CANONICALS.values():
        assert canonical in urls
    assert "Sitemap: https://alo186.com/sitemap-growth-v313.xml" in read(ROBOTS)
    print(json.dumps({"ok":True,"version":313,"newCanonicalRoutes":3,"newMerchantLinks":0,"consumerAffiliateClasses":0,"professionalOnlyClasses":len(decision["professionalOnlyClasses"]),"activeSecurityEventCommerceClosed":True,"personalDataFields":0,"repeatVisitDays":[30,90,365]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
