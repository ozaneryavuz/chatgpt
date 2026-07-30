from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REVENUE_MARKER = 'data-alo186-revenue-proof="true"'
EDAS_STYLE_MARKER = 'data-alo186-edas-mobile-quality="true"'
PRODUCT_ENTRY_MARKER = 'data-alo186-shortlist-product-entry="true"'
EDAS_STYLE = (
    '<style data-alo186-edas-mobile-quality="true">'
    '.search-shell>*{min-inline-size:0}'
    '.search-panel{min-inline-size:0;max-inline-size:100%}'
    '.search-input-wrap{display:grid;grid-template-columns:minmax(0,1fr) 44px;gap:8px;align-items:center;min-inline-size:0;max-inline-size:100%}'
    '.search-input-wrap input{min-inline-size:0;padding-right:12px!important}'
    '.search-input-wrap button{position:static!important;inset:auto!important;width:44px!important;height:44px!important}'
    '.route-row{grid-template-columns:minmax(76px,auto) minmax(0,1fr)}'
    '.route-row strong{overflow-wrap:anywhere}'
    '@media(max-width:900px){.search-shell{grid-template-columns:minmax(0,1fr)!important}}'
    '</style>'
)

# Bazı eski büyüme katmanları gelir açıklamasını "<footer>" kelimesinin ortasına
# yerleştiriyordu: <fo<aside ...></aside>oter>. Bu desen yalnız gelir kanıtı
# markerı taşıyan aside için onarılır; genel HTML üzerinde kör replace yapılmaz.
SPLIT_FOOTER_PATTERN = re.compile(
    r'<(?P<prefix>f|fo|foo|foot|foote)'
    r'(?P<aside><aside\b[^>]*data-alo186-revenue-proof=["\']true["\'][^>]*>.*?</aside>)'
    r'(?P<suffix>ooter|oter|ter|er|r)>',
    re.I | re.S,
)
SEARCH_INPUT_ID_PATTERN = re.compile(r'<input\b[^>]*\bid=(?P<quote>["\'])searchInput(?P=quote)', re.I)
SEARCH_RESULTS_ID_PATTERN = re.compile(r'<div\b[^>]*\bid=(?P<quote>["\'])searchResults(?P=quote)', re.I)
SEARCH_INPUT_ROLE_PATTERN = re.compile(
    r'<input\b[^>]*\bid=(?P<quote>["\'])searchInput(?P=quote)[^>]*\brole=["\']combobox["\']', re.I
)
SEARCH_RESULTS_LABEL_PATTERN = re.compile(
    r'<div\b[^>]*\bid=(?P<quote>["\'])searchResults(?P=quote)[^>]*\baria-(?:label|labelledby)=', re.I
)


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    base_path = normalize_base_path(base_path)
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def repair_split_footers(site: Path) -> tuple[int, int]:
    repaired_files = 0
    repaired_tags = 0
    failures: list[str] = []

    def replace(match: re.Match[str]) -> str:
        nonlocal repaired_tags
        if (match.group("prefix") + match.group("suffix")).casefold() != "footer":
            return match.group(0)
        repaired_tags += 1
        return match.group("aside") + "<footer>"

    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        updated = SPLIT_FOOTER_PATTERN.sub(replace, html)
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            repaired_files += 1
        if REVENUE_MARKER in updated and re.search(r'<(?:f|fo|foo|foot|foote)<aside\b', updated, re.I):
            failures.append(path.relative_to(site).as_posix())

    if failures:
        raise RuntimeError("Bölünmüş footer onarımı tamamlanamadı: " + ", ".join(failures[:30]))
    return repaired_files, repaired_tags


def harden_edas_search(site: Path) -> int:
    path = site / "edas-bul/index.html"
    if not path.is_file():
        return 0
    html = path.read_text(encoding="utf-8", errors="ignore")
    updated = html

    if SEARCH_INPUT_ID_PATTERN.search(updated) and not SEARCH_INPUT_ROLE_PATTERN.search(updated):
        updated = SEARCH_INPUT_ID_PATTERN.sub(lambda match: match.group(0) + ' role="combobox"', updated, count=1)
    if SEARCH_RESULTS_ID_PATTERN.search(updated) and not SEARCH_RESULTS_LABEL_PATTERN.search(updated):
        updated = SEARCH_RESULTS_ID_PATTERN.sub(lambda match: match.group(0) + ' aria-label="Arama sonuçları"', updated, count=1)
    if EDAS_STYLE_MARKER not in updated:
        if "</head>" not in updated:
            raise RuntimeError("EDAŞ Bul sayfasında head kapanışı bulunamadı")
        updated = updated.replace("</head>", EDAS_STYLE + "\n</head>", 1)

    if updated == html:
        return 0
    path.write_text(updated, encoding="utf-8")
    return 1


