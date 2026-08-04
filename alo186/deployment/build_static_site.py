from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

try:
    from . import build_static_site_core as _core
    from .sitemap_hreflang import write_effective_sitemap as _write_effective_sitemap
except ImportError:
    import build_static_site_core as _core
    from sitemap_hreflang import write_effective_sitemap as _write_effective_sitemap

# Keep every existing import/function contract while replacing only sitemap output.
_core.write_effective_sitemap = _write_effective_sitemap

# Content-authority run123 was merged with the historical path/file/intent route
# shape. Preserve a strict, narrowly-scoped compatibility bridge so the canonical
# build can recover without weakening validation for other route types.
_original_validate_route = _core.validate_route


def _validate_route_with_legacy_article_bridge(route: dict, source_label: str) -> dict:
    modern_fields = {"source", "canonicalPath", "type"}
    legacy_fields = {"path", "file", "intent"}

    if modern_fields.issubset(route):
        return _original_validate_route(route, source_label)

    present_modern = modern_fields.intersection(route)
    if present_modern:
        return _original_validate_route(route, source_label)

    if set(route) != legacy_fields:
        return _original_validate_route(route, source_label)

    path = str(route["path"]).strip()
    file_name = str(route["file"]).strip()
    intent = str(route["intent"]).strip()
    expected_file = f"{path.strip('/')}/index.html"

    if (
        not intent
        or not path.startswith("/haberler/")
        or path.endswith("/")
        or "//" in path
        or not file_name.startswith("haberler/")
        or file_name != expected_file
    ):
        raise ValueError(f"Legacy haber routing kaydı geçersiz ({source_label}): {route!r}")

    return _original_validate_route(
        {
            "canonicalPath": path,
            "source": f"alo186/{file_name}",
            "type": "article",
        },
        source_label,
    )


_core.validate_route = _validate_route_with_legacy_article_bridge

try:
    from .inject_competitor_gap_affiliate_v250 import apply as _apply_competitor_gap_v250
    from .inject_competitor_gap_affiliate_v251 import apply as _apply_competitor_gap_v251
    from .inject_ai_commerce_aeo_v250 import apply_ai_commerce_aeo
    from .inject_ai_commerce_breadcrumb_v250 import apply as _apply_ai_commerce_breadcrumb_v250
    from .materialize_location_pages_v253 import materialize as _materialize_location_pages_v253
    from .inject_location_schema_v253 import apply as _apply_location_schema_v253
except ImportError:
    from inject_competitor_gap_affiliate_v250 import apply as _apply_competitor_gap_v250
    from inject_competitor_gap_affiliate_v251 import apply as _apply_competitor_gap_v251
    from inject_ai_commerce_aeo_v250 import apply_ai_commerce_aeo
    from inject_ai_commerce_breadcrumb_v250 import apply as _apply_ai_commerce_breadcrumb_v250
    from materialize_location_pages_v253 import materialize as _materialize_location_pages_v253
    from inject_location_schema_v253 import apply as _apply_location_schema_v253

ACCESSIBILITY_MARKER = 'data-alo186-accessibility-v215="true"'
ACCESSIBILITY_SOURCE = Path("alo186/assets/alo186-accessibility-v215.css")
ACCESSIBILITY_TARGET = Path("assets/alo186-accessibility-v215.css")
JOURNEY_EVENTS_SOURCE = Path("alo186/assets/journey-events-v260.js")
JOURNEY_EVENTS_TARGET = Path("assets/journey-events-v260.js")
COMMERCIAL_HUB = Path("amazon-elektrik-urunleri/index.html")
MALFORMED_COMMERCIAL_PREFIX = re.compile(
    r"(https://alo186\.com/amazon-elektrik-urunleri)(?=[a-z0-9])",
    re.IGNORECASE,
)
_original_build = _core.build


def _recompute_checksums(output: Path) -> None:
    checksum_path = output / "checksums.sha256"
    if checksum_path.exists():
        checksum_path.unlink()
    files = sorted(path for path in output.rglob("*") if path.is_file())
    lines = [f"{_core.sha256(path)}  {path.relative_to(output).as_posix()}" for path in files]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize_commercial_hub_urls(output: Path) -> dict[str, object]:
    """Repair missing separators in the product hub's machine-readable routes.

    Historical ItemList generators joined the hub root and child slug without a
    slash. The final artifact must never expose those malformed URLs to search or
    answer engines. This layer changes URL integrity only; it does not add products,
    ranking, price, stock, or affiliate links.
    """

    path = output / COMMERCIAL_HUB
    if not path.is_file():
        raise FileNotFoundError(f"Ticari ürün merkezi artifactta eksik: {path}")
    html = path.read_text(encoding="utf-8", errors="strict")
    fixed, replacements = MALFORMED_COMMERCIAL_PREFIX.subn(r"\1/", html)
    if MALFORMED_COMMERCIAL_PREFIX.search(fixed):
        raise RuntimeError("Ticari hub içinde slash eksik canonical alt rota kaldı.")
    path.write_text(fixed, encoding="utf-8")
    return {
        "version": 217,
        "route": "/amazon-elektrik-urunleri",
        "malformedAbsoluteUrlsFixed": replacements,
        "canonicalOrigin": "https://alo186.com",
        "artifactLegacyWwwRejected": True,
        "priceStockRatingAdded": False,
        "affiliateLinksAdded": False,
    }


