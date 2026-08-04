from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

try:
    from .device_damage_deadline import (
        AMENDMENT_URL,
        CURRENT_DEADLINE,
        REGULATION_URL,
        normalize_published_site,
        validate_published_site,
    )
    from .export_chatgpt_sites_bundle import (
        collect_schema_types,
        extract_text,
        jsonld_blocks,
        markdown_document,
        read_json,
        safe_filename,
        write_json,
    )
    from .export_chatgpt_sites_bundle_v2 import export_bundle as export_v2_bundle
except ImportError:
    from device_damage_deadline import (
        AMENDMENT_URL,
        CURRENT_DEADLINE,
        REGULATION_URL,
        normalize_published_site,
        validate_published_site,
    )
    from export_chatgpt_sites_bundle import (
        collect_schema_types,
        extract_text,
        jsonld_blocks,
        markdown_document,
        read_json,
        safe_filename,
        write_json,
    )
    from export_chatgpt_sites_bundle_v2 import export_bundle as export_v2_bundle

VERSION = 3
ROOT = Path(__file__).resolve().parents[2]
CLAIMS_PATH = ROOT / "alo186/growth/critical-claims-v258.json"
DEADLINE_SCRIPT = ROOT / "alo186/hesaplama/kesinti-gunlugu/damage-deadline-v258.js"

HOME_ROUTE = "/elektrik-portali"
JOURNAL_ROUTE = "/hesaplama/kesinti-gunlugu/"
ARTICLE_ROUTE = "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu"
SOURCES_ROUTE = "/kaynaklar"
CURRENT_HOME_TITLE = "Cihaz hasarında başvuru süresi 30 gündür"
CURRENT_HOME_BODY = "zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong>"


def _page_record(manifest: dict[str, Any], route: str) -> dict[str, Any]:
    for page in manifest.get("pages", []):
        if page.get("canonicalPath") == route:
            return page
    raise RuntimeError(f"ChatGPT Sites manifestinde rota bulunamadı: {route}")


def _source_path(output: Path, page: dict[str, Any]) -> Path:
    value = page.get("sourceCopy")
    if not isinstance(value, str) or not value.startswith("source/"):
        raise RuntimeError(f"Geçersiz sourceCopy: {page.get('canonicalPath')}")
    path = output / value
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: beklenen ifade sayısı 1, bulunan {count}")
    return source.replace(old, new, 1)


def _refresh_page(output: Path, page: dict[str, Any], html: str) -> None:
    blocks = jsonld_blocks(html)
    page["jsonLd"] = blocks
    page["schemaTypes"] = sorted(set().union(*(collect_schema_types(item) for item in blocks))) if blocks else []
    destination = output / "content/pages" / f"{safe_filename(page['canonicalPath'])}.md"
    if not destination.is_file():
        raise FileNotFoundError(destination)
    destination.write_text(markdown_document(page, extract_text(html)), encoding="utf-8")


def _patch_home(output: Path, manifest: dict[str, Any]) -> None:
    page = _page_record(manifest, HOME_ROUTE)
    path = _source_path(output, page)
    html = path.read_text(encoding="utf-8")
    if CURRENT_HOME_TITLE not in html or CURRENT_HOME_BODY not in html:
        raise RuntimeError("Ana sayfa güncel 30 günlük cihaz hasarı talep süresini taşımıyor")
    old = "Olay zamanı, cihaz bilgisi, fotoğraflar, servis raporu ve şirketin yazılı kararını saklayın. ALO186 başvuru veya hasar kaydı almaz."
    new = "Olay zamanı, cihaz bilgisi, fotoğraflar, servis raporu ve şirketin yazılı kararını saklayın. Hasarın dağıtım sisteminden kaynaklandığı teknik raporla belirlenir; ALO186 başvuru, hasar veya tazminat kararı almaz."
    if old in html:
        html = _replace_once(html, old, new, "Ana sayfa güven açıklaması")
    elif new not in html:
        raise RuntimeError("Ana sayfa cihaz hasarı güven açıklaması bulunamadı")
    path.write_text(html, encoding="utf-8")
    _refresh_page(output, page, html)


