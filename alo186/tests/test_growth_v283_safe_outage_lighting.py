#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesintisinde-ev-nasil-aydinlatilir-mum-mu-led-fener-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/elektrik-kesintisi-ev-aydinlatma-plani/index.html"
AFFILIATE = ROOT / "alo186/amazon-elektrik-urunleri/kesinti-led-fener-kafa-lambasi-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v283-safe-outage-lighting.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/safe-outage-lighting-v283.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"

ROUTES = {
    ARTICLE: "https://alo186.com/haberler/elektrik-kesintisinde-ev-nasil-aydinlatilir-mum-mu-led-fener-mi/",
    TOOL: "https://alo186.com/hesaplama/elektrik-kesintisi-ev-aydinlatma-plani/",
    AFFILIATE: "https://alo186.com/amazon-elektrik-urunleri/kesinti-led-fener-kafa-lambasi-secimi/",
}


def text(path: Path) -> str:
    assert path.is_file(), f"Eksik dosya: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def json_ld(source: str) -> list[dict]:
    blocks = re.findall(
        r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>',
        source,
        flags=re.I | re.S,
    )
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
        "Mum yerine çalışan bir el feneri",
        "U.S. Fire Administration",
        "AFAD",
        "gevşek lityum",
        "yeni ürün almayın",
        "ALO186 EDAŞ, AFAD, itfaiye, üretici, servis veya satıcı değildir",
        "/hesaplama/elektrik-kesintisi-ev-aydinlatma-plani/",
        "/amazon-elektrik-urunleri/kesinti-led-fener-kafa-lambasi-secimi/",
    ):
        assert required in article, required
    assert_no_unverified_commerce(article)

    tool = text(TOOL)
    for required in (
        "Ücretsiz · kişisel veri yok · mağaza bağlantısı yok",
        "Mevcut sistem yeterli — yeni ürün almayın",
        "Mum yerine el feneri kullanın",
        "Gevşek lityum hücreyi kullanmayın",
        "Profesyonel acil aydınlatma kapsamı",
        "30 günlük pil ve gövde kontrolü",
        "90 günlük gerçek kesinti provası",
        "180 günlük afet çantası gözden geçirme",
    ):
        assert required in tool, required
    for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", 'type="email"', 'type="tel"'):
        assert forbidden not in tool, forbidden
    assert "www.amazon.com.tr" not in tool
    assert_no_unverified_commerce(tool)

    affiliate = text(AFFILIATE)
    for required in (
        "Amazon Türkiye satış ortaklığı",
        "Ürün sınıfları komisyon oranına göre sıralanmaz",
        "Mevcut fenerlerim kritik rotaları gerçek testte karşılıyor",
        "gevşek 18650 hücre kullanmayacağım",
        'rel="sponsored nofollow noopener"',
        "alo186rehber-21",
        "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti bilgisi ALO186 tarafından yayımlanmaz",
    ):
        assert required in affiliate, required
    static_amazon = re.findall(r'<a\b[^>]*href=["\']https://www\.amazon\.com\.tr', affiliate, flags=re.I)
    assert not static_amazon, static_amazon
    assert affiliate.count('class="button store"') == 3
    assert affiliate.count("https://www.amazon.com.tr/s?k=") == 3
    assert_no_unverified_commerce(affiliate)
    graph = json_ld(affiliate)[0]["@graph"]
    item_list = next(item for item in graph if item.get("@type") == "ItemList")
    assert len(item_list["itemListElement"]) == 3
    assert all(row["item"]["@type"] == "Product" for row in item_list["itemListElement"])

    overlay = json.loads(text(OVERLAY))
    assert overlay["version"] == 283
    assert overlay["name"] == "growth-v283-safe-outage-lighting"
    assert {route["canonicalPath"] for route in overlay["routes"]} == {
        "/haberler/elektrik-kesintisinde-ev-nasil-aydinlatilir-mum-mu-led-fener-mi/",
        "/hesaplama/elektrik-kesintisi-ev-aydinlatma-plani/",
        "/amazon-elektrik-urunleri/kesinti-led-fener-kafa-lambasi-secimi/",
    }

    decision = json.loads(text(DECISION))
    assert decision["decision"] == "conditional-consumer-affiliate"
    assert decision["conversionPolicy"]["linksLockedByDefault"] is True
    assert decision["conversionPolicy"]["activeHazardCommerceClosed"] is True
    assert decision["conversionPolicy"]["activeOutageUrgencyCommerceClosed"] is True
    assert decision["conversionPolicy"]["noBuyOutcomeRequired"] is True
    assert decision["conversionPolicy"]["noPriceStockRatingWarrantyClaims"] is True
    assert len(decision["allowedConsumerAffiliateClasses"]) == 3
    assert any("18650" in item for item in decision["excludedConsumerAffiliateClasses"])
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 180]

    policy = json.loads(text(POLICY))
    assert "kesinti-led-fener-kafa-lambasi" in policy["governedAffiliateRoutePatterns"]
    assert "jenerator" in policy["professionalLeadOnlyRoutePatterns"]

    print(json.dumps({
        "ok": True,
        "version": 283,
        "routes": 3,
        "genericProductClasses": 3,
        "unsafeStaticAmazonLinks": 0,
        "unverifiedCommercialFields": 0,
        "repeatVisitDays": [30, 90, 180],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
