from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
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
    safe = (
        '<html><body><p>Reklam / satış ortaklığı: nitelikli satın alımlardan komisyon kazanılabilir.</p>'
        '<p>USB-C powerbank teknik eşleşmesi.</p>'
        '<a href="https://www.amazon.com.tr/dp/B000000000?tag=alo186hazirlik-21" '
        'rel="sponsored nofollow noopener">Amazon ürün sayfasını aç</a></body></html>'
    )
    assert write_and_scan(safe) == []

    missing_rel = safe.replace('rel="sponsored nofollow noopener"', 'rel="nofollow"')
    errors = write_and_scan(missing_rel)
    assert any("eksik rel tokenları" in item for item in errors)

    missing_disclosure = safe.replace(
        '<p>Reklam / satış ortaklığı: nitelikli satın alımlardan komisyon kazanılabilir.</p>',
        '<p>Bağımsız teknik liste.</p>',
    )
    errors = write_and_scan(missing_disclosure)
    assert any("görünür satış ortaklığı açıklaması yok" in item for item in errors)

    high_risk = safe.replace("USB-C powerbank teknik eşleşmesi", "RCCB ve pano tipi SPD seçimi")
    errors = write_and_scan(high_risk)
    assert any("yüksek riskli/sabit tesisat" in item for item in errors)


def test_disclosure_equivalence() -> None:
    assert has_no_buy("Mevcut cihaz yeterli ve güvenliyse satın alma yapmayın.")
    assert has_no_buy("Satın almama seçeneği korunur.")
    assert has_no_buy("Satın almama koruması proje kararının parçasıdır.")
    assert has_no_buy("Elinizdeki ürün yeterliyse yeni ürün almak gerekmeyebilir.")
    assert has_no_buy("Ürün satın alma zorunluluğu yoktur.")
    assert has_no_buy("Bilgiler yoksa sipariş vermeyin.")
    assert not has_no_buy("En yeni ürünü hemen satın alın.")

    assert has_independence("ALO186 bağımsız bilgi platformudur; EDAŞ veya kamu kurumu değildir.")
    assert has_independence("Bağımsız elektrik bilgi ağı. Ürün satıcısı değildir.")
    assert not has_independence("Resmî EDAŞ başvuru merkezi.")


def test_actual_source_contracts() -> None:
    affiliate_pages = 0
    professional_only_pages = 0
    for route, policy in COMMERCIAL_ROUTES.items():
        path = REPO_ROOT / "alo186" / route.strip("/") / "index.html"
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        assert f'rel="canonical" href="https://www.alo186.com{route}"' in html
        assert "amazon.com.tr" not in lower, "Kaynak HTML statik mağaza URL'si içermemeli"
        assert "data-fresh-products" in html if policy["direct"] else "data-fresh-products" not in html
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
        assert f'rel="canonical" href="https://www.alo186.com{route}"' in html
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
    assert catalog.count("mode:'direct'") == 1
    assert "{id:'powerbank'" in catalog and "verificationMaxAgeDays=45" in catalog
    for forbidden in ("product.price", "product.stock", "product.rating", "product.warranty", "affiliateCommission"):
        assert forbidden not in runtime


def main() -> None:
    test_affiliate_anchor_policy()
    test_disclosure_equivalence()
    test_actual_source_contracts()
    print(json.dumps({
        "ok": True,
        "commercialPages": len(COMMERCIAL_ROUTES),
        "affiliateCommercialPages": 7,
        "professionalOnlyPages": 1,
        "servicePages": len(SERVICE_ROUTES),
        "directAffiliateCategories": 1,
        "highRiskDirectAffiliate": False,
        "professionalOnlyDirectAffiliate": False,
        "unverifiedCommercialClaims": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