def _critical_claim_schema(claims: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for position, claim in enumerate(claims["claims"], start=1):
        items.append(
            {
                "@type": "ListItem",
                "position": position,
                "item": {
                    "@type": "Claim",
                    "@id": f"https://alo186.com/kaynaklar#claim-{claim['id']}",
                    "name": claim["label"],
                    "text": claim["value"],
                    "dateModified": claims["verifiedAt"],
                    "appearance": {
                        "@type": "CreativeWork",
                        "url": claim["sourceUrl"],
                        "publisher": {"@type": "Organization", "name": claim["sourcePublisher"]},
                    },
                },
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "@id": "https://alo186.com/kaynaklar#critical-claims",
        "name": "ALO186 kritik bilgi doğrulama kayıtları",
        "dateModified": claims["verifiedAt"],
        "numberOfItems": len(items),
        "itemListElement": items,
    }


def _claims_section(claims: dict[str, Any]) -> str:
    cards: list[str] = []
    for claim in claims["claims"]:
        caveat = claim["requiredCaveats"][0]
        conflict = ""
        if claim.get("conflictingSource"):
            conflict = (
                '<p class="danger-note"><strong>Çelişen eski kaynak:</strong> '
                'EPDK tüketici SSS sayfasında eski süre görülebilir. Güncel Kalite Yönetmeliği Madde 26/1 esas alınır.</p>'
            )
        cards.append(
            '<article class="source-card">'
            f'<span class="eyebrow">Son doğrulama: {claims["verifiedAt"]}</span>'
            f'<h3>{claim["label"]}</h3>'
            f'<p><strong>{claim["value"]}</strong></p>'
            f'<p>{claim["scope"]}</p>'
            f'<p><small>{caveat}</small></p>'
            f'{conflict}'
            f'<a href="{claim["sourceUrl"]}" rel="external noopener">{claim["sourcePublisher"]} kaynağını aç ↗</a>'
            '</article>'
        )
    return (
        '<section class="section" data-alo186-critical-claims="v258">'
        '<div class="wrap">'
        '<div class="section-heading"><span class="eyebrow">Kritik bilgi · güncel mevzuat · fail-closed</span>'
        '<h2>Kritik bilgiler ve son doğrulama</h2>'
        '<p>Telefon, başvuru süresi ve resmî işlem yönleri değişebildiği için birincil ve yürürlükteki kaynaklar periyodik olarak kontrol edilir. Çelişki varsa ticari içerik değil güncel mevzuat ve resmî kanal önceliklendirilir.</p></div>'
        f'<div class="sources">{"".join(cards)}</div>'
        '</div></section>'
    )


def _patch_sources(output: Path, manifest: dict[str, Any], claims: dict[str, Any]) -> None:
    page = _page_record(manifest, SOURCES_ROUTE)
    path = _source_path(output, page)
    html = path.read_text(encoding="utf-8")
    marker = 'data-alo186-critical-claims="v258"'
    if marker in html:
        raise RuntimeError("Kritik bilgi bölümü daha önce enjekte edilmiş")
    html = _replace_once(html, "</main>", _claims_section(claims) + "</main>", "Kaynak merkezi main kapanışı")
    schema = _critical_claim_schema(claims)
    schema_tag = '<script type="application/ld+json" data-alo186-critical-claims-schema="v258">' + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"
    html = _replace_once(html, "</head>", schema_tag + "\n</head>", "Kaynak merkezi head kapanışı")
    html = html.replace("Kaynak merkezi son gözden geçirme: 30 Temmuz 2026.", "Kaynak merkezi son gözden geçirme: 4 Ağustos 2026.")
    path.write_text(html, encoding="utf-8")
    _refresh_page(output, page, html)


def _deadline_panel() -> str:
    return (
        '<section id="damageDeadlinePlanner" class="content-section" data-alo186-damage-deadline="v258" hidden>'
        '<div class="result-card">'
        '<span class="step">5</span><h2>Cihaz hasarı için 30 günlük süre planı</h2>'
        '<p id="damageDeadlineSummary" class="info" aria-live="polite"></p>'
        '<ul id="damageDeadlineEntries" class="evidence-list"></ul>'
        '<div class="warning"><strong>Hukukî sınır:</strong> Bu araç olay tarihine 30 takvim günü ekleyen yardımcı bir plandır. Hasarın dağıtım sisteminden kaynaklanıp kaynaklanmadığını ve sürecin sonucunu dağıtım şirketinin teknik incelemesi belirler. ALO186 başvuru veya tazminat kararı almaz.</div>'
        '<div class="actions"><button class="btn btn-secondary" type="button" id="damageReminderBtn">Yerel takvim hatırlatıcısı oluştur</button>'
        '<a class="btn btn-secondary" href="/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu">Belge rehberini aç</a>'
        f'<a class="btn btn-secondary" href="{REGULATION_URL}" target="_blank" rel="external noopener">Kalite Yönetmeliğini doğrula</a></div>'
        '<small>Hatırlatıcı cihazınızda oluşturulur; ad, e-posta, telefon, adres, abonelik veya başvuru numarası istenmez.</small>'
        '</div></section>'
    )


def _patch_journal(output: Path, manifest: dict[str, Any]) -> None:
    page = _page_record(manifest, JOURNAL_ROUTE)
    path = _source_path(output, page)
    html = path.read_text(encoding="utf-8")
    if 'data-alo186-damage-deadline="v258"' in html:
        raise RuntimeError("Cihaz hasarı süre planı daha önce enjekte edilmiş")
    html = _replace_once(
        html,
        '<section class="content-section"><div class="faq">',
        _deadline_panel() + '<section class="content-section"><div class="faq">',
        "Kesinti günlüğü FAQ başlangıcı",
    )
    html = _replace_once(
        html,
        '<script src="./app.js"></script></body>',
        '<script src="./app.js"></script><script src="./damage-deadline-v258.js"></script></body>',
        "Kesinti günlüğü script zinciri",
    )
    path.write_text(html, encoding="utf-8")
    shutil.copy2(DEADLINE_SCRIPT, path.parent / "damage-deadline-v258.js")
    _refresh_page(output, page, html)


def _patch_article_date(output: Path, manifest: dict[str, Any]) -> None:
    page = _page_record(manifest, ARTICLE_ROUTE)
    path = _source_path(output, page)
    html = path.read_text(encoding="utf-8")
    html = html.replace('"dateModified":"2026-07-28"', '"dateModified":"2026-08-04"')
    html = html.replace("Son doğrulama: 28 Temmuz 2026", "Son doğrulama: 4 Ağustos 2026")
    path.write_text(html, encoding="utf-8")
    _refresh_page(output, page, html)


def _assert_claim_contract(output: Path, claims: dict[str, Any]) -> dict[str, object]:
    source_root = output / "source"
    deadline_report = validate_published_site(source_root)
    forbidden = [phrase for claim in claims["claims"] for phrase in claim.get("forbiddenPhrases", [])]
    manifest = read_json(output / "sites-import.json", {})
    for route in (HOME_ROUTE, JOURNAL_ROUTE, ARTICLE_ROUTE):
        text = _source_path(output, _page_record(manifest, route)).read_text(encoding="utf-8")
        for phrase in forbidden:
            if phrase in text:
                raise RuntimeError(f"Eski kritik iddia bulundu: {route}: {phrase}")
    home = _source_path(output, _page_record(manifest, HOME_ROUTE)).read_text(encoding="utf-8")
    if CURRENT_HOME_TITLE not in home or CURRENT_HOME_BODY not in home:
        raise RuntimeError("Ana sayfa 30 günlük cihaz hasarı sözleşmesini taşımıyor")
    if deadline_report["deadline"] != CURRENT_DEADLINE:
        raise RuntimeError("Cihaz hasarı süre doğrulaması beklenmeyen değer döndürdü")
    return deadline_report


def _rebuild_checksums(output: Path) -> None:
    checksum = output / "checksums.sha256"
    if checksum.exists():
        checksum.unlink()
    lines: list[str] = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(output).as_posix()}")
    checksum.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_bundle(output: Path, source_commit: str) -> dict[str, Any]:
    manifest = export_v2_bundle(output, source_commit)
    claims = read_json(CLAIMS_PATH, {})
    if claims.get("version") != 258 or len(claims.get("claims", [])) != 3:
        raise RuntimeError("Kritik bilgi kayıtları eksik veya geçersiz")

    normalized = normalize_published_site(output / "source")
    _patch_home(output, manifest)
    _patch_sources(output, manifest, claims)
    _patch_journal(output, manifest)
    _patch_article_date(output, manifest)

    manifest["exporterVersion"] = VERSION
    manifest["criticalClaimsVersion"] = claims["version"]
    manifest["criticalClaimsVerifiedAt"] = claims["verifiedAt"]
    manifest["deviceDamageDeadline"] = CURRENT_DEADLINE
    manifest["deviceDamageRegulationUrl"] = REGULATION_URL
    manifest["deviceDamageAmendmentUrl"] = AMENDMENT_URL
    manifest["growthActionVersion"] = 258
    write_json(output / "sites-import.json", manifest)
    deadline_report = _assert_claim_contract(output, claims)
    write_json(output / "data/critical-claims.json", claims)
    write_json(
        output / "data/growth-action-v258.json",
        {
            "version": 258,
            "implementedAt": "2026-08-04",
            "actions": [
                {
                    "priority": 1,
                    "action": "Eski 10 iş günü içeriklerini yürürlükteki Kalite Yönetmeliği Madde 26/1 uyarınca 30 güne tekilleştir",
                    "userBenefit": "Kullanıcı güncel talep süresini tek ve tutarlı biçimde görür; eski EPDK SSS metniyle yanıltılmaz.",
                    "revenueImpact": "Doğrudan gelir hedeflemez; hukukî doğruluk ve marka güvenini koruyarak organik dönüşüm kaybını azaltır."
                },
                {
                    "priority": 2,
                    "action": "112, 186 ve cihaz hasarı süresini kaynak, değişiklik ve tazelik kaydıyla yönet",
                    "userBenefit": "Acil durum, dağıtım arızası ve hasar talebi birbirinden ayrılır; resmî kurum izlenimi önlenir.",
                    "revenueImpact": "Yanlış bilgi kaynaklı terk ve güven kaybını azaltır; güvenli teknik yolculukların tamamlanma olasılığını artırır."
                },
                {
                    "priority": 3,
                    "action": "Kesinti günlüğüne kişisel verisiz 30 günlük süre planı ve yerel takvim hatırlatıcısı ekle",
                    "userBenefit": "Cihaz hasarı işaretleyen kullanıcı belge ve resmî talep adımını zamanında takip eder.",
                    "revenueImpact": "Fiyat veya kampanya yerine gerçek olay ve takip ihtiyacına dayalı tekrar ziyaret üretir."
                }
            ],
            "deviceDamageDeadline": CURRENT_DEADLINE,
            "normalizedSourceFiles": normalized,
            "verifiedDeadlineLocations": deadline_report["verifiedLocations"],
            "commercialFieldsPublished": [],
            "affiliateLinksAdded": 0,
            "officialInstitutionImpressionCreated": False
        },
    )
    brief = output / "SITE_BRIEF.md"
    brief.write_text(
        brief.read_text(encoding="utf-8")
        + "\n## Kritik bilgi tazeliği v258\n\n"
        + "Telefon, resmî kanal ve başvuru süresi iddiaları `data/critical-claims.json` kaydından uygulanır. "
        + "Cihaz hasarı talebi için yürürlükteki Kalite Yönetmeliği Madde 26/1 kapsamındaki 30 günlük süre kullanılır; eski 10 iş günü ifadesi yayımlanamaz. "
        + "Takvim hatırlatıcısı yalnız yardımcıdır ve başvuru veya tazminat kararı vermez.\n",
        encoding="utf-8",
    )
    _rebuild_checksums(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 ChatGPT Sites kritik bilgi ve güven paketi v258")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--commit", default=os.environ.get("GITHUB_SHA", "unknown"))
    args = parser.parse_args()
    manifest = export_bundle(args.output.resolve(), args.commit)
    print(
        json.dumps(
            {
                "ok": True,
                "exporterVersion": VERSION,
                "criticalClaimsVersion": manifest["criticalClaimsVersion"],
                "deviceDamageDeadline": manifest["deviceDamageDeadline"],
                "stats": manifest["stats"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
