#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/elektrik-kesilince-kombi-calisir-mi/index.html"
PLANNER = ROOT / "alo186/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/apartman-otel-kazan-kombi-kesinti-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/boiler-outage-trust-v310.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v310-boiler-outage-trust.json"
DISCOVERY = ROOT / "alo186/sitemap-growth-v310.xml"

CANONICALS = {
    GUIDE: "https://alo186.com/haberler/elektrik-kesilince-kombi-calisir-mi/",
    PLANNER: "https://alo186.com/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/",
    SECTOR: "https://alo186.com/sektor-rehberi/apartman-otel-kazan-kombi-kesinti-surekliligi/",
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
        "amazon.com.tr",
        "data-merchant-url",
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
    sector = validate_page(SECTOR, CANONICALS[SECTOR])

    assert_visible(guide, (
        "187 Doğal Gaz Acil",
        "186",
        "112",
        "Aktif kesintide alışveriş",
        "professional-only",
        "Amazon veya başka mağaza bağlantısı yoktur",
        "yeni ürün almayın",
        "30 gün",
        "90 gün",
        "365 gün",
        "/sektor-rehberi/apartman-otel-kazan-kombi-kesinti-surekliligi/",
    ))

    assert_visible(planner, (
        "Aktif kesintide ticaret ve yeniden başlatma kapalı",
        "Mevcut sistem yeterli — yeni ürün almayın",
        "Kişisel veri",
        "sunucuya gönderilmez",
        "kalıcı tarayıcı depolaması",
        "Blob",
        "text/calendar",
        "30 gün",
        "90 gün",
        "365 gün",
        "/sektor-rehberi/apartman-otel-kazan-kombi-kesinti-surekliligi/",
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

    assert_visible(sector, (
        "Dokuz katman",
        "Professional-only",
        "Bu sayfada Amazon veya başka mağaza bağlantısı yoktur",
        "yeni ürün almayın",
        "30 gün",
        "90 gün",
        "365 gün",
        "187",
        "186",
        "112",
    ))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 310
    assert decision["decision"] == "professional-only-no-consumer-affiliate"
    assert decision["newMerchantLinks"] == 0
    assert decision["affiliatePolicy"]["consumerAffiliateClasses"] == 0
    assert decision["affiliatePolicy"]["merchantLinks"] == 0
    assert decision["affiliatePolicy"]["activeOutageCommerceClosed"] is True
    assert decision["affiliatePolicy"]["gasOrElectricalDangerCommerceClosed"] is True
    assert decision["affiliatePolicy"]["noBuyOutcomeRequired"] is True
    assert decision["privacyPolicy"]["personalDataFields"] == 0
    assert decision["privacyPolicy"]["serverSubmission"] is False
    assert decision["privacyPolicy"]["persistentBrowserStorage"] is False
    assert decision["privacyPolicy"]["localIcsGeneration"] is True
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 310
    assert overlay["name"] == "growth-v310-boiler-outage-trust"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/sektor-rehberi/apartman-otel-kazan-kombi-kesinti-surekliligi/",
    ]
    assert [item["canonicalPath"] for item in overlay["updatedExistingRoutes"]] == [
        "/haberler/elektrik-kesilince-kombi-calisir-mi/",
        "/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/",
    ]

    root = ET.fromstring(read(DISCOVERY))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in root.findall("s:url/s:loc", ns)]
    assert len(urls) == 4, urls
    assert len(urls) == len(set(urls)), "duplicate discovery inventory URL"
    assert all(url and url.startswith("https://alo186.com/") for url in urls)
    assert all("www.alo186.com" not in url for url in urls)
    for canonical in CANONICALS.values():
        assert canonical in urls
    assert "https://alo186.com/amazon-elektrik-urunleri/kombi-ups-yedek-guc-secimi/" in urls

    print(json.dumps({
        "ok": True,
        "version": 310,
        "updatedCanonicalRoutes": 2,
        "newCanonicalRoutes": 1,
        "newMerchantLinks": 0,
        "consumerAffiliateClasses": 0,
        "professionalOnlyClasses": len(decision["professionalOnlyClasses"]),
        "personalDataFields": 0,
        "activeOutageCommerceClosed": True,
        "noBuyOutcome": True,
        "localIcsGeneration": True,
        "repeatVisitDays": [30, 90, 365],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
