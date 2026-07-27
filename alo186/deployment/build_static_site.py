from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


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

    for root_file in ("robots.txt", "sitemap.xml"):
        shutil.copy2(repo_root / "alo186" / root_file, output / root_file)

    htaccess = repo_root / "alo186/deployment/apache-production.htaccess"
    if htaccess.exists():
        shutil.copy2(htaccess, output / ".htaccess")

    (output / ".nojekyll").touch()
    release = {
        "schemaVersion": 1,
        "commit": commit_sha,
        "canonicalHost": manifest["canonicalHost"],
        "routeCount": len(manifest["routes"]),
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
