#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-gidip-gelince-cihazlar-bozulur-mu/index.html"
TOOL = ROOT / "alo186/hesaplama/elektrik-gidip-gelince-cihaz-koruma-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/kesinti-sonrasi-elektronik-koruma-secimi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/power-return-device-protection-v305.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v305-power-return-device-protection.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-gidip-gelince-cihazlar-bozulur-mu/",
    TOOL: "https://alo186.com/hesaplama/elektrik-gidip-gelince-cihaz-koruma-plani/",
    SELECTOR: "https://alo186.com/amazon-elektrik-urunleri/kesinti-sonrasi-elektronik-koruma-secimi/",
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
    selector = validate_page(SELECTOR, ROUTES[SELECTOR])

    assert_visible(article, (
        "Bütün cihazlar için geçerli tek bir dakika değeri yoktur",
        "Transient darbe",
        "Nötr arızası",
        "on iş günü içinde",
        "ALO186 arıza kaydı almaz",
        "Mevcut ürün ve tesisat ihtiyacı karşılıyorsa yeni ürün almayın",
        "/hesaplama/elektrik-gidip-gelince-cihaz-koruma-plani/",
        "/amazon-elektrik-urunleri/kesinti-sonrasi-elektronik-koruma-secimi/",
    ))

    assert_visible(tool, (
        "Kişisel veri yok",
        "Tehlikede ticaret kapalı",
        "Mevcut koruma yeterli — yeni ürün almayın",
        "Professional-only değerlendirme",
        "30 gün",
        "90 gün",
        "365 gün",
        "Bütün cihazlar için geçerli tek bir bekleme süresi yoktur",
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

    assert_visible(selector, (
        "Amazon Türkiye satış ortaklığı açıklaması",
        "Mevcut güvenli ürün ihtiyacınızı karşılıyorsa yeni ürün almayın",
        "Bağlantılar kilitli",
        "Consumer affiliate dışında kalan professional-only sınıflar",
        "gerilim gözlem cihazını koruma cihazı",
        "Doğrulanmamış fiyat, stok, puan, yorum, teslimat veya garanti",
    ))
    assert selector.index("Amazon Türkiye satış ortaklığı açıklaması") < selector.index("data-merchant-url")
    assert selector.count('data-merchant-url="https://www.amazon.com.tr/') == 2
    assert 'href="https://www.amazon.com.tr/' not in selector
    assert selector.count('rel="sponsored noopener"') == 2
    assert "tag=alo186rehber-21" in selector

    decision = json.loads(read(DECISION))
    assert decision["version"] == 305
    assert decision["decision"] == "conditional-consumer-affiliate-plus-professional-lead"
    assert decision["newMerchantLinks"] == 2
    assert len(decision["consumerAffiliateClasses"]) == 2
    assert len(decision["professionalClasses"]) >= 10
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]
    for key, value in decision["conversionPolicy"].items():
        assert value is True, key

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 305
    assert overlay["name"] == "growth-v305-power-return-device-protection"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/haberler/elektrik-gidip-gelince-cihazlar-bozulur-mu/",
        "/hesaplama/elektrik-gidip-gelince-cihaz-koruma-plani/",
        "/amazon-elektrik-urunleri/kesinti-sonrasi-elektronik-koruma-secimi/",
    ]

    print(json.dumps({
        "ok": True,
        "version": 305,
        "newCanonicalRoutes": 3,
        "newMerchantLinks": 2,
        "merchantLinksLockedByDefault": True,
        "professionalClasses": len(decision["professionalClasses"]),
        "repeatVisitDays": [30, 90, 365],
        "personalDataFields": 0,
        "unverifiedCommercialClaims": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
