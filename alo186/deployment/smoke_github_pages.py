from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

CANONICAL_ORIGIN = "https://www.alo186.com"
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


def route_exists(site: Path, route: str) -> bool:
    parsed = urlsplit(route)
    clean = parsed.path or "/"
    if clean == "/":
        return (site / "index.html").is_file()
    target = site / clean.lstrip("/")
    return target.is_file() or (target / "index.html").is_file()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if core_release.get("deviceDamageDeadline") != "10 iş günü":
        failures.append("core release cihaz hasarı süresi yanlış")

    for route in manifest["routes"]:
        path = route["canonicalPath"]
        if not route_exists(site, path):
            failures.append(f"Canonical rota GitHub Pages artifactında eksik: {path}")

    for critical in CRITICAL_ROUTES:
        if not route_exists(site, critical):
            failures.append(f"Offline kritik rota eksik: {critical}")

    for html_path in sorted(site.rglob("*.html")):
        checked_pages += 1
        text = html_path.read_text(encoding="utf-8", errors="ignore")
        parser = PageParser()
        parser.feed(text)
        if not parser.has_service_worker:
            failures.append(f"Service worker kaydı eksik: {html_path.relative_to(site)}")
        if base_path and (parser.robots or "").lower().find("noindex") == -1:
            failures.append(f"Default project Pages yüzeyinde noindex eksik: {html_path.relative_to(site)}")
        if not base_path and html_path.relative_to(site).as_posix() != "durum/index.html":
            if "İçerik yeni adresine taşındı" not in text and parser.canonical is None:
                failures.append(f"Custom-domain sayfasında canonical eksik: {html_path.relative_to(site)}")

        for kind, reference in parser.references:
            parsed = urlsplit(reference)
            if parsed.scheme or reference.startswith(("//", "mailto:", "tel:", "javascript:", "data:", "blob:", "#")):
                continue
            checked_references += 1
            if parsed.path.startswith("/"):
                stripped = strip_base_path(parsed.path, base_path)
                if stripped is None:
                    failures.append(
                        f"Base path öneki eksik: {html_path.relative_to(site)} → {reference} (beklenen={base_path or '/'})"
                    )
                    continue
                internal = stripped
            else:
                target = (html_path.parent / parsed.path).resolve()
                try:
                    internal = "/" + target.relative_to(site.resolve()).as_posix()
                except ValueError:
                    failures.append(f"Referans bundle dışına çıkıyor: {html_path.relative_to(site)} → {reference}")
                    continue

            if kind == "href" and (not Path(urlsplit(internal).path).suffix or internal.endswith("/")):
                if not route_exists(site, internal):
                    failures.append(f"İç bağlantı hedefi eksik: {html_path.relative_to(site)} → {reference}")
            elif kind in {"src", "poster", "data-src", "srcset"} or (kind == "href" and Path(urlsplit(internal).path).suffix):
                target = site / urlsplit(internal).path.lstrip("/")
                if not target.is_file():
                    failures.append(f"Asset hedefi eksik: {html_path.relative_to(site)} → {reference}")

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
        for path in sorted(site.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".html", ".js", ".css", ".json", ".webmanifest"}:
                continue
            if path.name in {"robots.txt", "sitemap.xml"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
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
