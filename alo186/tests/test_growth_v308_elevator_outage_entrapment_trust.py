#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-asansorde-kalinirsa-ne-yapilir/index.html"
TOOL = ROOT / "alo186/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-plani/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/apartman-otel-asansor-kesinti-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/elevator-outage-entrapment-continuity-v308.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v308-elevator-outage-entrapment-trust.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-asansorde-kalinirsa-ne-yapilir/",
    TOOL: "https://alo186.com/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-plani/",
    SECTOR: "https://alo186.com/sektor-rehberi/apartman-otel-asansor-kesinti-surekliligi/",
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
        "Kapıyı zorlamayın",
        "kendi başınıza çıkmaya çalışmayın",
        "alarm veya acil haberleşmeyi kullanın",
        "can güvenliği riskinde 112",
        "yılda en az bir periyodik kontrol",
        "yılda en az bir kez eğitim",
        "Amazon veya başka mağaza bağlantısı yoktur",
        "yeni ürün almayın",
        "/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-plani/",
        "/sektor-rehberi/apartman-otel-asansor-kesinti-surekliligi/",
    ))

    assert_visible(tool, (
        "Kişisel veri yok",
        "Şu anda bir kişi asansörde mahsursa bu formu doldurmayın",
        "Aktif olay — form ve ticaret kapalı",
        "Mevcut kurtarma hazırlığı yeterli — yeni ürün almayın",
        "Professional-only süreklilik incelemesi",
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
        "Asansör sürekliliği, yalnız batarya veya jeneratör eklemek değildir",
        "Süreklilik matrisi",
        "İki yönlü haberleşme",
        "Otomatik kurtarma",
        "Jeneratör ve ATS",
        "Affiliate kararı",
        "professional-only",
        "yeni ürün almayın",
        "30 gün",
        "90 gün",
        "365 gün",
    ))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 308
    assert decision["decision"] == "professional-only-no-consumer-affiliate"
    assert decision["newMerchantLinks"] == 0
    assert decision["consumerAffiliateClasses"] == []
    assert len(decision["professionalClasses"]) >= 12
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]
    for key, value in decision["conversionPolicy"].items():
        assert value is True, key

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 308
    assert overlay["name"] == "growth-v308-elevator-outage-entrapment-trust"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/haberler/elektrik-kesilince-asansorde-kalinirsa-ne-yapilir/",
        "/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-plani/",
        "/sektor-rehberi/apartman-otel-asansor-kesinti-surekliligi/",
    ]

    print(json.dumps({
        "ok": True,
        "version": 308,
        "newCanonicalRoutes": 3,
        "newMerchantLinks": 0,
        "professionalClasses": len(decision["professionalClasses"]),
        "repeatVisitDays": [30, 90, 365],
        "personalDataFields": 0,
        "unverifiedCommercialClaims": 0,
        "activeEntrapmentCommerceClosed": True,
        "selfRescueForbidden": True,
        "noBuyOutcome": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
