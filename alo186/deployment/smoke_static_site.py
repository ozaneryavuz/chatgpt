from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


CANONICAL_HOST = "https://alo186.com"
LEGACY_HOST = "https://www.alo186.com"
REQUIRED_ROOT_FILES = (
    "robots.txt",
    "sitemap.xml",
    ".htaccess",
    "404.html",
    "tailwindcss",
    "alo186-release.json",
    "checksums.sha256",
)
REQUIRED_SECURITY_HEADERS = (
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "Content-Security-Policy",
    "Referrer-Policy",
    "Permissions-Policy",
)
REQUIRED_APACHE_TOKENS = (
    "RewriteRule ^ https://alo186.com%{REQUEST_URI}",
    "Cihaz hasarı başvuru süresi HTML yanıt katmanında değiştirilmez",
    "ForceType text/css",
)
FORBIDDEN_PUBLIC_DIRECTORIES = {
    ".git",
    ".github",
    "__pycache__",
    "node_modules",
    "tests",
    "test",
    "fixtures",
    "reports",
    "audits",
    "artifacts",
    "docs",
    "documentation",
    "deployment",
    "infra",
}
FORBIDDEN_PUBLIC_FILE_PATTERNS = (
    "README*",
    "CHANGELOG*",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "test.js",
    "*.test.js",
    "*-test.js",
    "*_test.js",
    "*.spec.js",
    "*-spec.js",
    "*.md",
    "*.py",
    "*.pyc",
    "*.sh",
    "*.yml",
    "*.yaml",
    "*.sql",
    "*.log",
    "*.bak",
    "*.map",
    ".DS_Store",
)
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


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.assets: list[str] = []
        self.canonical: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "script" and values.get("src"):
            self.assets.append(values["src"] or "")
        if tag == "link" and values.get("href") and values.get("rel") in {"stylesheet", "preload"}:
            self.assets.append(values["href"] or "")
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")


def resolve_asset(bundle: Path, html_path: Path, reference: str) -> Path | None:
    parsed = urlparse(reference)
    if parsed.scheme or reference.startswith("//") or reference.startswith("data:"):
        return None
    clean = parsed.path
    if not clean or clean.startswith("#"):
        return None
    if clean.startswith("/"):
        return bundle / clean.lstrip("/")
    return (html_path.parent / clean).resolve()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_forbidden_public_file(path: Path, bundle: Path) -> bool:
    relative = path.relative_to(bundle)
    if set(relative.parts[:-1]) & FORBIDDEN_PUBLIC_DIRECTORIES:
        return True
    return any(fnmatch.fnmatch(path.name, pattern) for pattern in FORBIDDEN_PUBLIC_FILE_PATTERNS)


def stale_damage_application_contexts(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text)
    contexts: list[str] = []
    for match in STALE_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 260)
        end = min(len(normalized), match.end() + 260)
        context = normalized[start:end]
        if (
            DAMAGE_TERMS.search(context)
            and APPLICATION_TERMS.search(context)
            and not RESPONSE_TERMS.search(context)
        ):
            contexts.append(context[:520])
    return contexts


