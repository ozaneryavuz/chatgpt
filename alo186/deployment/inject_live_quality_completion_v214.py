from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

import inject_live_quality_hardening_v2 as previous

VERSION = 214
CANONICAL_ORIGIN = "https://alo186.com"
CSS_FILE = "alo186-live-quality.css"
CSS_MARKER = "/* ALO186 live quality completion v214 */"
RECEIPT_FILE = "live-quality-v214.json"

CRITICAL_ROUTES = (
    "/",
    "/elektrik-portali/",
    "/edas-bul/",
    "/elektrik-durum-merkezi/",
    "/hesaplama/",
    "/amazon-elektrik-urunleri/",
    "/akilli-urun-secimi/",
    "/urun-bilgi-grafigi/",
    "/arama/",
)

COPY_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (
        "Sorun sayfası aramayın. Doğru eylem yolunu seçin.",
        "Elektrik sorununu güvenli biçimde sınıflandırın; doğru sonraki adıma ilerleyin.",
    ),
    (
        "Sorun sayfası aramayın",
        "Elektrik sorununu güvenli biçimde sınıflandırın",
    ),
    (
        "zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın",
        "zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    ),
    (
        "Zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın",
        "Zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    ),
    ("89 rehber", "Dağıtım sektörü rehberleri"),
    ("25 rehber", "Ürün ve sistem seçimi rehberleri"),
    ("12 kaynaklı makale", "Kaynak doğrulamalı teknik makaleler"),
)

FORBIDDEN_VISIBLE_COPY = (
    "sorun sayfası aramayın",
    "30 gün içinde edaş kaydı açın",
    "89 rehber",
    "25 rehber",
    "12 kaynaklı makale",
)

PERSONAL_FIELD_TOKENS = (
    "ad-soyad",
    "ad_soyad",
    "fullname",
    "full-name",
    "email",
    "e-posta",
    "eposta",
    "telefon",
    "phone",
    "adres",
    "address",
    "konum",
    "location",
    "abone",
    "subscriber",
)

TEXT_SUFFIXES = {".html", ".htm", ".json", ".js", ".css", ".webmanifest", ".txt", ".xml"}

COMPLETION_CSS = f"""
{CSS_MARKER}
html{{overflow-x:clip}}
body{{min-width:320px}}
:where(main,section,article,aside,header,footer,.wrap,.shell,.grid,.card){{min-width:0}}
:where(h1,h2,h3,h4,p,a,button,label,summary,td,th,code,pre){{overflow-wrap:anywhere}}
img,video,canvas{{max-width:100%;height:auto}}
svg,iframe{{max-width:100%}}
.table-wrap,[class*="table-wrap"]{{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}}
.skip-link{{position:fixed;z-index:10000;left:16px;top:16px;transform:translateY(-180%);padding:10px 14px;border:3px solid #ffbf47;border-radius:10px;background:#fff;color:#071631;font-weight:900}}
.skip-link:focus{{transform:none}}
@media(max-width:760px){{:where(button,.button,.btn,a[role="button"]){{min-height:44px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}*,*::before,*::after{{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}}}
""".strip() + "\n"


class DocumentAuditParser(HTMLParser):
    SKIP_TEXT = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.srcsets: list[str] = []
        self.h1_count = 0
        self.images = 0
        self.images_missing_alt = 0
        self.images_missing_dimensions = 0
        self.forms = 0
        self.personal_fields: list[str] = []
        self.placeholder_links = 0
        self.visible_parts: list[str] = []
        self.skip_depth = 0
        self.has_viewport = False
        self.has_title = False
        self.description_count = 0
        self.canonical_values: list[str] = []
        self.robots_values: list[str] = []
        self.lang = ""
        self.main_ids: set[str] = set()
        self.skip_targets: list[str] = []
        self.head_external_blocking_scripts = 0
        self.in_head = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.casefold()
        values = {str(key).casefold(): (value or "") for key, value in attrs}
        if name == "html":
            self.lang = values.get("lang", "")
        if name == "head":
            self.in_head = True
        if name in self.SKIP_TEXT:
            self.skip_depth += 1
        identifier = values.get("id")
        if identifier:
            self.ids.append(identifier)
        if name == "main" and identifier:
            self.main_ids.add(identifier)
        if name == "h1":
            self.h1_count += 1
        if name == "title":
            self.has_title = True
        if name == "meta":
            meta_name = values.get("name", "").casefold()
            if meta_name == "viewport" and "width=device-width" in values.get("content", "").casefold():
                self.has_viewport = True
            elif meta_name == "description" and values.get("content", "").strip():
                self.description_count += 1
            elif meta_name == "robots":
                self.robots_values.append(values.get("content", ""))
        if name == "link" and values.get("rel", "").casefold() == "canonical" and values.get("href"):
            self.canonical_values.append(values["href"])
        for attribute in ("href", "src", "action", "poster", "data-src", "data-href"):
            reference = values.get(attribute)
            if reference:
                self.links.append((attribute, reference))
                if attribute == "href" and reference.strip() == "#":
                    self.placeholder_links += 1
        if values.get("srcset"):
            self.srcsets.append(values["srcset"])
        if name == "a" and values.get("class", "").find("skip-link") >= 0:
            target = values.get("href", "")
            if target.startswith("#") and len(target) > 1:
                self.skip_targets.append(target[1:])
        if name == "img":
            self.images += 1
            if "alt" not in values:
                self.images_missing_alt += 1
            if not (values.get("width") and values.get("height")) and "aspect-ratio" not in values.get("style", ""):
                self.images_missing_dimensions += 1
        if name == "form":
            self.forms += 1
        if name in {"input", "select", "textarea"}:
            field_type = values.get("type", "").casefold()
            identity = " ".join((values.get("name", ""), values.get("id", ""), values.get("autocomplete", ""))).casefold()
            if field_type in {"email", "tel"} or any(token in identity for token in PERSONAL_FIELD_TOKENS):
                self.personal_fields.append(identity.strip() or field_type)
        if name == "script" and self.in_head and values.get("src") and not ("defer" in values or "async" in values or values.get("type") == "module"):
            self.head_external_blocking_scripts += 1

    def handle_endtag(self, tag: str) -> None:
        name = tag.casefold()
        if name in self.SKIP_TEXT and self.skip_depth:
            self.skip_depth -= 1
        if name == "head":
            self.in_head = False

    def handle_data(self, data: str) -> None:
        if not self.skip_depth and data.strip():
            self.visible_parts.append(data)

    @property
    def visible_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.visible_parts)).strip()


class SimpleHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.srcsets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {str(key).casefold(): (value or "") for key, value in attrs}
        for attribute in ("href", "src", "action", "poster", "data-src", "data-href"):
            if values.get(attribute):
                self.links.append((attribute, values[attribute]))
        if values.get("srcset"):
            self.srcsets.append(values["srcset"])


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def normalize_route(value: str) -> str:
    parsed = urlsplit(value)
    route = unquote(parsed.path or "/")
    if route != "/":
        route = "/" + route.strip("/")
    return route


def route_file(site: Path, route: str, base_path: str = "") -> Path | None:
    clean = normalize_route(route)
    if base_path and (clean == base_path or clean.startswith(base_path + "/")):
        clean = clean[len(base_path):] or "/"
    if clean == "/":
        candidate = site / "index.html"
        return candidate if candidate.is_file() else None
    target = site / clean.lstrip("/")
    candidates = [target, target / "index.html"]
    if target.suffix.lower() in {".html", ".htm"}:
        candidates.append(target.with_suffix("") / "index.html")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def resolve_reference(site: Path, source: Path, reference: str, base_path: str) -> Path | None:
    if not reference or reference.startswith(("#", "mailto:", "tel:", "javascript:", "data:", "blob:")):
        return source if reference.startswith("#") else None
    parsed = urlsplit(reference)
    if parsed.scheme:
        host = (parsed.hostname or "").casefold().removeprefix("www.")
        if host != "alo186.com":
            return None
        reference_path = parsed.path or "/"
    elif reference.startswith("//"):
        return None
    else:
        reference_path = parsed.path
    if not reference_path:
        return source
    if reference_path.startswith("/"):
        return route_file(site, reference_path, base_path)
    relative_parent = source.relative_to(site).parent.as_posix()
    normalized = posixpath.normpath(posixpath.join("/" + relative_parent, unquote(reference_path)))
    return route_file(site, normalized, "")


