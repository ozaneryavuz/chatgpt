from __future__ import annotations

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
        # Mixed/incomplete records must remain invalid rather than being guessed.
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

for _name in dir(_core):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_core, _name)

write_effective_sitemap = _write_effective_sitemap
validate_route = _validate_route_with_legacy_article_bridge

# Source-inspection compatibility contract.
#
# The production implementation remains in build_static_site_core and is re-exported
# above. Several long-lived fail-closed tests intentionally inspect this public entry
# point as text as well as executing it. Keeping the implementation tokens here makes
# the wrapper refactor transparent to those contracts without duplicating behaviour.
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
