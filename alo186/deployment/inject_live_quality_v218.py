from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

VERSION = 218
CANONICAL_ORIGIN = "https://alo186.com"
ASSET_RELATIVE = Path("assets/alo186-live-quality-v218.css")
RECEIPT_RELATIVE = Path("live-quality-v218.json")
STYLE_MARKER = 'data-alo186-live-quality-v218="true"'

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

COPY_REPLACEMENTS = (
    (
        "Sorun sayfası aramayın. Doğru eylem yolunu seçin.",
        "Elektrik sorununu güvenli biçimde sınıflandırın; doğru sonraki adıma ilerleyin.",
    ),
    (
        "Sorun sayfası aramayın",
        "Elektrik sorununu güvenli biçimde sınıflandırın",
    ),
    ("89 rehber", "Dağıtım sektörü rehberleri"),
    ("25 rehber", "Ürün ve sistem seçimi rehberleri"),
    ("12 kaynaklı makale", "Kaynak doğrulamalı teknik makaleler"),
)
FORBIDDEN_VISIBLE_COPY = tuple(old.casefold() for old, _new in COPY_REPLACEMENTS)
PERSONAL_FIELD_TOKENS = (
    "ad-soyad", "ad_soyad", "fullname", "full-name", "email", "e-posta",
    "eposta", "telefon", "phone", "adres", "address", "konum", "location",
    "abone", "subscriber",
)
TEXT_SUFFIXES = {".html", ".htm", ".json", ".js", ".css", ".webmanifest", ".txt", ".xml"}

QUALITY_CSS = """
/* ALO186 final artifact quality v218 */
:where(main,section,article,aside,header,footer,.wrap,.shell,.grid,.card){min-width:0}
:where(h1,h2,h3,h4,p,a,button,label,summary,td,th,code,pre){overflow-wrap:anywhere}
img,video,canvas{max-width:100%;height:auto}
svg,iframe{max-width:100%}
.table-wrap,[class*="table-wrap"]{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.skip-link{position:fixed;z-index:10000;left:16px;top:16px;transform:translateY(-180%);padding:10px 14px;border:3px solid #ffbf47;border-radius:10px;background:#fff;color:#071631;font-weight:900}
.skip-link:focus{transform:none}
@media(max-width:760px){:where(button,.button,.btn,a[role="button"]){min-height:44px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
""".strip() + "\n"


@dataclass
class PageAudit:
    ids: list[str] = field(default_factory=list)
    references: list[tuple[str, str]] = field(default_factory=list)
    h1_count: int = 0
    images_missing_alt: int = 0
    personal_fields: list[str] = field(default_factory=list)
    placeholder_links: int = 0
    visible_parts: list[str] = field(default_factory=list)
    skip_depth: int = 0
    has_viewport: bool = False
    has_title: bool = False
    description_count: int = 0
    canonical_values: list[str] = field(default_factory=list)
    robots_values: list[str] = field(default_factory=list)
    lang: str = ""
    main_ids: set[str] = field(default_factory=set)
    skip_targets: list[str] = field(default_factory=list)

    @property
    def visible_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.visible_parts)).strip()


