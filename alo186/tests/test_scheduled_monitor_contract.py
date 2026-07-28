#!/usr/bin/env python3
"""Fail-closed manual gate and low-noise scheduled monitoring contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/alo186-production-synthetic.yml"


def main() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'cron: "*/15 * * * *"' in text
    assert "concurrency:" in text
    assert "group: alo186-production-synthetic" in text
    assert "cancel-in-progress: true" in text

    # Probe and release drift are captured as incident data, not allowed to stop the
    # scheduled run before artifact and issue deduplication execute.
    assert text.count("continue-on-error: true") >= 2
    assert "alo186-production-synthetic-incident" in text
    assert "signatureMarker" in text
    assert "Aynı incident imzası" in text
    assert "issues.update" in text
    assert "issues.createComment" in text

    # Scheduled failures remain visible through an issue and job summary, while an
    # explicit operator-run verification still fails closed.
    assert "scheduled koşu e-posta gürültüsü üretmez" in text
    assert "Manuel doğrulamada hatayı workflow sonucuna yansıt" in text
    assert "github.event_name == 'workflow_dispatch'" in text
    assert "Manuel production doğrulaması başarısız" in text

    # The old unconditional failure converted every 15-minute incident into a failed
    # scheduled workflow and notification storm; it must not return.
    assert "Kontrol sonucunu workflow sonucuna yansıt" not in text
    assert "if: steps.probe.outcome == 'failure' || steps.drift.outcome == 'failure'\n        run: exit 1" not in text

    print("PASS: scheduled production monitor deduplicates incidents and manual checks fail closed.")


if __name__ == "__main__":
    main()
