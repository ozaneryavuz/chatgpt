from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import finalize_user_entrypoints as entrypoints
import inject_live_quality_hardening as core
from device_damage_deadline import BLOCK_BOUNDARY, REPLACEMENTS as DEVICE_DAMAGE_REPLACEMENTS
from prepare_github_pages import UX_MARKER, install_sitewide_ux


_original_normalize_text = core.normalize_text
_DAMAGE_CONTEXT = re.compile(r"\b(hasar|zarar)\w*\b", re.IGNORECASE)
_APPLICATION_CONTEXT = re.compile(
    r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*",
    re.IGNORECASE,
)
_RESPONSE_CONTEXT = re.compile(
    r"\b(cevap|yanıt|bildir|haklı bulun|ret|redd|teknik rapor)\w*",
    re.IGNORECASE,
)

# Growth injectors run after the canonical source normalization and can add their
# own explanatory cards. These are the exact obsolete application-deadline
# phrases previously observed in final artifacts. The list is intentionally
# narrow so the valid 10-business-day response/report period remains untouched.
_FINAL_ARTIFACT_DEADLINE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (
        "10 iş günlük süreç, kanıt ve resmî başvuru durumunu izleyin.",
        "30 günlük süreç, kanıt ve resmî başvuru durumunu izleyin.",
    ),
    (
        "10 iş günlük başvuru süresini ve dağıtım şirketine götürülecek kanıt kontrolünü düzenler.",
        "30 günlük başvuru süresini ve dağıtım şirketine götürülecek kanıt kontrolünü düzenler.",
    ),
    (
        "10 iş günlük resmî başvuru süresini kontrol edin.",
        "30 günlük resmî başvuru süresini kontrol edin.",
    ),
    ("10 iş günü · kanıt · resmî kanal", "30 gün · kanıt · resmî kanal"),
    (
        "10 iş günlük süreyi, kanıtı ve resmî takip adımlarını düzenleyin.",
        "30 günlük süreyi, kanıtı ve resmî takip adımlarını düzenleyin.",
    ),
)


