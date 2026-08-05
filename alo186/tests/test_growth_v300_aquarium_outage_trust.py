#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-akvaryum-baligi-ne-yapilir/index.html"
TOOL = ROOT / "alo186/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/index.html"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/aquarium-outage-v300.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"
ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesilince-akvaryum-baligi-ne-yapilir/",
    TOOL: "https://alo186.com/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-plani/",
    SELECTOR: "https://alo186.com/amazon-elektrik-urunleri/akvaryum-kesinti-hava-pompasi-termometre-secici/",
}


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == "a":
            self.anchors.append({key.casefold(): value or "" for key, value in attrs})


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
    for forbidden in (
        "https://www.alo186.com",
        '"@type":"Offer"',
        '"@type":"AggregateRating"',
        '"@type":"Review"',
        '"price":',
        '"availability":',
        '"warranty":',
    ):
        assert forbidden not in html, (path, forbidden)
    return html


def main() -> None:
    article = validate_page(ARTICLE, ROUTES[ARTICLE])
    tool = validate_page(TOOL, ROUTES[TOOL])
    selector = validate_page(SELECTOR, ROUTES[SELECTOR])

    for required in (
        "Kesintide “kaç saat dayanır?” yerine",
        "Kesin yaşam süresi yayımlamayın",
        "Kesinti devam ederken yem vermeyin",
        "Mevcut plan yeterliyse yeni ürün almayın",
        "Bu rehberde Amazon veya başka mağaza bağlantısı yoktur",
        "professional-only",
        "ALO186 bağımsız bilgilendirme platformudur",
    ):
        assert required in article, required
    assert "amazon.com.tr" not in article.casefold()

    for required in (
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "Canlı stresi veya su-elektrik tehlikesinde ticari yol kapalı",
        "Mevcut plan yeterli — yeni ürün almayın",
        "30 gün: pil, hortum ve termometre",
        "90 gün: gözetimli kesinti provası",
        "180 gün: sıcaklık, stok ve filtre planı",
        "Bu araçta Amazon veya başka mağaza bağlantısı yoktur",
        "professional-only",
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
        "Amazon Türkiye satış ortaklığı",
        "bağlantılar başlangıçta kilitlidir",
        "Satın almama geçerli sonuçtur",
        "yeni ürün almayacağım",
        "Aktif kesinti, canlı sıkıntısı veya elektrik tehlikesinde mağaza yolu kapalıdır",
        "Pilli hava motoru",
        "Açıkça 5 V USB hava pompası",
        "Basit akvaryum termometresi",
        'rel="sponsored nofollow noopener"',
        "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz",
        "professional-only",
    ):
        assert required in selector, required
    for anchor_id in ("batteryLink", "usbLink", "tempLink"):
        assert selector.index("Satış ortaklığı açıklaması") < selector.index(f'id="{anchor_id}"')
    assert 'href="https://www.amazon.com.tr' not in selector.casefold()
    assert 'data-url="https://www.amazon.com.tr' not in selector.casefold()

    parser = AnchorParser()
    parser.feed(selector)
    product_ids = {"batteryLink", "usbLink", "tempLink"}
    product_anchors = [anchor for anchor in parser.anchors if anchor.get("id") in product_ids]
    assert len(product_anchors) == 3
    for anchor in product_anchors:
        assert not anchor.get("href")
        assert anchor.get("aria-disabled") == "true"
        assert {"sponsored", "nofollow", "noopener"}.issubset(set(anchor.get("rel", "").split()))

    decision = json.loads(read(DECISION))
    assert decision["version"] == 300
    assert decision["decision"] == "guarded-low-risk-consumer-affiliate-with-professional-exclusions"
    policy = decision["conversionPolicy"]
    expected = {
        "newMerchantLinks": True,
        "linksLockedByDefault": True,
        "noBuyOutcomeRequired": True,
        "activeOutageCommerceClosed": True,
        "animalDistressCommerceClosed": True,
        "electricalHazardCommerceClosed": True,
        "personalDataCollectionForbidden": True,
        "animalHealthRecordCollectionForbidden": True,
        "noPriceStockRatingWarrantyClaims": True,
        "affiliateDisclosureRequiredBeforeAnyMerchantLink": True,
        "officialInstitutionImpressionForbidden": True,
        "professionalScopeForComplexSystems": True,
        "universalSurvivalTimeClaimsForbidden": True,
    }
    for key, value in expected.items():
        assert policy[key] is value, (key, policy[key])
    assert policy["merchant"] == "Amazon Türkiye"
    assert len(decision["allowedLowRiskClasses"]) == 3
    assert len(decision["excludedProfessionalClasses"]) >= 9
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 180]

    central_policy = json.loads(read(POLICY))
    governed = central_policy["governedAffiliateRoutePatterns"]
    assert "akvaryum-kesinti-hava-pompasi-termometre-secici" in governed

    print(json.dumps({
        "ok": True,
        "version": 300,
        "updatedRoutes": 3,
        "initialActiveMerchantLinks": 0,
        "guardedProductClasses": 3,
        "professionalExclusions": len(decision["excludedProfessionalClasses"]),
        "repeatVisitDays": [30, 90, 180],
        "personalDataFields": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
