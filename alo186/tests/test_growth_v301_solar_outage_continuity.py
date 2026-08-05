#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-gunes-paneli-elektrik-verir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/gunes-paneli-elektrik-kesintisi-yedekleme-uygunluk-kontrolu/index.html"
GUIDE = ROOT / "alo186/sektor-rehberi/ev-isletme-ges-kesinti-yedek-guc-surekliligi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v301-solar-outage-continuity.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/solar-outage-v301.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-gunes-paneli-elektrik-verir-mi/",
    TOOL: "https://alo186.com/hesaplama/gunes-paneli-elektrik-kesintisi-yedekleme-uygunluk-kontrolu/",
    GUIDE: "https://alo186.com/sektor-rehberi/ev-isletme-ges-kesinti-yedek-guc-surekliligi/",
}


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def check_page(path: Path, canonical: str) -> str:
    html = read(path)
    assert re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I) == [canonical]
    blocks = re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.I | re.S)
    assert blocks, path
    for block in blocks:
        json.loads(block)
    for forbidden in (
        "https://www.alo186.com",
        '"@type":"Product"',
        '"@type":"Offer"',
        '"@type":"AggregateRating"',
        '"@type":"Review"',
        '"price":',
        '"priceCurrency":',
        '"availability":',
        '"warranty":',
        '"delivery":',
    ):
        assert forbidden not in html, (path, forbidden)
    return html


def main() -> None:
    article = check_page(ARTICLE, ROUTES[ARTICLE])
    tool = check_page(TOOL, ROUTES[TOOL])
    guide = check_page(GUIDE, ROUTES[GUIDE])

    for required in (
        "standart şebeke bağlantılı GES, elektrik kesintisinde çoğunlukla enerji vermez",
        "anti-adalanma",
        "yalnız “batarya var” demek yeterli değildir",
        "Backup sistemi UPS ile aynı olmayabilir",
        "yeni ürün almayın",
        "bu kümede tüketici ürünü yönlendirmesi yoktur",
        "Bu rehberde Amazon veya başka mağaza bağlantısı yoktur",
        "/hesaplama/gunes-paneli-elektrik-kesintisi-yedekleme-uygunluk-kontrolu/",
        "/sektor-rehberi/ev-isletme-ges-kesinti-yedek-guc-surekliligi/",
        "ALO186 bağımsız bilgilendirme platformudur",
    ):
        assert required in article, required
    assert "amazon.com.tr" not in article.casefold()

    for required in (
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "Aktif elektrik, yangın veya batarya tehlikesinde aracı kullanmayı bırakın",
        "Mevcut sistem yeterli — yeni ürün almayın",
        "Professional-only değerlendirme",
        "Batarya tek başına yeterli kanıt değil",
        "30 gün: olay ve izleme kaydı",
        "90 gün: kontrollü görev testi",
        "365 gün: profesyonel inceleme",
        "Bu araçta Amazon veya başka mağaza bağlantısı yoktur",
        "Yanıtlar sunucuya gönderilmez",
    ):
        assert required in tool, required
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
    assert "amazon.com.tr" not in tool.casefold()

    for required in (
        "Professional-only · sıfır tüketici affiliate",
        "Aktif arıza veya hasarlı bataryada ticari dönüşüm yoktur",
        "Süreklilik matrisi",
        "Tek hata noktasını bulun",
        "Gerçek kabul testi",
        "Affiliate ürün kategorisi kararı",
        "Dönüşüm noktaları",
        "Bu sayfada Amazon veya başka mağaza bağlantısı yoktur",
        "Doğrulanmamış fiyat, stok, puan, yorum, teslimat veya garanti bilgisi kullanılmaz",
        "ALO186 bağımsız bilgilendirme platformudur",
    ):
        assert required in guide, required
    assert "amazon.com.tr" not in guide.casefold()

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 301
    assert overlay["name"] == "growth-v301-solar-outage-continuity"
    assert len(overlay["routes"]) == 3
    assert {item["canonicalPath"] for item in overlay["routes"]} == {
        "/haberler/elektrik-kesilince-gunes-paneli-elektrik-verir-mi/",
        "/hesaplama/gunes-paneli-elektrik-kesintisi-yedekleme-uygunluk-kontrolu/",
        "/sektor-rehberi/ev-isletme-ges-kesinti-yedek-guc-surekliligi/",
    }

    decision = json.loads(read(DECISION))
    assert decision["version"] == 301
    assert decision["decision"] == "professional-lead-only"
    assert decision["newMerchantLinks"] == 0
    required_policy = (
        "activeElectricalHazardCommerceClosed",
        "batteryFireOrDamageCommerceClosed",
        "fixedSolarEquipmentConsumerAffiliateClosed",
        "batteryAndHybridInverterConsumerAffiliateClosed",
        "generatorAndTransferConsumerAffiliateClosed",
        "noBuyOutcomeRequired",
        "personalDataCollectionForbidden",
        "productionDataCollectionForbidden",
        "noPriceStockRatingWarrantyClaims",
        "affiliateDisclosureRequiredBeforeAnyFutureMerchantLink",
        "officialInstitutionImpressionForbidden",
        "professionalScopeForComplexSystems",
        "batteryPresenceAloneCannotClaimBackup",
        "antiIslandingBypassInstructionsForbidden",
        "universalBackupDurationClaimsForbidden",
    )
    for key in required_policy:
        assert decision["conversionPolicy"][key] is True, key
    assert len(decision["professionalClasses"]) >= 12
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    central_policy = json.loads(read(POLICY))
    patterns = set(central_policy["professionalLeadOnlyRoutePatterns"])
    for pattern in (
        "gunes-paneli-kesinti",
        "ges-kesinti-yedekleme",
        "ges-yedek-guc",
        "hybrid-inverter",
        "batarya-depolama",
        "backup-interface",
        "ada-isletmesi",
        "kritik-yuk-panosu",
    ):
        assert pattern in patterns, pattern

    print(json.dumps({
        "ok": True,
        "version": 301,
        "newRoutes": 3,
        "newMerchantLinks": 0,
        "professionalClasses": len(decision["professionalClasses"]),
        "repeatVisitDays": [30, 90, 365],
        "activeHazardCommerceClosed": True,
        "noBuyOutcomeRequired": True,
        "personalDataFields": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
