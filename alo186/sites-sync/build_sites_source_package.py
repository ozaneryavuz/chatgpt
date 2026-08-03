#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ORIGIN = "https://alo186.com"
PUBLIC_SUFFIXES = {
    ".html", ".css", ".js", ".json", ".jsonld", ".xml", ".txt",
    ".svg", ".png", ".jpg", ".jpeg", ".webp", ".avif", ".ico",
    ".webmanifest", ".map", ".wasm",
}
BLOCKED_NAMES = {
    ".htaccess", "pages-release.json", "alo186-release.json",
    "checksums.sha256", "SHA256SUMS",
}
BLOCKED_PARTS = {
    ".git", ".github", "__pycache__", "node_modules", "tests",
    "fixtures", "reports", "infra",
}
CORE_ROUTES = {
    "/", "/elektrik-portali", "/edas-bul", "/karar-motoru",
    "/hesaplama/", "/acil-numaralar/", "/planli-kesintiler/",
    "/urun-rehberleri/", "/amazon-elektrik-urunleri/",
}


class PackageError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageError(f"Dosya bulunamadı: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PackageError(f"Geçersiz JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageError(f"JSON kökü nesne olmalı: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_route(value: str) -> str:
    route = "/" + str(value or "").strip()
    return re.sub(r"/+", "/", route)


def public_file(path: Path) -> bool:
    if not path.is_file() or path.is_symlink() or path.name.startswith("."):
        return False
    if path.name in BLOCKED_NAMES or path.suffix.casefold() not in PUBLIC_SUFFIXES:
        return False
    name = path.name.casefold()
    if name.startswith(("test", "spec")) or any(
        token in name for token in (".test.", ".spec.", "-test.", "_test.", "-spec.", "_spec.")
    ):
        return False
    return not any(part.casefold() in BLOCKED_PARTS for part in path.parts)


def copy_tree(source: Path, target: Path) -> int:
    if source.is_file():
        if not public_file(source):
            return 0
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return 1
    copied = 0
    if source.is_dir():
        for path in sorted(source.rglob("*")):
            if not public_file(path):
                continue
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            copied += 1
    return copied


def route_source(bundle: Path, route: str) -> Path | None:
    route = normalize_route(route)
    if route == "/":
        path = bundle / "index.html"
        return path if path.is_file() else None
    relative = route.strip("/")
    for path in (bundle / relative / "index.html", bundle / f"{relative}.html"):
        if path.is_file():
            return path
    return None


def route_target(public_root: Path, route: str, source: Path) -> Path:
    route = normalize_route(route)
    if route == "/":
        return public_root / "index.html"
    relative = Path(route.strip("/"))
    return public_root / relative / "index.html" if source.name == "index.html" else public_root / f"{relative}.html"


def priority(route: str, route_type: str) -> str:
    if route in CORE_ROUTES or route.startswith(("/il/", "/dagitim-sirketleri/")):
        return "P0"
    if route.startswith(("/haberler/", "/hesaplama/", "/amazon-elektrik-urunleri/")):
        return "P1"
    if route_type in {"article", "tool", "calculator", "business-tool", "commerce-guide"}:
        return "P1"
    return "P2"


def transfer_mode(route: str, route_type: str) -> str:
    if route in CORE_ROUTES:
        return "merge-content-data-schema-into-native-sites-design"
    if route.startswith(("/il/", "/dagitim-sirketleri/", "/haberler/")):
        return "create-or-update-canonical-page"
    if route_type in {"tool", "calculator", "business-tool"} or route.startswith("/hesaplama/"):
        return "port-accessible-component-and-deterministic-logic"
    if route.startswith(("/amazon-elektrik-urunleri/", "/urun-rehberleri/")):
        return "merge-after-safety-and-need-gates"
    return "create-or-update-route"


def inferred_type(route: str) -> str:
    for prefix, value in (
        ("/il/", "province"),
        ("/dagitim-sirketleri/", "distribution-company"),
        ("/haberler/", "article"),
        ("/hesaplama/", "tool"),
        ("/amazon-elektrik-urunleri/", "commerce-guide"),
        ("/en/", "translation"),
    ):
        if route.startswith(prefix):
            return value
    return "page"


def discover_routes(bundle: Path, prefixes: list[str]) -> list[str]:
    found: set[str] = set()
    for prefix in prefixes:
        root = bundle / prefix.strip("/")
        if not root.is_dir():
            continue
        for index in root.rglob("index.html"):
            found.add("/" + index.parent.relative_to(bundle).as_posix() + "/")
    return sorted(found)


def copy_metadata(repo: Path, target: Path, patterns: list[str]) -> list[str]:
    copied: list[str] = []
    for pattern in patterns:
        for source in sorted(repo.glob(pattern)):
            if not source.is_file() or source.is_symlink():
                continue
            if source.suffix.casefold() not in {".json", ".jsonld", ".js", ".txt", ".xml"}:
                continue
            relative = source.relative_to(repo)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(relative.as_posix())
    return copied


def copy_published_records(repo: Path, target: Path) -> list[str]:
    source_root = repo / "alo186/ai-cms/content"
    slugs: list[str] = []
    if not source_root.is_dir():
        return slugs
    for source in sorted(source_root.glob("*.json")):
        try:
            record = read_json(source)
        except PackageError:
            continue
        if record.get("state") != "published":
            continue
        destination = target / "ai-cms/content" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        slugs.append(str(record.get("slug") or source.stem))
    return slugs


def copy_machine_files(bundle: Path, public_root: Path) -> list[str]:
    copied: set[str] = set()
    for required in ("robots.txt", "sitemap.xml"):
        source = bundle / required
        if not source.is_file():
            raise PackageError(f"Zorunlu makine kaynağı eksik: {required}")
        shutil.copy2(source, public_root / required)
        copied.add(required)
    for pattern in (
        "sitemap*.xml", "llms*.txt", "knowledge-graph*.json",
        "knowledge-graph*.jsonld", "manifest*.webmanifest", "site.webmanifest",
    ):
        for source in bundle.glob(pattern):
            if public_file(source):
                shutil.copy2(source, public_root / source.name)
                copied.add(source.name)
    return sorted(copied)


def validate_affiliate(public_root: Path) -> dict[str, int]:
    links = invalid = location_links = 0
    for path in public_root.rglob("*.html"):
        text = path.read_text(encoding="utf-8", errors="strict")
        anchors = re.findall(r"<a\b[^>]*amazon\.com\.tr[^>]*>", text, re.I | re.S)
        links += len(anchors)
        relative = path.relative_to(public_root).as_posix()
        if relative.startswith(("il/", "dagitim-sirketleri/")):
            location_links += len(anchors)
        for anchor in anchors:
            match = re.search(r'\brel=["\']([^"\']+)["\']', anchor, re.I)
            tokens = set((match.group(1) if match else "").casefold().split())
            if not {"sponsored", "nofollow", "noopener"} <= tokens:
                invalid += 1
    if invalid:
        raise PackageError(f"{invalid} Amazon bağlantısında rel sözleşmesi eksik")
    if location_links:
        raise PackageError(f"Konum sayfalarında {location_links} affiliate bağlantısı bulundu")
    return {
        "amazonTurkeyLinks": links,
        "invalidRelLinks": invalid,
        "locationAffiliateLinks": location_links,
    }


def integrity(root: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in {"source-integrity.json", "package-result.json"}:
            continue
        files.append({
            "path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        })
    return {
        "schemaVersion": 1,
        "algorithm": "SHA-256",
        "fileCount": len(files),
        "packageDigest": sha256_bytes(canonical_json(files).encode("utf-8")),
        "files": files,
    }


def build(repo: Path, bundle: Path, out: Path, source_commit: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{7,40}", source_commit):
        raise PackageError("Geçersiz source commit")
    repo, bundle, out = repo.resolve(), bundle.resolve(), out.resolve()
    if not bundle.is_dir():
        raise PackageError(f"Canonical bundle bulunamadı: {bundle}")

    sync_root = repo / "alo186/sites-sync"
    template = read_json(sync_root / "sites-source-manifest.json")
    routing = read_json(repo / "alo186/deployment/routing-manifest.json")
    if out.exists():
        shutil.rmtree(out)
    public_root, metadata_root = out / "public", out / "metadata"
    public_root.mkdir(parents=True)
    metadata_root.mkdir(parents=True)

    records: dict[str, dict[str, Any]] = {}

    def add(route: str, route_type: str, source_name: str) -> None:
        route = normalize_route(route)
        if route in records:
            return
        source = route_source(bundle, route)
        status, entry, count = "missing-from-canonical-bundle", None, 0
        if source:
            destination = route_target(public_root, route, source)
            count = copy_tree(source.parent, destination.parent) if source.name == "index.html" else copy_tree(source, destination)
            status, entry = "packaged", destination.relative_to(out).as_posix()
        records[route] = {
            "route": route,
            "type": route_type,
            "priority": priority(route, route_type),
            "transferMode": transfer_mode(route, route_type),
            "source": source_name,
            "packageEntry": entry,
            "status": status,
            "filesCopied": count,
        }

    add("/", "native-home-reference", "canonical bundle root")
    allowed = set(template["routeSelection"]["includeRoutingManifestTypes"])
    for item in routing.get("routes", []):
        if not isinstance(item, dict) or item.get("type") not in allowed:
            continue
        add(str(item.get("canonicalPath", "")), str(item.get("type", "page")), str(item.get("source", "")))
    for route in discover_routes(bundle, list(template["routeSelection"]["extraRoutePrefixes"])):
        add(route, inferred_type(route), "canonical bundle discovery")

    for directory in ("assets", "brand", "icons", "images"):
        if (bundle / directory).is_dir():
            copy_tree(bundle / directory, public_root / directory)
    machine = copy_machine_files(bundle, public_root)
    metadata = copy_metadata(repo, metadata_root, list(template.get("metadataSourcePatterns", [])))
    published = copy_published_records(repo, metadata_root)

    required = {normalize_route(item) for item in template["routeSelection"]["requiredRoutes"]}
    missing_required = sorted(route for route in required if records.get(route, {}).get("status") != "packaged")
    if missing_required:
        raise PackageError("Zorunlu rota eksik: " + ", ".join(missing_required))

    packaged = [item for item in records.values() if item["status"] == "packaged"]
    province_count = sum(item["route"].startswith("/il/") for item in packaged)
    company_count = sum(item["route"].startswith("/dagitim-sirketleri/") for item in packaged)
    if (province_count, company_count) != (81, 21):
        raise PackageError(f"Konum kapsamı 81/21 olmalı; bulunan={province_count}/{company_count}")

    affiliate = validate_affiliate(public_root)
    inventory = {
        "schemaVersion": 1,
        "sourceCommit": source_commit,
        "canonicalHost": ORIGIN,
        "routeCount": len(packaged),
        "missingOptionalRouteCount": len(records) - len(packaged),
        "countsByType": dict(sorted(Counter(item["type"] for item in packaged).items())),
        "countsByPriority": dict(sorted(Counter(item["priority"] for item in packaged).items())),
        "provincePages": province_count,
        "distributionCompanyPages": company_count,
        "publishedAiCmsRecords": len(published),
        "publishedAiCmsSlugs": published,
        "machineResources": machine,
        "metadataFiles": len(metadata),
        "metadataPaths": metadata,
        "affiliateValidation": affiliate,
        "routes": sorted(records.values(), key=lambda item: (item["priority"], item["route"])),
    }
    (out / "route-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    manifest = deepcopy(template)
    manifest["sourceCommit"], manifest["generatedAt"] = source_commit, now_utc()
    manifest["inventory"] = {
        "routeCount": len(packaged),
        "provincePages": province_count,
        "distributionCompanyPages": company_count,
        "publishedAiCmsRecords": len(published),
        "machineResources": machine,
        "affiliateValidation": affiliate,
    }
    unsigned = deepcopy(manifest)
    unsigned.pop("packageHash", None)
    manifest["packageHash"] = sha256_bytes(canonical_json(unsigned).encode("utf-8"))
    (out / "sites-source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(sync_root / "sites-import-prompt.md", out / "sites-import-prompt.md")
    shutil.copy2(sync_root / "README.md", out / "README.md")

    proof = integrity(out)
    (out / "source-integrity.json").write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    result = {
        "ok": True,
        "target": "chatgpt-sites",
        "siteSlug": "alo186",
        "sourceCommit": source_commit,
        "packageHash": manifest["packageHash"],
        "integrityDigest": proof["packageDigest"],
        "routeCount": len(packaged),
        "provincePages": province_count,
        "distributionCompanyPages": company_count,
        "publishedAiCmsRecords": len(published),
        "amazonTurkeyLinks": affiliate["amazonTurkeyLinks"],
        "output": str(out),
    }
    (out / "package-result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canonical bundle'dan ChatGPT Sites kaynak paketi üretir.")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(
        build(args.repo, args.bundle, args.out, args.source_commit),
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()
