from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


CANONICAL_HOST = "https://www.alo186.com"
LEGACY_HOST = "https://alo186.com"

LEGACY_ASSET_DIRECTORIES = (
    # Karar motoru CSS tabanı bu klasöre relatif @import kullanıyor.
    "yedek-guc-hesaplayici",
)

SHARED_STATIC_ASSETS = (
    # Teknik makaleler canonical alt dizinlere taşınırken ortak responsive CSS
    # /haberler kökünde tek kopya olarak yayınlanır.
    ("alo186/haberler/alo186-article.css", "haberler/alo186-article.css"),
)

ROOT_STATIC_FILES = (
    ("alo186/robots.txt", "robots.txt"),
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
    "RewriteRule ^ https://www.alo186.com%{REQUEST_URI}",
    "AddOutputFilterByType SUBSTITUTE text/html application/xhtml+xml",
    "zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde",
    "10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
)
DAMAGE_TERMS = re.compile(r"\b(cihaz|teçhizat|techizat|hasar|zarar)\w*\b", re.IGNORECASE)
APPLICATION_TERMS = re.compile(
    r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*",
    re.IGNORECASE,
)
WRONG_DEADLINE = re.compile(r"\b30\s*gün\b", re.IGNORECASE)


def copy_route(repo_root: Path, output: Path, route: dict) -> None:
    source = repo_root / route["source"]
    if not source.is_file():
        raise FileNotFoundError(f"Kaynak bulunamadı: {source}")
    target_path = route["canonicalPath"].strip("/") or "."
    target = output / target_path
    target.mkdir(parents=True, exist_ok=True)

    # Ana ALO186 merkezi, kaynak kökündeki diğer modülleri portalın altına kopyalamaz.
    if source.parent == repo_root / "alo186":
        shutil.copy2(source, target / "index.html")
        for asset_name in ("styles.css",):
            asset = source.parent / asset_name
            if asset.exists():
                shutil.copy2(asset, target / asset_name)
        return

    shutil.copytree(source.parent, target, dirs_exist_ok=True)


