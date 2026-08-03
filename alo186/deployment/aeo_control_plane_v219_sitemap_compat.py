from __future__ import annotations

"""AEO v219 compatibility wrapper with final sitemap apex normalization and v260 semantic SSR layer."""

from pathlib import Path

import aeo_control_plane_v219 as _base
import inject_competitor_gap_affiliate_v260 as _competitor_gap
import normalize_sitemap_apex_v236 as _sitemap


def inject(site: Path, base_path: str = "") -> dict:
    competitor = _competitor_gap.inject(site.resolve(), base_path)
    result = _base.inject(site.resolve(), base_path)
    result["competitorGapAffiliateV260"] = competitor
    return result


def validate(
    site: Path,
    repo_root: Path,
    *,
    require_release_proof: bool = False,
) -> dict:
    _sitemap.normalize(site.resolve())
    result = _base.validate(
        site.resolve(),
        repo_root.resolve(),
        require_release_proof=require_release_proof,
    )
    report = site.resolve() / _competitor_gap.REPORT_NAME
    if not report.is_file():
        raise RuntimeError("AEO v260 şema doğrulama raporu artifactta eksik")
    result["competitorGapAffiliateV260"] = _competitor_gap.validate_jsonld(site.resolve())
    return result
