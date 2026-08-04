from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PAGE = ROOT / "alo186/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/index.html"
SOURCE_ASSET = ROOT / "alo186/assets/alo186-track-v253.js"
ASSET_REFERENCE = "/assets/alo186-track-v253.js"
ASSET_TARGET = Path("assets/alo186-track-v253.js")


def run_regression(workspace: Path) -> None:
    canonical = workspace / "canonical"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "alo186/deployment/build_static_site.py"),
            "--repo-root",
            str(ROOT),
            "--output",
            str(canonical),
            "--commit",
            "pages-track-asset-v261-test",
        ],
        cwd=ROOT,
        check=True,
    )

    source_html = SOURCE_PAGE.read_text(encoding="utf-8")
    built_page = canonical / "amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/index.html"
    built_asset = canonical / ASSET_TARGET
    assert ASSET_REFERENCE in source_html
    assert built_page.is_file(), built_page
    assert ASSET_REFERENCE in built_page.read_text(encoding="utf-8")
    assert built_asset.is_file(), built_asset
    assert built_asset.read_bytes() == SOURCE_ASSET.read_bytes()

    release = json.loads((canonical / "alo186-release.json").read_text(encoding="utf-8"))
    assert ASSET_TARGET.as_posix() in release["sharedStaticAssets"]
    checksums = (canonical / "checksums.sha256").read_text(encoding="utf-8")
    assert f"  {ASSET_TARGET.as_posix()}\n" in checksums

    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        site = workspace / name
        shutil.copytree(canonical, site)
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "alo186/deployment/prepare_github_pages.py"),
                "--site",
                str(site),
                "--base-path",
                base_path,
                "--repository",
                "ozaneryavuz/chatgpt",
                "--commit",
                "pages-track-asset-v261-test",
            ],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "alo186/deployment/smoke_github_pages.py"),
                "--site",
                str(site),
                "--base-path",
                base_path,
            ],
            cwd=ROOT,
            check=True,
        )
        assert (site / ASSET_TARGET).read_bytes() == SOURCE_ASSET.read_bytes()


def test_pages_shared_track_asset_v261(tmp_path: Path) -> None:
    run_regression(tmp_path)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="alo186-track-asset-v261-") as temp_dir:
        run_regression(Path(temp_dir))
    print(json.dumps({
        "ok": True,
        "asset": ASSET_TARGET.as_posix(),
        "hostingModes": ["custom-domain", "project-path"],
        "sourceAndArtifactMatch": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
