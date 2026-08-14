from __future__ import annotations

import argparse
import hashlib
import json
import re
from html import escape
from pathlib import Path

CANONICAL_ORIGIN = "https://alo186.com"
CANONICAL_HOST = "alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
LEGACY_HOST = "www.alo186.com"
QUALITY_MARKER = 'data-alo186-technical-quality="true"'
LAZY_RUNTIME_MARKER = 'data-alo186-interaction-runtime="true"'
QUALITY_STYLE = (
    '<style data-alo186-technical-quality="true">'
    ':where(img,svg,video,canvas,iframe){max-inline-size:100%}'
    ':where(img,video,canvas){block-size:auto}'
    ':where(pre,code){overflow-wrap:anywhere;white-space:pre-wrap}'
    ':where(table){max-inline-size:100%}'
    ':where(.table-wrap,[role="region"][aria-label*="tablo" i]){max-inline-size:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}'
    ':where(a,button,input,select,textarea,summary){touch-action:manipulation}'
    '.amazon-intent-card small{color:#514b44!important;font-size:max(.875rem,14px)!important;line-height:1.45}'
    '.amazon-intent-card a[href]{min-height:44px;align-items:center;padding-block:.5rem}'
    '[class*="heroProof"] span{color:#454a45!important;font-size:max(.875rem,14px)!important;line-height:1.45}'
    '[class*="taskTop"]>span,[class*="answerList"]>article>span{color:#5d390d!important;font-size:max(.875rem,14px)!important;font-weight:750}'
    '[class*="taskCard"] small,[class*="task-card"] small{color:#484d48!important;font-size:max(.875rem,14px)!important;line-height:1.45}'
    '#analytics-preferences-open,button[data-analytics-choice]{min-height:44px;font-size:max(.875rem,14px)!important;line-height:1.35}'
    '@media(max-width:720px){:where(h1,h2,h3,p,a,button,summary,th,td){overflow-wrap:anywhere}:where(input,select,textarea,button){font-size:16px}:where(header) a[href]{display:inline-flex;align-items:center;justify-content:center;min-width:44px;min-height:44px}:where(.hero-card)>a[href]{display:inline-flex;align-items:center;min-height:44px;padding-block:.55rem}:where(.popular) button{min-height:44px;font-size:16px!important}:where(h1){font-size:clamp(1.85rem,9vw,3rem);overflow-wrap:break-word}}'
    '@media(prefers-reduced-motion:reduce){html:focus-within{scroll-behavior:auto!important}}'
    '</style>'
)
TEXT_SUFFIXES = {".html", ".htm", ".xml", ".txt", ".json", ".js", ".css", ".webmanifest"}
JSON_LD_PATTERN = re.compile(
    r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.I | re.S,
)
TABLE_WRAP_PATTERN = re.compile(
    r'<(?P<tag>div|section)(?P<attrs>[^>]*\bclass=["\'][^"\']*\btable-wrap\b[^"\']*["\'][^>]*)>',
    re.I,
)
SCRIPT_SRC_PATTERN = re.compile(
    r'<script\b(?P<before>[^>]*)\bsrc=["\'](?P<src>[^"\']+)["\'](?P<after>[^>]*)>\s*</script>',
    re.I,
)
OPTIONAL_RUNTIME_SUFFIXES = (
    "/hesaplama/common.js",
    "/assets/article-growth.js",
    "/hesaplama/outcome-bridge.js",
    "/hesaplama/evidence-wallet.js",
    "/hesaplama/intent-action-router.js",
    "/akilli-urun-secimi/outcome-trust-circuit-core.js",
    "/akilli-urun-secimi/documentation-growth-core.js",
    "/akilli-urun-secimi/outcome-trust-circuit.js",
    "/akilli-urun-secimi/documentation-growth.js",
)
INTERACTION_RUNTIME_TARGETS = (
    Path("index.html"),
    Path("amazon-elektrik-urunleri/index.html"),
)
KNOWN_FAQ_BREADCRUMB_DEFECT = '"}]},{"@type":"BreadcrumbList"'
KNOWN_FAQ_BREADCRUMB_REPAIR = '"}}]},{"@type":"BreadcrumbList"'


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


