from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/alo186-commerce-governance-v2.yml"
text = WORKFLOW.read_text(encoding="utf-8")

required = (
    "LIVE_ORIGIN: https://alo186.com",
    "LIVE_ALIAS_ORIGIN: https://www.alo186.com",
    "alo186/deployment/verify_live_origin.py",
    "alo186/tests/test_live_origin_verifier.py",
    "--expected-commit",
    "github.event.workflow_run.head_sha",
    "--origin \"$LIVE_ORIGIN\"",
    "--alias-origin \"$LIVE_ALIAS_ORIGIN\"",
    "--repository \"$GITHUB_REPOSITORY\"",
    "--receipt /tmp/alo186-live-origin-receipt.json",
    "--diagnostics /tmp/alo186-live-origin-diagnostics",
    "alo186-live-origin-receipt",
)
for token in required:
    assert token in text, f"Canlı origin sözleşmesi eksik: {token}"

for forbidden in (
    '"https://www.alo186.com/pages-release.json?deploy=',
    '"https://www.alo186.com${route}?commerce_check=',
    "assert data.get('canonicalHost') == 'https://www.alo186.com'",
    "Canlı apex alan adı beklenen deploy commitini sunmuyor",
):
    assert forbidden not in text, f"Eski tek-modlu canlı doğrulama varsayımı kaldı: {forbidden}"

verifier = (ROOT / "alo186/deployment/verify_live_origin.py").read_text(encoding="utf-8")
for token in (
    'PAGES_MODE = "github-pages"',
    'SITES_MODE = "chatgpt-sites"',
    "classify_release_response",
    "verify_pages_mode",
    "verify_sites_mode",
    "exactCommitReceiptAvailable",
    "liveContentContractVerified",
    "unavailable-on-chatgpt-sites",
    "wwwAlias",
    "application/json",
    "text/html",
):
    assert token in verifier, f"İki-modlu canlı verifier sözleşmesi eksik: {token}"

print("ALO186 canlı origin workflow Pages ve ChatGPT Sites modlarıyla doğrulandı.")
