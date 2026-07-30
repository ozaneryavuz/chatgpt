from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import finalize_live_quality as live  # noqa: E402
import prepare_github_pages as pages  # noqa: E402
import prepare_github_pages_core as core  # noqa: E402

EXPECTED_ORIGIN = "https://alo186.com"
EXPECTED_HOST = "alo186.com"

assert live.CANONICAL_ORIGIN == EXPECTED_ORIGIN
assert live.CANONICAL_HOST == EXPECTED_HOST
assert pages.LIVE_CANONICAL_ORIGIN == EXPECTED_ORIGIN
assert pages.CANONICAL_ORIGIN == EXPECTED_ORIGIN
assert core.CANONICAL_ORIGIN == EXPECTED_ORIGIN

source = (DEPLOYMENT / "prepare_github_pages.py").read_text(encoding="utf-8")
assert "CANONICAL_ORIGIN as LIVE_CANONICAL_ORIGIN" in source
assert "CANONICAL_ORIGIN = LIVE_CANONICAL_ORIGIN" in source
assert "_core.CANONICAL_ORIGIN = LIVE_CANONICAL_ORIGIN" in source
assert 'release["canonicalHost"] = LIVE_CANONICAL_ORIGIN' in source

with tempfile.TemporaryDirectory(prefix="alo186-pages-origin-") as temp:
    canonical = Path(temp) / "canonical"
    pages_site = Path(temp) / "pages"
    subprocess.run(
        [
            sys.executable,
            str(DEPLOYMENT / "build_static_site.py"),
            "--output",
            str(canonical),
            "--commit",
            "pages-origin-test",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["cp", "-a", str(canonical), str(pages_site)], check=True)
    subprocess.run(
        [
            sys.executable,
            str(DEPLOYMENT / "prepare_github_pages.py"),
            "--site",
            str(pages_site),
            "--base-path",
            "",
            "--repository",
            "ozaneryavuz/chatgpt",
            "--commit",
            "pages-origin-test",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    release = json.loads((pages_site / "pages-release.json").read_text(encoding="utf-8"))
    assert release["canonicalHost"] == EXPECTED_ORIGIN
    assert release["customDomain"] == EXPECTED_HOST
    subprocess.run(
        [
            sys.executable,
            str(DEPLOYMENT / "smoke_github_pages.py"),
            "--site",
            str(pages_site),
            "--base-path",
            "",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

print(json.dumps({
    "ok": True,
    "canonicalOrigin": EXPECTED_ORIGIN,
    "customDomain": EXPECTED_HOST,
    "wildcardNamespaceCollision": False,
}, ensure_ascii=False))
