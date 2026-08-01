from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "alo186/deployment/GITHUB_PAGES_CUTOVER.md"
DEADLINE_SOURCE = ROOT / "alo186/deployment/device_damage_deadline.py"
LIVE_WORKFLOW = ROOT / ".github/workflows/alo186-pages-autobootstrap-live.yml"
GATE_WORKFLOW = ROOT / ".github/workflows/alo186-v177-hosting-aware-live.yml"


def main() -> None:
    runbook = RUNBOOK.read_text(encoding="utf-8")
    deadline = DEADLINE_SOURCE.read_text(encoding="utf-8")
    live_workflow = LIVE_WORKFLOW.read_text(encoding="utf-8")
    gate_workflow = GATE_WORKFLOW.read_text(encoding="utf-8")

    required_runbook_tokens = (
        "ALO186_PAGES_ADMIN_TOKEN",
        "Pages: Read and write",
        "Administration: Read and write",
        "Custom domain** alanına `alo186.com`",
        "Final canonical origin: `https://alo186.com`",
        "Cihaz hasarı başvuru süresi güncel kaynak sözleşmesine göre **30 gün**",
        "data-alo186-contextual-affiliate-v177",
        "tam **3** bağlamsal ürün yerleşimi ve **3** ticari kapı",
        "alo186rehber-21",
        "sponsored nofollow noopener",
        "affiliate_context_view",
        "affiliate_gate_open",
        "affiliate_product_select",
        "localStorage",
        "document.cookie",
        "*/30 * * * *",
        ".github/workflows/alo186-pages-autobootstrap-live.yml",
        "Pages hazır değilken ChatGPT Sites kabulü",
        "alo186-full-live-reference",
        "alo186-full-live-receipt",
    )
    for token in required_runbook_tokens:
        assert token in runbook, f"Runbook sözleşmesi eksik: {token}"

    forbidden_runbook_patterns = (
        r"Cihaz hasarı metni\s*`10 iş günü`",
        r"Cihaz hasarı başvuru süresi[^\n]*10 iş günü",
        r"Custom domain[^\n]*`www\.alo186\.com`",
        r"Final canonical origin[^\n]*www\.alo186\.com",
        r"Ana workflow:\s*`?\.github/workflows/alo186-github-pages\.yml`?",
    )
    for pattern in forbidden_runbook_patterns:
        assert not re.search(pattern, runbook, re.IGNORECASE), (
            f"Runbookta eski veya çelişkili sözleşme kaldı: {pattern}"
        )

    assert 'CURRENT_DEADLINE = "30 gün"' in deadline
    assert 'CURRENT_DEADLINE = "10 iş günü"' not in deadline

    required_live_workflow_tokens = (
        "ALO186_PAGES_ADMIN_TOKEN",
        "ADMIN_TOKEN_PRESENT",
        "verify_contextual_affiliate_live_v177.py",
        "sites_current",
        "schedule:",
        "*/30 * * * *",
        "Pages: Read and write",
        "Administration: Read and write",
    )
    for token in required_live_workflow_tokens:
        assert token in live_workflow, f"Canlı workflow sözleşmesi eksik: {token}"

    assert "alo186/deployment/GITHUB_PAGES_CUTOVER.md" in gate_workflow
    assert "alo186/tests/test_pages_cutover_runbook_v177.py" in gate_workflow
    assert "python alo186/tests/test_pages_cutover_runbook_v177.py" in gate_workflow

    print(
        json.dumps(
            {
                "ok": True,
                "canonicalOrigin": "https://alo186.com",
                "deviceDamageDeadline": "30 gün",
                "pagesAdminTokenDocumented": True,
                "pagesPermissionsDocumented": [
                    "Pages: Read and write",
                    "Administration: Read and write",
                ],
                "v177LiveContractDocumented": True,
                "scheduledRetryMinutes": 30,
                "staleTenBusinessDayCopy": False,
                "staleWwwPrimaryDomainCopy": False,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
