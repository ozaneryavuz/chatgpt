#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

try:
    from .build_sites_source_package import PackageError, build as build_v254
except ImportError:
    from build_sites_source_package import PackageError, build as build_v254

VERSION = 255
ROOT_CANONICAL = "https://alo186.com/"
ROOT_FALLBACK_ROUTE = "/elektrik-portali"


def _root_reference_html(source: str) -> str:
    canonical_pattern = re.compile(
        r'(<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\'])[^>]*\bhref=["\'])([^"\']+)(["\'][^>]*>)',
        re.I,
    )
    if canonical_pattern.search(source):
        return canonical_pattern.sub(rf"\g<1>{ROOT_CANONICAL}\g<3>", source, count=1)
    if "</head>" not in source.casefold():
        raise PackageError("Elektrik portalı kök referansı için geçerli <head> kapanışı bulunamadı")
    return re.sub(
        r"</head>",
        f'<link rel="canonical" href="{ROOT_CANONICAL}"></head>',
        source,
        count=1,
        flags=re.I,
    )


def ensure_root_reference(bundle: Path) -> str:
    bundle = bundle.resolve()
    root = bundle / "index.html"
    if root.is_file():
        return "canonical-bundle-root"

    fallback = bundle / ROOT_FALLBACK_ROUTE.strip("/") / "index.html"
    if not fallback.is_file():
        raise PackageError(
            "ChatGPT Sites kök referansı üretilemedi: canonical bundle içinde "
            f"index.html veya {ROOT_FALLBACK_ROUTE}/index.html bulunamadı"
        )

    root.write_text(_root_reference_html(fallback.read_text(encoding="utf-8")), encoding="utf-8")
    return ROOT_FALLBACK_ROUTE


def build(repo: Path, bundle: Path, out: Path, source_commit: str) -> dict[str, Any]:
    root_source = ensure_root_reference(bundle)
    result = build_v254(repo=repo, bundle=bundle, out=out, source_commit=source_commit)
    result["sitesSyncVersion"] = VERSION
    result["rootRouteSource"] = root_source
    result["rootRouteCanonical"] = ROOT_CANONICAL

    result_path = out.resolve() / "package-result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 canonical bundle'dan ChatGPT Sites kaynak paketi üretir; kök rota referansını güvenle tamamlar."
    )
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            build(args.repo, args.bundle, args.out, args.source_commit),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
