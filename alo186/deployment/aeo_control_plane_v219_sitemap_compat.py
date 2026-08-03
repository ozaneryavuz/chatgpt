from __future__ import annotations

"""AEO v219 compatibility wrapper with final sitemap apex normalization."""

from pathlib import Path

import aeo_control_plane_v219 as _base
import normalize_sitemap_apex_v236 as _sitemap

inject = _base.inject


def validate(
    site: Path,
    repo_root: Path,
    *,
    require_release_proof: bool = False,
) -> dict:
    _sitemap.normalize(site.resolve())
    return _base.validate(
        site.resolve(),
        repo_root.resolve(),
        require_release_proof=require_release_proof,
    )
