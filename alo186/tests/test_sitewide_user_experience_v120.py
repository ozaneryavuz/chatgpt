from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PORTAL = (ROOT / "alo186/index.html").read_text(encoding="utf-8")
PORTAL_CSS = (ROOT / "alo186/styles.css").read_text(encoding="utf-8")
FINALIZER = (ROOT / "alo186/deployment/finalize_user_experience.py").read_text(encoding="utf-8")
AUDIT_MARKER = 'data-alo186-user-experience="true"'
ALIASES = {
    "bilgi-guncelligi/index.html": "/kaynaklar/",
    "edas/index.html": "/elektrik-dagitim-sirketleri/",
    "isletmeler/index.html": "/isletme-surekliligi/",
    "urun-eslestirme/index.html": "/akilli-urun-secimi/",
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


# Kaynak portal, kullanıcı görevi → hak bilgisi → ücretsiz kaynak → ticari seçenek
# sırasını korumalıdır.
for token in (
    'data-alo186-user-first="true"',
    'data-alo186-toc-disabled="true"',
    'class="task-start"',
    'data-alo186-primary-task="emergency"',
    'data-alo186-primary-task="official"',
    'data-alo186-primary-task="decision"',
    'data-alo186-primary-task="tools"',
    '<details class="resource-library"',
    'Cihaz hasarında başvuru süresi 10 iş günüdür',
    'Satış ortaklığı',
    'Ücretli profesyonel hizmet',
    'Sponsorlu iş birliği',
):
    assert token in PORTAL, token

assert PORTAL.index('class="task-start"') < PORTAL.index('class="legal-alert"')
assert PORTAL.index('class="legal-alert"') < PORTAL.index('class="resource-library"')
assert PORTAL.index('class="resource-library"') < PORTAL.index('class="revenue-sprint"')
for forbidden in ("gelire dönüştüren", "ASIN kartı", "local-first", "30 gün içinde EDAŞ kaydı"):
    assert forbidden not in PORTAL, forbidden
for token in (".task-start", ".task-grid", ".task-card.emergency", ".resource-library"):
    assert token in PORTAL_CSS, token

for token in (
    "brokenInternalLinks",
    "unlabelledControls",
    "unsafeBlankTargets",
    "userFacingMonetizationCopy",
    "aliasPagesCreated",
    "metaDescriptionsPresent",
    "Duplicate id",
    "Old alias",
):
    assert token in FINALIZER, token

with tempfile.TemporaryDirectory(prefix="alo186-sitewide-v120-") as folder:
    canonical = Path(folder) / "canonical"
    custom = Path(folder) / "custom"
    project = Path(folder) / "project"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(canonical),
        "--commit",
        "sitewide-v120-test",
    ])

    results = []
    for target, base_path in ((custom, ""), (project, "/chatgpt")):
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site",
            str(target),
            "--base-path",
            base_path,
            "--repository",
            "ozaneryavuz/chatgpt",
            "--commit",
            "sitewide-v120-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site",
            str(target),
            "--base-path",
            base_path,
        ])

        html_files = sorted(target.rglob("*.html"))
        assert html_files
        release = json.loads((target / "pages-release.json").read_text(encoding="utf-8"))
        audit = release["sitewideUserExperienceAudit"]
        assert audit["ok"] is True
        assert audit["htmlPagesScanned"] == len(html_files)
        assert audit["metaDescriptionsPresent"] == len(html_files)
        assert audit["brokenInternalLinks"] == 0
        assert audit["unlabelledControls"] == 0
        assert audit["unsafeBlankTargets"] == 0
        assert audit["userFacingMonetizationCopy"] == 0
        assert audit["personalDataFieldsAdded"] == 0

        for page in html_files:
            text = page.read_text(encoding="utf-8")
            assert AUDIT_MARKER in text, page.relative_to(target)
            assert len(re.findall(r"<h1\b", text, re.I)) == 1, page.relative_to(target)
            assert re.search(r'<meta\b[^>]*name=["\']description["\']', text, re.I), page.relative_to(target)

        for alias, destination in ALIASES.items():
            alias_page = target / alias
            assert alias_page.is_file(), alias
            alias_html = alias_page.read_text(encoding="utf-8")
            assert f"https://alo186.com{destination}" in alias_html
            assert 'name="robots" content="noindex,follow"' in alias_html

        portal = (target / "elektrik-portali/index.html").read_text(encoding="utf-8")
        assert 'data-alo186-user-first="true"' in portal
        assert 'data-alo186-primary-task="emergency"' in portal
        assert '<details class="resource-library"' in portal
        assert "10 iş günü" in portal
        assert "30 gün içinde EDAŞ kaydı" not in portal
        assert "gerçek ihtiyacı gelire dönüştüren" not in portal

        results.append({
            "target": "custom" if not base_path else "project",
            "htmlPages": len(html_files),
            "aliases": len(ALIASES),
            "brokenLinks": 0,
            "unlabelledControls": 0,
            "unsafeBlankTargets": 0,
            "metaDescriptions": len(html_files),
            "userFirstPortal": True,
        })

run([sys.executable, "-m", "py_compile", "alo186/deployment/finalize_user_experience.py"])
run(["node", "alo186/tests/test_portal_hardening.js"])
run(["node", "alo186/tests/test_portal_inventory_claims.js"])
print(json.dumps({
    "ok": True,
    "targets": results,
    "allPageAudit": True,
    "userFirstPortal": True,
    "progressiveResourceLibrary": True,
    "knownAliases": len(ALIASES),
    "personalDataFieldsAdded": 0,
}, ensure_ascii=False))
