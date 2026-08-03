from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .competitor_gap_affiliate_v250 import (
        apply_competitor_gap_affiliate_v250 as _apply_competitor_gap_affiliate_v250,
    )
    from .materialize_location_pages_v251 import materialize as _materialize_location_pages
except ImportError:
    from competitor_gap_affiliate_v250 import (
        apply_competitor_gap_affiliate_v250 as _apply_competitor_gap_affiliate_v250,
    )
    from materialize_location_pages_v251 import materialize as _materialize_location_pages

VERSION = 251
AI_AGENTS = (
    "OAI-SearchBot",
    "GPTBot",
    "ChatGPT-User",
    "PerplexityBot",
    "ClaudeBot",
    "anthropic-ai",
    "Bytespider",
    "Google-Extended",
)


def robots(site: Path) -> dict[str, object]:
    """Write an explicit, auditable crawler policy while preserving sitemap rows."""

    path = Path(site) / "robots.txt"
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    sitemaps: list[str] = []
    for line in old.splitlines():
        normalized = line.strip()
        if normalized.lower().startswith("sitemap:") and normalized not in sitemaps:
            sitemaps.append(normalized)
    if not sitemaps:
        sitemaps = ["Sitemap: https://alo186.com/sitemap.xml"]

    rows: list[str] = []
    for agent in AI_AGENTS:
        rows.extend((f"User-agent: {agent}", "Allow: /", ""))
    rows.extend(("User-agent: *", "Allow: /", ""))
    rows.extend(sitemaps)
    path.write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")
    return {
        "explicitAllow": list(AI_AGENTS),
        "sitemaps": sitemaps,
        "trainingAndSearchPoliciesKeptSeparate": True,
    }


def apply(repo: Path, site: Path, base_path: str = "") -> dict[str, object]:
    """Materialize location routes, then apply final-artifact schema and SSR hardening."""

    del base_path
    repo, site = Path(repo), Path(site)
    materialization = _materialize_location_pages(repo, site)
    report = _apply_competitor_gap_affiliate_v250(site)
    report["adapterVersion"] = VERSION
    report["locationPageMaterializationV251"] = materialization
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    print(
        json.dumps(
            apply(args.repo.resolve(), args.site.resolve(), args.base_path),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
