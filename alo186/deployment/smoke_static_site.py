from __future__ import annotations

import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


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
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def smoke(bundle: Path, repo_root: Path) -> dict:
    manifest = json.loads((repo_root / "alo186/deployment/routing-manifest.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    checked_assets = 0

    for route in manifest["routes"]:
        target = bundle / route["canonicalPath"].strip("/") / "index.html"
        if not target.exists():
            failures.append(f"Route index eksik: {route['canonicalPath']}")
            continue
        parser = AssetParser()
        parser.feed(target.read_text(encoding="utf-8"))
        expected = f"{manifest['canonicalHost']}{route['canonicalPath']}"
        if parser.canonical != expected:
            failures.append(f"Canonical eşleşmiyor: {route['canonicalPath']} → {parser.canonical!r}")
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

    for required in ("robots.txt", "sitemap.xml", ".htaccess", "alo186-release.json", "checksums.sha256"):
        if not (bundle / required).is_file():
            failures.append(f"Kök yayın dosyası eksik: {required}")

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