def copy_file(repo_root: Path, output: Path, source_name: str, target_name: str) -> None:
    source = repo_root / source_name
    if not source.is_file():
        raise FileNotFoundError(f"Yayın dosyası bulunamadı: {source}")
    target = output / target_name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def iter_text_files(output: Path):
    for path in sorted(output.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".htaccess" or path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def normalize_canonical_host(output: Path) -> None:
    for path in iter_text_files(output):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_HOST in text:
            path.write_text(text.replace(LEGACY_HOST, CANONICAL_HOST), encoding="utf-8")


def find_wrong_damage_deadlines(output: Path) -> list[str]:
    violations: list[str] = []
    for path in iter_text_files(output):
        try:
            text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
        for match in WRONG_DEADLINE.finditer(text):
            start = max(0, match.start() - 260)
            end = min(len(text), match.end() + 260)
            context = text[start:end]
            if DAMAGE_TERMS.search(context) and APPLICATION_TERMS.search(context):
                violations.append(f"{path.relative_to(output)}:{match.start()} -> {context[:520]}")
    return violations


def validate_bundle(output: Path, manifest: dict) -> None:
    failures: list[str] = []

    if manifest.get("canonicalHost") != CANONICAL_HOST:
        failures.append(
            f"routing manifest canonicalHost yanlış: {manifest.get('canonicalHost')!r}; beklenen={CANONICAL_HOST}"
        )

    for route in manifest["routes"]:
        target = output / route["canonicalPath"].strip("/") / "index.html"
        if not target.is_file():
            failures.append(f"Canonical rota artifact'ta eksik: {route['canonicalPath']}")

    for _source_name, target_name in (*SHARED_STATIC_ASSETS, *ROOT_STATIC_FILES):
        if not (output / target_name).is_file():
            failures.append(f"Kök/ortak yayın dosyası eksik: {target_name}")

    legacy_locations: list[str] = []
    for path in iter_text_files(output):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_HOST in text:
            legacy_locations.append(path.relative_to(output).as_posix())
    if legacy_locations:
        failures.append(f"Eski apex origin artifact'ta kaldı: {', '.join(legacy_locations[:20])}")

    wrong_deadlines = find_wrong_damage_deadlines(output)
    if wrong_deadlines:
        failures.append("Cihaz hasarı başvurusu bağlamında yanlış 30 gün ifadesi:\n" + "\n".join(wrong_deadlines))

    htaccess_path = output / ".htaccess"
    if htaccess_path.is_file():
        htaccess = htaccess_path.read_text(encoding="utf-8")
        for header in REQUIRED_SECURITY_HEADERS:
            if header not in htaccess:
                failures.append(f"Aktif production .htaccess güvenlik başlığı eksik: {header}")
        for token in REQUIRED_APACHE_TOKENS:
            if token not in htaccess:
                failures.append(f"Aktif production .htaccess sözleşmesi eksik: {token}")
    else:
        failures.append("Aktif production .htaccess artifact'ta yok")

    robots = output / "robots.txt"
    if robots.is_file() and f"Sitemap: {CANONICAL_HOST}/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        failures.append("robots.txt www canonical sitemap adresini taşımıyor")

    sitemap = output / "sitemap.xml"
    if sitemap.is_file():
        sitemap_text = sitemap.read_text(encoding="utf-8")
        if CANONICAL_HOST not in sitemap_text:
            failures.append("sitemap.xml www canonical origin taşımıyor")
        if LEGACY_HOST in sitemap_text:
            failures.append("sitemap.xml eski apex origin taşıyor")

    if failures:
        raise RuntimeError("ALO186 production bundle doğrulaması başarısız:\n- " + "\n- ".join(failures))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(repo_root: Path, output: Path, commit_sha: str = "local") -> dict:
    manifest_path = repo_root / "alo186/deployment/routing-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    for route in manifest["routes"]:
        copy_route(repo_root, output, route)

    for source_name, target_name in SHARED_STATIC_ASSETS:
        copy_file(repo_root, output, source_name, target_name)

    # Canonical HTML üretmeyen ancak mevcut relatif CSS/JS bağımlılıklarını sağlayan
    # uyumluluk klasörleri. İçlerindeki index sayfaları kendi canonical URL'lerini taşır.
    for directory in LEGACY_ASSET_DIRECTORIES:
        source = repo_root / "alo186" / directory
        if source.is_dir():
            shutil.copytree(source, output / directory, dirs_exist_ok=True)

    for source_name, target_name in ROOT_STATIC_FILES:
        copy_file(repo_root, output, source_name, target_name)

    (output / ".nojekyll").touch()
    normalize_canonical_host(output)
    validate_bundle(output, manifest)

    release = {
        "schemaVersion": 2,
        "commit": commit_sha,
        "canonicalHost": manifest["canonicalHost"],
        "routeCount": len(manifest["routes"]),
        "legacyAssetDirectories": list(LEGACY_ASSET_DIRECTORIES),
        "sharedStaticAssets": [target for _, target in SHARED_STATIC_ASSETS],
        "rootStaticFiles": [target for _, target in ROOT_STATIC_FILES],
        "securityHeaders": list(REQUIRED_SECURITY_HEADERS),
        "deviceDamageDeadline": "10 iş günü",
        "routes": [
            {
                "canonicalPath": item["canonicalPath"],
                "source": item["source"],
                "type": item["type"],
            }
            for item in manifest["routes"]
        ],
    }
    (output / "alo186-release.json").write_text(
        json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    files = sorted(path for path in output.rglob("*") if path.is_file())
    checksum_lines = [f"{sha256(path)}  {path.relative_to(output).as_posix()}" for path in files]
    (output / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return release


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canonical production bundle oluşturur.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path("_production_site"))
    parser.add_argument("--commit", default="local")
    args = parser.parse_args()
    release = build(args.repo_root.resolve(), args.output.resolve(), args.commit)
    print(json.dumps(release, ensure_ascii=False))


if __name__ == "__main__":
    main()
