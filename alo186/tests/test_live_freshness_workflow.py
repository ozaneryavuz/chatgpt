from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/alo186-commerce-governance-v2.yml"
text = WORKFLOW.read_text(encoding="utf-8")

required = (
    "LIVE_ORIGIN: https://alo186.com",
    "LIVE_ALIAS_ORIGIN: https://www.alo186.com",
    "--location",
    "--fail-with-body",
    "%{content_type}",
    "%{url_effective}",
    "application/json",
    "alo186-live-release.meta",
    "alo186-live-alias.meta",
    "assert pages['canonicalHost'] == release['canonicalHost']",
    "canonical_host=release['canonicalHost'].rstrip('/')",
)
for token in required:
    assert token in text, f"Canlı tazelik sözleşmesi eksik: {token}"

for forbidden in (
    '"https://www.alo186.com/pages-release.json?deploy=',
    '"https://www.alo186.com${route}?commerce_check=',
    'assert data.get(\'canonicalHost\') == \'https://www.alo186.com\'',
    "assert f'https://www.alo186.com{route}' in sitemap",
):
    assert forbidden not in text, f"Eski www canlı doğrulama varsayımı kaldı: {forbidden}"

assert "redirect_url" in text and "308" in text
assert "Path('/tmp/alo186-live-release.json').stat().st_size > 0" in text
assert "urlparse(effective_url).hostname == 'alo186.com'" in text
assert "content_type.lower().startswith('application/json')" in text

print("ALO186 canlı tazelik workflow apex, yönlendirme ve MIME sözleşmeleri başarılı.")
