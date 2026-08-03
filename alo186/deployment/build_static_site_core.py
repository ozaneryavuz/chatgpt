from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from .device_damage_deadline import (
        CURRENT_DEADLINE,
        AMENDMENT_URL as DEVICE_DAMAGE_AMENDMENT_URL,
        REGULATION_URL as DEVICE_DAMAGE_REGULATION_URL,
        find_stale_application_deadlines,
        normalize_published_site,
        validate_published_site,
    )
except ImportError:
    from device_damage_deadline import (
        CURRENT_DEADLINE,
        AMENDMENT_URL as DEVICE_DAMAGE_AMENDMENT_URL,
        REGULATION_URL as DEVICE_DAMAGE_REGULATION_URL,
        find_stale_application_deadlines,
        normalize_published_site,
        validate_published_site,
    )

CANONICAL_HOST = "https://alo186.com"
LEGACY_HOST = "https://www.alo186.com"
ROUTING_OVERLAY_DIRECTORY = "alo186/deployment/routing-overlays"

LEGACY_ASSET_DIRECTORIES = (
    # Karar motoru CSS tabanı bu klasöre relatif @import kullanıyor.
    "yedek-guc-hesaplayici",
)

SHARED_STATIC_ASSETS = (
    # Teknik makaleler canonical alt dizinlere taşınırken ortak responsive CSS
    # /haberler kökünde tek kopya olarak yayınlanır.
    ("alo186/haberler/alo186-article.css", "haberler/alo186-article.css"),
    # Kritik sistem hesaplayıcıları aynı erişilebilir ve mobil stil sözleşmesini
    # canonical ile project-path paketlerinde tek public asset olarak kullanır.
    ("alo186/assets/critical-continuity-v126.css", "assets/critical-continuity-v126.css"),
)

ROOT_STATIC_FILES = (
    ("alo186/robots.txt", "robots.txt"),
    ("alo186/llms.txt", "llms.txt"),
    ("alo186/sitemap.xml", "sitemap.xml"),
    ("alo186/deployment/apache-production.htaccess", ".htaccess"),
    ("alo186/deployment/404.html", "404.html"),
    ("alo186/deployment/tailwindcss", "tailwindcss"),
)

TEXT_SUFFIXES = {".html", ".htm", ".xml", ".txt", ".json", ".js", ".css", ".md"}
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


def is_forbidden_public_name(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in FORBIDDEN_PUBLIC_FILE_PATTERNS)


def public_copy_ignore(_directory: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in FORBIDDEN_PUBLIC_DIRECTORIES or is_forbidden_public_name(name):
            ignored.add(name)
    return ignored


def is_forbidden_public_path(path: Path, output: Path) -> bool:
    relative = path.relative_to(output)
    if set(relative.parts[:-1]) & FORBIDDEN_PUBLIC_DIRECTORIES:
        return True
    return is_forbidden_public_name(path.name)


def validate_route(route: dict, source_label: str) -> dict:
    required = {"source", "canonicalPath", "type"}
    missing = sorted(required - set(route))
    if missing:
        raise ValueError(f"Routing kaydı eksik alan taşıyor ({source_label}): {', '.join(missing)}")
    source = str(route["source"]).strip()
    canonical_path = "/" + str(route["canonicalPath"]).strip().strip("/")
    if str(route["canonicalPath"]).strip().endswith("/") and canonical_path != "/":
        canonical_path += "/"
    route_type = str(route["type"]).strip()
    if not source.startswith("alo186/") or not source.endswith("index.html"):
        raise ValueError(f"Routing source geçersiz ({source_label}): {source}")
    if not canonical_path.startswith("/") or "//" in canonical_path:
        raise ValueError(f"Canonical path geçersiz ({source_label}): {canonical_path}")
    if not route_type:
        raise ValueError(f"Routing type boş ({source_label}): {canonical_path}")
    return {"source": source, "canonicalPath": canonical_path, "type": route_type}


def load_effective_manifest(repo_root: Path) -> dict:
    manifest_path = repo_root / "alo186/deployment/routing-manifest.json"
    base = json.loads(manifest_path.read_text(encoding="utf-8"))
    if base.get("canonicalHost") != CANONICAL_HOST:
        raise ValueError(f"Base routing canonicalHost yanlış: {base.get('canonicalHost')!r}")

    routes: list[dict] = []
    canonical_paths: set[str] = set()
    sources: set[str] = set()

    def append_route(raw_route: dict, source_label: str) -> None:
        route = validate_route(raw_route, source_label)
        if route["canonicalPath"] in canonical_paths:
            raise ValueError(f"Yinelenen canonical rota ({source_label}): {route['canonicalPath']}")
        if route["source"] in sources:
            raise ValueError(f"Yinelenen routing source ({source_label}): {route['source']}")
        canonical_paths.add(route["canonicalPath"])
        sources.add(route["source"])
        routes.append(route)

    for route in base.get("routes", []):
        append_route(route, "routing-manifest.json")

    overlay_directory = repo_root / ROUTING_OVERLAY_DIRECTORY
    overlay_names: list[str] = []
    effective_version = int(base.get("version", 0))
    generated_at = str(base.get("generatedAt", ""))
    if overlay_directory.is_dir():
        for overlay_path in sorted(overlay_directory.glob("*.json")):
            overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
            overlay_names.append(overlay_path.name)
            effective_version = max(effective_version, int(overlay.get("version", 0)))
            generated_at = max(generated_at, str(overlay.get("generatedAt", "")))
            for route in overlay.get("routes", []):
                append_route(route, overlay_path.name)

    return {
        "version": effective_version,
        "canonicalHost": CANONICAL_HOST,
        "generatedAt": generated_at,
        "routes": routes,
        "routingOverlays": overlay_names,
        "requiredIntegrations": list(base.get("requiredIntegrations", [])),
    }


def copy_route(repo_root: Path, output: Path, route: dict) -> None:
    source = repo_root / route["source"]
    if not source.is_file():
        raise FileNotFoundError(f"Kaynak bulunamadı: {source}")
    target_path = route["canonicalPath"].strip("/") or "."
    target = output / target_path
    target.mkdir(parents=True, exist_ok=True)

    if source.parent == repo_root / "alo186":
        shutil.copy2(source, target / "index.html")
        for asset_name in ("styles.css",):
            asset = source.parent / asset_name
            if asset.exists():
                shutil.copy2(asset, target / asset_name)
        return

    shutil.copytree(
        source.parent,
        target,
        dirs_exist_ok=True,
        ignore=public_copy_ignore,
    )


def normalize_text_file(path: Path) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".htaccess", "tailwindcss"}:
        return
    content = path.read_text(encoding="utf-8", errors="strict")
    content = content.replace(LEGACY_HOST, CANONICAL_HOST)
    path.write_text(content, encoding="utf-8")


