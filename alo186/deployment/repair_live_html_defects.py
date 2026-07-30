from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REVENUE_MARKER = 'data-alo186-revenue-proof="true"'
EDAS_STYLE_MARKER = 'data-alo186-edas-mobile-quality="true"'
EDAS_STYLE = (
    '<style data-alo186-edas-mobile-quality="true">'
    '.search-shell>*{min-inline-size:0}'
    '.search-panel,.search-input-wrap{min-inline-size:0;max-inline-size:100%}'
    '.search-input-wrap input{min-inline-size:0}'
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


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


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

    if 'id="searchInput"' in updated and not re.search(r'<input\b[^>]*id=["\']searchInput["\'][^>]*\brole=["\']combobox["\']', updated, re.I):
        updated = re.sub(
            r'(<input\b[^>]*id=["\']searchInput["\'])',
            r'\1 role="combobox"',
            updated,
            count=1,
            flags=re.I,
        )
    if 'id="searchResults"' in updated and not re.search(r'<div\b[^>]*id=["\']searchResults["\'][^>]*\baria-(?:label|labelledby)=', updated, re.I):
        updated = re.sub(
            r'(<div\b[^>]*id=["\']searchResults["\'])',
            r'\1 aria-label="Arama sonuçları"',
            updated,
            count=1,
            flags=re.I,
        )
    if EDAS_STYLE_MARKER not in updated:
        if "</head>" not in updated:
            raise RuntimeError("EDAŞ Bul sayfasında head kapanışı bulunamadı")
        updated = updated.replace("</head>", EDAS_STYLE + "\n</head>", 1)

    if updated == html:
        return 0
    path.write_text(updated, encoding="utf-8")
    return 1


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
        if not re.search(r'<input\b[^>]*id=["\']searchInput["\'][^>]*\brole=["\']combobox["\']', html, re.I):
            failures.append("EDAŞ arama alanında combobox rolü eksik")
        if not re.search(r'<div\b[^>]*id=["\']searchResults["\'][^>]*\baria-label=["\']Arama sonuçları["\']', html, re.I):
            failures.append("EDAŞ sonuç listesinde erişilebilir ad eksik")
        if EDAS_STYLE_MARKER not in html:
            failures.append("EDAŞ mobil min-width koruması eksik")
    if failures:
        raise RuntimeError("Canlı HTML kabuk kalite sözleşmesi başarısız:\n- " + "\n- ".join(failures))


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    repaired_files, repaired_tags = repair_split_footers(site)
    edas_pages_hardened = harden_edas_search(site)
    validate(site)
    return {
        "ok": True,
        "basePath": normalize_base_path(base_path),
        "splitFooterFilesRepaired": repaired_files,
        "splitFooterTagsRepaired": repaired_tags,
        "edasPagesHardened": edas_pages_hardened,
        "personalDataFieldsAdded": 0,
        "officialAffiliationClaimed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final artifactındaki bozuk footer enjeksiyonlarını ve EDAŞ arama erişilebilirliğini onarır.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
