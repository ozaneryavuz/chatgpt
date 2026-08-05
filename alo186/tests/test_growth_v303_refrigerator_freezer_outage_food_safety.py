#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/index.html"
TOOL = ROOT / "alo186/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/refrigerator-freezer-outage-v303.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v303-refrigerator-freezer-outage-food-safety.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/",
    TOOL: "https://alo186.com/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/",
    SELECTOR: "https://alo186.com/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/",
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


def visible(html: str, *phrases: str) -> None:
    folded = html.casefold()
    for phrase in phrases:
        assert phrase.casefold() in folded, phrase


def main() -> None:
    article = validate_page(ARTICLE, ROUTES[ARTICLE])
    tool = validate_page(TOOL, ROUTES[TOOL])
    selector = validate_page(SELECTOR, ROUTES[SELECTOR])

    visible(
        article,
        "4 saat",
        "48 saat",
        "24 saat",
        "cihaz veya gıda garantisi değildir",
        "Şüpheli gıdanın tadına bakmayın",
        "Kesinti sürüyor",
        "Elektrik yeni geldi",
        "Elektrik normal, gelecek kesintiye hazırlık",
        "yeni ürün almayın",
        "Tarım ve Orman Bakanlığı",
        "Sağlık Bakanlığı",
        "/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/",
        "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/",
    )
    assert "amazon.com.tr" not in article.casefold()

    visible(
        tool,
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "4, 24 ve 48 saatlik resmî planlama bilgilerini",
        "Şüpheli gıdayı tatmayın",
        "Mevcut hazırlık yeterli — yeni ürün almayın",
        "30 günlük termometre kontrolü",
        "90 günlük kesinti tatbikatı",
        "180 günlük",
        "Bu sayfada Amazon veya başka mağaza bağlantısı yoktur",
    )
    for forbidden in (
        "fetch(",
        "XMLHttpRequest",
        "localStorage.",
        "sessionStorage.",
        "document.cookie",
        'type="email"',
        'type="tel"',
        'name="address"',
        'name="phone"',
    ):
        assert forbidden not in tool, forbidden

    visible(
        selector,
        "Amazon Türkiye satış ortaklığı",
        "bağlantılar başlangıçta kilitlidir",
        "Elektrik şu anda normal",
        "yalnız gelecekteki kesintiye hazırlanıyorum",
        "Mevcut termometre yeterli — yeni ürün almayın",
        "Analog cihaz içi termometre",
        "Dijital min/max termometre",
        "professional-only",
        "Restoran, otel, market",
        "İlaç, aşı, anne sütü",
        "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti",
        "ALO186 ürün satıcısı, üretici, servis, EDAŞ, gıda veya sağlık otoritesi değildir",
    )
    assert not re.search(r'href=["\']https?://[^"\']*amazon\.com\.tr', selector, re.I)
    assert selector.count('aria-disabled="true"') >= 2
    assert selector.count('rel="sponsored nofollow noopener"') == 2
    disclosure = selector.index("Bu sayfadaki açılabilen Amazon Türkiye bağlantıları satış ortaklığı bağlantısıdır")
    first_store = selector.index('id="analogLink"')
    assert disclosure < first_store

    decision = json.loads(read(DECISION))
    assert decision["version"] == 303
    assert decision["decision"] == "guarded-low-risk-affiliate-plus-professional-boundary"
    assert len(decision["consumerAffiliateClasses"]) == 2
    assert len(decision["professionalOnlyClasses"]) >= 10
    policy = decision["conversionPolicy"]
    for key in (
        "activeOutageCommerceClosed",
        "postOutageFoodDecisionBeforeCommerce",
        "futurePreparationOnlyUnlock",
        "homeUseOnly",
        "medicalAndCommercialAffiliateClosed",
        "realMeasurementGapRequired",
        "noBuyOutcomeRequired",
        "linksLockedByDefault",
        "affiliateDisclosureBeforeLinks",
        "relSponsoredNofollowNoopenerRequired",
        "noPriceStockSellerRatingReviewDeliveryWarrantyClaims",
        "personalDataCollectionForbidden",
        "officialInstitutionImpressionForbidden",
        "fourTwentyFourFortyEightHourGuaranteeClaimsForbidden",
        "tasteSmellAppearanceSafetyTestForbidden",
        "genericFridgeUpsGeneratorRecommendationForbidden",
    ):
        assert policy[key] is True, key
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 180]

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 303
    assert overlay["name"] == "growth-v303-refrigerator-freezer-outage-food-safety"
    assert {item["canonicalPath"] for item in overlay["routes"]} == {
        "/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/",
        "/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/",
        "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/",
    }

    print(json.dumps({
        "ok": True,
        "version": 303,
        "routes": 3,
        "consumerAffiliateClasses": 2,
        "professionalOnlyClasses": len(decision["professionalOnlyClasses"]),
        "linksLockedByDefault": True,
        "activeOutageCommerceClosed": True,
        "repeatVisitDays": [30, 90, 180],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
