from __future__ import annotations

try:
    from . import build_static_site_core as _core
    from .sitemap_hreflang import write_effective_sitemap as _write_effective_sitemap
except ImportError:
    import build_static_site_core as _core
    from sitemap_hreflang import write_effective_sitemap as _write_effective_sitemap

# Keep every existing import/function contract while replacing only sitemap output.
_core.write_effective_sitemap = _write_effective_sitemap

for _name in dir(_core):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_core, _name)

write_effective_sitemap = _write_effective_sitemap


if __name__ == "__main__":
    _core.main()
