from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import inject_live_quality_hardening as core


_original_normalize_text = core.normalize_text
_DAMAGE_CONTEXT = re.compile(r"\b(hasar|zarar)\w*\b", re.IGNORECASE)
_APPLICATION_CONTEXT = re.compile(
    r"\b(başvur|basvur|talep|tazmin|dağıtım şirket|dagitim sirket|edaş|edas)\w*",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    # En uzun ve kullanıcıyı doğrudan yanlış kanala yönlendiren eski cümleyi
    # önce düzeltiriz; aksi halde daha kısa 30 gün değişimi ikinci eşleşmeyi bozar.
    text = text.replace(
        "zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın",
        "zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    text = text.replace(
        "Zararın ortaya çıktığı tarihten itibaren 30 gün içinde EDAŞ kaydı açın",
        "Zararın ortaya çıktığı tarihten itibaren 10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    updated = _original_normalize_text(text)
    # Kısa dönüşüm daha önce çalışmış eski artifactlar için de fail-safe temizlik.
    updated = updated.replace(
        "10 iş günü içinde EDAŞ kaydı açın",
        "10 iş günü içinde ilgili dağıtım şirketinin resmî kanalına başvurun",
    )
    return updated


def wrong_damage_deadline_contexts(text: str) -> list[str]:
    """Yalnız hasar/zarar başvurusu bağlamındaki 30 gün ifadelerini yakalar.

    Tarayıcıdaki yerel kayıtların 30 gün saklanması gibi gizlilik süreleri bu
    güvenlik kapısının konusu değildir ve yanlış pozitif üretmemelidir.
    """
    normalized = re.sub(r"\s+", " ", text)
    contexts: list[str] = []
    for match in core.WRONG_DEADLINE.finditer(normalized):
        start = max(0, match.start() - 180)
        end = min(len(normalized), match.end() + 180)
        context = normalized[start:end]
        if _DAMAGE_CONTEXT.search(context) and _APPLICATION_CONTEXT.search(context):
            contexts.append(context[:360])
    return contexts


def physical_route(route: str, base_path: str) -> str:
    value = str(route or "")
    if base_path and (value == base_path or value.startswith(base_path + "/")):
        value = value[len(base_path):] or "/"
    return value


def validate(site: Path, base_path: str) -> dict:
    failures: list[str] = []
    html_count = 0
    canonical_count = 0
    css_href = core.public_url(base_path, f"/{core.CSS_FILE}")

    css_path = site / core.CSS_FILE
    if not css_path.is_file():
        failures.append(f"Canlı kalite CSS dosyası eksik: {core.CSS_FILE}")
    else:
        css = css_path.read_text(encoding="utf-8")
        for token in ("min-height:44px", "focus-visible", ".amazon-intent-card small", "overflow-wrap:anywhere"):
            if token not in css:
                failures.append(f"Canlı kalite CSS sözleşmesi eksik: {token}")

    for path in core.iter_text_files(site):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if core.LEGACY_ORIGIN in text:
            failures.append(f"Eski www origin kaldı: {path.relative_to(site)}")
        for context in wrong_damage_deadline_contexts(text):
            failures.append(f"Yanlış cihaz hasarı süresi: {path.relative_to(site)} → {context}")
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        html_count += 1
        if core.CSS_MARKER not in text or css_href not in text:
            failures.append(f"Canlı kalite stylesheet bağlantısı eksik: {path.relative_to(site)}")
        canonical_match = core.CANONICAL_RE.search(text)
        if canonical_match:
            canonical_count += 1
            canonical = canonical_match.group(1)
            if canonical != core.CANONICAL_ORIGIN and not canonical.startswith(core.CANONICAL_ORIGIN + "/"):
                failures.append(f"Canonical origin yanlış: {path.relative_to(site)} → {canonical}")

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
        if quality.get("personalDataCollectionAdded") is not False:
            failures.append(f"{release_name} kişisel veri güven sözleşmesi eksik")
        if quality.get("officialInstitutionClaimed") is not False:
            failures.append(f"{release_name} resmî kurum güven sözleşmesi eksik")

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
        "deviceDamageDeadline": "10 iş günü",
        "minimumTouchTargetCssPx": 44,
        "personalDataCollectionAdded": False,
        "officialInstitutionClaimed": False,
    }


core.normalize_text = normalize_text
core.validate = validate
run = core.run


def main() -> None:
    parser = argparse.ArgumentParser(description="ALO186 canlı artifactına apex canonical ve erişilebilirlik hardening uygular.")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(json.dumps(run(args.site, args.base_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
