from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from export_chatgpt_sites_bundle_v3 import export_bundle  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "alo186-chatgpt-sites-v258"
        manifest = export_bundle(output, "test-v258")

        assert manifest["targetPlatform"] == "ChatGPT Sites"
        assert manifest["exporterVersion"] == 3
        assert manifest["criticalClaimsVersion"] == 258
        assert manifest["criticalClaimsVerifiedAt"] == "2026-08-04"
        assert manifest["deviceDamageDeadline"] == "30 gün"
        assert manifest["deviceDamageRegulationUrl"].startswith("https://www.resmigazete.gov.tr/")

        home = (output / "source/index.html").read_text(encoding="utf-8")
        assert "Cihaz hasarında başvuru süresi 30 gündür" in home
        assert "zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong>" in home
        assert "Cihaz hasarında başvuru süresi 10 iş günüdür" not in home
        assert "zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong>" not in home
        assert "ALO186 başvuru, hasar veya tazminat kararı almaz" in home

        home_md = (output / "content/pages/elektrik-portali.md").read_text(encoding="utf-8")
        assert "30 gün" in home_md
        assert "başvuru süresi 10 iş günüdür" not in home_md

        claims = json.loads((output / "data/critical-claims.json").read_text(encoding="utf-8"))
        assert claims["version"] == 258
        assert claims["verifiedAt"] == "2026-08-04"
        assert len(claims["claims"]) == 3
        deadline = next(item for item in claims["claims"] if item["id"] == "device-damage-claim-deadline")
        assert deadline["value"] == "30 gün"
        assert deadline["sourcePublisher"] == "T.C. Resmî Gazete"
        assert deadline["sourceUrl"].startswith("https://www.resmigazete.gov.tr/")
        assert deadline["amendmentUrl"].endswith("20251023-5.htm")
        assert deadline["maximumVerificationAgeDays"] == 30
        assert deadline["conflictingSource"]["staleValue"] == "10 iş günü"

        sources = (output / "source/kaynaklar/index.html").read_text(encoding="utf-8")
        assert 'data-alo186-critical-claims="v258"' in sources
        assert 'data-alo186-critical-claims-schema="v258"' in sources
        assert "Kritik bilgiler ve son doğrulama" in sources
        assert '"@type":"Claim"' in sources
        assert "Çelişen eski kaynak" in sources
        assert "güncel Kalite Yönetmeliği Madde 26/1 esas alınır" in sources
        assert "Kaynak merkezi son gözden geçirme: 4 Ağustos 2026." in sources

        journal = (output / "source/hesaplama/kesinti-gunlugu/index.html").read_text(encoding="utf-8")
        assert 'data-alo186-damage-deadline="v258"' in journal
        for token in ("damageDeadlineSummary", "damageDeadlineEntries", "damageReminderBtn"):
            assert token in journal
        assert '<script src="./damage-deadline-v258.js"></script>' in journal
        assert "Cihaz hasarı için 30 günlük süre planı" in journal
        assert "30 takvim günü" in journal
        assert "ad, e-posta, telefon, adres, abonelik veya başvuru numarası istenmez" in journal
        assert "zararın ortaya çıktığı tarihten itibaren 30 gün içinde" in journal

        script_path = output / "source/hesaplama/kesinti-gunlugu/damage-deadline-v258.js"
        assert script_path.is_file()
        script = script_path.read_text(encoding="utf-8")
        for token in ("addCalendarDays", "BEGIN:VCALENDAR", "30 günlük talep süresi", "localStorage"):
            assert token in script
        assert "10 iş günü" not in script
        for forbidden in ("fetch(", "XMLHttpRequest", "amazon.com.tr", "price", "stock", "rating", "warranty"):
            assert forbidden not in script

        article = (output / "source/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/index.html").read_text(encoding="utf-8")
        assert '"dateModified":"2026-08-04"' in article
        assert "Son doğrulama: 4 Ağustos 2026" in article
        assert "Cihaz hasarı başvurusunda süre 30 gündür" in article
        assert "talebin zararın ortaya çıktığı tarihten itibaren <strong>30 gün</strong> içinde" in article
        assert "özel süre 10 iş günüdür" not in article

        action = json.loads((output / "data/growth-action-v258.json").read_text(encoding="utf-8"))
        assert action["version"] == 258
        assert action["deviceDamageDeadline"] == "30 gün"
        assert len(action["actions"]) == 3
        assert action["affiliateLinksAdded"] == 0
        assert action["commercialFieldsPublished"] == []
        assert action["officialInstitutionImpressionCreated"] is False
        assert action["verifiedDeadlineLocations"] > 0
        assert action["normalizedSourceFiles"]

        sites_manifest = json.loads((output / "sites-import.json").read_text(encoding="utf-8"))
        sources_page = next(page for page in sites_manifest["pages"] if page["canonicalPath"] == "/kaynaklar/")
        assert "Claim" in sources_page["schemaTypes"]
        assert any(item.get("@id") == "https://alo186.com/kaynaklar#critical-claims" for item in sources_page["jsonLd"])

        checksums = (output / "checksums.sha256").read_text(encoding="utf-8")
        for required in (
            "data/critical-claims.json",
            "data/growth-action-v258.json",
            "source/hesaplama/kesinti-gunlugu/damage-deadline-v258.js",
        ):
            assert required in checksums

        print(json.dumps({
            "ok": True,
            "criticalClaimsVersion": manifest["criticalClaimsVersion"],
            "deviceDamageDeadline": manifest["deviceDamageDeadline"],
            "actions": len(action["actions"]),
            "affiliateLinksAdded": action["affiliateLinksAdded"],
            "importReady": manifest["stats"]["importReady"],
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
