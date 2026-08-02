from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import ai_cms_v220 as cms


def copy_fixture(target: Path) -> None:
    source_root = Path(__file__).resolve().parents[2]
    for relative in (
        cms.CONFIG_PATH,
        cms.SOURCE_POLICY_PATH,
        cms.CONTENT_SCHEMA_PATH,
        cms.PROMPT_PATH,
        cms.REQUESTS_DIR / "example.json",
        cms.PUBLICATION_LOG_PATH,
    ):
        source = source_root / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for directory in (cms.DRAFTS_DIR, cms.APPROVED_DIR, cms.ARCHIVE_DIR):
        (target / directory).mkdir(parents=True, exist_ok=True)


def approved_article(draft: dict) -> dict:
    draft["status"] = "approved"
    draft["sources"] = [
        {
            "title": "Elektrik güvenliği resmî kaynağı",
            "publisher": "T.C. resmî kurum",
            "url": "https://example.gov.tr/teknik-guvenlik?utm_source=test",
            "source_type": "official",
            "supports": "Elektrik güvenliği ve yetkili uzman sınırını destekler.",
            "verified_at": "2026-08-02"
        },
        {
            "title": "UPS üretici bakım dokümanı",
            "publisher": "Üretici teknik dokümantasyonu",
            "url": "https://manufacturer.example.com/docs/ups-maintenance#section",
            "source_type": "manufacturer",
            "supports": "Bakım kaydı, akü testi ve çalışma koşulları için teknik çerçeve sağlar.",
            "verified_at": "2026-08-02"
        }
    ]
    draft["editorial"].update(
        {
            "approval_state": "approved",
            "approval_scope": "institutional",
            "evidence_complete": True,
            "reviewed_at": "2026-08-02",
            "review_notes": ["Kaynak ve güvenlik sınırı kurumsal olarak kontrol edildi."]
        }
    )
    return draft


def main() -> None:
    assert cms.slugify("Kaçak Akım Rölesi Şeçimi") == "kacak-akim-rolesi-secimi"
    assert cms.clean_source_url("https://example.gov.tr/a?utm_source=x&keep=1#b") == "https://example.gov.tr/a?keep=1"
    assert cms.privacy_findings({"contact": "test@example.com"})
    assert cms.privacy_findings({"schema": {"@type": "Person"}})

    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        copy_fixture(root)
        request_path = root / cms.REQUESTS_DIR / "example.json"
        report = cms.generate(
            root,
            request_path,
            None,
            model="offline-test",
            offline_scaffold=True
        )
        assert report["ok"] is True
        assert report["autoPublished"] is False
        draft_path = root / cms.DRAFTS_DIR / "ornek-ups-bakim-karari.json"
        draft = json.loads(draft_path.read_text(encoding="utf-8"))
        assert draft["status"] == "draft"
        assert draft["generation"]["personal_data_used"] is False

        failed = False
        try:
            cms.compile_article(root, draft_path)
        except cms.CmsError:
            failed = True
        assert failed, "Onaysız taslak derlenmemeli"

        approved = approved_article(draft)
        approved_path = root / cms.APPROVED_DIR / "ornek-ups-bakim-karari.json"
        cms.write_json(approved_path, approved)
        compiled = cms.compile_article(root, approved_path)
        assert compiled["ok"] is True
        page = root / compiled["page"]
        text = page.read_text(encoding="utf-8")
        assert 'data-ai-cms-approved="true"' in text
        assert '"@type":"Organization"' in text
        assert '"@type":"Person"' not in text
        assert "ProfilePage" not in text
        assert "amazon." not in text.casefold()
        assert "utm_source" not in text
        overlay = json.loads((root / compiled["overlay"]).read_text(encoding="utf-8"))
        assert overlay["aiCms"]["autoPublished"] is False
        assert overlay["aiCms"]["personalProfilePublished"] is False

        validation = cms.validate_repository(root)
        assert validation["ok"] is True, validation
        audit = cms.audit_repository(root)
        assert audit["ok"] is True, audit
        assert audit["personalProfilePublished"] is False

        approved["title"] = "İletişim test@example.com"
        cms.write_json(approved_path, approved)
        validation = cms.validate_repository(root)
        assert validation["ok"] is False
        assert any("e-posta" in item for item in validation["errors"])

    print(json.dumps({"ok": True, "cmsVersion": cms.VERSION, "autoPublish": False}))


if __name__ == "__main__":
    main()
