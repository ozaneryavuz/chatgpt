from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

CANONICAL_ORIGIN = "https://alo186.com"
LEGACY_ORIGIN = "https://www.alo186.com"
CSS_FILE = "alo186-live-quality.css"
CSS_MARKER = 'data-alo186-live-quality="true"'
TEXT_SUFFIXES = {".html", ".htm", ".xml", ".txt", ".json", ".js", ".css", ".webmanifest"}
DAMAGE_TERMS = re.compile(r"\b(cihaz|teçhizat|techizat|hasar|zarar)\w*\b", re.IGNORECASE)
APPLICATION_TERMS = re.compile(
    r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*",
    re.IGNORECASE,
)
RESPONSE_TERMS = re.compile(
    r"\b(cevap|yanıt|bildir|haklı bulun|ret|redd|teknik rapor)\w*",
    re.IGNORECASE,
)
STALE_DEADLINE = re.compile(
    r"\b(?:10\s*iş\s*gün|on\s*iş\s*gün)(?:ü|lük|de|den|içinde|icerisinde|içerisinde)?\b",
    re.IGNORECASE,
)
CURRENT_DEADLINE = re.compile(
    r"\b30\s*(?:takvim\s*)?gün(?:lük|ü|ün|de|den|içinde)?\b",
    re.IGNORECASE,
)
# Compatibility for v2 and any external callers that still import the old name.
WRONG_DEADLINE = STALE_DEADLINE
CANONICAL_RE = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\'][^>]*>',
    re.IGNORECASE,
)

QUALITY_CSS = r"""
/* ALO186 canlı teknik kalite katmanı — güvenli, içerikten bağımsız düzeltmeler */
html{-webkit-text-size-adjust:100%;text-size-adjust:100%;scroll-padding-top:5rem}
img,svg,video,canvas{max-width:100%;height:auto}
main,section,article,aside,nav,header,footer,form,fieldset,div{min-width:0}
h1,h2,h3,h4,p,li,dd,dt,a,button,label,summary,small,strong,span{overflow-wrap:anywhere}
a,button,input,select,textarea,summary,[role="button"]{touch-action:manipulation}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,summary:focus-visible,[role="button"]:focus-visible{outline:4px solid #ffbf47!important;outline-offset:3px!important}
.amazon-intent-card small{color:#514b44!important;font-size:max(.875rem,14px)!important;line-height:1.45}
.amazon-intent-card a[href]{min-height:44px;align-items:center;padding-block:.5rem}
[class*="heroProof"] span{color:#454a45!important;font-size:max(.875rem,14px)!important;line-height:1.45}
[class*="taskTop"]>span{color:#5d390d!important;font-size:max(.875rem,14px)!important;font-weight:750}
[class*="taskCard"] small,[class*="task-card"] small{color:#484d48!important;font-size:max(.875rem,14px)!important;line-height:1.45}
[class*="answerList"]>article>span{color:#5d390d!important;font-size:max(.875rem,14px)!important;font-weight:750}
#analytics-preferences-open,button[data-analytics-choice]{min-height:44px;font-size:max(.875rem,14px)!important;line-height:1.35}
@media(max-width:760px){
  nav a,.button,.btn,button,summary,[role="button"],input[type="submit"],input[type="button"]{min-height:44px}
  button,.button,.btn,[role="button"]{max-width:100%;white-space:normal}
  input,select,textarea,button{font-size:16px}
  :where(header) a[href]{display:inline-flex;align-items:center;justify-content:center;min-width:44px;min-height:44px}
  :where(.hero-card)>a[href]{display:inline-flex;align-items:center;min-height:44px;padding-block:.55rem}
  :where(.popular) button{min-height:44px;font-size:16px!important}
  h1{font-size:clamp(1.85rem,9vw,3rem);overflow-wrap:break-word}
  table{max-width:100%}
  .table-wrap,[class*="table-wrap"]{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
""".strip() + "\n"


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.canonical: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "link" and (values.get("rel") or "").casefold() == "canonical":
            self.canonical = values.get("href")
        for key in ("href", "src", "poster", "data-src"):
            value = values.get(key)
            if value:
                self.references.append((key, value))


def normalize_base_path(value: str) -> str:
    cleaned = str(value or "").strip()
    return "" if not cleaned or cleaned == "/" else "/" + cleaned.strip("/")