class AuditParser(HTMLParser):
    SKIP_TEXT = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.page = PageAudit()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.casefold()
        values = {str(key).casefold(): (value or "") for key, value in attrs}
        if name == "html":
            self.page.lang = values.get("lang", "")
        if name in self.SKIP_TEXT:
            self.page.skip_depth += 1
        identifier = values.get("id")
        if identifier:
            self.page.ids.append(identifier)
        if name == "main" and identifier:
            self.page.main_ids.add(identifier)
        if name == "h1":
            self.page.h1_count += 1
        if name == "title":
            self.page.has_title = True
        if name == "meta":
            meta_name = values.get("name", "").casefold()
            content = values.get("content", "")
            if meta_name == "viewport" and "width=device-width" in content.casefold():
                self.page.has_viewport = True
            elif meta_name == "description" and content.strip():
                self.page.description_count += 1
            elif meta_name == "robots":
                self.page.robots_values.append(content)
        if name == "link" and "canonical" in values.get("rel", "").casefold().split() and values.get("href"):
            self.page.canonical_values.append(values["href"])
        for attribute in ("href", "src", "action", "poster", "data-src", "data-href"):
            reference = values.get(attribute)
            if reference:
                self.page.references.append((attribute, reference))
                if attribute == "href" and reference.strip() == "#":
                    self.page.placeholder_links += 1
        if name == "a" and "skip-link" in values.get("class", "").split():
            target = values.get("href", "")
            if target.startswith("#") and len(target) > 1:
                self.page.skip_targets.append(target[1:])
        if name == "img" and "alt" not in values:
            self.page.images_missing_alt += 1
        if name in {"input", "select", "textarea"}:
            field_type = values.get("type", "").casefold()
            identity = " ".join((values.get("name", ""), values.get("id", ""), values.get("autocomplete", ""))).casefold()
            if field_type in {"email", "tel"} or any(token in identity for token in PERSONAL_FIELD_TOKENS):
                self.page.personal_fields.append(identity.strip() or field_type)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in self.SKIP_TEXT and self.page.skip_depth:
            self.page.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.page.skip_depth and data.strip():
            self.page.visible_parts.append(data)


def parse_html(path: Path) -> PageAudit:
    parser = AuditParser()
    parser.feed(path.read_text(encoding="utf-8", errors="strict"))
    parser.close()
    return parser.page


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def route_file(site: Path, route: str, base_path: str = "") -> Path | None:
    clean = unquote(urlsplit(route).path or "/")
    if base_path and (clean == base_path or clean.startswith(base_path + "/")):
        clean = clean[len(base_path):] or "/"
    if clean == "/":
        candidate = site / "index.html"
        return candidate if candidate.is_file() else None
    target = site / clean.lstrip("/")
    for candidate in (target, target / "index.html", Path(str(target) + ".html")):
        if candidate.is_file():
            return candidate
    return None


def resolve_reference(site: Path, source: Path, reference: str, base_path: str) -> tuple[Path | None, str]:
    parsed = urlsplit(reference)
    if reference.startswith(("mailto:", "tel:", "javascript:", "data:", "blob:")):
        return None, ""
    if reference.startswith("#"):
        return source, parsed.fragment
    if parsed.scheme:
        host = (parsed.hostname or "").casefold().removeprefix("www.")
        if host != "alo186.com":
            return None, ""
        reference_path = parsed.path or "/"
    elif reference.startswith("//"):
        return None, ""
    else:
        reference_path = parsed.path
    if not reference_path:
        return source, parsed.fragment
    if reference_path.startswith("/"):
        return route_file(site, reference_path, base_path), parsed.fragment
    parent = source.relative_to(site).parent.as_posix()
    normalized = posixpath.normpath(posixpath.join("/" + parent, unquote(reference_path)))
    return route_file(site, normalized, ""), parsed.fragment


def normalize_project_links(site: Path, base_path: str) -> dict[str, int]:
    base = normalize_base_path(base_path)
    patterns = [("/chatgpt/chatgpt/", "/chatgpt/")]
    if base:
        patterns.append((base + base + "/", base + "/"))
    changed = replacements = 0
    for path in sorted(item for item in site.rglob("*") if item.is_file() and item.suffix.lower() in TEXT_SUFFIXES):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = text
        count = 0
        for old, new in patterns:
            found = updated.count(old)
            if found:
                updated = updated.replace(old, new)
                count += found
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            replacements += count
    return {"changedFiles": changed, "rewrittenReferences": replacements}


def normalize_visible_copy(site: Path) -> dict[str, object]:
    changed = replacements = 0
    detail: dict[str, int] = {}
    for path in sorted(site.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="strict")
        updated = text
        for old, new in COPY_REPLACEMENTS:
            found = updated.count(old)
            if found:
                updated = updated.replace(old, new)
                detail[old] = detail.get(old, 0) + found
                replacements += found
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return {"changedFiles": changed, "replacementCount": replacements, "replacements": detail}