def stabilize_product_center_layout(site: Path, base_path: str) -> int:
    """Sonradan DOM'a eklenen karşılaştırma kartını ilk HTML'e alarak CLS'yi kaldırır."""

    href = public_url(base_path, "/hesaplama/teknik-urun-karsilastirma/")
    targets = [
        (
            site / "amazon-elektrik-urunleri/index.html",
            '<div class="affiliate-disclosure">',
            f'<section class="section" {PRODUCT_ENTRY_MARKER}><span class="eyebrow">Karşılaştırma öncesi güven kapısı</span><h2>Üç adayı marka ve fiyat kullanmadan karşılaştırın</h2><p class="lead">Mevcut ekipmanı dördüncü seçenek olarak koruyun; kritik teknik belge eksikse ürün rotasını açmayın.</p><div class="button-row"><a class="button secondary" href="{href}">Teknik kısa listeyi aç</a></div><p class="fine">Bu araç doğrudan mağaza bağlantısı, fiyat, stok, puan veya garanti göstermez.</p></section>',
        ),
        (
            site / "akilli-urun-secimi/index.html",
            '<section id="savedDecision"',
            f'<section class="content-section" {PRODUCT_ENTRY_MARKER}><div class="panel"><span class="eyebrow">Karşılaştırma öncesi güven kapısı</span><h2>Üç adayı marka ve fiyat kullanmadan karşılaştırın</h2><p>Mevcut ekipmanı dördüncü seçenek olarak koruyun; kritik teknik belge eksikse ürün rotasını açmayın. Karar makbuzu ve yeniden kontrol yalnız tarayıcınızda tutulur.</p><div class="actions"><a class="btn btn-secondary" href="{href}">Teknik kısa listeyi aç</a></div><small>Bu araç doğrudan mağaza bağlantısı, fiyat, stok, puan veya garanti göstermez.</small></div></section>',
        ),
    ]
    changed = 0
    for path, anchor, block in targets:
        if not path.is_file():
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        if PRODUCT_ENTRY_MARKER in html:
            continue
        if anchor not in html:
            raise RuntimeError(f"Ürün merkezi CLS sabitleme hedefi bulunamadı: {path.relative_to(site)}")
        path.write_text(html.replace(anchor, block + anchor, 1), encoding="utf-8")
        changed += 1
    return changed


def validate(site: Path) -> None:
    failures: list[str] = []
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(site).as_posix()
        if re.search(r'<(?:f|fo|foo|foot|foote)<aside\b[^>]*data-alo186-revenue-proof=', html, re.I):
            failures.append(f"Bölünmüş footer kaldı: {relative}")
    edas = site / "edas-bul/index.html"
    if edas.is_file():
        html = edas.read_text(encoding="utf-8", errors="ignore")
        if not SEARCH_INPUT_ROLE_PATTERN.search(html):
            failures.append("EDAŞ arama alanında combobox rolü eksik")
        if not re.search(
            r'<div\b[^>]*\bid=(?P<quote>["\'])searchResults(?P=quote)[^>]*\baria-label=["\']Arama sonuçları["\']',
            html,
            re.I,
        ):
            failures.append("EDAŞ sonuç listesinde erişilebilir ad eksik")
        if EDAS_STYLE_MARKER not in html:
            failures.append("EDAŞ mobil min-width koruması eksik")
    for relative in ("amazon-elektrik-urunleri/index.html", "akilli-urun-secimi/index.html"):
        path = site / relative
        if path.is_file() and PRODUCT_ENTRY_MARKER not in path.read_text(encoding="utf-8", errors="ignore"):
            failures.append(f"Ürün merkezi ilk HTML karşılaştırma alanı eksik: {relative}")
    if failures:
        raise RuntimeError("Canlı HTML kabuk kalite sözleşmesi başarısız:\n- " + "\n- ".join(failures))


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    repaired_files, repaired_tags = repair_split_footers(site)
    edas_pages_hardened = harden_edas_search(site)
    product_centers_stabilized = stabilize_product_center_layout(site, base_path)
    validate(site)
    return {
        "ok": True,
        "basePath": normalize_base_path(base_path),
        "splitFooterFilesRepaired": repaired_files,
        "splitFooterTagsRepaired": repaired_tags,
        "edasPagesHardened": edas_pages_hardened,
        "productCentersStabilized": product_centers_stabilized,
        "personalDataFieldsAdded": 0,
        "officialAffiliationClaimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final artifactındaki bozuk footer, mobil erişilebilirlik ve CLS kusurlarını onarır.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
