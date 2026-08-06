#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-isi-pompasi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/isi-pompasi-elektrik-kesintisi-donma-sureklilik-plani/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/villa-otel-isi-pompasi-kesinti-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/heat-pump-outage-continuity-v306.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v306-heat-pump-outage-continuity.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-isi-pompasi-calisir-mi/",
    TOOL: "https://alo186.com/hesaplama/isi-pompasi-elektrik-kesintisi-donma-sureklilik-plani/",
    SECTOR: "https://alo186.com/sektor-rehberi/villa-otel-isi-pompasi-kesinti-surekliligi/",
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
        '"@type":"offer"',
        '"@type":"aggregaterating"',
        '"@type":"review"',
        '"price":',
        '"pricecurrency":',
        '"availability":',
        '"warranty":',
        '"delivery":',
        "amazon.com.tr",
        "data-merchant-url",
    ):
        assert forbidden.casefold() not in folded, (path, forbidden)
    return html


def assert_visible(html: str, phrases: tuple[str, ...]) -> None:
    folded = html.casefold()
    for phrase in phrases:
        assert phrase.casefold() in folded, phrase


def main() -> None:
    article = validate_page(ARTICLE, ROUTES[ARTICLE])
    tool = validate_page(TOOL, ROUTES[TOOL])
    sector = validate_page(SECTOR, ROUTES[SECTOR])

    assert_visible(article, (
        "Belgeli bir yedekleme sistemi yoksa elektrik kesintisinde ısı pompası durur",
        "hidronik donma riski",
        "Hava-su monoblok",
        "korumayı köprülemeyin",
        "mevcut plan yeterlidir — yeni ürün almayın",
        "Neden consumer affiliate yok?",
        "Amazon veya başka mağaza bağlantısı yoktur",
        "/hesaplama/isi-pompasi-elektrik-kesintisi-donma-sureklilik-plani/",
        "/sektor-rehberi/villa-otel-isi-pompasi-kesinti-surekliligi/",
    ))

    assert_visible(tool, (
        "Kişisel veri yok",
        "Aktif tehlikede ticaret kapalı",
        "Mevcut plan yeterli — yeni ürün almayın",
        "Professional-only değerlendirme",
        "30 gün",
        "90 gün",
        "365 gün",
        "Amazon veya başka mağaza bağlantısı yoktur",
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
    ):
        assert forbidden not in tool, forbidden

    assert_visible(sector, (
        "Isı pompası sürekliliği, yalnız jeneratör gücü seçmek değildir",
        "Süreklilik matrisi",
        "Jeneratör ve ATS",
        "Yeniden başlatma",
        "Affiliate kararı",
        "professional-only",
        "yeni ürün almayın",
        "30 gün",
        "90 gün",
        "365 gün",
    ))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 306
    assert decision["decision"] == "professional-only-no-consumer-affiliate"
    assert decision["newMerchantLinks"] == 0
    assert decision["consumerAffiliateClasses"] == []
    assert len(decision["professionalClasses"]) >= 12
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]
    for key, value in decision["conversionPolicy"].items():
        assert value is True, key

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 306
    assert overlay["name"] == "growth-v306-heat-pump-outage-continuity"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/haberler/elektrik-kesilince-isi-pompasi-calisir-mi/",
        "/hesaplama/isi-pompasi-elektrik-kesintisi-donma-sureklilik-plani/",
        "/sektor-rehberi/villa-otel-isi-pompasi-kesinti-surekliligi/",
    ]

    print(json.dumps({
        "ok": True,
        "version": 306,
        "newCanonicalRoutes": 3,
        "newMerchantLinks": 0,
        "professionalClasses": len(decision["professionalClasses"]),
        "repeatVisitDays": [30, 90, 365],
        "personalDataFields": 0,
        "unverifiedCommercialClaims": 0,
        "noBuyOutcome": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
