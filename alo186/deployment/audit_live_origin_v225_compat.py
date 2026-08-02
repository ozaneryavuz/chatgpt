from __future__ import annotations

import argparse
import json
from pathlib import Path

import audit_live_origin_v225 as core
import verify_live_origin as hosting

PAGES_ROUTES = tuple(core.CRITICAL_ROUTES)
SITES_ROUTES = tuple(hosting.CRITICAL_SITES_ROUTES)


def routes_for_mode(mode: str) -> tuple[str, ...]:
    if mode == hosting.SITES_MODE:
        return SITES_ROUTES
    return PAGES_ROUTES


def run(
    *,
    origin: str,
    expected_commit: str,
    timeout: float,
    workers: int,
    max_sitemap_urls: int,
    mobile_lighthouse: Path | None,
    desktop_lighthouse: Path | None,
) -> core.Report:
    mode, _live_commit = core.detect_hosting_mode(origin.rstrip("/"), timeout)
    routes = routes_for_mode(mode)
    original = core.CRITICAL_ROUTES
    core.CRITICAL_ROUTES = routes
    try:
        report = core.run(
            origin=origin,
            expected_commit=expected_commit,
            timeout=timeout,
            workers=workers,
            max_sitemap_urls=max_sitemap_urls,
            mobile_lighthouse=mobile_lighthouse,
            desktop_lighthouse=desktop_lighthouse,
        )
    finally:
        core.CRITICAL_ROUTES = original
    report.critical_route_count = len(routes)
    report.hosting_mode = mode
    report.ok = not any(issue.severity in {"P0", "P1"} for issue in report.issues)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 canlı-origin kalite denetimini GitHub Pages veya ChatGPT Sites rota yüzeyine göre çalıştırır."
    )
    parser.add_argument("--origin", default=core.DEFAULT_ORIGIN)
    parser.add_argument("--expected-commit", default="")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-sitemap-urls", type=int, default=800)
    parser.add_argument("--mobile-lighthouse", type=Path)
    parser.add_argument("--desktop-lighthouse", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--no-fail", action="store_true")
    args = parser.parse_args()
    report = run(
        origin=args.origin,
        expected_commit=args.expected_commit,
        timeout=args.timeout,
        workers=args.workers,
        max_sitemap_urls=args.max_sitemap_urls,
        mobile_lighthouse=args.mobile_lighthouse,
        desktop_lighthouse=args.desktop_lighthouse,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(core.render_markdown(report), encoding="utf-8")
    print(json.dumps(report.to_json(), ensure_ascii=False, indent=2))
    if not report.ok and not args.no_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
