from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

try:
    from . import export_chatgpt_sites_bundle_v3 as base
except ImportError:
    import export_chatgpt_sites_bundle_v3 as base

VERSION = 4
JOURNAL_ROUTE = "/hesaplama/elektrik-kesintisi-sure-gunlugu/"


def _damage_deadline_panel() -> str:
    return (
        '<section class="trust" data-alo186-damage-deadline="v258">'
        '<h2>Cihaz hasarı şüphesinde 30 günlük süreyi ayrı takip edin</h2>'
        '<p>Kesinti veya şebeke olayı sonrasında cihaz hasarı şüphesi varsa bu günlük yalnız olayın tarih ve süresini düzenler. '
        'Cihaz hasarı talebi için güncel Kalite Yönetmeliği Madde 26/1 kapsamındaki özel süreci ayrıca izleyin; '
        'ALO186 kritik bilgi kaydında zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong> resmî kanaldan işlem yapılması gerektiği esas alınır.</p>'
        '<p><a class="cta" href="/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu">Cihaz hasarı belge rehberini aç</a>'
        f'<a class="cta secondary" href="{base.REGULATION_URL}" target="_blank" rel="external noopener">Kalite Yönetmeliğini doğrula</a></p>'
        '<p class="muted"><strong>Hukukî sınır:</strong> Hasarın dağıtım sisteminden kaynaklanıp kaynaklanmadığını ve sürecin sonucunu dağıtım şirketinin teknik incelemesi belirler. '
        'ALO186 başvuru, hasar veya tazminat kararı almaz. Bu sayfaya ad, e-posta, telefon, açık adres, abonelik veya T.C. kimlik bilgisi girmeyin.</p>'
        '</section>'
    )


def _patch_current_journal(output: Path, manifest: dict[str, Any]) -> None:
    page = base._page_record(manifest, JOURNAL_ROUTE)
    path = base._source_path(output, page)
    html = path.read_text(encoding="utf-8")
    marker = 'data-alo186-damage-deadline="v258"'
    if marker in html:
        raise RuntimeError("Cihaz hasarı süre yönlendirmesi daha önce enjekte edilmiş")
    anchor = '<section class="panel"><h2>Hazırlık planına ne zaman geçilir?</h2>'
    html = base._replace_once(
        html,
        anchor,
        _damage_deadline_panel() + anchor,
        "Güncel kesinti günlüğü hazırlık bölümü",
    )
    path.write_text(html, encoding="utf-8")
    base._refresh_page(output, page, html)


def _assert_claim_contract(output: Path, claims: dict[str, Any]) -> dict[str, object]:
    source_root = output / "source"
    deadline_report = base.validate_published_site(source_root)
    forbidden = [phrase for claim in claims["claims"] for phrase in claim.get("forbiddenPhrases", [])]
    manifest = base.read_json(output / "sites-import.json", {})
    for route in (base.HOME_ROUTE, JOURNAL_ROUTE, base.ARTICLE_ROUTE):
        text = base._source_path(output, base._page_record(manifest, route)).read_text(encoding="utf-8")
        for phrase in forbidden:
            if phrase in text:
                raise RuntimeError(f"Eski kritik iddia bulundu: {route}: {phrase}")
    home = base._source_path(output, base._page_record(manifest, base.HOME_ROUTE)).read_text(encoding="utf-8")
    if base.CURRENT_HOME_TITLE not in home or base.CURRENT_HOME_BODY not in home:
        raise RuntimeError("Ana sayfa 30 günlük cihaz hasarı sözleşmesini taşımıyor")
    journal = base._source_path(output, base._page_record(manifest, JOURNAL_ROUTE)).read_text(encoding="utf-8")
    if 'data-alo186-damage-deadline="v258"' not in journal or "30 gün içinde" not in journal:
        raise RuntimeError("Güncel kesinti günlüğü cihaz hasarı süre yönlendirmesini taşımıyor")
    if deadline_report["deadline"] != base.CURRENT_DEADLINE:
        raise RuntimeError("Cihaz hasarı süre doğrulaması beklenmeyen değer döndürdü")
    return deadline_report