def ensure_skip_links(site: Path, base_path: str) -> dict[str, int]:
    injected = existing = 0
    for route in CRITICAL_ROUTES:
        path = route_file(site, route, base_path)
        if path is None:
            continue
        html = path.read_text(encoding="utf-8")
        audit = parse_html(path)
        if audit.skip_targets:
            existing += 1
            continue
        main_match = re.search(r"<main\b([^>]*)>", html, re.I)
        body_match = re.search(r"<body\b[^>]*>", html, re.I)
        if not main_match or not body_match:
            continue
        attrs = main_match.group(1)
        id_match = re.search(r"\bid=[\"']([^\"']+)[\"']", attrs, re.I)
        target_id = id_match.group(1) if id_match else "main-content"
        if not id_match:
            replacement = "<main" + attrs + f' id="{target_id}">'
            html = html[:main_match.start()] + replacement + html[main_match.end():]
            body_match = re.search(r"<body\b[^>]*>", html, re.I)
        skip = f'<a class="skip-link" href="#{target_id}">İçeriğe geç</a>'
        html = html[:body_match.end()] + "\n" + skip + html[body_match.end():]
        path.write_text(html, encoding="utf-8")
        injected += 1
    return {"injected": injected, "alreadyPresent": existing}


def install_quality_css(site: Path) -> dict[str, object]:
    target = site / ASSET_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(QUALITY_CSS, encoding="utf-8")
    link = f'<link rel="stylesheet" href="/{ASSET_RELATIVE.as_posix()}" {STYLE_MARKER}>'
    injected = existing = 0
    missing: list[str] = []
    for path in sorted(site.rglob("*.html")):
        html = path.read_text(encoding="utf-8")
        if STYLE_MARKER in html:
            existing += 1
            continue
        updated, count = re.subn(r"</head\s*>", link + "\n</head>", html, count=1, flags=re.I)
        if count != 1:
            missing.append(path.relative_to(site).as_posix())
            continue
        path.write_text(updated, encoding="utf-8")
        injected += 1
    if missing:
        raise RuntimeError("Live quality CSS head kapanışı eksik: " + ", ".join(missing[:30]))
    return {"asset": f"/{ASSET_RELATIVE.as_posix()}", "injectedPages": injected, "alreadyPresent": existing}