def public_url(base_path: str, route: str) -> str:
    route = "/" + route.lstrip("/")
    return f"{base_path}{route}" if base_path else route


def iter_text_files(site: Path):
    for path in sorted(site.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".htaccess" or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def route_exists(site: Path, route: str) -> bool:
    path = urlsplit(str(route or "")).path or "/"
    if path == "/":
        return (site / "index.html").is_file()
    target = site / path.lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def normalize_text(text: str) -> str:
    text = text.replace(LEGACY_ORIGIN, CANONICAL_ORIGIN)
    # Only known obsolete application wording is migrated. The valid 10-business-day
    # response period after a rejected claim must remain untouched.
    text = text.replace(
        "zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde",
        "zararın ortaya çıktığı tarihten itibaren 30 gün içinde",
    )
    text = text.replace(
        "Zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde",
        "Zararın ortaya çıktığı tarihten itibaren 30 gün içinde",
    )
    text = text.replace(
        "10 iş günü içinde EDAŞ kaydı açın",
        "30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    text = text.replace(
        "ilgili dağıtım şirketine kayıtlı başvuru yapmalı",
        "ilgili dağıtım şirketinin resmî kanalına başvurmalı",
    )
    text = text.replace("!^www\\.alo186\\.com$", "!^alo186\\.com$")
    text = text.replace("canonical www", "canonical apex")
    text = text.replace("www host", "apex host")
    return text


def inject_stylesheet(html: str, href: str) -> tuple[str, bool]:
    if CSS_MARKER in html:
        return html, False
    if "</head>" not in html.casefold():
        return html, False
    tag = f'<link rel="stylesheet" href="{href}" {CSS_MARKER}>'
    updated, count = re.subn(r"</head>", tag + "\n</head>", html, count=1, flags=re.IGNORECASE)
    return updated, bool(count)


def wrong_deadline_contexts(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    contexts: list[str] = []
    for match in STALE_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 280)
        end = min(len(normalized), match.end() + 280)
        context = normalized[start:end]
        if (
            DAMAGE_TERMS.search(context)
            and APPLICATION_TERMS.search(context)
            and not RESPONSE_TERMS.search(context)
        ):
            contexts.append(context[:560])
    return contexts


def current_deadline_contexts(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    contexts: list[str] = []
    for match in CURRENT_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 280)
        end = min(len(normalized), match.end() + 280)
        context = normalized[start:end]
        if DAMAGE_TERMS.search(context) and APPLICATION_TERMS.search(context):
            contexts.append(context[:560])
    return contexts


def update_release(path: Path, base_path: str) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["canonicalHost"] = CANONICAL_ORIGIN
    payload["liveTechnicalQuality"] = {
        "version": 1,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "servingOrigin": CANONICAL_ORIGIN,
        "responsiveOverflowGuard": True,
        "minimumTouchTargetCssPx": 44,
        "focusVisible": True,
        "knownContrastSelectorsHardened": [
            ".amazon-intent-card small",
            "[class*=heroProof] span",
            "[class*=taskTop]>span",
            "[class*=taskCard] small",
        ],
        "deviceDamageDeadline": "30 gün",
        "officialInstitutionClaimed": False,
        "personalDataCollectionAdded": False,
        "stylesheet": public_url(base_path, f"/{CSS_FILE}"),
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


def validate(site: Path, base_path: str) -> dict:
    failures: list[str] = []
    html_count = 0
    canonical_count = 0
    reference_count = 0
    current_deadline_count = 0
    css_href = public_url(base_path, f"/{CSS_FILE}")

    if not (site / CSS_FILE).is_file():
        failures.append(f"Canlı kalite CSS dosyası eksik: {CSS_FILE}")

    for path in iter_text_files(site):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_ORIGIN in text:
            failures.append(f"Eski www origin kaldı: {path.relative_to(site)}")
        for context in wrong_deadline_contexts(text):
            failures.append(f"Yanlış cihaz hasarı süresi: {path.relative_to(site)} → {context}")
        current_deadline_count += len(current_deadline_contexts(text))
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        html_count += 1
        if CSS_MARKER not in text or css_href not in text:
            failures.append(f"Canlı kalite stylesheet bağlantısı eksik: {path.relative_to(site)}")
        parser = ReferenceParser()
        parser.feed(text)
        if parser.canonical:
            canonical_count += 1
            if not parser.canonical.startswith(CANONICAL_ORIGIN + "/") and parser.canonical != CANONICAL_ORIGIN:
                failures.append(f"Canonical origin yanlış: {path.relative_to(site)} → {parser.canonical}")
        for kind, reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme or reference.startswith(("//", "mailto:", "tel:", "javascript:", "data:", "blob:", "#")):
                continue
            reference_count += 1
            internal = parsed.path
            if base_path and internal.startswith(base_path + "/"):
                internal = internal[len(base_path):]
            if kind == "href" and internal and not Path(internal).suffix and not route_exists(site, internal):
                failures.append(f"İç bağlantı hedefi eksik: {path.relative_to(site)} → {reference}")
            if kind in {"src", "poster", "data-src"} or (kind == "href" and Path(internal).suffix):
                target = site / internal.lstrip("/")
                if internal and not target.is_file():
                    failures.append(f"Asset hedefi eksik: {path.relative_to(site)} → {reference}")

    if current_deadline_count == 0:
        failures.append("Cihaz hasarı başvurusunu yürürlükteki 30 güne bağlayan yayın metni bulunamadı")

    for release_name in ("alo186-release.json", "pages-release.json"):
        release_path = site / release_name
        if release_path.is_file():
            release = json.loads(release_path.read_text(encoding="utf-8"))
            if release.get("canonicalHost") != CANONICAL_ORIGIN:
                failures.append(f"{release_name} canonicalHost apex değil")
            quality = release.get("liveTechnicalQuality") or {}
            if quality.get("minimumTouchTargetCssPx") != 44:
                failures.append(f"{release_name} canlı kalite sözleşmesi eksik")
            if quality.get("deviceDamageDeadline") != "30 gün":
                failures.append(f"{release_name} cihaz hasarı süre sözleşmesi yanlış")

    core_release = site / "alo186-release.json"
    route_count = 0
    if core_release.is_file():
        release = json.loads(core_release.read_text(encoding="utf-8"))
        routes = release.get("routes") or []
        route_count = len(routes)
        for item in routes:
            route = item.get("canonicalPath") if isinstance(item, dict) else None
            if route and not route_exists(site, route):
                failures.append(f"Release rotası fiziksel olarak eksik: {route}")

    robots = site / "robots.txt"
    if robots.is_file() and f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        failures.append("robots.txt apex sitemap adresini taşımıyor")
    sitemap = site / "sitemap.xml"
    if sitemap.is_file():
        sitemap_text = sitemap.read_text(encoding="utf-8")
        if LEGACY_ORIGIN in sitemap_text or CANONICAL_ORIGIN not in sitemap_text:
            failures.append("sitemap.xml apex canonical origin sözleşmesi başarısız")

    if failures:
        raise RuntimeError("ALO186 canlı kalite hardening doğrulaması başarısız:\n- " + "\n- ".join(failures[:100]))
    return {
        "ok": True,
        "canonicalOrigin": CANONICAL_ORIGIN,
        "basePath": base_path,
        "htmlCount": html_count,
        "canonicalCount": canonical_count,
        "checkedReferences": reference_count,
        "releaseRouteCount": route_count,
        "deviceDamageDeadline": "30 gün",
        "deviceDamageDeadlineContexts": current_deadline_count,
        "minimumTouchTargetCssPx": 44,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    base_path = normalize_base_path(base_path)
    if not site.is_dir():
        raise FileNotFoundError(f"Yayın artifactı bulunamadı: {site}")

    (site / CSS_FILE).write_text(QUALITY_CSS, encoding="utf-8")
    css_href = public_url(base_path, f"/{CSS_FILE}")
    changed_text_files = 0
    injected_pages = 0

    for path in list(iter_text_files(site)):
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = normalize_text(original)
        if path.suffix.lower() in {".html", ".htm"}:
            updated, injected = inject_stylesheet(updated, css_href)
            injected_pages += int(injected)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed_text_files += 1

    update_release(site / "alo186-release.json", base_path)
    update_release(site / "pages-release.json", base_path)
    recompute_checksums(site)
    result = validate(site, base_path)
    result.update({"changedTextFiles": changed_text_files, "stylesheetsInjected": injected_pages})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı artifactına apex canonical, erişilebilirlik ve hukukî süre hardening uygular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
