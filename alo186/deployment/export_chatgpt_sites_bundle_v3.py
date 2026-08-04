from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

try:
    from .export_chatgpt_sites_bundle import extract_text, markdown_document, read_json, safe_filename, write_json
    from .export_chatgpt_sites_bundle_v2 import export_bundle as export_v2_bundle
except ImportError:
    from export_chatgpt_sites_bundle import extract_text, markdown_document, read_json, safe_filename, write_json
    from export_chatgpt_sites_bundle_v2 import export_bundle as export_v2_bundle

VERSION = 3
ROOT = Path(__file__).resolve().parents[2]
CLAIMS_PATH = ROOT / "alo186/growth/critical-claims-v258.json"
DEADLINE_SCRIPT = ROOT / "alo186/hesaplama/kesinti-gunlugu/damage-deadline-v258.js"

HOME_ROUTE = "/elektrik-portali"
JOURNAL_ROUTE = "/hesaplama/kesinti-gunlugu/"
ARTICLE_ROUTE = "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu"
SOURCES_ROUTE = "/kaynaklar/"

WRONG_HOME_TITLE = "Cihaz hasarında başvuru süresi 30 gündür"
WRONG_HOME_BODY = "zararın ortaya çıktığı tarihten itibaren <strong>30 gün içinde</strong>"
CORRECT_HOME_TITLE = "Cihaz hasarında talep süresi 10 iş günüdür"
CORRECT_HOME_BODY = "zararın ortaya çıktığı tarihten itibaren <strong>10 iş günü içinde</strong>"


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


def _write_page_markdown(output: Path, page: dict[str, Any], html: str) -> None:
    destination = output / "content/pages" / f"{safe_filename(page['canonicalPath'])}.md"
    if not destination.is_file():
        raise FileNotFoundError(destination)
    destination.write_text(markdown_document(page, extract_text(html)), encoding="utf-8")


