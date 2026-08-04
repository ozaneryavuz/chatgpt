from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

CANONICAL_ORIGIN = "https://alo186.com"
REQUIRED_FILES = (
    "index.html",
    "404.html",
    ".nojekyll",
    "alo186-release.json",
    "pages-release.json",
    "route-bridges.json",
    "manifest.webmanifest",
    "alo186-mark.svg",
    "sw.js",
    "durum/index.html",
    "robots.txt",
    "sitemap.xml",
    "checksums.sha256",
)
CRITICAL_ROUTES = (
    "/elektrik-portali/",
    "/edas-bul/",
    "/karar-motoru/",
    "/hesaplama/",
    "/hesaplama/kesinti-gunlugu/",
    "/kesintiye-hazirlik-atolyesi/",
    "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/",
)
CANONICAL_METADATA_FILES = {
    "alo186-release.json",
    "pages-release.json",
    "route-bridges.json",
    "checksums.sha256",
    "robots.txt",
    "sitemap.xml",
    "manifest.webmanifest",
    "sw.js",
    "search-index.json",
}
SEARCH_INDEX_PATH = Path("arama/search-index.json")
SEARCH_FORBIDDEN_FIELDS = {
    "price",
    "stock",
    "rating",
    "seller",
    "warranty",
    "asin",
    "affiliateCommission",
}
BASE_PATH_AWARE_INLINE_SCRIPT_MARKERS = (
    "data-alo186-ga4-consent",
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.has_service_worker = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")
        if tag == "meta" and (values.get("name") or "").lower() == "robots":
            self.robots = values.get("content")
        if tag == "script" and "data-alo186-pages-sw" in values:
            self.has_service_worker = True
        for key in ("href", "src", "action", "poster", "data-src", "data-href"):
            value = values.get(key)
            if value:
                self.references.append((key, value))
        srcset = values.get("srcset")
        if srcset:
            for item in srcset.split(","):
                candidate = item.strip().split(" ", 1)[0]
                if candidate:
                    self.references.append(("srcset", candidate))


def normalize_base_path(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def strip_base_path(path: str, base_path: str) -> str | None:
    if not path.startswith("/"):
        return path
    if not base_path:
        return path
    if path == base_path:
        return "/"
    if path.startswith(base_path + "/"):
        return path[len(base_path) :]
    return None


def normalize_canonical_path(value: str, base_path: str) -> str:
    path = urlsplit(str(value or "")).path or "/"
    stripped = strip_base_path(path, base_path)
    return stripped if stripped is not None else path


def public_url(base_path: str, route: str) -> str:
    if not route.startswith("/"):
        route = "/" + route
    if not base_path:
        return route
    if route == "/":
        return base_path + "/"
    return base_path + route


def executable_html_text(text: str) -> str:
    """Return executable inline bodies, excluding explicitly base-path-aware runtimes."""
    chunks: list[str] = []
    script_pattern = re.compile(
        r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>",
        re.IGNORECASE | re.DOTALL,
    )
    for match in script_pattern.finditer(text):
        attrs = match.group("attrs").casefold()
        body = match.group("body")
        is_marked_base_path_runtime = any(
            marker in attrs for marker in BASE_PATH_AWARE_INLINE_SCRIPT_MARKERS
        ) and re.search(r"\bconst\s+BASE\s*=", body)
        if is_marked_base_path_runtime:
            continue
        chunks.append(body)
    chunks.extend(re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.IGNORECASE | re.DOTALL))
    return "\n".join(chunks)


def route_exists(site: Path, route: str) -> bool:
    clean = urlsplit(route).path or "/"
    if clean == "/":
        return (site / "index.html").is_file()
    target = site / clean.lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_search_index(
    site: Path,
    base_path: str,
    core_release: dict,
    pages_release: dict,
    failures: list[str],
) -> int:
    index_path = site / SEARCH_INDEX_PATH
    if not index_path.is_file():
        if core_release.get("siteSearch") or pages_release.get("siteSearch"):
            failures.append("Release metadata teknik arama bildiriyor fakat search-index.json eksik")
        return 0

    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"Teknik arama indeksi geçersiz JSON: {exc}")
        return 0

    entries = payload.get("entries")
    if not isinstance(entries, list):
        failures.append("Teknik arama indeksi entries alanı liste değil")
        return 0
    if payload.get("entryCount") != len(entries):
        failures.append("Teknik arama indeksi entryCount gerçek kayıt sayısıyla eşleşmiyor")

    declared_exclusions = payload.get("commercialRankingExcluded")
    expected_exclusions = ["price", "stock", "rating", "seller", "warranty", "affiliateCommission"]
    if declared_exclusions != expected_exclusions:
        failures.append("Teknik arama ticari sıralama dışlama sözleşmesi değişmiş")

    aliases: set[str] = set()
    consolidation = core_release.get("contentConsolidation") or {}
    for item in consolidation.get("aliases") or []:
        if isinstance(item, dict) and item.get("aliasPath"):
            aliases.add(normalize_canonical_path(item["aliasPath"], base_path))

    canonical_paths: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            failures.append(f"Teknik arama kaydı nesne değil: sıra={index}")
            continue
        canonical = normalize_canonical_path(entry.get("canonicalPath"), base_path)
        if not canonical.startswith("/") or canonical == "/arama/":
            failures.append(f"Teknik arama canonicalPath geçersiz: {entry.get('canonicalPath')!r}")
            continue
        if canonical in canonical_paths:
            failures.append(f"Teknik arama indeksinde yinelenen canonicalPath: {canonical}")
        canonical_paths.add(canonical)
        if canonical in aliases:
            failures.append(f"Canonical alias teknik arama indeksine sızmış: {canonical}")

        expected_url = public_url(base_path, canonical)
        if entry.get("url") != expected_url:
            failures.append(
                f"Teknik arama base-path URL eşleşmiyor: {canonical} → {entry.get('url')!r}, beklenen={expected_url!r}"
            )
        if not route_exists(site, canonical):
            failures.append(f"Teknik arama kaydının fiziksel rotası eksik: {canonical}")
        forbidden = SEARCH_FORBIDDEN_FIELDS.intersection(entry.keys())
        if forbidden:
            failures.append(f"Teknik arama kaydında ticari alan bulundu: {canonical} → {sorted(forbidden)}")

    core_search = core_release.get("siteSearch") or {}
    pages_search = pages_release.get("siteSearch") or {}
    if core_search:
        if core_search.get("entryCount") != len(entries):
            failures.append("alo186-release siteSearch entryCount eşleşmiyor")
        if core_search.get("rawQueryStored") is not False:
            failures.append("alo186-release teknik arama ham sorgu saklamamalı")
        if core_search.get("commercialRankingUsed") is not False:
            failures.append("alo186-release teknik arama ticari sıralama kullanmamalı")
    if pages_search:
        if pages_search.get("entryCount") != len(entries):
            failures.append("pages-release siteSearch entryCount eşleşmiyor")
        if pages_search.get("route") != public_url(base_path, "/arama/"):
            failures.append("pages-release teknik arama rotası base-path ile uyumsuz")
        if pages_search.get("index") != public_url(base_path, "/arama/search-index.json"):
            failures.append("pages-release teknik arama indeks rotası base-path ile uyumsuz")
        if pages_search.get("rawQueryStored") is not False:
            failures.append("pages-release teknik arama ham sorgu saklamamalı")

    return len(entries)


