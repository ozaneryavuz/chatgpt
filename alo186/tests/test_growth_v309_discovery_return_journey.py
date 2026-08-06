#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HUB = ROOT / "alo186/kesinti-cihaz-surekliligi-karar-merkezi/index.html"
CALENDAR = ROOT / "alo186/hesaplama/kesinti-hazirlik-takvimi/index.html"
SITEMAP = ROOT / "alo186/sitemap-growth-v309.xml"
ROBOTS = ROOT / "alo186/robots.txt"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/discovery-return-journey-v309.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v309-discovery-return-journey.json"

CANONICALS = {
    HUB: "https://alo186.com/kesinti-cihaz-surekliligi-karar-merkezi/",
    CALENDAR: "https://alo186.com/hesaplama/kesinti-hazirlik-takvimi/",
}

REQUIRED_JOURNEY_PATHS = {
    "/hesaplama/fiber-internet-modem-ont-mini-ups-calisma-suresi/",
    "/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-sureklilik-plani/",
    "/hesaplama/nas-ups-guvenli-kapatma-calisma-suresi/",
    "/hesaplama/alarm-paneli-aku-bekleme-suresi/",
    "/hesaplama/cpap-elektrik-kesintisi-batarya-calisma-suresi/",
    "/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/",
    "/hesaplama/elektrik-kesintisi-insulin-ilac-soguk-zincir-karar-destegi/",
    "/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/",
    "/hesaplama/gunes-paneli-elektrik-kesintisi-yedekleme-uygunluk-kontrolu/",
    "/hesaplama/garaj-kapisi-elektrik-kesintisi-erisim-plani/",
    "/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/",
    "/hesaplama/elektrik-gidip-gelince-cihaz-koruma-plani/",
    "/hesaplama/isi-pompasi-elektrik-kesintisi-donma-sureklilik-plani/",
    "/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/",
    "/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-plani/",
    "/hesaplama/mobil-hotspot-yedek-internet-veri-gb-batarya-sure-hesabi/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def validate_page(path: Path, canonical: str) -> str:
    html = read(path)
    assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I) == [canonical]
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
    hub = validate_page(HUB, CANONICALS[HUB])
    calendar = validate_page(CALENDAR, CANONICALS[CALENDAR])

    assert_visible(hub, (
        "16 yolculuk",
        "Aktif kesintide alışveriş yolu kapalı",
        "Mevcut sistem yeterli — yeni ürün almayın",
        "Bağımsızlık ve ticari açıklama",
        "Professional-only",
        "Affiliate açıklaması mağaza bağlantısından önce",
        "30 gün",
        "90 gün",
        "365 gün",
        "/hesaplama/kesinti-hazirlik-takvimi/",
    ))
    hrefs = set(re.findall(r'<a\s+[^>]*href="([^"]+)"', hub, re.I))
    assert REQUIRED_JOURNEY_PATHS.issubset(hrefs), sorted(REQUIRED_JOURNEY_PATHS - hrefs)
    assert len(REQUIRED_JOURNEY_PATHS) == 16

    assert_visible(calendar, (
        "Kişisel veri yok",
        "yerel ICS",
        "mağaza bağlantısı yok",
        "yeni ürün almayın",
        "Aktif tehlike — plan ve ticaret kapalı",
        "30 gün",
        "90 gün",
        "365 gün",
        "Blob",
        "text/calendar",
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
        assert forbidden not in calendar, forbidden

    root = ET.fromstring(read(SITEMAP))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in root.findall("s:url/s:loc", ns)]
    assert len(urls) == 38, len(urls)
    assert len(urls) == len(set(urls)), "duplicate sitemap URL"
    assert all(url and url.startswith("https://alo186.com/") for url in urls)
    assert all("www.alo186.com" not in url for url in urls)
    assert CANONICALS[HUB] in urls
    assert CANONICALS[CALENDAR] in urls
    for path in REQUIRED_JOURNEY_PATHS:
        assert "https://alo186.com" + path in urls, path

    robots = read(ROBOTS)
    assert "Allow: /sektor-rehberi/" in robots
    assert "Sitemap: https://alo186.com/sitemap-growth-v309.xml" in robots

    decision = json.loads(read(DECISION))
    assert decision["version"] == 309
    assert decision["decision"] == "discovery-first-no-new-consumer-affiliate"
    assert decision["newMerchantLinks"] == 0
    assert decision["discoveryPolicy"]["growthSitemapUrlCount"] == 38
    assert decision["affiliatePolicy"]["directMerchantLinksOnHub"] is False
    assert decision["affiliatePolicy"]["directMerchantLinksOnCalendar"] is False
    assert decision["affiliatePolicy"]["activeOutageCommerceClosed"] is True
    assert decision["affiliatePolicy"]["noBuyOutcomeRequired"] is True
    assert decision["privacyPolicy"]["personalDataFields"] == 0
    assert decision["privacyPolicy"]["serverSubmission"] is False
    assert decision["privacyPolicy"]["persistentBrowserStorage"] is False
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 309
    assert overlay["name"] == "growth-v309-discovery-return-journey"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/hesaplama/kesinti-hazirlik-takvimi/",
    ]
    assert [item["canonicalPath"] for item in overlay["updatedExistingRoutes"]] == [
        "/kesinti-cihaz-surekliligi-karar-merkezi/",
    ]
    assert "alo186/sitemap-growth-v309.xml" in overlay["staticAssets"]
    assert "alo186/robots.txt" in overlay["staticAssets"]

    print(json.dumps({
        "ok": True,
        "version": 309,
        "updatedCanonicalRoutes": 1,
        "newCanonicalRoutes": 1,
        "staticJourneyLinks": len(REQUIRED_JOURNEY_PATHS),
        "growthSitemapUrls": len(urls),
        "newMerchantLinks": 0,
        "personalDataFields": 0,
        "activeOutageCommerceClosed": True,
        "noBuyOutcome": True,
        "repeatVisitDays": [30, 90, 365],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
