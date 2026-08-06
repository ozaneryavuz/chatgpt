#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/elektrik-kesilince-klima-calisir-mi/index.html"
PLANNER = ROOT / "alo186/hesaplama/klima-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/index.html"
AFFILIATE = ROOT / "alo186/amazon-elektrik-urunleri/yaz-kesintisi-serinleme-olcum-secimi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/air-conditioner-outage-trust-v311.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v311-air-conditioner-outage-trust.json"
DISCOVERY = ROOT / "alo186/sitemap-growth-v311.xml"
ROBOTS = ROOT / "alo186/robots.txt"

CANONICALS = {
    GUIDE: "https://alo186.com/haberler/elektrik-kesilince-klima-calisir-mi/",
    PLANNER: "https://alo186.com/hesaplama/klima-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/",
    AFFILIATE: "https://alo186.com/amazon-elektrik-urunleri/yaz-kesintisi-serinleme-olcum-secimi/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def validate_page(path: Path, canonical: str) -> str:
    html = read(path)
    canonicals = re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I)
    assert canonicals == [canonical], (path, canonicals)
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.I | re.S)
    assert blocks, path
    for block in blocks:
        json.loads(block)
    folded = html.casefold()
    for forbidden in (
        "https://www.alo186.com",
        '"@type":"aggregaterating"',
        '"@type":"review"',
        '"availability":',
        '"warranty":',
        '"delivery":',
    ):
        assert forbidden.casefold() not in folded, (path, forbidden)
    return html


def assert_visible(html: str, phrases: tuple[str, ...]) -> None:
    folded = html.casefold()
    for phrase in phrases:
        assert phrase.casefold() in folded, phrase


def main() -> None:
    guide = validate_page(GUIDE, CANONICALS[GUIDE])
    planner = validate_page(PLANNER, CANONICALS[PLANNER])
    affiliate = validate_page(AFFILIATE, CANONICALS[AFFILIATE])

    assert_visible(guide, (
        "Aktif kesintide, kararsız gerilimde veya sıcaklığa bağlı sağlık riskinde ticaret kapalıdır",
        "Amazon veya başka mağaza bağlantısı yoktur",
        "üç dakika",
        "bütün marka ve modeller için genel garanti değildir",
        "professional-only",
        "yeni ürün almayın",
        "112",
        "186",
        "30 gün",
        "90 gün",
        "365 gün",
        "https://www.daikin.eu/",
        "https://www.samsung.com/",
        "https://www.cdc.gov/",
    ))
    assert "amazon.com.tr" not in guide.casefold()
    assert "data-merchant-url" not in guide.casefold()

    assert_visible(planner, (
        "Aktif kesintide ticaret ve yeniden başlatma kapalıdır",
        "Mevcut yeniden başlatma planı yeterli — yeni ürün almayın",
        "Kişisel verisiz",
        "sunucuya gönderilmez",
        "kalıcı tarayıcı depolaması",
        "Blob",
        "text/calendar",
        "professional-only",
        "30/90/365",
    ))
    for forbidden in (
        "fetch(",
        "XMLHttpRequest",
        "localStorage.",
        "sessionStorage.",
        "document.cookie",
        'type="email"',
        'type="tel"',
        'type="text"',
        "navigator.geolocation",
    ):
        assert forbidden not in planner, forbidden
    assert "amazon.com.tr" not in planner.casefold()

    assert_visible(affiliate, (
        "Amazon Türkiye satış ortaklığı açıklaması",
        "nitelikli satın alımlardan komisyon",
        "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi yayımlanmaz",
        "Mevcut güvenli termometre veya fan ihtiyacınızı karşılıyorsa yeni ürün almayın",
        "yaklaşık 32 °C",
        "professional-only",
        "oda termometresi / nem ölçer",
        "Şarjlı / USB masa fanı",
    ))
    merchant_links = re.findall(r'<a\s+class="merchant"([^>]*)>', affiliate, re.I)
    assert len(merchant_links) == 2, merchant_links
    for attrs in merchant_links:
        assert "data-merchant-url=" in attrs
        assert 'rel="sponsored noopener"' in attrs
        assert " href=" not in attrs.lower(), attrs
        assert 'aria-disabled="true"' in attrs
    assert affiliate.count("amazon.com.tr") == 2
    assert affiliate.count("tag=alo186rehber-21") == 2
    assert affiliate.count('class="gate"') == 7

    decision = json.loads(read(DECISION))
    assert decision["version"] == 311
    assert decision["decision"] == "gated-low-risk-consumer-affiliate-plus-professional-only"
    assert decision["newMerchantLinks"] == 2
    assert decision["affiliatePolicy"]["consumerAffiliateClasses"] == 2
    assert decision["affiliatePolicy"]["merchantLinks"] == 2
    assert decision["affiliatePolicy"]["activeOutageCommerceClosed"] is True
    assert decision["affiliatePolicy"]["unstablePowerCommerceClosed"] is True
    assert decision["affiliatePolicy"]["heatHealthRiskCommerceClosed"] is True
    assert decision["affiliatePolicy"]["noBuyOutcomeRequired"] is True
    assert decision["privacyPolicy"]["personalDataFields"] == 0
    assert decision["privacyPolicy"]["serverSubmission"] is False
    assert decision["privacyPolicy"]["persistentBrowserStorage"] is False
    assert decision["privacyPolicy"]["localIcsGeneration"] is True
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 311
    assert overlay["name"] == "growth-v311-air-conditioner-outage-trust"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/hesaplama/klima-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/",
        "/amazon-elektrik-urunleri/yaz-kesintisi-serinleme-olcum-secimi/",
    ]
    assert [item["canonicalPath"] for item in overlay["updatedExistingRoutes"]] == [
        "/haberler/elektrik-kesilince-klima-calisir-mi/",
    ]

    root = ET.fromstring(read(DISCOVERY))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in root.findall("s:url/s:loc", ns)]
    assert len(urls) == 5, urls
    assert len(urls) == len(set(urls)), "duplicate discovery inventory URL"
    assert all(url and url.startswith("https://alo186.com/") for url in urls)
    assert all("www.alo186.com" not in url for url in urls)
    for canonical in CANONICALS.values():
        assert canonical in urls

    robots = read(ROBOTS)
    assert "Sitemap: https://alo186.com/sitemap-growth-v311.xml" in robots

    print(json.dumps({
        "ok": True,
        "version": 311,
        "updatedCanonicalRoutes": 1,
        "newCanonicalRoutes": 2,
        "newMerchantLinks": 2,
        "consumerAffiliateClasses": 2,
        "professionalOnlyClasses": len(decision["professionalOnlyClasses"]),
        "personalDataFields": 0,
        "activeOutageCommerceClosed": True,
        "unstablePowerCommerceClosed": True,
        "heatHealthRiskCommerceClosed": True,
        "noBuyOutcome": True,
        "localIcsGeneration": True,
        "repeatVisitDays": [30, 90, 365],
        "discoveryUrls": len(urls),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
