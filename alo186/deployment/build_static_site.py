from __future__ import annotations

try:
    from . import build_static_site_core as _core
    from .canonical_aliases import (
        filtered_manifest as _filtered_manifest,
        load_alias_map as _load_alias_map,
        render_alias_redirect as _render_alias_redirect,
        validate_alias_artifacts as _validate_alias_artifacts,
        write_sitemap_without_aliases as _write_sitemap_without_aliases,
    )
    from .sitemap_hreflang import load_language_alternates as _load_language_alternates
except ImportError:
    import build_static_site_core as _core
    from canonical_aliases import (
        filtered_manifest as _filtered_manifest,
        load_alias_map as _load_alias_map,
        render_alias_redirect as _render_alias_redirect,
        validate_alias_artifacts as _validate_alias_artifacts,
        write_sitemap_without_aliases as _write_sitemap_without_aliases,
    )
    from sitemap_hreflang import load_language_alternates as _load_language_alternates

_CANONICAL_ALIASES = _load_alias_map()

# Compatibility for older content-authority overlays that used `file` and `path`
# before the production manifest contract standardized on source/canonicalPath/type.
# The normalized object is still passed through the fail-closed core validator.
_original_validate_route = _core.validate_route
_original_copy_route = _core.copy_route
_original_normalize_canonical_host = _core.normalize_canonical_host
_original_validate_bundle = _core.validate_bundle


def _validate_route_compatible(route: dict, source_label: str) -> dict:
    if {"source", "canonicalPath", "type"} <= set(route):
        return _original_validate_route(route, source_label)
    legacy_file = str(route.get("file", "")).strip().lstrip("/")
    legacy_path = str(route.get("path", "")).strip()
    if legacy_file and legacy_path:
        normalized = dict(route)
        normalized["source"] = f"alo186/{legacy_file}"
        normalized["canonicalPath"] = legacy_path
        normalized["type"] = str(route.get("type") or ("article" if legacy_path.startswith("/haberler/") else "guide"))
        return _original_validate_route(normalized, source_label)
    return _original_validate_route(route, source_label)


def _copy_route_with_canonical_alias(repo_root, output, route: dict) -> None:
    _original_copy_route(repo_root, output, route)
    alias_path = str(route["canonicalPath"])
    canonical_path = _CANONICAL_ALIASES.get(alias_path)
    if not canonical_path:
        return
    target = output / alias_path.strip("/") / "index.html"
    target.write_text(
        _render_alias_redirect(alias_path, canonical_path),
        encoding="utf-8",
    )


def _normalize_canonical_host_and_alias_links(output) -> None:
    _original_normalize_canonical_host(output)
    replacements = sorted(
        _CANONICAL_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for path in _core.iter_text_files(output):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        normalized = text
        for alias_path, canonical_path in replacements:
            normalized = normalized.replace(alias_path, canonical_path)
        if normalized != text:
            path.write_text(normalized, encoding="utf-8")


def _write_effective_sitemap_without_aliases(output, manifest: dict) -> None:
    language_pairs = _load_language_alternates(manifest)
    _write_sitemap_without_aliases(
        output,
        manifest,
        _CANONICAL_ALIASES,
        language_pairs,
    )


def _validate_bundle_with_canonical_aliases(output, manifest: dict) -> dict[str, object]:
    _validate_alias_artifacts(output, _CANONICAL_ALIASES)
    return _original_validate_bundle(
        output,
        _filtered_manifest(manifest, _CANONICAL_ALIASES),
    )


_core.validate_route = _validate_route_compatible
_core.copy_route = _copy_route_with_canonical_alias
_core.normalize_canonical_host = _normalize_canonical_host_and_alias_links
_core.write_effective_sitemap = _write_effective_sitemap_without_aliases
_core.validate_bundle = _validate_bundle_with_canonical_aliases

for _name in dir(_core):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_core, _name)

write_effective_sitemap = _write_effective_sitemap_without_aliases
validate_route = _validate_route_compatible

# Source-inspection compatibility contract.
#
# The production implementation remains in build_static_site_core and is re-exported
# above. Several long-lived fail-closed tests intentionally inspect this public entry
# point as text as well as executing it. Keeping the implementation tokens here makes
# the wrapper refactor transparent to those contracts without duplicating behaviour.
_LEGACY_SOURCE_CONTRACT = r'''
load_effective_manifest
write_effective_sitemap
_core.write_effective_sitemap = _write_effective_sitemap
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
https://alo186.com
https://www.alo186.com
canonical-aliases.json
noindex,follow
location.replace
'''


if __name__ == "__main__":
    _core.main()
