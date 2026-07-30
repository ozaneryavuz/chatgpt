from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

CANONICAL_ORIGIN = "https://alo186.com"
CANONICAL_HOST = "alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
LEGACY_HOST = "www.alo186.com"
QUALITY_MARKER = 'data-alo186-technical-quality="true"'
QUALITY_STYLE = (
    '<style data-alo186-technical-quality="true">'
    ':where(img,svg,video,canvas,iframe){max-inline-size:100%}'
    ':where(img,video,canvas){block-size:auto}'
    ':where(pre,code){overflow-wrap:anywhere;white-space:pre-wrap}'
    ':where(table){max-inline-size:100%}'
    ':where(.table-wrap,[role="region"][aria-label*="tablo" i]){max-inline-size:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}'
    ':where(a,button,input,select,textarea,summary){touch-action:manipulation}'
    '@media(max-width:720px){:where(h1,h2,h3,p,a,button,summary,th,td){overflow-wrap:anywhere}}'
    '@media(prefers-reduced-motion:reduce){html:focus-within{scroll-behavior:auto!important}}'
    '</style>'
)
TEXT_SUFFIXES = {".html", ".htm", ".xml", ".txt", ".json", ".js", ".css", ".webmanifest"}


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def canonical_links(html: str) -> list[str]:
    links: list[str] = []
    for tag in re.findall(r"<link\b[^>]*>", html, re.I):
        if not re.search(r"\brel=[\"'][^\"']*\bcanonical\b[^\"']*[\"']", tag, re.I):
            continue
        match = re.search(r"\bhref=[\"']([^\"']+)[\"']", tag, re.I)
        if match:
            links.append(match.group(1))
    return links


def normalize_live_origin(site: Path) -> int:
    changed = 0
    for path in sorted(site.rglob("*")):
        if not path.is_file() or (path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"robots.txt", "sitemap.xml"}):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated = text.replace(LEGACY_ORIGIN, CANONICAL_ORIGIN).replace(LEGACY_HOST, CANONICAL_HOST)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def inject_responsive_hardening(site: Path) -> int:
    changed = 0
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        if QUALITY_MARKER in html:
            continue
        if "</head>" not in html:
            raise RuntimeError(f"HTML head kapanışı bulunamadı: {path.relative_to(site)}")
        path.write_text(html.replace("</head>", QUALITY_STYLE + "\n</head>", 1), encoding="utf-8")
        changed += 1
    return changed


def validate(site: Path, base_path: str) -> dict:
    failures: list[str] = []
    base_path = normalize_base_path(base_path)
    indexable_count = 0
    noindex_count = 0
    html_count = 0

    for path in sorted(site.rglob("*.html")):
        html_count += 1
        html = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(site).as_posix()
        if QUALITY_MARKER not in html:
            failures.append(f"Responsive kalite stili eksik: {relative}")
        if LEGACY_ORIGIN in html or LEGACY_HOST in html:
            failures.append(f"www host artifactta kaldı: {relative}")
        robots_match = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)', html, re.I)
        noindex = bool(robots_match and "noindex" in robots_match.group(1).casefold())
        if noindex:
            noindex_count += 1
            continue
        indexable_count += 1
        links = canonical_links(html)
        if len(links) != 1:
            failures.append(f"Indexlenebilir sayfada canonical sayısı {len(links)}: {relative}")
        elif not links[0].startswith(CANONICAL_ORIGIN + "/"):
            failures.append(f"Canonical apex hostta değil: {relative} -> {links[0]}")
        if re.search(r'<meta\s+http-equiv=["\']refresh["\']', html, re.I):
            failures.append(f"Indexlenebilir sayfada meta refresh var: {relative}")

    robots_path = site / "robots.txt"
    sitemap_path = site / "sitemap.xml"
    if not robots_path.is_file():
        failures.append("robots.txt eksik")
    else:
        robots = robots_path.read_text(encoding="utf-8")
        if f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots:
            failures.append("robots.txt apex sitemap adresini taşımıyor")
        if "Allow: /" not in robots:
            failures.append("robots.txt genel taramaya izin vermiyor")
    if not sitemap_path.is_file():
        failures.append("sitemap.xml eksik")
    else:
        sitemap = sitemap_path.read_text(encoding="utf-8")
        if LEGACY_ORIGIN in sitemap or LEGACY_HOST in sitemap:
            failures.append("sitemap.xml www host taşıyor")
        if f"<loc>{CANONICAL_ORIGIN}/" not in sitemap:
            failures.append("sitemap.xml apex canonical URL taşımıyor")

    release_path = site / "pages-release.json"
    if not release_path.is_file():
        failures.append("pages-release.json eksik")
    else:
        release = json.loads(release_path.read_text(encoding="utf-8"))
        if release.get("canonicalHost") != CANONICAL_ORIGIN:
            failures.append("pages-release canonicalHost apex değil")
        if release.get("customDomain") != CANONICAL_HOST:
            failures.append("pages-release customDomain apex değil")

    if not base_path and indexable_count == 0:
        failures.append("Custom-domain artifactında indexlenebilir HTML bulunamadı")
    if base_path and noindex_count != html_count:
        failures.append("Project-path artifactındaki bütün HTML sayfaları noindex değil")
    if failures:
        raise RuntimeError("Final canlı kalite sözleşmesi başarısız:\n- " + "\n- ".join(failures[:100]))
    return {
        "htmlCount": html_count,
        "indexableHtmlCount": indexable_count,
        "noindexHtmlCount": noindex_count,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "customDomain": CANONICAL_HOST,
    }


def recompute_checksums(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(site).as_posix()}"
        for path in sorted(item for item in site.rglob("*") if item.is_file())
    ]
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    normalized = normalize_base_path(base_path)
    origin_files_changed = normalize_live_origin(site)
    responsive_html_hardened = inject_responsive_hardening(site)

    release_path = site / "pages-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        release["canonicalHost"] = CANONICAL_ORIGIN
        release["customDomain"] = CANONICAL_HOST
        release["liveTechnicalQuality"] = {
            "version": 1,
            "canonicalOrigin": CANONICAL_ORIGIN,
            "redirectChainRemoved": "www-to-apex",
            "originFilesChanged": origin_files_changed,
            "responsiveHtmlHardened": responsive_html_hardened,
            "personalDataFieldsAdded": 0,
            "officialAffiliationClaimed": False,
        }
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validation = validate(site, normalized)
    recompute_checksums(site)
    return {
        "ok": True,
        "basePath": normalized,
        "originFilesChanged": origin_files_changed,
        "responsiveHtmlHardened": responsive_html_hardened,
        **validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final Pages artifactında canlı canonical ve responsive kalite sözleşmesini uygular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