def repair_and_validate_json_ld(site: Path) -> int:
    """Bilinen eksik Question kapanışını düzeltir; diğer JSON-LD hatalarında yayını durdurur."""
    repairs = 0
    failures: list[str] = []
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(site).as_posix()
        changed = False
        rebuilt: list[str] = []
        cursor = 0
        for index, match in enumerate(JSON_LD_PATTERN.finditer(html), start=1):
            block = match.group(2)
            try:
                json.loads(block)
            except json.JSONDecodeError:
                repaired = block.replace(KNOWN_FAQ_BREADCRUMB_DEFECT, KNOWN_FAQ_BREADCRUMB_REPAIR)
                if repaired != block:
                    try:
                        json.loads(repaired)
                    except json.JSONDecodeError as exc:
                        snippet = repaired[max(0, exc.pos - 80): exc.pos + 80]
                        failures.append(
                            f"JSON-LD düzeltme sonrası geçersiz: {relative} blok {index}, "
                            f"satır {exc.lineno} sütun {exc.colno}: {snippet!r}"
                        )
                    else:
                        block = repaired
                        repairs += 1
                        changed = True
                else:
                    try:
                        json.loads(block)
                    except json.JSONDecodeError as exc:
                        snippet = block[max(0, exc.pos - 80): exc.pos + 80]
                        failures.append(
                            f"Bilinmeyen JSON-LD hatası: {relative} blok {index}, "
                            f"satır {exc.lineno} sütun {exc.colno}: {snippet!r}"
                        )
            rebuilt.append(html[cursor:match.start()])
            rebuilt.append(match.group(1) + block + match.group(3))
            cursor = match.end()
        if changed:
            rebuilt.append(html[cursor:])
            path.write_text("".join(rebuilt), encoding="utf-8")
    if failures:
        raise RuntimeError("Final JSON-LD kalite sözleşmesi başarısız:\n- " + "\n- ".join(failures[:50]))
    return repairs


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


def make_scrollable_regions_accessible(site: Path) -> int:
    """CSS ile kaydırılabilen tablo sarmalayıcılarını klavyeyle odaklanabilir yapar."""
    changed_files = 0

    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        additions: list[str] = []
        if not re.search(r"\btabindex\s*=", attrs, re.I):
            additions.append('tabindex="0"')
        if not re.search(r"\brole\s*=", attrs, re.I):
            additions.append('role="region"')
        if not re.search(r"\baria-(?:label|labelledby)\s*=", attrs, re.I):
            additions.append('aria-label="Yatay kaydırılabilir tablo"')
        suffix = (" " + " ".join(additions)) if additions else ""
        return f'<{match.group("tag")}{attrs}{suffix}>'

    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8", errors="ignore")
        updated = TABLE_WRAP_PATTERN.sub(replace, html)
        if updated != html:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
    return changed_files


def defer_optional_runtimes(site: Path) -> tuple[int, int]:
    """Salt bağlantı sunan iki giriş sayfasında ağır zenginleştirmeleri ilk etkileşime erteler."""
    changed_files = 0
    deferred_scripts = 0
    for relative in INTERACTION_RUNTIME_TARGETS:
        path = site / relative
        if not path.is_file():
            continue
        html = path.read_text(encoding="utf-8", errors="ignore")
        if LAZY_RUNTIME_MARKER in html:
            continue
        selected: list[str] = []

        def replace(match: re.Match[str]) -> str:
            nonlocal deferred_scripts
            src = match.group("src")
            source_path = src.split("?", 1)[0].split("#", 1)[0]
            if not any(source_path.endswith(suffix) for suffix in OPTIONAL_RUNTIME_SUFFIXES):
                return match.group(0)
            selected.append(src)
            deferred_scripts += 1
            markers = " ".join(
                re.findall(r'data-alo186-[a-z0-9-]+(?:=["\'][^"\']*["\'])?', match.group(0), re.I)
            )
            marker_suffix = (" " + markers) if markers else ""
            return (
                '<script type="application/x-alo186-interaction-runtime" '
                f'data-alo186-lazy-src="{escape(src, quote=True)}"{marker_suffix}></script>'
            )

        updated = SCRIPT_SRC_PATTERN.sub(replace, html)
        if not selected:
            continue
        loader = (
            f'<script {LAZY_RUNTIME_MARKER}>'
            "(()=>{'use strict';let started=false;const load=()=>{if(started)return;started=true;"
            "const nodes=[...document.querySelectorAll('script[type=\"application/x-alo186-interaction-runtime\"][data-alo186-lazy-src]')];"
            "let index=0;const next=()=>{const node=nodes[index++];if(!node)return;const script=document.createElement('script');"
            "script.src=node.dataset.alo186LazySrc;script.async=false;script.onload=next;script.onerror=next;document.body.appendChild(script)};next()};"
            "addEventListener('pointerdown',load,{once:true,passive:true});addEventListener('touchstart',load,{once:true,passive:true});"
            "addEventListener('keydown',load,{once:true});})();"
            "</script>"
        )
        if "</body>" not in updated:
            raise RuntimeError(f"Etkileşim runtime yükleyicisi için body kapanışı yok: {relative}")
        path.write_text(updated.replace("</body>", loader + "\n</body>", 1), encoding="utf-8")
        changed_files += 1
    return changed_files, deferred_scripts


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


