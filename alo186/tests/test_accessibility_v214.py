from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import ACCESSIBILITY_MARKER, build  # noqa: E402
from prepare_github_pages import prepare  # noqa: E402

A11Y_ASSET = Path("assets/alo186-accessibility-v214.css")
LINK_PATTERN = re.compile(
    r'<link\s+rel=["\']stylesheet["\']\s+href=["\']([^"\']*alo186-accessibility-v214\.css)["\']\s+data-alo186-accessibility-v214=["\']true["\']>',
    re.IGNORECASE,
)
IMG_PATTERN = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTR_PATTERN = re.compile(
    r"([\w:-]+)(?:\s*=\s*([\"\'])(.*?)\2|\s*=\s*([^\s>]+))?",
    re.DOTALL,
)


def attrs(tag: str) -> dict[str, str]:
    body = tag[tag.find(" ") + 1 : tag.rfind(">")]
    result: dict[str, str] = {}
    for match in ATTR_PATTERN.finditer(body):
        result[match.group(1).lower()] = match.group(3) if match.group(3) is not None else (match.group(4) or "")
    return result


def assert_css_contract(css: str) -> None:
    compact = re.sub(r"\s+", " ", css)
    required = (
        'a[href^="tel:112"]',
        'a[href^="tel:186"]',
        ".article-card > a",
        ".breadcrumbs a",
        ".footer-links a",
        ".sources a",
        'nav[aria-label*="içerik yolu" i] a',
        'input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"])',
        "min-block-size:44px",
        "gap:8px",
        "aspect-ratio:16 / 9",
        "@media(max-width:390px)",
        "max-inline-size:100%",
    )
    missing = [token for token in required if token not in compact]
    assert not missing, missing
    normalized = compact.replace(" ", "").lower()
    assert "overflow-x:hidden" not in normalized
    assert "overflow-inline:hidden" not in normalized


def count_media_fallback_candidates(site: Path) -> int:
    count = 0
    for page in sorted(site.rglob("*.html")):
        route = page.relative_to(site).as_posix()
        if not (route == "haberler/index.html" or route.startswith("haberler/")):
            continue
        source = page.read_text(encoding="utf-8", errors="ignore")
        for tag in IMG_PATTERN.findall(source):
            parsed = attrs(tag)
            if "width" not in parsed or "height" not in parsed:
                count += 1
                assert ACCESSIBILITY_MARKER in source, route
    return count


def assert_bundle(site: Path, release: dict) -> int:
    report = release["accessibilityHardeningV214"]
    assert report["version"] == 214
    assert report["minimumTouchTargetPx"] == 44
    assert report["emergencyTelephoneTargets"] == ["112", "186"]
    assert report["contentImageFallbackRatio"] == "16:9"
    assert report["horizontalOverflowHidden"] is False

    asset = site / A11Y_ASSET
    assert asset.is_file()
    assert_css_contract(asset.read_text(encoding="utf-8"))

    pages = sorted(site.rglob("*.html"))
    assert pages
    assert report["injectedPages"] == len(pages)
    for page in pages:
        source = page.read_text(encoding="utf-8", errors="strict")
        assert source.count(ACCESSIBILITY_MARKER) == 1, page.relative_to(site)
        match = LINK_PATTERN.search(source)
        assert match, page.relative_to(site)
        assert match.group(1) == "/assets/alo186-accessibility-v214.css"

    for route in (
        "elektrik-portali/index.html",
        "elektrik-kesintisi/index.html",
        "acil-numaralar/index.html",
        "haberler/index.html",
    ):
        assert (site / route).is_file(), route
        assert ACCESSIBILITY_MARKER in (site / route).read_text(encoding="utf-8")

    release_file = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    assert release_file["accessibilityHardeningV214"] == report
    checksums = (site / "checksums.sha256").read_text(encoding="utf-8")
    assert "assets/alo186-accessibility-v214.css" in checksums
    return count_media_fallback_candidates(site)


def test_source_contract() -> None:
    css = (ROOT / "alo186/assets/alo186-accessibility-v214.css").read_text(encoding="utf-8")
    assert_css_contract(css)
    wrapper = (ROOT / "alo186/deployment/build_static_site.py").read_text(encoding="utf-8")
    for token in (
        "install_accessibility_hardening",
        "ACCESSIBILITY_MARKER",
        "accessibilityHardeningV214",
        "_recompute_checksums",
    ):
        assert token in wrapper


def test_canonical_and_pages_modes() -> int:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        canonical = base / "canonical"
        release = build(ROOT, canonical, "accessibility-v214-test")
        media_candidates = assert_bundle(canonical, release)

        custom = base / "custom"
        shutil.copytree(canonical, custom)
        custom_release = prepare(custom, "", "ozaneryavuz/chatgpt", "accessibility-v214-test")
        assert custom_release["basePath"] == ""
        custom_page = (custom / "elektrik-kesintisi/index.html").read_text(encoding="utf-8")
        assert 'href="/assets/alo186-accessibility-v214.css"' in custom_page
        assert (custom / A11Y_ASSET).is_file()

        project = base / "project"
        shutil.copytree(canonical, project)
        project_release = prepare(project, "/chatgpt", "ozaneryavuz/chatgpt", "accessibility-v214-test")
        assert project_release["basePath"] == "/chatgpt"
        project_page = (project / "elektrik-kesintisi/index.html").read_text(encoding="utf-8")
        assert 'href="/chatgpt/assets/alo186-accessibility-v214.css"' in project_page
        assert (project / A11Y_ASSET).is_file()
        return media_candidates


def main() -> None:
    test_source_contract()
    media_candidates = test_canonical_and_pages_modes()
    print(json.dumps({
        "ok": True,
        "version": 214,
        "minimumTouchTargetPx": 44,
        "mediaFallbackCandidates": media_candidates,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
