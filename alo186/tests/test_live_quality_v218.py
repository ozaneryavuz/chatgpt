from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build  # noqa: E402
from guard_commerce_routes_v3 import validate_site  # noqa: E402
from inject_live_quality_v218 import (  # noqa: E402
    ASSET_RELATIVE,
    COPY_REPLACEMENTS,
    CRITICAL_ROUTES,
    FORBIDDEN_VISIBLE_COPY,
    QUALITY_CSS,
    RECEIPT_RELATIVE,
    STYLE_MARKER,
)
from prepare_github_pages import prepare  # noqa: E402


def source_contracts() -> None:
    source = (DEPLOYMENT / "inject_live_quality_v218.py").read_text(encoding="utf-8")
    guard = (DEPLOYMENT / "guard_commerce_routes_v3.py").read_text(encoding="utf-8")
    for token in (
        "globalBrokenInternalLinkCount",
        "criticalBrokenInternalLinkCount",
        "canonicalViolations",
        "forbiddenVisibleCopyHits",
        "duplicateIdPageCount",
        "imagesMissingAltGlobal",
        "strictCriticalInternalLinks",
        "personalDataCollectionAdded",
        "officialInstitutionClaimed",
        "newCommerceLinksAdded",
        "live-quality-v218.json",
    ):
        assert token in source, token
    for old, new in COPY_REPLACEMENTS:
        assert old.casefold() in FORBIDDEN_VISIBLE_COPY
        assert new and old != new
    assert "overflow-x:hidden" not in QUALITY_CSS.replace(" ", "").casefold()
    assert "overflow-x:clip" not in QUALITY_CSS.replace(" ", "").casefold()
    assert "prefers-reduced-motion" in QUALITY_CSS
    assert "min-height:44px" in QUALITY_CSS
    assert "inject_live_quality_v218 as live_quality" in guard
    assert "quality_result = live_quality.run" in guard
    assert 'result["liveQualityV218"]' in guard


def assert_final_site(site: Path, base_path: str) -> dict:
    result = validate_site(site)
    quality = result["liveQualityV218"]
    assert quality["version"] == 218
    assert quality["basePath"] == base_path
    assert quality["finalArtifact"] is True
    assert quality["personalDataCollectionAdded"] is False
    assert quality["officialInstitutionClaimed"] is False
    assert quality["newCommerceLinksAdded"] is False
    assert quality["audit"]["canonicalViolations"] == 0
    assert quality["audit"]["criticalBrokenInternalLinkCount"] == 0
    assert quality["audit"]["forbiddenVisibleCopyHits"] == 0
    assert quality["audit"]["criticalPageCount"] == len(CRITICAL_ROUTES)
    assert quality["audit"]["horizontalOverflowHidden"] is False
    assert quality["audit"]["horizontalOverflowClipped"] is False

    receipt = json.loads((site / RECEIPT_RELATIVE).read_text(encoding="utf-8"))
    assert receipt == quality
    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    pages = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
    assert release["liveQualityV218"] == quality
    assert pages["liveQualityV218"] == quality
    assert (site / ASSET_RELATIVE).is_file()

    expected_asset = f"{base_path}/{ASSET_RELATIVE.as_posix()}" if base_path else f"/{ASSET_RELATIVE.as_posix()}"
    for route in CRITICAL_ROUTES:
        target = site / (route.strip("/") or ".")
        page = target if target.is_file() else target / "index.html"
        assert page.is_file(), route
        html = page.read_text(encoding="utf-8")
        assert STYLE_MARKER in html, route
        assert expected_asset in html, (route, expected_asset)
        assert "skip-link" in html, route
        for forbidden in FORBIDDEN_VISIBLE_COPY:
            assert forbidden not in html.casefold(), (route, forbidden)
    checksums = (site / "checksums.sha256").read_text(encoding="utf-8")
    assert RECEIPT_RELATIVE.as_posix() in checksums
    assert ASSET_RELATIVE.as_posix() in checksums
    return result


def full_artifact_contracts() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        canonical = root / "canonical"
        build(ROOT, canonical, "live-quality-v218-test")

        custom = root / "custom"
        shutil.copytree(canonical, custom)
        prepare(custom, "", "ozaneryavuz/chatgpt", "live-quality-v218-test")
        assert_final_site(custom, "")

        project = root / "project"
        shutil.copytree(canonical, project)
        prepare(project, "/chatgpt", "ozaneryavuz/chatgpt", "live-quality-v218-test")
        assert_final_site(project, "/chatgpt")


def main() -> None:
    source_contracts()
    full_artifact_contracts()
    print(json.dumps({
        "ok": True,
        "version": 218,
        "criticalRoutes": len(CRITICAL_ROUTES),
        "canonicalOrigin": "https://alo186.com",
        "personalDataCollectionAdded": False,
        "newCommerceLinksAdded": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