def _apply_deadline_replacements(text: str) -> str:
    # Reuse the canonical publication migration map so generated copies cannot
    # diverge from the same legal policy. Exact replacements are idempotent.
    for replacements in DEVICE_DAMAGE_REPLACEMENTS.values():
        for old, new in replacements:
            text = text.replace(old, new)
    for old, new in _FINAL_ARTIFACT_DEADLINE_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def normalize_text(text: str) -> str:
    # A previously generated artifact may still contain obsolete application
    # wording. Normalize both canonical source phrases and exact post-injector
    # variants, while preserving a valid 10-business-day response period.
    text = _apply_deadline_replacements(text)
    text = text.replace(
        "zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde EDAŞ kaydı açın",
        "zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    text = text.replace(
        "Zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde EDAŞ kaydı açın",
        "Zararın ortaya çıktığı tarihten itibaren 30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    updated = _original_normalize_text(text)
    updated = updated.replace(
        "10 iş günü içinde EDAŞ kaydı açın",
        "30 gün içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    return _apply_deadline_replacements(updated)


def _normalize_for_scan(text: str) -> str:
    # HTML block endings are legal-statement boundaries. Without this step, a
    # valid response deadline in the next element could mask an obsolete
    # application deadline in the preceding card or paragraph.
    return re.sub(r"\s+", " ", BLOCK_BOUNDARY.sub(". ", text))


def _statement_for_match(normalized: str, match: re.Match[str]) -> str:
    left = max(
        normalized.rfind(".", 0, match.start()),
        normalized.rfind("!", 0, match.start()),
        normalized.rfind("?", 0, match.start()),
    )
    right_candidates = [
        position
        for marker in (".", "!", "?")
        if (position := normalized.find(marker, match.end())) >= 0
    ]
    right = min(right_candidates) if right_candidates else len(normalized)
    return normalized[left + 1 : right + 1]


def wrong_damage_deadline_contexts(text: str) -> list[str]:
    """Yalnız hasar/zarar başvurusu bağlamındaki eski 10 iş günü ifadelerini yakalar.

    Başvurunun reddedilmesinden sonra dağıtım şirketinin teknik raporu veya cevabı
    için geçerli olan 10 iş günlük bildirim süresi yanlış pozitif sayılmaz. Yanıt
    istisnası yalnız aynı cümleye uygulanır; sonraki paragraf eski başvuru süresini
    maskeleyemez.
    """
    normalized = _normalize_for_scan(text)
    contexts: list[str] = []
    for match in core.STALE_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 180)
        end = min(len(normalized), match.end() + 180)
        context = normalized[start:end]
        statement = _statement_for_match(normalized, match)
        if (
            _DAMAGE_CONTEXT.search(context)
            and _APPLICATION_CONTEXT.search(context)
            and not _RESPONSE_CONTEXT.search(statement)
        ):
            contexts.append(context[:360])
    return contexts


def physical_route(route: str, base_path: str) -> str:
    value = str(route or "")
    if base_path and (value == base_path or value.startswith(base_path + "/")):
        value = value[len(base_path):] or "/"
    return value


def update_sitewide_ux_release(path: Path, ux: dict) -> None:
    if not path.is_file():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    existing = payload.get("sitewideUx") if isinstance(payload.get("sitewideUx"), dict) else {}
    existing.update(
        {
            "finalInjectedPages": int(ux.get("injectedPages", 0)),
            "finalAlreadyInjectedPages": int(ux.get("alreadyInjectedPages", 0)),
            "finalHtmlPages": int(ux.get("injectedPages", 0)) + int(ux.get("alreadyInjectedPages", 0)),
            "finalizedAfterGrowthInjectors": True,
            "css": ux.get("css"),
            "js": ux.get("js"),
        }
    )
    payload["sitewideUx"] = existing
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(site: Path, base_path: str) -> dict:
    failures: list[str] = []
    html_count = 0
    canonical_count = 0
    current_deadline_count = 0
    css_href = core.public_url(base_path, f"/{core.CSS_FILE}")
    ux_css_href = core.public_url(base_path, "/assets/alo186-ux.css")
    ux_js_src = core.public_url(base_path, "/assets/alo186-ux.js")

    css_path = site / core.CSS_FILE
    if not css_path.is_file():
        failures.append(f"Canlı kalite CSS dosyası eksik: {core.CSS_FILE}")
    else:
        css = css_path.read_text(encoding="utf-8")
        for token in ("min-height:44px", "focus-visible", ".amazon-intent-card small", "overflow-wrap:anywhere"):
            if token not in css:
                failures.append(f"Canlı kalite CSS sözleşmesi eksik: {token}")

    if not (site / "assets/alo186-ux.css").is_file():
        failures.append("Site geneli UX CSS artifactı eksik")
    if not (site / "assets/alo186-ux.js").is_file():
        failures.append("Site geneli UX JavaScript artifactı eksik")

    for path in core.iter_text_files(site):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if core.LEGACY_ORIGIN in text:
            failures.append(f"Eski www origin kaldı: {path.relative_to(site)}")
        for context in wrong_damage_deadline_contexts(text):
            failures.append(f"Yanlış cihaz hasarı süresi: {path.relative_to(site)} → {context}")
        current_deadline_count += len(core.current_deadline_contexts(text))
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        html_count += 1
        relative = path.relative_to(site)
        if core.CSS_MARKER not in text or css_href not in text:
            failures.append(f"Canlı kalite stylesheet bağlantısı eksik: {relative}")
        if text.count(UX_MARKER) != 2 or ux_css_href not in text or ux_js_src not in text:
            failures.append(f"Final site geneli UX katmanı eksik veya yinelenmiş: {relative}")
        canonical_match = core.CANONICAL_RE.search(text)
        if canonical_match:
            canonical_count += 1
            canonical = canonical_match.group(1)
            if canonical != core.CANONICAL_ORIGIN and not canonical.startswith(core.CANONICAL_ORIGIN + "/"):
                failures.append(f"Canonical origin yanlış: {relative} → {canonical}")

    if current_deadline_count == 0:
        failures.append("Cihaz hasarı başvurusunu yürürlükteki 30 güne bağlayan yayın metni bulunamadı")

    for release_name in ("alo186-release.json", "pages-release.json"):
        release_path = site / release_name
        if not release_path.is_file():
            continue
        release = json.loads(release_path.read_text(encoding="utf-8"))
        if release.get("canonicalHost") != core.CANONICAL_ORIGIN:
            failures.append(f"{release_name} canonicalHost apex değil")
        quality = release.get("liveTechnicalQuality") or {}
        if quality.get("minimumTouchTargetCssPx") != 44:
            failures.append(f"{release_name} canlı kalite sözleşmesi eksik")
        if quality.get("deviceDamageDeadline") != "30 gün":
            failures.append(f"{release_name} cihaz hasarı süre sözleşmesi yanlış")
        if quality.get("personalDataCollectionAdded") is not False:
            failures.append(f"{release_name} kişisel veri güven sözleşmesi eksik")
        if quality.get("officialInstitutionClaimed") is not False:
            failures.append(f"{release_name} resmî kurum güven sözleşmesi eksik")
        sitewide = release.get("sitewideUx") or {}
        if sitewide.get("finalizedAfterGrowthInjectors") is not True:
            failures.append(f"{release_name} final site geneli UX aşaması eksik")
        if sitewide.get("finalHtmlPages") != html_count:
            failures.append(f"{release_name} final HTML/UX sayfa sayısı eşleşmiyor")

    route_count = 0
    core_release = site / "alo186-release.json"
    if core_release.is_file():
        release = json.loads(core_release.read_text(encoding="utf-8"))
        routes = release.get("routes") or []
        route_count = len(routes)
        for item in routes:
            route = item.get("canonicalPath") if isinstance(item, dict) else None
            target_route = physical_route(route, base_path) if route else None
            if target_route and not core.route_exists(site, target_route):
                failures.append(f"Release rotası fiziksel olarak eksik: {route}")

    robots = site / "robots.txt"
    if robots.is_file() and f"Sitemap: {core.CANONICAL_ORIGIN}/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        failures.append("robots.txt apex sitemap adresini taşımıyor")
    sitemap = site / "sitemap.xml"
    if sitemap.is_file():
        sitemap_text = sitemap.read_text(encoding="utf-8")
        if core.LEGACY_ORIGIN in sitemap_text or core.CANONICAL_ORIGIN not in sitemap_text:
            failures.append("sitemap.xml apex canonical origin sözleşmesi başarısız")

    htaccess = site / ".htaccess"
    if htaccess.is_file():
        text = htaccess.read_text(encoding="utf-8")
        if "https://alo186.com%{REQUEST_URI}" not in text or "!^alo186\\.com$" not in text:
            failures.append("Apache apex redirect sözleşmesi eksik")

    if failures:
        raise RuntimeError("ALO186 canlı kalite hardening doğrulaması başarısız:\n- " + "\n- ".join(failures[:100]))
    return {
        "ok": True,
        "canonicalOrigin": core.CANONICAL_ORIGIN,
        "basePath": base_path,
        "htmlCount": html_count,
        "canonicalCount": canonical_count,
        "releaseRouteCount": route_count,
        "sitewideUxHtmlCount": html_count,
        "sitewideUxFinalizedAfterGrowthInjectors": True,
        "deviceDamageDeadline": "30 gün",
        "deviceDamageDeadlineContexts": current_deadline_count,
        "minimumTouchTargetCssPx": 44,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }


core.normalize_text = normalize_text
core.validate = validate


def run(site: Path, base_path: str = "") -> dict:
    site = site.resolve()
    normalized = core.normalize_base_path(base_path)
    ux = install_sitewide_ux(site, normalized)
    update_sitewide_ux_release(site / "alo186-release.json", ux)
    update_sitewide_ux_release(site / "pages-release.json", ux)
    result = core.run(site, normalized)
    result["finalUserEntryPoints"] = entrypoints.run(site, normalized)
    result["sitewideUxFinal"] = {
        **ux,
        "finalHtmlPages": int(ux.get("injectedPages", 0)) + int(ux.get("alreadyInjectedPages", 0)),
        "finalizedAfterGrowthInjectors": True,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı artifactına apex canonical, erişilebilirlik ve final site geneli UX hardening uygular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