def audit_site(site: Path, base_path: str, *, final_mode: bool) -> dict[str, object]:
    failures: list[str] = []
    pages = sorted(site.rglob("*.html"))
    audits = {path: parse_html(path) for path in pages}
    broken_global: list[str] = []
    broken_critical: list[str] = []
    canonical_errors: list[str] = []
    copy_errors: list[str] = []
    critical_paths: dict[Path, str] = {}

    for route in CRITICAL_ROUTES:
        path = route_file(site, route, base_path)
        if path is None:
            failures.append(f"kritik rota eksik: {route}")
        else:
            critical_paths[path.resolve()] = route

    id_cache = {path: set(audit.ids) for path, audit in audits.items()}
    for path, audit in audits.items():
        relative = path.relative_to(site).as_posix()
        noindex = any("noindex" in value.casefold() for value in audit.robots_values)
        if not noindex:
            if len(audit.canonical_values) != 1:
                canonical_errors.append(f"{relative}: canonical sayısı={len(audit.canonical_values)}")
            else:
                canonical = urlsplit(audit.canonical_values[0])
                if canonical.scheme != "https" or canonical.hostname != "alo186.com":
                    canonical_errors.append(f"{relative}: canonical={audit.canonical_values[0]}")
        visible = audit.visible_text.casefold()
        for forbidden in FORBIDDEN_VISIBLE_COPY:
            if forbidden in visible:
                copy_errors.append(f"{relative}: {forbidden}")
        for attribute, reference in audit.references:
            target, fragment = resolve_reference(site, path, reference, base_path)
            parsed = urlsplit(reference)
            if target is None:
                if parsed.scheme or reference.startswith(("//", "mailto:", "tel:", "javascript:", "data:", "blob:")):
                    continue
                item = f"{relative}: {attribute}={reference}"
                broken_global.append(item)
                if path.resolve() in critical_paths:
                    broken_critical.append(item)
                continue
            if fragment and fragment not in id_cache.get(target, set()):
                item = f"{relative}: eksik fragment #{fragment}"
                broken_global.append(item)
                if path.resolve() in critical_paths:
                    broken_critical.append(item)

    for path_resolved, route in critical_paths.items():
        path = Path(path_resolved)
        audit = audits[path]
        relative = path.relative_to(site).as_posix()
        if audit.h1_count != 1:
            failures.append(f"{relative}: h1 sayısı={audit.h1_count}")
        if not audit.has_title or not audit.has_viewport or audit.description_count != 1:
            failures.append(f"{relative}: title/viewport/description sözleşmesi eksik")
        if not audit.lang:
            failures.append(f"{relative}: html lang eksik")
        if not audit.main_ids:
            failures.append(f"{relative}: main id eksik")
        if not audit.skip_targets or not any(target in audit.main_ids for target in audit.skip_targets):
            failures.append(f"{relative}: skip-link hedefi eksik")
        if audit.personal_fields:
            failures.append(f"{relative}: kişisel veri alanı={audit.personal_fields[:5]}")
        if audit.images_missing_alt:
            failures.append(f"{relative}: alt metni eksik görsel={audit.images_missing_alt}")
        if audit.placeholder_links:
            failures.append(f"{relative}: href=# placeholder={audit.placeholder_links}")

    failures.extend(canonical_errors)
    failures.extend(copy_errors)
    if final_mode:
        failures.extend(f"kritik kırık iç bağlantı: {item}" for item in broken_critical[:100])

    sitemap = site / "sitemap.xml"
    sitemap_count = 0
    if not sitemap.is_file():
        failures.append("sitemap.xml eksik")
    else:
        root = ElementTree.parse(sitemap).getroot()
        locations = [node.text or "" for node in root.findall(".//{*}loc")]
        sitemap_count = len(locations)
        if len(locations) != len(set(locations)):
            failures.append("sitemap.xml yinelenen URL içeriyor")
        for location in locations:
            parsed = urlsplit(location)
            if parsed.scheme != "https" or parsed.hostname != "alo186.com":
                failures.append(f"sitemap canonical origin yanlış: {location}")
            elif route_file(site, parsed.path, "") is None:
                failures.append(f"sitemap fiziksel rota eksik: {location}")

    if failures:
        raise AssertionError(json.dumps({"ok": False, "failures": failures[:200]}, ensure_ascii=False, indent=2))

    return {
        "ok": True,
        "version": VERSION,
        "htmlFileCount": len(pages),
        "criticalPageCount": len(critical_paths),
        "globalBrokenInternalLinkCount": len(broken_global),
        "criticalBrokenInternalLinkCount": len(broken_critical),
        "canonicalViolations": len(canonical_errors),
        "forbiddenVisibleCopyHits": len(copy_errors),
        "imagesMissingAltGlobal": sum(audit.images_missing_alt for audit in audits.values()),
        "sitemapUrlCount": sitemap_count,
        "strictCriticalInternalLinks": final_mode,
        "horizontalOverflowHidden": False,
        "horizontalOverflowClipped": False,
    }


def recompute_checksums(site: Path) -> None:
    checksum = site / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines = []
    for path in sorted(item for item in site.rglob("*") if item.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(site).as_posix()}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(site: Path, base_path: str = "") -> dict[str, object]:
    resolved = site.resolve()
    base = normalize_base_path(base_path)
    final_mode = (resolved / "pages-release.json").is_file()
    report = {
        "version": VERSION,
        "basePath": base,
        "finalArtifact": final_mode,
        "projectLinkNormalization": normalize_project_links(resolved, base),
        "copyNormalization": normalize_visible_copy(resolved),
        "skipLinks": ensure_skip_links(resolved, base),
        "css": install_quality_css(resolved),
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
        "newCommerceLinksAdded": False,
    }
    report["audit"] = audit_site(resolved, base, final_mode=final_mode)
    (resolved / RECEIPT_RELATIVE).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name in ("alo186-release.json", "pages-release.json"):
        path = resolved / name
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["liveQualityV218"] = report
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    recompute_checksums(resolved)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 final artifact UX, link, canonical ve kopya kalite kapısı v218")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
