#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-camasir-bulasik-makinesi-yarida-kalirsa-ne-yapilir/index.html"
TOOL = ROOT / "alo186/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/otel-camasirhane-endustriyel-mutfak-kesinti-surekliligi/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/washer-dishwasher-outage-continuity-v307.json"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v307-washer-dishwasher-outage-trust.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-camasir-bulasik-makinesi-yarida-kalirsa-ne-yapilir/",
    TOOL: "https://alo186.com/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/",
    SECTOR: "https://alo186.com/sektor-rehberi/otel-camasirhane-endustriyel-mutfak-kesinti-surekliligi/",
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
        "Elektrik kesildiğinde program durur; elektrik geldiğinde ne olacağı tam modele bağlıdır",
        "Kapı kilitliyse zorlamayın",
        "sigortayı tekrar tekrar kaldırmayın",
        "mevcut plan yeterlidir — yeni ürün almayın",
        "Neden consumer affiliate yok?",
        "Amazon veya başka mağaza bağlantısı yoktur",
        "/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/",
        "/sektor-rehberi/otel-camasirhane-endustriyel-mutfak-kesinti-surekliligi/",
    ))

    assert_visible(tool, (
        "Kişisel veri yok",
        "Aktif tehlikede test ve ticaret kapalı",
        "Mevcut yeniden başlatma planı yeterli — yeni ürün almayın",
        "Professional-only değerlendirme",
        "Kapıyı zorlamayın",
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
        "Süreklilik, yalnız jeneratör gücü seçmek değildir",
        "Süreklilik matrisi",
        "Jeneratör ve ATS",
        "İşletme prosedürü",
        "Affiliate kararı",
        "professional-only",
        "yeni ürün almayın",
        "30 gün",
        "90 gün",
        "365 gün",
    ))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 307
    assert decision["decision"] == "professional-only-no-new-consumer-affiliate"
    assert decision["newMerchantLinks"] == 0
    assert decision["consumerAffiliateClasses"] == []
    assert len(decision["professionalClasses"]) >= 12
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]
    for key, value in decision["conversionPolicy"].items():
        assert value is True, key

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 307
    assert overlay["name"] == "growth-v307-washer-dishwasher-outage-trust"
    assert [item["canonicalPath"] for item in overlay["routes"]] == [
        "/haberler/elektrik-kesilince-camasir-bulasik-makinesi-yarida-kalirsa-ne-yapilir/",
        "/hesaplama/camasir-bulasik-makinesi-elektrik-kesintisi-guvenli-yeniden-baslatma-plani/",
        "/sektor-rehberi/otel-camasirhane-endustriyel-mutfak-kesinti-surekliligi/",
    ]

    print(json.dumps({
        "ok": True,
        "version": 307,
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
