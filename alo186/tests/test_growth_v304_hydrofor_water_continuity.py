#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-hidrofor-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/index.html"
GUIDE = ROOT / "alo186/sektor-rehberi/apartman-otel-hidrofor-su-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/hydrofor-water-continuity-v304.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v304-hydrofor-water-continuity.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-hidrofor-calisir-mi/",
    TOOL: "https://alo186.com/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/",
    GUIDE: "https://alo186.com/sektor-rehberi/apartman-otel-hidrofor-su-surekliligi/",
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
        "depoda su bulunması tek başına",
        "Basınç tankını yedek su deposu sanmayın",
        "Kuru çalışma korumasını köprülemeyin",
        "Yangın pompasını kullanım suyu hidroforuyla karıştırmayın",
        "yeni ürün almayın",
        "Bu rehberde Amazon veya başka mağaza bağlantısı yoktur",
        "ALO186 su idaresi, belediye, itfaiye, EDAŞ, üretici, pompa servisi, tesisatçı veya kamu kurumu değildir",
        "/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/",
        "/sektor-rehberi/apartman-otel-hidrofor-su-surekliligi/",
    ))

    assert_visible(tool, (
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "Su-elektrik teması veya kritik hizmet kaybında aracı bırakın",
        "Kuru çalışma riski — resetlemeyin veya korumayı köprülemeyin",
        "Mevcut sistem yeterli — yeni ürün almayın",
        "30 gün: alarm, seviye ve basınç kaydı",
        "90 gün: kontrollü kesinti ve geri dönüş testi",
        "365 gün: pompa, pano, tank ve yedek enerji",
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
        "Aktif su-elektrik tehlikesi veya kritik hizmet kaybında ticari dönüşüm yoktur",
        "Depoyu gereğinden büyük seçmeyin",
        "Affiliate ürün kategorisi kararı",
        "Bu sayfada Amazon veya başka mağaza bağlantısı yoktur",
        "Doğrulanmamış fiyat, stok, puan, yorum, teslimat veya garanti bilgisi kullanılmaz",
        "Mevcut sistem görev testini geçiyor ve bina kullanımı değişmediyse",
        "yeni ürün almayın",
        "ALO186 bağımsız bilgilendirme platformudur",
    ))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 304
    assert decision["decision"] == "professional-lead-only"
    assert decision["newMerchantLinks"] == 0
    policy = decision["conversionPolicy"]
    for key in (
        "activeWaterElectricalOrFireHazardCommerceClosed",
        "dryRunProtectionBypassForbidden",
        "fixedPumpEquipmentConsumerAffiliateClosed",
        "generatorAtsAndFixedUpsConsumerAffiliateClosed",
        "fireAndCriticalWaterProfessionalOnly",
        "potableWaterHygieneProfessionalOnly",
        "noBuyOutcomeRequired",
        "personalDataCollectionForbidden",
        "addressTankLocationAndSerialCollectionForbidden",
        "noPriceStockRatingWarrantyClaims",
        "affiliateDisclosureRequiredBeforeAnyFutureMerchantLink",
        "officialInstitutionImpressionForbidden",
        "professionalScopeForSharedCommercialWellAndCriticalSystems",
        "universalRuntimePressureOrRestartClaimsForbidden",
        "pressureVesselAsLongDurationBackupClaimForbidden",
    ):
        assert policy[key] is True, key
    assert len(decision["professionalClasses"]) >= 12
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 304
    assert overlay["name"] == "growth-v304-hydrofor-water-continuity"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/sektor-rehberi/apartman-otel-hidrofor-su-surekliligi/"
    ]
    assert set(overlay["existingCanonicalRoutesValidated"]) == {
        "/haberler/elektrik-kesilince-hidrofor-calisir-mi/",
        "/hesaplama/hidrofor-elektrik-kesintisi-su-surekliligi-plani/",
    }

    print(json.dumps({
        "ok": True,
        "version": 304,
        "updatedCanonicalRoutes": 2,
        "newRoutes": 1,
        "newMerchantLinks": 0,
        "professionalClasses": len(decision["professionalClasses"]),
        "repeatVisitDays": [30, 90, 365],
        "activeHazardCommerceClosed": True,
        "noBuyOutcomeRequired": True,
        "personalDataFields": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