def smoke(bundle: Path, repo_root: Path) -> dict:
    manifest = json.loads((repo_root / "alo186/deployment/routing-manifest.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    checked_assets = 0

    if manifest.get("canonicalHost") != CANONICAL_HOST:
        failures.append(f"Manifest canonicalHost yanlış: {manifest.get('canonicalHost')!r}")

    for route in manifest["routes"]:
        target = bundle / route["canonicalPath"].strip("/") / "index.html"
        if not target.exists():
            failures.append(f"Route index eksik: {route['canonicalPath']}")
            continue
        html = target.read_text(encoding="utf-8")
        parser = AssetParser()
        parser.feed(html)
        expected = f"{manifest['canonicalHost']}{route['canonicalPath']}"
        if parser.canonical != expected:
            failures.append(f"Canonical eşleşmiyor: {route['canonicalPath']} → {parser.canonical!r}")
        if LEGACY_HOST in html:
            failures.append(f"Eski www origin route HTML içinde kaldı: {route['canonicalPath']}")
        for context in stale_damage_application_contexts(html):
            failures.append(f"{route['canonicalPath']}: eski cihaz hasarı başvuru süresi → {context}")
        for reference in parser.assets:
            asset = resolve_asset(bundle, target, reference)
            if asset is None:
                continue
            checked_assets += 1
            try:
                inside = asset.relative_to(bundle.resolve())
            except ValueError:
                failures.append(f"Asset bundle dışına çıkıyor: {target} → {reference}")
                continue
            if not (bundle / inside).is_file():
                failures.append(f"Asset eksik: {route['canonicalPath']} → {reference}")

    for required in REQUIRED_ROOT_FILES:
        if not (bundle / required).is_file():
            failures.append(f"Kök yayın dosyası eksik: {required}")

    forbidden_files = [
        path.relative_to(bundle).as_posix()
        for path in sorted(bundle.rglob("*"))
        if path.is_file() and is_forbidden_public_file(path, bundle)
    ]
    if forbidden_files:
        failures.append("Public bundle iç kaynak/test dosyası taşıyor: " + ", ".join(forbidden_files[:50]))

    htaccess_path = bundle / ".htaccess"
    if htaccess_path.is_file():
        htaccess = htaccess_path.read_text(encoding="utf-8")
        for header in REQUIRED_SECURITY_HEADERS:
            if header not in htaccess:
                failures.append(f"Aktif .htaccess güvenlik başlığı eksik: {header}")
        for token in REQUIRED_APACHE_TOKENS:
            if token not in htaccess:
                failures.append(f"Aktif .htaccess sözleşmesi eksik: {token}")
        if "<IfModule mod_substitute.c>" in htaccess or "Substitute \"s|" in htaccess:
            failures.append("Aktif .htaccess hukukî içeriği yanıt katmanında değiştiremez")
    else:
        failures.append("Aktif .htaccess okunamadı")

    release_path = bundle / "alo186-release.json"
    if release_path.is_file():
        release = json.loads(release_path.read_text(encoding="utf-8"))
        if release.get("canonicalHost") != CANONICAL_HOST:
            failures.append(f"Release canonicalHost yanlış: {release.get('canonicalHost')!r}")
        if release.get("deviceDamageDeadline") != "30 gün":
            failures.append("Release cihaz hasarı süresi sözleşmesi eksik")
        if not release.get("deviceDamageRegulationUrl"):
            failures.append("Release cihaz hasarı mevzuat kaynağı eksik")
        if int(release.get("deviceDamageVerifiedLocations", 0)) <= 0:
            failures.append("Release cihaz hasarı 30 gün doğrulaması eksik")
        for header in REQUIRED_SECURITY_HEADERS:
            if header not in release.get("securityHeaders", []):
                failures.append(f"Release güvenlik başlığı envanteri eksik: {header}")
        policy = release.get("publicArtifactPolicy") or {}
        for key in ("sourceDocsExcluded", "testsExcluded", "packageMetadataExcluded"):
            if policy.get(key) is not True:
                failures.append(f"Release public artifact politikası eksik: {key}")

    robots_path = bundle / "robots.txt"
    if robots_path.is_file():
        robots = robots_path.read_text(encoding="utf-8")
        if f"Sitemap: {CANONICAL_HOST}/sitemap.xml" not in robots:
            failures.append("robots.txt canonical sitemap adresi yanlış")

    sitemap_path = bundle / "sitemap.xml"
    if sitemap_path.is_file():
        sitemap = sitemap_path.read_text(encoding="utf-8")
        if CANONICAL_HOST not in sitemap or LEGACY_HOST in sitemap:
            failures.append("sitemap canonical origin sözleşmesi başarısız")

    checksum_path = bundle / "checksums.sha256"
    if checksum_path.exists():
        for line in checksum_path.read_text(encoding="utf-8").splitlines():
            expected, relative = line.split("  ", 1)
            target = bundle / relative
            if not target.exists() or file_sha256(target) != expected:
                failures.append(f"Checksum doğrulanamadı: {relative}")

    result = {
        "ok": not failures,
        "routeCount": len(manifest["routes"]),
        "assetReferencesChecked": checked_assets,
        "requiredRootFiles": list(REQUIRED_ROOT_FILES),
        "requiredSecurityHeaders": list(REQUIRED_SECURITY_HEADERS),
        "forbiddenPublicFileCount": len(forbidden_files),
        "deviceDamageDeadline": "30 gün",
        "failures": failures,
    }
    if failures:
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 üretim bundle smoke testi.")
    parser.add_argument("--bundle", type=Path, default=Path("_production_site"))
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(smoke(args.bundle.resolve(), args.repo_root.resolve()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
