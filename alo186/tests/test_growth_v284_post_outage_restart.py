#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-geldikten-sonra-cihazlar-nasil-guvenli-acilir/index.html"
TOOL = ROOT / "alo186/hesaplama/elektrik-geldikten-sonra-cihaz-yeniden-baslatma-plani/index.html"
CENTER = ROOT / "alo186/sektor-rehberi/elektrik-kesintisi-sonrasi-cihaz-koruma-karar-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v284-post-outage-restart.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/post-outage-appliance-restart-v284.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"

ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-geldikten-sonra-cihazlar-nasil-guvenli-acilir/",
    TOOL: "https://alo186.com/hesaplama/elektrik-geldikten-sonra-cihaz-yeniden-baslatma-plani/",
    CENTER: "https://alo186.com/sektor-rehberi/elektrik-kesintisi-sonrasi-cihaz-koruma-karar-merkezi/",
}


def text(path: Path) -> str:
    assert path.is_file(), f"Eksik dosya: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def json_ld(source: str) -> list[dict]:
    blocks = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', source, flags=re.I | re.S)
    assert blocks, "JSON-LD eksik"
    return [json.loads(block) for block in blocks]


def assert_canonical(path: Path, canonical: str) -> None:
    source = text(path)
    found = re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', source, flags=re.I)
    assert found == [canonical], (path, found)
    assert "https://www.alo186.com" not in source
    json_ld(source)


def assert_no_unverified_commerce(source: str) -> None:
    for token in ('"@type":"Offer"', '"@type":"AggregateRating"', '"@type":"Review"', '"price"', '"priceCurrency"', '"availability"', '"warranty"'):
        assert token not in source, token


def main() -> None:
    for path, canonical in ROUTES.items():
        assert_canonical(path, canonical)

    article = text(ARTICLE)
    for required in (
        "Enerji geri geldiğinde önce tehlikeyi dışlayın",
        "Koruma yeniden açıyorsa zorlamayın",
        "ek ürün almanız gerekmez",
        "ALO186 EDAŞ, servis, üretici veya kamu kurumu değildir",
        "/hesaplama/elektrik-geldikten-sonra-cihaz-yeniden-baslatma-plani/",
        "/sektor-rehberi/elektrik-kesintisi-sonrasi-cihaz-koruma-karar-merkezi/",
        "Samsung UK",
        "Siemens Ev Aletleri",
    ):
        assert required in article, required
    assert_no_unverified_commerce(article)

    tool = text(TOOL)
    for required in (
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "Normal çalışma doğrulandı — yeni ürün almayın",
        "Koruma cihazını tekrar tekrar kaldırmayın",
        "Sabit yüksek güçlü cihaz profesyonel kapsamda",
        "30 günlük fiş ve kablo kontrolü",
        "90 günlük kontrollü kesinti provası",
        "Yıllık profesyonel kontrol",
    ):
        assert required in tool, required
    for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", 'type="email"', 'type="tel"'):
        assert forbidden not in tool, forbidden
    assert "amazon.com.tr" not in tool.lower()
    assert_no_unverified_commerce(tool)

    center = text(CENTER)
    for required in (
        "Sıfır doğrudan mağaza bağlantısı",
        "Arızayı ürünle değil, doğru çözüm kanalıyla eşleştirin",
        "Mevcut cihaz normal çalışıyor",
        "Yetkili destek",
        "Elektrikçi",
        "Resmî kesinti kanalı",
        "Ücretsiz uygunluk testini aç",
        "Bu karar merkezinde doğrudan Amazon veya başka mağaza bağlantısı yoktur",
        "Amazon Türkiye satış ortaklığı bağlantısıdır",
    ):
        assert required in center, required
    assert "https://www.amazon.com.tr" not in center
    assert_no_unverified_commerce(center)

    overlay = json.loads(text(OVERLAY))
    assert overlay["version"] == 284
    assert overlay["name"] == "growth-v284-post-outage-restart"
    assert {route["canonicalPath"] for route in overlay["routes"]} == {
        "/haberler/elektrik-geldikten-sonra-cihazlar-nasil-guvenli-acilir/",
        "/hesaplama/elektrik-geldikten-sonra-cihaz-yeniden-baslatma-plani/",
        "/sektor-rehberi/elektrik-kesintisi-sonrasi-cihaz-koruma-karar-merkezi/",
    }

    decision = json.loads(text(DECISION))
    assert decision["decision"] == "decision-first-no-new-affiliate-route"
    assert decision["conversionPolicy"]["newMerchantLinks"] == 0
    assert decision["conversionPolicy"]["reuseExistingGatedRoutesOnly"] is True
    assert decision["conversionPolicy"]["activeHazardCommerceClosed"] is True
    assert decision["conversionPolicy"]["repeatedTripCommerceClosed"] is True
    assert decision["conversionPolicy"]["noBuyOutcomeRequired"] is True
    assert decision["conversionPolicy"]["noPriceStockRatingWarrantyClaims"] is True
    assert len(decision["conversionPoints"]) == 5
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    policy = json.loads(text(POLICY))
    assert policy["legacyMigrationQueue"] == []
    assert "modem-ont-mini-ups-yedekleme" in policy["governedAffiliateRoutePatterns"]
    assert "post-outage-appliance-restart" in policy["reviewOnlyRoutePatterns"]

    print(json.dumps({
        "ok": True,
        "version": 284,
        "routes": 3,
        "newMerchantLinks": 0,
        "conversionPoints": 5,
        "unverifiedCommercialFields": 0,
        "repeatVisitDays": [30, 90, 365],
        "legacyMigrationQueue": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