def _growth_action(normalized: list[str], deadline_report: dict[str, object]) -> dict[str, Any]:
    return {
        "version": 258,
        "implementedAt": "2026-08-15",
        "actions": [
            {
                "priority": 1,
                "action": "Eski 10 iş günü içeriklerini yürürlükteki Kalite Yönetmeliği Madde 26/1 uyarınca 30 güne tekilleştir",
                "userBenefit": "Kullanıcı güncel talep süresini tek ve tutarlı biçimde görür; eski SSS metniyle yanıltılmaz.",
                "revenueImpact": "Doğrudan gelir hedeflemez; hukukî doğruluk ve marka güvenini korur."
            },
            {
                "priority": 2,
                "action": "112, 186 ve cihaz hasarı süresini kaynak, değişiklik ve tazelik kaydıyla yönet",
                "userBenefit": "Acil durum, dağıtım arızası ve hasar talebi birbirinden ayrılır; resmî kurum izlenimi önlenir.",
                "revenueImpact": "Yanlış bilgi kaynaklı terk ve güven kaybını azaltır."
            },
            {
                "priority": 3,
                "action": "Güncel Elektrik Kesintisi Süre Günlüğüne cihaz hasarı için 30 günlük resmî süre yönlendirmesi ve belge rehberi ekle",
                "userBenefit": "Kullanıcı kesinti süresi kaydıyla cihaz hasarı talep sürecini karıştırmadan doğru resmî adıma geçer; kişisel veri ALO186'ya gönderilmez.",
                "revenueImpact": "Ürün baskısı yerine olay sonrası yararlı takip ve tekrar ziyaret üretir."
            }
        ],
        "deviceDamageDeadline": base.CURRENT_DEADLINE,
        "normalizedSourceFiles": normalized,
        "verifiedDeadlineLocations": deadline_report["verifiedLocations"],
        "commercialFieldsPublished": [],
        "affiliateLinksAdded": 0,
        "officialInstitutionImpressionCreated": False,
    }


def export_bundle(output: Path, source_commit: str) -> dict[str, Any]:
    manifest = base.export_v2_bundle(output, source_commit)
    claims = base.read_json(base.CLAIMS_PATH, {})
    if claims.get("version") != 258 or len(claims.get("claims", [])) != 3:
        raise RuntimeError("Kritik bilgi kayıtları eksik veya geçersiz")

    normalized = base.normalize_published_site(output / "source")
    base._patch_home(output, manifest)
    base._patch_sources(output, manifest, claims)
    _patch_current_journal(output, manifest)
    base._patch_article_date(output, manifest)

    manifest["exporterVersion"] = VERSION
    manifest["criticalClaimsVersion"] = claims["version"]
    manifest["criticalClaimsVerifiedAt"] = claims["verifiedAt"]
    manifest["deviceDamageDeadline"] = base.CURRENT_DEADLINE
    manifest["deviceDamageRegulationUrl"] = base.REGULATION_URL
    manifest["deviceDamageAmendmentUrl"] = base.AMENDMENT_URL
    manifest["growthActionVersion"] = 258
    manifest["outageJournalCanonicalPath"] = JOURNAL_ROUTE
    base.write_json(output / "sites-import.json", manifest)

    deadline_report = _assert_claim_contract(output, claims)
    base.write_json(output / "data/critical-claims.json", claims)
    base.write_json(output / "data/growth-action-v258.json", _growth_action(normalized, deadline_report))

    brief = output / "SITE_BRIEF.md"
    brief.write_text(
        brief.read_text(encoding="utf-8")
        + "\n## Kritik bilgi tazeliği v258 · güncel kesinti günlüğü\n\n"
        + "Telefon, resmî kanal ve başvuru süresi iddiaları `data/critical-claims.json` kaydından uygulanır. "
        + "Cihaz hasarı talebi için yürürlükteki Kalite Yönetmeliği Madde 26/1 kapsamındaki 30 günlük süre kullanılır; eski 10 iş günü ifadesi yayımlanamaz. "
        + "Kesinti süresi kaydı `/hesaplama/elektrik-kesintisi-sure-gunlugu/` rotasında kişisel veri göndermeden tutulur; cihaz hasarı süreci ayrı belge rehberine yönlendirilir.\n",
        encoding="utf-8",
    )
    base._rebuild_checksums(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ChatGPT Sites kritik bilgi ve güncel kesinti günlüğü export paketi v4")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = parser.parse_args()
    manifest = export_bundle(args.output, args.commit)
    print(json.dumps({
        "targetPlatform": manifest.get("targetPlatform"),
        "exporterVersion": manifest.get("exporterVersion"),
        "criticalClaimsVersion": manifest.get("criticalClaimsVersion"),
        "outageJournalCanonicalPath": manifest.get("outageJournalCanonicalPath"),
        "stats": manifest.get("stats", {}),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