def normalize_canonical_host(output: Path) -> None:
    for path in output.rglob("*"):
        if path.is_file():
            normalize_text_file(path)


def write_effective_sitemap(output: Path, routes: list[dict]) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    urlset = ET.Element(f"{{{namespace}}}urlset")
    for route in routes:
        url = ET.SubElement(urlset, f"{{{namespace}}}url")
        loc = ET.SubElement(url, f"{{{namespace}}}loc")
        loc.text = CANONICAL_HOST + route["canonicalPath"]
    tree = ET.ElementTree(urlset)
    tree.write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_forbidden_public_files(output: Path) -> list[str]:
    return sorted(
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and is_forbidden_public_path(path, output)
    )


def build(repo_root: Path, output: Path, commit_sha: str = "local") -> dict:
    manifest = load_effective_manifest(repo_root)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    copied_routes: list[dict] = []
    article_count = 0
    for route in manifest["routes"]:
        copy_route(repo_root, output, route)
        copied_routes.append(route)
        if route["type"] == "article":
            article_count += 1

    copied_legacy_assets: list[str] = []
    for directory in LEGACY_ASSET_DIRECTORIES:
        source = repo_root / "alo186" / directory
        if not source.is_dir():
            raise FileNotFoundError(f"Legacy asset dizini bulunamadı: {source}")
        shutil.copytree(
            source,
            output / directory,
            dirs_exist_ok=True,
            ignore=public_copy_ignore,
        )
        copied_legacy_assets.append(directory)

    copied_shared_assets: list[str] = []
    for source_name, target_name in SHARED_STATIC_ASSETS:
        source = repo_root / source_name
        if not source.is_file():
            raise FileNotFoundError(f"Ortak statik asset bulunamadı: {source}")
        target = output / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied_shared_assets.append(target_name)

    copied_root_files: list[str] = []
    for source_name, target_name in ROOT_STATIC_FILES:
        source = repo_root / source_name
        if not source.is_file():
            raise FileNotFoundError(f"Kök statik dosya bulunamadı: {source}")
        target = output / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied_root_files.append(target_name)

    write_effective_sitemap(output, copied_routes)
    normalize_canonical_host(output)
    normalize_published_site(output)
    forbidden_public_files = find_forbidden_public_files(output)
    if forbidden_public_files:
        raise RuntimeError("Yayın paketinde kaynak/test dosyası kaldı: " + ", ".join(forbidden_public_files[:30]))

    device_damage_validation = validate_published_site(output)
    release = {
        "schemaVersion": 5,
        "commit": commit_sha,
        "canonicalHost": CANONICAL_HOST,
        "routingVersion": manifest["version"],
        "routingGeneratedAt": manifest["generatedAt"],
        "routingOverlays": manifest["routingOverlays"],
        "routeCount": len(copied_routes),
        "articleCount": article_count,
        "legacyAssetDirectories": copied_legacy_assets,
        "sharedStaticAssets": copied_shared_assets,
        "rootStaticFiles": copied_root_files,
        "securityHeaders": list(REQUIRED_SECURITY_HEADERS),
        "deviceDamageDeadline": CURRENT_DEADLINE,
        "deviceDamageRegulationUrl": DEVICE_DAMAGE_REGULATION_URL,
        "deviceDamageAmendmentUrl": DEVICE_DAMAGE_AMENDMENT_URL,
        "deviceDamageNormalizedFiles": device_damage_validation["normalizedFiles"],
        "deviceDamageVerifiedLocations": device_damage_validation["verifiedLocations"],
        "publicArtifactPolicy": {
            "sourceDocsExcluded": True,
            "testsExcluded": True,
            "packageMetadataExcluded": True,
        },
        "routes": copied_routes,
    }
    release_path = output / "alo186-release.json"
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checksums = []
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        checksums.append(f"{sha256(path)}  {path.relative_to(output).as_posix()}")
    (output / "checksums.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return release


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 statik üretim paketini oluştur")
    parser.add_argument("--output", required=True)
    parser.add_argument("--commit", default="local")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    release = build(repo_root, Path(args.output).resolve(), args.commit)
    print(json.dumps(release, ensure_ascii=False))


if __name__ == "__main__":
    main()