def smoke(site: Path, manifest_path: Path, base_path: str) -> dict:
    base_path = normalize_base_path(base_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pages_release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
    core_release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    checked_pages = 0
    checked_references = 0

    for required in REQUIRED_FILES:
        if not (site / required).is_file():
            failures.append(f"GitHub Pages kök dosyası eksik: {required}")

    if (site / ".htaccess").exists():
        failures.append("GitHub Pages artifact Apache .htaccess taşımamalı")
    if (site / "tailwindcss").exists():
        failures.append("GitHub Pages artifact extensionless tailwindcss uyumluluk dosyası taşımamalı")

    if pages_release.get("hostingMode") != "github-pages":
        failures.append("pages-release hostingMode yanlış")
    if pages_release.get("basePath") != base_path:
        failures.append(f"pages-release basePath yanlış: {pages_release.get('basePath')!r}")
    if pages_release.get("canonicalHost") != CANONICAL_ORIGIN:
        failures.append("pages-release canonicalHost yanlış")
    if core_release.get("deviceDamageDeadline") != "30 gün":
        failures.append("core release cihaz hasarı süresi yanlış")
    if pages_release.get("rootDeviceDamageDeadline") != "30 gün":
        failures.append("Pages kök cihaz hasarı süresi yanlış")

    for route in manifest["routes"]:
        if not route_exists(site, route["canonicalPath"]):
            failures.append(f"Canonical rota GitHub Pages artifactında eksik: {route['canonicalPath']}")

    for critical in CRITICAL_ROUTES:
        if not route_exists(site, critical):
            failures.append(f"Offline kritik rota eksik: {critical}")

    for html_path in sorted(site.rglob("*.html")):
        checked_pages += 1
        relative = html_path.relative_to(site).as_posix()
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        parser = PageParser()
        parser.feed(text)
        robots = (parser.robots or "").lower()
        if not parser.has_service_worker:
            failures.append(f"Service worker kaydı eksik: {relative}")
        if base_path and "noindex" not in robots:
            failures.append(f"Default project Pages yüzeyinde noindex eksik: {relative}")
        if relative == "404.html" and "noindex" not in robots:
            failures.append("404 sayfası noindex,follow olmalı")
        if not base_path and relative not in {"durum/index.html", "404.html"}:
            if "İçerik yeni adresine taşındı" not in text and parser.canonical is None:
                failures.append(f"Custom-domain sayfasında canonical eksik: {relative}")

        for kind, reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme or reference.startswith(("//", "mailto:", "tel:", "javascript:", "data:", "blob:", "#")):
                continue
            checked_references += 1
            if parsed.path.startswith("/"):
                stripped = strip_base_path(parsed.path, base_path)
                if stripped is None:
                    failures.append(f"Base path öneki eksik: {relative} → {reference} (beklenen={base_path or '/'})")
                    continue
                internal = stripped
            else:
                target = (html_path.parent / parsed.path).resolve()
                try:
                    internal = "/" + target.relative_to(site.resolve()).as_posix()
                except ValueError:
                    failures.append(f"Referans bundle dışına çıkıyor: {relative} → {reference}")
                    continue

            internal_path = urlsplit(internal).path
            if kind == "href" and (not Path(internal_path).suffix or internal.endswith("/")):
                if not route_exists(site, internal):
                    failures.append(f"İç bağlantı hedefi eksik: {relative} → {reference}")
            elif kind in {"src", "poster", "data-src", "srcset"} or (kind == "href" and Path(internal_path).suffix):
                target = site / internal_path.lstrip("/")
                if not target.is_file():
                    failures.append(f"Asset hedefi eksik: {relative} → {reference}")

    manifest_json = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
    expected_start = (base_path + "/") if base_path else "/"
    if manifest_json.get("start_url") != expected_start or manifest_json.get("scope") != expected_start:
        failures.append("Web manifest start_url/scope base path ile uyumlu değil")

    sw = (site / "sw.js").read_text(encoding="utf-8")
    if f'const BASE={json.dumps(base_path)};' not in sw:
        failures.append("Service worker base path sözleşmesi yanlış")
    if "alo186-emergency-" not in sw or "Promise.allSettled" not in sw:
        failures.append("Service worker offline kritik cache sözleşmesi eksik")

    bridge_manifest = json.loads((site / "route-bridges.json").read_text(encoding="utf-8"))
    for bridge in bridge_manifest.get("routes", []):
        if not route_exists(site, bridge["source"]):
            failures.append(f"Route bridge dosyası eksik: {bridge['source']}")
        if not route_exists(site, bridge["target"]):
            failures.append(f"Route bridge hedefi eksik: {bridge['target']}")

    search_index_entries = validate_search_index(site, base_path, core_release, pages_release, failures)

    checksum_path = site / "checksums.sha256"
    if checksum_path.is_file():
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            expected, relative = line.split("  ", 1)
            target = site / relative
            if not target.is_file() or file_sha256(target) != expected:
                failures.append(f"GitHub Pages checksum doğrulanamadı: {relative}")

    if base_path:
        unresolved = re.compile(r'(?P<quote>["\'`])/(?!/)(?P<rest>[^"\'`\s<>]*)')
        known_top_levels = {path.name for path in site.iterdir()}
        base_path_aware_scripts = {
            Path("assets/alo186-ux.js"),
            Path("assets/affiliate-measurement-v211.js"),
            Path("assets/alo186-contextual-affiliate-v177.js"),
        }
        for path in sorted(site.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".json", ".webmanifest"}:
                continue
            if path.name in CANONICAL_METADATA_FILES:
                continue
            relative_path = path.relative_to(site)
            if relative_path in base_path_aware_scripts:
                # These runtimes either derive the public prefix dynamically or
                # keep canonical route identifiers/path separators as data.
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix.lower() == ".html":
                # Structural attributes are already checked by PageParser. Keep
                # scanning executable inline script/style content, but exclude
                # logical data-* route identifiers that are not browser URLs.
                text = executable_html_text(text)
            for match in unresolved.finditer(text):
                rest = match.group("rest")
                first = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
                if (rest == "" or first in known_top_levels) and not match.group(0).startswith(match.group("quote") + base_path + "/"):
                    failures.append(f"Project base path sonrası kök referans kaldı: {path.relative_to(site)} → /{rest}")
                    break

    result = {
        "ok": not failures,
        "basePath": base_path,
        "routeCount": len(manifest["routes"]),
        "routeBridgeCount": bridge_manifest.get("count", 0),
        "searchIndexEntryCount": search_index_entries,
        "checkedPages": checked_pages,
        "checkedReferences": checked_references,
        "failures": failures,
    }
    if failures:
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 GitHub Pages artifact smoke testi.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=Path("alo186/deployment/routing-manifest.json"))
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(smoke(args.site.resolve(), args.manifest.resolve(), args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