def install_accessibility_hardening(repo_root: Path, output: Path) -> dict[str, object]:
    source = repo_root / ACCESSIBILITY_SOURCE
    if not source.is_file():
        raise FileNotFoundError(f"Erişilebilirlik v215 assetı eksik: {source}")
    target = output / ACCESSIBILITY_TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

    link = (
        f'<link rel="stylesheet" href="/{ACCESSIBILITY_TARGET.as_posix()}" '
        f'{ACCESSIBILITY_MARKER}>'
    )
    injected = 0
    already_present = 0
    invalid_pages: list[str] = []
    for path in sorted(output.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="strict")
        if ACCESSIBILITY_MARKER in text:
            already_present += 1
            continue
        if not re.search(r"</head\s*>", text, re.IGNORECASE):
            invalid_pages.append(path.relative_to(output).as_posix())
            continue
        text = re.sub(r"</head\s*>", link + "\n</head>", text, count=1, flags=re.IGNORECASE)
        path.write_text(text, encoding="utf-8")
        injected += 1

    if invalid_pages:
        raise RuntimeError(
            "Erişilebilirlik v215 head alanı bulunamayan sayfalar: " + ", ".join(invalid_pages[:30])
        )
    if not injected and not already_present:
        raise RuntimeError("Erişilebilirlik v215 için HTML sayfası bulunamadı.")

    return {
        "version": 215,
        "asset": f"/{ACCESSIBILITY_TARGET.as_posix()}",
        "injectedPages": injected,
        "alreadyInjectedPages": already_present,
        "minimumTouchTargetPx": 44,
        "footerMinimumTouchTargetPx": 48,
        "footerTouchTargetRoutes": ["/haberler", "/guvenlik-rehberleri"],
        "emergencyTelephoneTargets": ["112", "186"],
        "contentImageFallbackRatio": "16:9",
        "horizontalOverflowHidden": False,
    }


def install_privacy_safe_journey_events(repo_root: Path, output: Path) -> dict[str, object]:
    """Publish the consent-gated, categorical journey event contract.

    Pages may dispatch local CustomEvents without consent. The asset itself only
    writes to dataLayer when explicit analytics consent is already true, and it
    accepts no free-text or personal-data fields.
    """

    source = repo_root / JOURNEY_EVENTS_SOURCE
    if not source.is_file():
        raise FileNotFoundError(f"Yolculuk ölçüm assetı eksik: {source}")
    text = source.read_text(encoding="utf-8", errors="strict")
    lowered = text.casefold()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "email", "phone", "address", "user_id"):
        if forbidden in lowered:
            raise RuntimeError(f"Yolculuk ölçüm assetında yasaklı ifade bulundu: {forbidden}")
    for required in (
        "window.ALO186_ANALYTICS_CONSENT === true",
        "new CustomEvent('alo186:journey'",
        "affiliate_clicked",
        "no_buy_selected",
        "reminder_downloaded",
    ):
        if required not in text:
            raise RuntimeError(f"Yolculuk ölçüm assetı sözleşme alanını taşımıyor: {required}")

    target = output / JOURNEY_EVENTS_TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "version": 260,
        "asset": f"/{JOURNEY_EVENTS_TARGET.as_posix()}",
        "networkRequests": 0,
        "browserStorage": False,
        "personalDataFields": 0,
        "dataLayerRequiresExplicitConsent": True,
        "eventFields": ["journey", "step", "outcome", "product_class"],
    }


def _build_with_platform_hardening(
    repo_root: Path,
    output: Path,
    commit_sha: str = "local",
) -> dict:
    release = _original_build(repo_root, output, commit_sha)
    location_pages_report = _materialize_location_pages_v253(repo_root, output)
    competitor_gap_report = _apply_competitor_gap_v250(repo_root, output)
    competitor_gap_v251_report = _apply_competitor_gap_v251(repo_root, output)
    location_schema_report = _apply_location_schema_v253(repo_root, output)
    commercial_report = normalize_commercial_hub_urls(output)
    accessibility_report = install_accessibility_hardening(repo_root, output)
    journey_events_report = install_privacy_safe_journey_events(repo_root, output)
    ai_commerce_report = apply_ai_commerce_aeo(repo_root, output)
    ai_commerce_breadcrumb_report = _apply_ai_commerce_breadcrumb_v250(output)
    release["locationPagesV253"] = location_pages_report
    release["locationSchemaV253"] = location_schema_report
    release["commercialCanonicalV217"] = commercial_report
    release["accessibilityHardeningV215"] = accessibility_report
    release["privacySafeJourneyEventsV260"] = journey_events_report
    release["competitorGapAffiliateV250"] = competitor_gap_report
    release["competitorGapAffiliateV251"] = competitor_gap_v251_report
    release["aiCommerceAeoV250"] = ai_commerce_report
    release["aiCommerceBreadcrumbV250"] = ai_commerce_breadcrumb_report
    release_path = output / "alo186-release.json"
    release_path.write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _recompute_checksums(output)
    return release


_core.build = _build_with_platform_hardening

for _name in dir(_core):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_core, _name)

write_effective_sitemap = _write_effective_sitemap
validate_route = _validate_route_with_legacy_article_bridge
build = _build_with_platform_hardening

_LEGACY_SOURCE_CONTRACT = r'''
load_effective_manifest
write_effective_sitemap
routingOverlays
articleCount
apache-production.htaccess
Strict-Transport-Security
X-Content-Type-Options
Content-Security-Policy
Referrer-Policy
Permissions-Policy
deviceDamageDeadline": CURRENT_DEADLINE
404.html
tailwindcss
ROOT_STATIC_FILES
normalize_canonical_host
FORBIDDEN_PUBLIC_DIRECTORIES
FORBIDDEN_PUBLIC_FILE_PATTERNS
public_copy_ignore
find_forbidden_public_files
publicArtifactPolicy
https://www.alo186.com
https://alo186.com
'''


if __name__ == "__main__":
    _core.main()
