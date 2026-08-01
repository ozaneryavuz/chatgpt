from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"
STANDARD = WORKFLOWS / "alo186-github-pages.yml"
BOOTSTRAP = WORKFLOWS / "alo186-pages-autobootstrap-live.yml"


def main() -> None:
    publishers: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        if path.name.startswith("alo186-one-shot-"):
            continue
        text = path.read_text(encoding="utf-8")
        if "actions/deploy-pages@" in text:
            publishers.append(path.name)

    assert publishers == ["alo186-github-pages.yml"], publishers

    standard = STANDARD.read_text(encoding="utf-8")
    assert standard.count("actions/deploy-pages@") == 1
    assert "alo186-pages-production" in standard
    assert "alo186-pages-pr-{0}" in standard
    assert "cancel-in-progress: false" in standard
    assert "python alo186/tests/test_pages_single_publisher.py" in standard
    assert "Fail-closed Pages yayın sonucu" in standard
    assert "verify_live_origin.py" in standard
    assert "verify_contextual_affiliate_live_v177.py" in standard
    assert "alo186-full-live-receipt" in standard

    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    assert "actions/deploy-pages@" not in bootstrap
    assert "actions: write" in bootstrap
    assert "group: alo186-pages-production" in bootstrap
    assert "cancel-in-progress: false" in bootstrap
    assert "already_live_on_sites:" in bootstrap
    assert "sites_current == 'true'" in bootstrap
    assert "dispatch_pages:" in bootstrap
    assert "workflow_id: 'alo186-github-pages.yml'" in bootstrap
    assert "ref: 'main'" in bootstrap

    print(json.dumps({
        "ok": True,
        "publisherCount": len(publishers),
        "publisher": publishers[0],
        "sharedProductionConcurrency": "alo186-pages-production",
        "bootstrapRole": "probe-and-dispatch",
        "chatGPTSitesFallbackPreserved": True,
        "failClosedLiveReceiptInPublisher": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()