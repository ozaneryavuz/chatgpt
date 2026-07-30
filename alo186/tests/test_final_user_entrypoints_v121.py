from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import finalize_user_entrypoints as entrypoints  # noqa: E402


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


finalizer_source = (DEPLOYMENT / "inject_live_quality_hardening_v2.py").read_text(encoding="utf-8")
for token in (
    "import finalize_user_entrypoints as entrypoints",
    'result["finalUserEntryPoints"] = entrypoints.run(site, normalized)',
):
    assert token in finalizer_source, token

helper_source = (DEPLOYMENT / "finalize_user_entrypoints.py").read_text(encoding="utf-8")
for token in (
    "FORBIDDEN_VISIBLE_TERMS",
    "data-alo186-secondary-tools",
    "minimumTouchTargetCssPx",
    "recompute_checksums",
):
    assert token in helper_source, token

with tempfile.TemporaryDirectory(prefix="alo186-final-entrypoints-v121-") as folder:
    site = Path(folder) / "site"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(site),
        "--commit",
        "final-entrypoints-v121-test",
    ])
    run([
        sys.executable,
        "alo186/deployment/prepare_github_pages.py",
        "--site",
        str(site),
        "--base-path",
        "",
        "--repository",
        "ozaneryavuz/chatgpt",
        "--commit",
        "final-entrypoints-v121-test",
    ])
    run([
        sys.executable,
        "alo186/deployment/inject_outcome_runtime.py",
        "--site",
        str(site),
        "--base-path",
        "",
    ])
    run([
        sys.executable,
        "alo186/deployment/inject_shortlist_growth.py",
        "--site",
        str(site),
        "--base-path",
        "",
    ])
    run([
        sys.executable,
        "alo186/deployment/inject_live_quality_hardening_v2.py",
        "--site",
        str(site),
        "--base-path",
        "",
    ])
    run([
        sys.executable,
        "alo186/deployment/smoke_github_pages.py",
        "--site",
        str(site),
        "--base-path",
        "",
    ])

    audit = entrypoints.audit(site)
    assert audit["ok"] is True
    assert audit["primaryCardCount"] == 5
    assert audit["secondaryCardCount"] >= 1
    assert audit["userFacingInternalJargon"] == 0
    assert audit["minimumTouchTargetCssPx"] == 44

    root = (site / "index.html").read_text(encoding="utf-8")
    portal = (site / "elektrik-portali/index.html").read_text(encoding="utf-8")
    assert root.index('data-alo186-primary-start="true"') < root.index('data-alo186-secondary-tools="true"')
    assert root.count('data-alo186-secondary-tools="true"') == 1
    for html in (root, portal):
        copy = entrypoints.visible_text(html).casefold()
        for forbidden in entrypoints.FORBIDDEN_VISIBLE_TERMS:
            assert forbidden.casefold() not in copy, forbidden

    css = (site / entrypoints.CSS_FILE).read_text(encoding="utf-8")
    assert entrypoints.CSS_MARKER in css
    assert '.button,.btn,a[role="button"]{display:inline-flex' in css
    assert ".alo186-more-tools" in css

    for release_name in ("alo186-release.json", "pages-release.json"):
        release = json.loads((site / release_name).read_text(encoding="utf-8"))
        final_audit = release["finalUserEntryPointAudit"]
        assert final_audit["primaryCardsFirst"] is True
        assert final_audit["primaryCardCount"] == 5
        assert final_audit["secondaryToolsProgressive"] is True
        assert final_audit["userFacingInternalJargon"] == 0
        assert final_audit["minimumTouchTargetCssPx"] == 44
        assert final_audit["personalDataCollectionAdded"] is False
        assert final_audit["officialInstitutionClaimed"] is False

print(json.dumps({
    "ok": True,
    "criticalPages": 2,
    "primaryCardCount": 5,
    "secondaryToolsProgressive": True,
    "userFacingInternalJargon": 0,
    "minimumTouchTargetCssPx": 44,
    "personalDataCollectionAdded": False,
    "officialInstitutionClaimed": False,
}, ensure_ascii=False))
