#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-garaj-kapisi-nasil-acilir/index.html"
TOOL = ROOT / "alo186/hesaplama/garaj-kapisi-elektrik-kesintisi-erisim-plani/index.html"
GUIDE = ROOT / "alo186/sektor-rehberi/apartman-otel-garaj-kapisi-kesinti-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/garage-door-outage-v302.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v302-garage-door-outage-access.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-garaj-kapisi-nasil-acilir/",
    TOOL: "https://alo186.com/hesaplama/garaj-kapisi-elektrik-kesintisi-erisim-plani/",
    GUIDE: "https://alo186.com/sektor-rehberi/apartman-otel-garaj-kapisi-kesinti-surekliligi/",
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
    guide = validate_page(GUIDE, ROUTES[GUIDE])

    assert_visible(article, (
        "kapıyı zorlamayın",
        "tam model kılavuzunda",
        "Kırık yay, gevşek/kopuk halat",
        "yeni ürün almayın",
        "Bu rehberde Amazon veya başka mağaza bağlantısı yoktur",
        "ALO186 kapı üreticisi, servis, güvenlik şirketi, belediye, itfaiye, EDAŞ veya kamu kurumu değildir",
        "/hesaplama/garaj-kapisi-elektrik-kesintisi-erisim-plani/",
        "/sektor-rehberi/apartman-otel-garaj-kapisi-kesinti-surekliligi/",
    ))

    assert_visible(tool, (
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "Mahsur kalma, yangın, sıkışma veya düşme riskinde aracı bırakın",
        "Mekanik hasar şüphesi — manuel ayırma yapmayın",
        "Mevcut plan yeterli — yeni ürün almayın",
        "30 gün: anahtar, aydınlatma ve iletişim",
        "90 gün: gözetimli kesinti provası",
        "180 gün: mekanik, sensör ve batarya",
        "Bu araçta Amazon veya başka mağaza bağlantısı yoktur",
        "professional-only",
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

    assert_visible(guide, (
        "Professional-only · sıfır tüketici affiliate",
        "Aktif sıkışma, yangın veya mekanik hasarda ticari dönüşüm yoktur",
        "Fail-safe ve fail-secure kavramlarını karıştırmayın",
        "Affiliate ürün kategorisi kararı",
        "Bu sayfada Amazon veya başka mağaza bağlantısı yoktur",
        "Doğrulanmamış fiyat, stok, puan, yorum, teslimat veya garanti bilgisi kullanılmaz",
        "Mevcut sistem görev testini geçiyor ve kullanım değişmediyse yeni ürün almayın",
        "ALO186 bağımsız bilgilendirme platformudur",
    ))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 302
    assert decision["decision"] == "professional-lead-only"
    assert decision["newMerchantLinks"] == 0
    policy = decision["conversionPolicy"]
    for key in (
        "activeEntrapmentFireOrSecurityCommerceClosed",
        "mechanicalDamageManualReleaseForbidden",
        "fixedDoorEquipmentConsumerAffiliateClosed",
        "batteryAndUpsConsumerAffiliateClosed",
        "springsCablesRailsConsumerAffiliateClosed",
        "noBuyOutcomeRequired",
        "personalDataCollectionForbidden",
        "accessCodeAddressPlateCollectionForbidden",
        "noPriceStockRatingWarrantyClaims",
        "affiliateDisclosureRequiredBeforeAnyFutureMerchantLink",
        "officialInstitutionImpressionForbidden",
        "professionalScopeForSharedCommercialAndEgressSystems",
        "universalManualReleaseInstructionsForbidden",
        "universalFailSafeFailSecureClaimsForbidden",
    ):
        assert policy[key] is True, key
    assert len(decision["professionalClasses"]) >= 12
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 180]

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 302
    assert overlay["name"] == "growth-v302-garage-door-outage-access"
    assert {item["canonicalPath"] for item in overlay["routes"]} == {
        "/haberler/elektrik-kesilince-garaj-kapisi-nasil-acilir/",
        "/hesaplama/garaj-kapisi-elektrik-kesintisi-erisim-plani/",
        "/sektor-rehberi/apartman-otel-garaj-kapisi-kesinti-surekliligi/",
    }

    print(json.dumps({
        "ok": True,
        "version": 302,
        "newRoutes": 3,
        "newMerchantLinks": 0,
        "professionalClasses": len(decision["professionalClasses"]),
        "repeatVisitDays": [30, 90, 180],
        "activeHazardCommerceClosed": True,
        "noBuyOutcomeRequired": True,
        "personalDataFields": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