def _patch_home(output: Path, manifest: dict[str, Any]) -> None:
    page = _page_record(manifest, HOME_ROUTE)
    path = _source_path(output, page)
    html = path.read_text(encoding="utf-8")
    html = _replace_once(html, WRONG_HOME_TITLE, CORRECT_HOME_TITLE, "Ana sayfa cihaz hasarı başlığı")
    html = _replace_once(html, WRONG_HOME_BODY, CORRECT_HOME_BODY, "Ana sayfa cihaz hasarı süresi")
    html = _replace_once(
        html,
        "Olay zamanı, cihaz bilgisi, fotoğraflar, servis raporu ve şirketin yazılı kararını saklayın. ALO186 başvuru veya hasar kaydı almaz.",
        "Olay zamanı, cihaz bilgisi, fotoğraflar, servis raporu ve şirketin yazılı kararını saklayın. Hasarın şebekeden kaynaklandığı resmî incelemeyle belirlenir; ALO186 başvuru, hasar veya tazminat kararı almaz.",
        "Ana sayfa güven açıklaması",
    )
    path.write_text(html, encoding="utf-8")
    _write_page_markdown(output, page, html)


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
        cards.append(
            '<article class="source-card">'
            f'<span class="eyebrow">Son doğrulama: {claims["verifiedAt"]}</span>'
            f'<h3>{claim["label"]}</h3>'
            f'<p><strong>{claim["value"]}</strong></p>'
            f'<p>{claim["scope"]}</p>'
            f'<p><small>{caveat}</small></p>'
            f'<a href="{claim["sourceUrl"]}" rel="external noopener">{claim["sourcePublisher"]} kaynağını aç ↗</a>'
            '</article>'
        )
    return (
        '<section class="section" data-alo186-critical-claims="v258">'
        '<div class="wrap">'
        '<div class="section-heading"><span class="eyebrow">Kritik bilgi · tek kaynak · fail-closed</span>'
        '<h2>Kritik bilgiler ve son doğrulama</h2>'
        '<p>Telefon, başvuru süresi ve resmî işlem yönleri değişebildiği için bu kayıtlar birincil kaynaktan periyodik olarak kontrol edilir. Çelişki varsa ticari içerik değil resmî kaynak önceliklendirilir.</p></div>'
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
    page.setdefault("jsonLd", []).append(schema)
    page["schemaTypes"] = sorted(set(page.get("schemaTypes", [])) | {"Claim", "CreativeWork", "ItemList", "ListItem"})
    _write_page_markdown(output, page, html)


def _deadline_panel() -> str:
    return (
        '<section id="damageDeadlinePlanner" class="content-section" data-alo186-damage-deadline="v258" hidden>'
        '<div class="result-card">'
        '<span class="step">5</span><h2>Cihaz hasarı için 10 iş günlük süre planı</h2>'
        '<p id="damageDeadlineSummary" class="info" aria-live="polite"></p>'
        '<ul id="damageDeadlineEntries" class="evidence-list"></ul>'
        '<div class="warning"><strong>Hukukî ve takvim sınırı:</strong> Bu yardımcı hesap yalnız hafta sonlarını dışlar; resmî tatilleri otomatik hesaplamaz. Hasarın şebekeden kaynaklanıp kaynaklanmadığını ve sürecin sonucunu dağıtım şirketinin resmî incelemesi belirler. ALO186 başvuru veya tazminat kararı almaz.</div>'
        '<div class="actions"><button class="btn btn-secondary" type="button" id="damageReminderBtn">Yerel takvim hatırlatıcısı oluştur</button>'
        '<a class="btn btn-secondary" href="/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu">Belge rehberini aç</a>'
        '<a class="btn btn-secondary" href="https://www.epdk.gov.tr/Detay/Icerik/12-3/1-elektrik-aboneligini-kendi-adima-almak-zorunda" target="_blank" rel="external noopener">EPDK kaynağını doğrula</a></div>'
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
    destination = path.parent / "damage-deadline-v258.js"
    shutil.copy2(DEADLINE_SCRIPT, destination)
    _write_page_markdown(output, page, html)


def _update_date_modified(value: Any) -> None:
    if isinstance(value, dict):
        if value.get("@type") == "Article":
            value["dateModified"] = "2026-08-04"
        for child in value.values():
            _update_date_modified(child)
    elif isinstance(value, list):
        for child in value:
            _update_date_modified(child)


def _patch_article(output: Path, manifest: dict[str, Any]) -> None:
    page = _page_record(manifest, ARTICLE_ROUTE)
    path = _source_path(output, page)
    html = path.read_text(encoding="utf-8")
    html = html.replace('"dateModified":"2026-07-28"', '"dateModified":"2026-08-04"')
    html = html.replace("Son doğrulama: 28 Temmuz 2026", "Son doğrulama: 4 Ağustos 2026")
    path.write_text(html, encoding="utf-8")
    _update_date_modified(page.get("jsonLd", []))
    _write_page_markdown(output, page, html)


def _assert_claim_contract(output: Path, claims: dict[str, Any]) -> None:
    forbidden = [phrase for claim in claims["claims"] for phrase in claim.get("forbiddenPhrases", [])]
    checked_routes = (HOME_ROUTE, JOURNAL_ROUTE, ARTICLE_ROUTE, SOURCES_ROUTE)
    manifest = read_json(output / "sites-import.json", {})
    for route in checked_routes:
        page = _page_record(manifest, route)
        text = _source_path(output, page).read_text(encoding="utf-8")
        for phrase in forbidden:
            if phrase in text:
                raise RuntimeError(f"Yasak kritik iddia bulundu: {route}: {phrase}")
    home = _source_path(output, _page_record(manifest, HOME_ROUTE)).read_text(encoding="utf-8")
    if CORRECT_HOME_TITLE not in home or CORRECT_HOME_BODY not in home:
        raise RuntimeError("Ana sayfa 10 iş günü sözleşmesini taşımıyor")


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

    _patch_home(output, manifest)
    _patch_sources(output, manifest, claims)
    _patch_journal(output, manifest)
    _patch_article(output, manifest)

    manifest["exporterVersion"] = VERSION
    manifest["criticalClaimsVersion"] = claims["version"]
    manifest["criticalClaimsVerifiedAt"] = claims["verifiedAt"]
    manifest["growthActionVersion"] = 258
    write_json(output / "sites-import.json", manifest)
    write_json(output / "data/critical-claims.json", claims)
    write_json(
        output / "data/growth-action-v258.json",
        {
            "version": 258,
            "implementedAt": "2026-08-04",
            "actions": [
                {
                    "priority": 1,
                    "action": "Ana sayfadaki cihaz hasarı talep süresini EPDK kaynağıyla 10 iş günü olarak düzelt",
                    "userBenefit": "Kullanıcının kritik başvuru süresini kaçırma riski azalır.",
                    "revenueImpact": "Doğrudan gelir hedeflemez; güven ve organik dönüşüm temelini korur."
                },
                {
                    "priority": 2,
                    "action": "Kritik telefon ve süre iddialarını kaynak, doğrulama tarihi ve yaş sınırıyla tek kayıt altında yönet",
                    "userBenefit": "112, 186 ve cihaz hasarı süreci açıkça ayrılır; resmî kurum izlenimi önlenir.",
                    "revenueImpact": "Yanlış bilgi kaynaklı güven kaybını ve dönüşüm hunisi terkini azaltır."
                },
                {
                    "priority": 3,
                    "action": "Kesinti günlüğüne kişisel verisiz 10 iş günü süre planı ve yerel takvim hatırlatıcısı ekle",
                    "userBenefit": "Cihaz hasarı işaretleyen kullanıcı belge ve resmî başvuru adımını zamanında takip eder.",
                    "revenueImpact": "Fiyat veya kampanya yerine gerçek olay ve takip ihtiyacına dayalı tekrar ziyaret üretir."
                }
            ],
            "commercialFieldsPublished": [],
            "affiliateLinksAdded": 0,
            "officialInstitutionImpressionCreated": false
        },
    )
    brief = output / "SITE_BRIEF.md"
    brief.write_text(
        brief.read_text(encoding="utf-8")
        + "\n## Kritik bilgi tazeliği v258\n\n"
        + "Telefon, resmî kanal ve başvuru süresi iddiaları `data/critical-claims.json` kaydından uygulanır. "
        + "Cihaz hasarı talebi için EPDK kaynağındaki 10 iş günlük süre kullanılır; 30 gün ifadesi yayımlanamaz. "
        + "Takvim hatırlatıcısı yalnız yardımcıdır, resmî tatilleri otomatik hesaplamaz ve başvuru kararı vermez.\n",
        encoding="utf-8",
    )
    _assert_claim_contract(output, claims)
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
                "stats": manifest["stats"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
