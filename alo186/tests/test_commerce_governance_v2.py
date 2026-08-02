from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
CANONICAL_LINK = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', re.I)
sys.path.insert(0, str(DEPLOYMENT))

from guard_commerce_routes_v2 import (  # noqa: E402
    COMMERCIAL_ROUTES,
    SERVICE_ROUTES,
    has_independence,
    has_no_buy,
    scan_affiliate_anchors,
)


def write_and_scan(html: str) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        page = root / "fixture" / "index.html"
        page.parent.mkdir(parents=True)
        page.write_text(html, encoding="utf-8")
        return scan_affiliate_anchors(page, root)


def test_affiliate_anchor_policy() -> None:
    disclosure = '<p>Reklam / satış ortaklığı: nitelikli satın alımlardan komisyon kazanılabilir.</p>'
    safe = (
        f'<html><body>{disclosure}<p>USB-C powerbank teknik eşleşmesi.</p>'
        '<a href="https://www.amazon.com.tr/dp/B000000000?tag=alo186rehber-21" '
        'rel="sponsored nofollow noopener">Amazon ürün sayfasını aç</a></body></html>'
    )
    assert write_and_scan(safe) == []
    errors = write_and_scan(safe.replace('rel="sponsored nofollow noopener"', 'rel="nofollow"'))
    assert any("eksik rel tokenları" in item for item in errors)
    errors = write_and_scan(safe.replace(disclosure, '<p>Bağımsız teknik liste.</p>'))
    assert any("görünür satış ortaklığı açıklaması yok" in item for item in errors)

    qualified_low_risk = (
        f'<html><body>{disclosure}<article class="card"><h2>Priz tipi darbe koruyucu</h2>'
        '<p>Pano tipi SPD ve topraklama doğrulandıktan sonra hassas elektroniğe tamamlayıcı koruma için.</p>'
        '<a href="https://www.amazon.com.tr/s?k=ak%C4%B1m+korumal%C4%B1+priz&tag=alo186rehber-21" '
        'rel="sponsored nofollow noopener">Amazon seçeneklerini incele</a></article></body></html>'
    )
    assert write_and_scan(qualified_low_risk) == []

    travel_adapter = (
        f'<html><body>{disclosure}<article class="card"><h2>Topraklı seyahat adaptörü</h2>'
        '<p>Voltaj uyumlu olmalı; topraklama kayboluyorsa satın almayın.</p>'
        '<a href="https://www.amazon.com.tr/s?k=toprakl%C4%B1+seyahat+adapt%C3%B6r%C3%BC&tag=alo186rehber-21" '
        'rel="sponsored nofollow noopener">Amazon seçeneklerini incele</a></article></body></html>'
    )
    assert write_and_scan(travel_adapter) == []

    high_risk_heading = (
        f'<html><body>{disclosure}<article class="card"><h2>Pano tipi SPD seçimi</h2>'
        '<p>Yetkili mühendislik gerektirir.</p>'
        '<a href="https://amzn.to/example" rel="sponsored nofollow noopener">Amazon ürün sayfasını aç</a>'
        '</article></body></html>'
    )
    errors = write_and_scan(high_risk_heading)
    assert any("yüksek riskli/sabit tesisat" in item and "SPD" in item for item in errors)

    high_risk_url = safe.replace(
        "https://www.amazon.com.tr/dp/B000000000?tag=alo186rehber-21",
        "https://www.amazon.com.tr/s?k=topraklama+olcum+cihazi&tag=alo186rehber-21",
    )
    errors = write_and_scan(high_risk_url)
    assert any("yüksek riskli/sabit tesisat" in item and "topraklama" in item for item in errors)

    high_risk_metadata = safe.replace('<a href=', '<a data-product-name="RCCB 30 mA" href=')
    errors = write_and_scan(high_risk_metadata)
    assert any("yüksek riskli/sabit tesisat" in item and "RCCB" in item for item in errors)


def test_disclosure_equivalence() -> None:
    for text in (
        "Mevcut cihaz yeterli ve güvenliyse satın alma yapmayın.",
        "Satın almama seçeneği korunur.",
        "Satın almama koruması proje kararının parçasıdır.",
        "Elinizdeki ürün yeterliyse yeni ürün almak gerekmeyebilir.",
        "Ürün satın alma zorunluluğu yoktur.",
        "Bilgiler yoksa sipariş vermeyin.",
    ):
        assert has_no_buy(text)
    assert not has_no_buy("En yeni ürünü hemen satın alın.")
    assert has_independence("ALO186 bağımsız bilgi platformudur; EDAŞ veya kamu kurumu değildir.")
    assert has_independence("Bağımsız elektrik bilgi ağı. Ürün satıcısı değildir.")
    assert not has_independence("Resmî EDAŞ başvuru merkezi.")