def has_optional_runtime(html: str) -> bool:
    """Sayfada ertelenecek kaynak veya dönüştürülmüş lazy placeholder var mı?"""
    if 'type="application/x-alo186-interaction-runtime"' in html:
        return True
    for match in SCRIPT_SRC_PATTERN.finditer(html):
        source_path = match.group("src").split("?", 1)[0].split("#", 1)[0]
        if any(source_path.endswith(suffix) for suffix in OPTIONAL_RUNTIME_SUFFIXES):
            return True
    return False


def validate(site: Path, base_path: str) -> dict:
    failures: list[str] = []
    base_path = normalize_base_path(base_path)
    indexable_count = 0
    noindex_count = 0
    html_count = 0
    json_ld_count = 0

    for path in sorted(site.rglob("*.html")):
        html_count += 1
        html = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(site).as_posix()
        if QUALITY_MARKER not in html:
            failures.append(f"Responsive kalite stili eksik: {relative}")
        if LEGACY_ORIGIN in html or LEGACY_HOST in html:
            failures.append(f"www host artifactta kaldı: {relative}")
        for index, match in enumerate(JSON_LD_PATTERN.finditer(html), start=1):
            json_ld_count += 1
            try:
                json.loads(match.group(2))
            except json.JSONDecodeError as exc:
                failures.append(
                    f"Geçersiz final JSON-LD: {relative} blok {index}, satır {exc.lineno} sütun {exc.colno}"
                )
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

    for relative in INTERACTION_RUNTIME_TARGETS:
        target = site / relative
        if not target.is_file():
            continue
        html = target.read_text(encoding="utf-8", errors="ignore")
        if has_optional_runtime(html) and LAZY_RUNTIME_MARKER not in html:
            failures.append(f"Etkileşim runtime kapısı eksik: {relative}")

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
        "jsonLdBlockCount": json_ld_count,
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
    json_ld_repairs = repair_and_validate_json_ld(site)
    origin_files_changed = normalize_live_origin(site)
    table_regions_hardened = make_scrollable_regions_accessible(site)
    deferred_runtime_pages, deferred_runtime_scripts = defer_optional_runtimes(site)
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
            "tableRegionsHardened": table_regions_hardened,
            "deferredRuntimePages": deferred_runtime_pages,
            "deferredRuntimeScripts": deferred_runtime_scripts,
            "jsonLdRepairs": json_ld_repairs,
            "personalDataFieldsAdded": 0,
            "officialAffiliationClaimed": False,
        }
        release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validation = validate(site, normalized)
    recompute_checksums(site)
    return {
        "ok": True,
        "basePath": normalized,
        "jsonLdRepairs": json_ld_repairs,
        "originFilesChanged": origin_files_changed,
        "responsiveHtmlHardened": responsive_html_hardened,
        "tableRegionsHardened": table_regions_hardened,
        "deferredRuntimePages": deferred_runtime_pages,
        "deferredRuntimeScripts": deferred_runtime_scripts,
        **validation,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final Pages artifactında canonical, JSON-LD, responsive ve klavye erişimi kalite sözleşmesini uygular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
