from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PAGE = ROOT / "alo186/urun-bilgi-grafigi/index.html"
SOURCE_APP = ROOT / "alo186/urun-bilgi-grafigi/sales-missions.js"
SOURCE_STYLE = ROOT / "alo186/urun-bilgi-grafigi/sales-missions.css"
SALES_EXTENSION = ROOT / "alo186/urun-eslestirme/generator-guide-extension.js"


def source_contracts() -> None:
    page = SOURCE_PAGE.read_text(encoding="utf-8")
    app = SOURCE_APP.read_text(encoding="utf-8")
    css = SOURCE_STYLE.read_text(encoding="utf-8")
    extension = SALES_EXTENSION.read_text(encoding="utf-8")

    for token in (
        'id="solutionBuilder"',
        'id="collectionGrid"',
        'id="collectionStatus"',
        "Elinizdekini işaretleyin; yalnız eksik parçayı açın.",
        "Mevcut ürün önce",
        "Uyum onayı zorunlu",
        "sales-missions.css",
        "sales-missions.js",
    ):
        assert token in page, token

    assert "amazon.com.tr" not in page.casefold()
    assert "localStorage" not in page and "sessionStorage" not in page

    for token in (
        "catalog.purchaseCollections",
        "catalog.publicAffiliateEligible",
        "catalog.verificationStatus",
        "data-owned-product",
        "data-compatibility-confirm",
        "Mevcut setiniz tamam görünüyor.",
        "Satın almama sonucu oluşturuldu.",
        "sponsored nofollow noopener",
        "sales_missing_parts_collection_rendered",
        "sales_missing_parts_planned",
        "sales_missing_part_opened",
        "URLSearchParams",
        "bundle",
    ):
        assert token in app, token

    for forbidden in (
        "localStorage",
        "sessionStorage",
        "stokta son",
        "hemen satın al",
        "kaçırma",
        "fiyat düştü",
        "window.open(",
    ):
        assert forbidden not in app.casefold(), forbidden

    for token in (
        ".solution-builder",
        ".collection-grid",
        ".mission-card",
        ".component-option:has(input:checked)",
        ".mission-output .no-buy",
        "@media(max-width:820px)",
        "@media(max-width:560px)",
        "prefers-reduced-motion",
        "min-height:50px",
    ):
        assert token in css, token

    for collection_id in (
        "travel-65w",
        "samsung-fast-charge",
        "desk-dock",
        "gaming-display",
        "mobile-presentation",
    ):
        assert collection_id in extension, collection_id


def artifact_contracts(site: Path, base_path: str) -> None:
    route = site / "urun-bilgi-grafigi"
    page_path = route / "index.html"
    app_path = route / "sales-missions.js"
    css_path = route / "sales-missions.css"
    assert page_path.is_file(), page_path
    assert app_path.is_file(), app_path
    assert css_path.is_file(), css_path

    page = page_path.read_text(encoding="utf-8")
    app = app_path.read_text(encoding="utf-8")
    expected_catalog = f'{base_path}/akilli-urun-secimi/catalog.js' if base_path else "/akilli-urun-secimi/catalog.js"
    assert f'src="{expected_catalog}"' in page
    assert 'src="./sales-missions.js"' in page
    assert 'href="./sales-missions.css"' in page
    assert "Elinizdekini işaretleyin; yalnız eksik parçayı açın." in page
    assert "amazon.com.tr" not in page.casefold()
    assert "sponsored nofollow noopener" in app
    assert "localStorage" not in app and "sessionStorage" not in app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    source_contracts()
    if args.site:
        artifact_contracts(args.site.resolve(), args.base_path.rstrip("/"))
    print("ALO186 eksik parça planlayıcı satış ve güven sözleşmeleri başarılı.")


if __name__ == "__main__":
    main()