def apply_copy_replacements(site: Path) -> dict:
    changed_files = 0
    replacement_count = 0
    replacements: dict[str, int] = {}
    for path in sorted(item for item in site.rglob("*") if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = text
        file_changes = 0
        for old, new in COPY_REPLACEMENTS:
            count = updated.count(old)
            if count:
                updated = updated.replace(old, new)
                file_changes += count
                replacements[old] = replacements.get(old, 0) + count
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed_files += 1
            replacement_count += file_changes
    return {"changedFiles": changed_files, "replacementCount": replacement_count, "replacements": replacements}


def ensure_skip_links(site: Path, base_path: str) -> dict:
    changed = 0
    existing = 0
    for route in CRITICAL_ROUTES:
        path = route_file(site, route, base_path)
        if path is None:
            continue
        html = path.read_text(encoding="utf-8")
        parser = DocumentAuditParser(); parser.feed(html)
        if parser.skip_targets:
            existing += 1
            continue
        main_match = re.search(r"<main\b([^>]*)>", html, re.I)
        if not main_match:
            continue
        attrs = main_match.group(1)
        id_match = re.search(r"\bid=[\"']([^\"']+)[\"']", attrs, re.I)
        target_id = id_match.group(1) if id_match else "main-content"
        if not id_match:
            replacement = "<main" + attrs + f' id="{target_id}">' 
            html = html[:main_match.start()] + replacement + html[main_match.end():]
        body_match = re.search(r"<body\b[^>]*>", html, re.I)
        if body_match:
            skip = f'<a class="skip-link" href="#{target_id}">İçeriğe geç</a>'
            html = html[:body_match.end()] + "\n" + skip + html[body_match.end():]
            path.write_text(html, encoding="utf-8")
            changed += 1
    return {"injected": changed, "alreadyPresent": existing}


def append_completion_css(site: Path) -> bool:
    path = site / CSS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Final canlı kalite CSS dosyası eksik: {CSS_FILE}")
    css = path.read_text(encoding="utf-8")
    if CSS_MARKER in css:
        return False
    path.write_text(css.rstrip() + "\n\n" + COMPLETION_CSS, encoding="utf-8")
    return True


def noindex(html: str) -> bool:
    return any("noindex" in value.casefold() for value in re.findall(r'<meta\b[^>]*name=["\']robots["\'][^>]*content=["\']([^"\']*)', html, re.I))


def normalize_canonical(value: str) -> str:
    parsed = urlsplit(value)
    path = parsed.path or "/"
    if path != "/":
        path = "/" + path.strip("/")
    return f"{parsed.scheme.casefold()}://{(parsed.hostname or '').casefold()}{path}"


def audit_critical_pages(site: Path, base_path: str) -> tuple[dict, list[str]]:
    failures: list[str] = []
    results: list[dict] = []
    for route in CRITICAL_ROUTES:
        path = route_file(site, route, base_path)
        if path is None:
            failures.append(f"Kritik rota fiziksel olarak eksik: {route}")
            continue
        html = path.read_text(encoding="utf-8")
        parser = DocumentAuditParser(); parser.feed(html)
        relative = path.relative_to(site).as_posix()
        duplicates = sorted({identifier for identifier in parser.ids if parser.ids.count(identifier) > 1})
        forbidden = [term for term in FORBIDDEN_VISIBLE_COPY if term in parser.visible_text.casefold()]
        missing_skip = not parser.skip_targets or any(target not in parser.ids for target in parser.skip_targets)
        if parser.h1_count != 1:
            failures.append(f"{route}: H1 sayısı {parser.h1_count}; beklenen 1")
        if not parser.has_viewport:
            failures.append(f"{route}: width=device-width viewport eksik")
        if not parser.has_title or parser.description_count != 1:
            failures.append(f"{route}: title/meta description sözleşmesi eksik")
        if not parser.lang.casefold().startswith("tr"):
            failures.append(f"{route}: html lang=tr eksik")
        if len(parser.canonical_values) != 1:
            failures.append(f"{route}: canonical sayısı {len(parser.canonical_values)}; beklenen 1")
        elif not normalize_canonical(parser.canonical_values[0]).startswith(CANONICAL_ORIGIN):
            failures.append(f"{route}: canonical apex değil → {parser.canonical_values[0]}")
        if duplicates:
            failures.append(f"{route}: yinelenen id → {duplicates[:8]}")
        if parser.images_missing_alt:
            failures.append(f"{route}: alt niteliği olmayan {parser.images_missing_alt} görsel")
        if parser.personal_fields:
            failures.append(f"{route}: kişisel veri alanı bulundu → {parser.personal_fields[:5]}")
        if missing_skip:
            failures.append(f"{route}: çalışan içerik-atlama bağlantısı eksik")
        if forbidden:
            failures.append(f"{route}: yasaklı/eski kullanıcı kopyası → {forbidden}")
        if parser.placeholder_links:
            failures.append(f"{route}: işlevsiz href=# bağlantısı sayısı {parser.placeholder_links}")
        results.append({
            "route": route,
            "file": relative,
            "h1Count": parser.h1_count,
            "canonical": parser.canonical_values[0] if len(parser.canonical_values) == 1 else None,
            "imageCount": parser.images,
            "imagesMissingAlt": parser.images_missing_alt,
            "imagesMissingDimensions": parser.images_missing_dimensions,
            "forms": parser.forms,
            "personalDataFields": len(parser.personal_fields),
            "blockingHeadScripts": parser.head_external_blocking_scripts,
            "duplicateIds": len(duplicates),
            "forbiddenCopy": forbidden,
        })
    return {"criticalPageCount": len(results), "pages": results}, failures


def audit_internal_links(site: Path, base_path: str) -> tuple[dict, list[str]]:
    failures: list[str] = []
    checked = 0
    internal = 0
    missing: list[dict[str, str]] = []
    for path in sorted(site.rglob("*.html")):
        parser = SimpleHtmlParser(); parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
        references = list(parser.links)
        for srcset in parser.srcsets:
            for item in srcset.split(","):
                candidate = item.strip().split(" ", 1)[0]
                if candidate:
                    references.append(("srcset", candidate))
        for attribute, reference in references:
            checked += 1
            parsed = urlsplit(reference)
            if parsed.scheme and (parsed.hostname or "").casefold().removeprefix("www.") != "alo186.com":
                continue
            if reference.startswith(("//", "mailto:", "tel:", "javascript:", "data:", "blob:", "#")):
                continue
            internal += 1
            target = resolve_reference(site, path, reference, base_path)
            if target is None or not target.is_file():
                record = {"source": path.relative_to(site).as_posix(), "attribute": attribute, "reference": reference}
                missing.append(record)
    if missing:
        for item in missing[:100]:
            failures.append(f"Kırık iç bağlantı: {item['source']} [{item['attribute']}] → {item['reference']}")
    return {"referencesChecked": checked, "internalReferences": internal, "brokenInternalLinks": len(missing), "examples": missing[:20]}, failures


def audit_robots_and_sitemap(site: Path, base_path: str) -> tuple[dict, list[str]]:
    failures: list[str] = []
    robots_path = site / "robots.txt"
    sitemap_path = site / "sitemap.xml"
    if not robots_path.is_file():
        return {}, ["robots.txt eksik"]
    if not sitemap_path.is_file():
        return {}, ["sitemap.xml eksik"]
    robots = robots_path.read_text(encoding="utf-8")
    if re.search(r"^\s*Disallow:\s*/\s*$", robots, re.I | re.M):
        failures.append("robots.txt tüm siteyi engelliyor")
    if not re.search(r"^\s*Allow:\s*/\s*$", robots, re.I | re.M):
        failures.append("robots.txt Allow: / taşımıyor")
    if f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots:
        failures.append("robots.txt apex sitemap adresini taşımıyor")
    try:
        root = ElementTree.fromstring(sitemap_path.read_text(encoding="utf-8"))
    except ElementTree.ParseError as exc:
        return {}, failures + [f"sitemap.xml XML olarak ayrıştırılamadı: {exc}"]
    locs = [element.text.strip() for element in root.iter() if element.tag.casefold().endswith("loc") and element.text]
    duplicates = sorted({loc for loc in locs if locs.count(loc) > 1})
    if duplicates:
        failures.append(f"sitemap.xml yinelenen URL taşıyor: {duplicates[:8]}")
    indexable_checked = 0
    canonical_mismatches = 0
    for loc in locs:
        parsed = urlsplit(loc)
        if parsed.scheme != "https" or (parsed.hostname or "").casefold() != "alo186.com":
            failures.append(f"Sitemap apex HTTPS dışı URL taşıyor: {loc}")
            continue
        path = route_file(site, parsed.path or "/", base_path)
        if path is None:
            failures.append(f"Sitemap rotası artifactta eksik: {loc}")
            continue
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        html = path.read_text(encoding="utf-8")
        if noindex(html):
            failures.append(f"Sitemap noindex sayfa içeriyor: {loc}")
            continue
        indexable_checked += 1
        parser = DocumentAuditParser(); parser.feed(html)
        if len(parser.canonical_values) != 1 or normalize_canonical(parser.canonical_values[0]) != normalize_canonical(loc):
            canonical_mismatches += 1
            failures.append(f"Sitemap/canonical eşleşmiyor: {loc} → {parser.canonical_values}")
    return {
        "robotsAllowsAll": "Allow: /" in robots,
        "robotsApexSitemap": f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" in robots,
        "sitemapUrlCount": len(locs),
        "sitemapDuplicateUrls": len(duplicates),
        "sitemapIndexablePagesChecked": indexable_checked,
        "sitemapCanonicalMismatches": canonical_mismatches,
    }, failures


def update_release(path: Path, receipt: dict) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["liveQualityCompletionV214"] = {
        "version": VERSION,
        "copyReplacements": receipt["copyNormalization"]["replacementCount"],
        "criticalPages": receipt["criticalPages"]["criticalPageCount"],
        "brokenInternalLinks": receipt["internalLinks"]["brokenInternalLinks"],
        "sitemapUrlCount": receipt["searchDiscovery"].get("sitemapUrlCount"),
        "sitemapCanonicalMismatches": receipt["searchDiscovery"].get("sitemapCanonicalMismatches"),
        "minimumTouchTargetCssPx": 44,
        "mobileOverflowGuard": True,
        "reducedMotionGuard": True,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
        "liveCopyAcceptanceRequired": True,
        "lighthouseLabBudgetRequired": True,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    previous_result = previous.run(site, normalized)
    copy_result = apply_copy_replacements(site)
    skip_result = ensure_skip_links(site, normalized)
    css_added = append_completion_css(site)
    critical, failures = audit_critical_pages(site, normalized)
    links, link_failures = audit_internal_links(site, normalized)
    discovery, discovery_failures = audit_robots_and_sitemap(site, normalized)
    failures.extend(link_failures)
    failures.extend(discovery_failures)
    receipt = {
        "ok": not failures,
        "version": VERSION,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "basePath": normalized,
        "previousLayer": previous_result,
        "copyNormalization": copy_result,
        "skipLinks": skip_result,
        "completionCssAdded": css_added,
        "criticalPages": critical,
        "internalLinks": links,
        "searchDiscovery": discovery,
        "minimumTouchTargetCssPx": 44,
        "mobileOverflowGuard": True,
        "reducedMotionGuard": True,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
        "failures": failures[:100],
    }
    if failures:
        raise RuntimeError("ALO186 canlı kalite v214 doğrulaması başarısız:\n- " + "\n- ".join(failures[:100]))
    update_release(site / "alo186-release.json", receipt)
    update_release(site / "pages-release.json", receipt)
    (site / RECEIPT_FILE).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    recompute_checksums(site)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final artifactında kullanıcı kopyası, mobil taşma, bağlantı, canonical, sitemap, robots ve erişilebilirlik kalite kapısını uygular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