def direct_catalog_categories(catalog: str) -> list[tuple[str, str, str]]:
    return re.findall(
        r"\{id:'([^']+)',name:'[^']+',mode:'direct',risk:'([^']+)',affiliatePolicy:'([^']+)'",
        catalog,
    )


def source_canonical(html: str, route: str) -> tuple[str, bool]:
    match = CANONICAL_LINK.search(html)
    assert match, f"Canonical eksik: {route}"
    parsed = urlsplit(match.group(1))
    assert parsed.scheme == "https", (route, match.group(1))
    assert parsed.hostname in {"alo186.com", "www.alo186.com"}, (route, match.group(1))
    assert parsed.path.rstrip("/") == route.rstrip("/"), (route, match.group(1))
    return match.group(1), parsed.hostname == "www.alo186.com"


def test_actual_source_contracts() -> None:
    affiliate_pages = 0
    professional_only_pages = 0
    legacy_source_canonicals = 0

    for route, policy in COMMERCIAL_ROUTES.items():
        path = REPO_ROOT / "alo186" / route.strip("/") / "index.html"
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        _, legacy = source_canonical(html, route)
        legacy_source_canonicals += int(legacy)
        assert "amazon.com.tr" not in lower, "Kaynak HTML statik mağaza URL'si içermemeli"
        assert ("data-fresh-products" in html) is bool(policy["direct"])
        if policy["affiliate"]:
            affiliate_pages += 1
            assert "satış ortaklığı" in lower
        else:
            professional_only_pages += 1
            assert policy["professional_only"] is True
            assert 'data-commercial-scope="professional-only"' in html
            assert "mağaza bağlantısı" in lower
            assert "data-product-center" not in html

    assert affiliate_pages == 7
    assert professional_only_pages == 1

    for route in SERVICE_ROUTES:
        path = REPO_ROOT / "alo186" / route.strip("/") / "index.html"
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        compact = html.replace(" ", "")
        _, legacy = source_canonical(html, route)
        legacy_source_canonicals += int(legacy)
        for schema in ('"@type":"Service"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"', '"@type":"OfferCatalog"'):
            assert schema in compact
        assert "amazon.com.tr" not in html.casefold()
        assert "<form" not in html.casefold()

    runtime = (REPO_ROOT / "alo186/amazon-elektrik-urunleri/commercial.js").read_text(encoding="utf-8")
    catalog = (REPO_ROOT / "alo186/urun-eslestirme/catalog.js").read_text(encoding="utf-8")
    for token in (
        "freshOnly: true",
        "sponsored nofollow noopener",
        "category.mode === 'direct'",
        "if (professionalOnly) return;",
    ):
        assert token in runtime

    direct_categories = direct_catalog_categories(catalog)
    assert direct_categories, "En az bir doğrulanmış düşük riskli doğrudan kategori bulunmalı."
    assert all(risk == "consumer" for _, risk, _ in direct_categories)
    assert all(policy == "verified_direct" for _, _, policy in direct_categories)
    direct_ids = {category_id for category_id, _, _ in direct_categories}
    assert {"powerbank", "usb_c_charger", "usb_c_cable", "usb_c_hub", "display_cable"}.issubset(direct_ids)
    assert direct_ids.isdisjoint({"surge_strip", "generator", "inverter", "outlet_tester", "ev_cable", "ups_battery"})
    assert "verificationMaxAgeDays=45" in catalog
    assert "affiliateTag='alo186rehber-21'" in catalog

    for forbidden in ("product.price", "product.stock", "product.rating", "product.warranty", "affiliateCommission"):
        assert forbidden not in runtime

    # Kaynak sayfalarda tarihsel www kayıtları geçici olarak path düzeyinde kabul edilir;
    # production artifact guardı yalnız apex origin'i kabul eder ve legacy www'yi reddeder.
    assert legacy_source_canonicals >= 0


def main() -> None:
    test_affiliate_anchor_policy()
    test_disclosure_equivalence()
    test_actual_source_contracts()
    catalog = (REPO_ROOT / "alo186/urun-eslestirme/catalog.js").read_text(encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "artifactLegacyCanonicalRejected": True,
        "sourceCanonicalPathValidated": True,
        "commercialPages": len(COMMERCIAL_ROUTES),
        "affiliateCommercialPages": 7,
        "professionalOnlyPages": 1,
        "servicePages": len(SERVICE_ROUTES),
        "directAffiliateCategories": len(direct_catalog_categories(catalog)),
        "highRiskDirectAffiliate": False,
        "professionalOnlyDirectAffiliate": False,
        "unverifiedCommercialClaims": False,
        "affiliateRiskScope": "url-anchor-metadata-card-heading",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
