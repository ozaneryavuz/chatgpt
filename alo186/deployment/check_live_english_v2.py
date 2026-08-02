from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import check_live_english as contract

DEFAULT_ORIGIN = contract.DEFAULT_ORIGIN
DEFAULT_REPOSITORY = contract.DEFAULT_REPOSITORY


@dataclass
class RouteProbe:
    route: str
    ok: bool
    status: int
    canonical: str = ""
    html_lang: str = ""
    checks: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class SmokeReport:
    ok: bool
    checked_at: str
    origin: str
    expected_commit: str
    hosting_mode: str = "unknown"
    release_marker_available: bool = False
    live_commit: str = ""
    live_commit_relation: str = "unknown"
    attempts: int = 0
    route_count: int = 0
    expected_route_count: int = len(contract.LANGUAGE_PAIRS)
    sitemap_ok: bool = False
    sitemap_url_count: int = 0
    routes: list[RouteProbe] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


class SnapshotValidationError(RuntimeError):
    def __init__(self, report: SmokeReport):
        self.report = report
        super().__init__("; ".join(report.errors) or "Canlı İngilizce yayın doğrulanamadı")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def cache_busted(url: str, expected_commit: str, attempt: int) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}" + urllib.parse.urlencode(
        {
            "alo186_english_v2": expected_commit[:12] or "manual",
            "attempt": attempt,
            "ts": int(time.time()),
        }
    )


def fetch_text(url: str, timeout: float) -> tuple[int, str, dict[str, str]]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ALO186-English-Live-Smoke/2.0 (+https://alo186.com/en/)",
            "Accept": "text/html,application/json,application/xml,text/xml;q=0.9,*/*;q=0.5",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return int(response.status), raw.decode(charset, errors="replace"), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return int(exc.code), body, dict(exc.headers.items())


def detect_hosting_mode(
    *,
    release_status: int,
    release_text: str,
    release_headers: dict[str, str],
) -> str:
    if release_status == 200:
        try:
            contract.parse_release_marker(release_text)
        except (json.JSONDecodeError, contract.LiveValidationError):
            return "invalid-release-marker"
        return "github-pages"

    header_text = " ".join(f"{key}:{value}" for key, value in release_headers.items()).casefold()
    body = release_text.casefold()
    if (
        "cloudflare" in header_text
        or "static-snapshot" in body
        or "vinext" in body
        or "chatgpt" in body
    ):
        return "chatgpt-sites"
    return "external-host"


def evaluate_snapshot(
    *,
    origin: str,
    repository: str,
    expected_commit: str,
    github_token: str,
    attempt: int,
    release_response: tuple[int, str, dict[str, str]],
    route_responses: dict[str, tuple[int, str, dict[str, str]]],
    sitemap_response: tuple[int, str, dict[str, str]],
) -> SmokeReport:
    origin = origin.rstrip("/")
    release_status, release_text, release_headers = release_response
    hosting_mode = detect_hosting_mode(
        release_status=release_status,
        release_text=release_text,
        release_headers=release_headers,
    )
    report = SmokeReport(
        ok=False,
        checked_at=now_iso(),
        origin=origin,
        expected_commit=expected_commit,
        hosting_mode=hosting_mode,
        attempts=attempt,
    )

    commit_contract_ok = True
    if release_status == 200:
        try:
            live_commit = contract.parse_release_marker(release_text)
        except (json.JSONDecodeError, contract.LiveValidationError) as exc:
            report.errors.append(f"pages-release.json geçersiz: {exc}")
            commit_contract_ok = False
        else:
            report.release_marker_available = True
            report.live_commit = live_commit
            relation = contract.compare_commits(repository, expected_commit, live_commit, github_token)
            report.live_commit_relation = relation
            if relation not in {"identical", "ahead"}:
                report.errors.append(
                    "Canlı commit beklenen yayını içermiyor: "
                    f"expected={expected_commit}, live={live_commit or 'boş'}, relation={relation}"
                )
                commit_contract_ok = False
    else:
        report.live_commit_relation = "unavailable-external-host"
        report.warnings.append(
            f"pages-release.json HTTP {release_status}; exact-commit kanıtı yok, içerik sözleşmesi ayrı doğrulanıyor"
        )

    for route in contract.LANGUAGE_PAIRS:
        status, html, _headers = route_responses.get(route, (0, "", {}))
        try:
            result = contract.validate_english_page(route, html, origin, status=status)
        except (contract.LiveValidationError, json.JSONDecodeError) as exc:
            probe = RouteProbe(route=route, ok=False, status=status, error=str(exc))
            report.errors.append(str(exc))
        else:
            probe = RouteProbe(
                route=route,
                ok=True,
                status=status,
                canonical=result.canonical,
                html_lang=result.html_lang,
                checks=list(result.checks),
            )
            report.route_count += 1
        report.routes.append(probe)

    sitemap_status, sitemap_text, _sitemap_headers = sitemap_response
    if sitemap_status != 200:
        report.errors.append(f"sitemap.xml HTTP {sitemap_status}")
    else:
        try:
            urls = contract.validate_sitemap(sitemap_text, origin)
        except contract.LiveValidationError as exc:
            report.errors.append(str(exc))
        else:
            report.sitemap_ok = True
            report.sitemap_url_count = len(urls)

    content_contract_ok = (
        report.route_count == report.expected_route_count and report.sitemap_ok
    )
    report.ok = commit_contract_ok and content_contract_ok
    report.checked_at = now_iso()
    return report


def collect_snapshot(
    *,
    origin: str,
    expected_commit: str,
    attempt: int,
    timeout: float,
) -> tuple[
    tuple[int, str, dict[str, str]],
    dict[str, tuple[int, str, dict[str, str]]],
    tuple[int, str, dict[str, str]],
]:
    origin = origin.rstrip("/")
    release = fetch_text(
        cache_busted(f"{origin}/pages-release.json", expected_commit, attempt),
        timeout,
    )
    routes = {
        route: fetch_text(
            cache_busted(origin + route, expected_commit, attempt),
            timeout,
        )
        for route in contract.LANGUAGE_PAIRS
    }
    sitemap = fetch_text(
        cache_busted(f"{origin}/sitemap.xml", expected_commit, attempt),
        timeout,
    )
    return release, routes, sitemap


def write_report(path: Path, report: SmokeReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_json(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_live_smoke(
    *,
    origin: str,
    repository: str,
    expected_commit: str,
    github_token: str,
    attempts: int,
    interval: float,
    timeout: float,
    report_path: Path,
) -> SmokeReport:
    latest: SmokeReport | None = None
    for attempt in range(1, attempts + 1):
        try:
            release, routes, sitemap = collect_snapshot(
                origin=origin,
                expected_commit=expected_commit,
                attempt=attempt,
                timeout=timeout,
            )
            latest = evaluate_snapshot(
                origin=origin,
                repository=repository,
                expected_commit=expected_commit,
                github_token=github_token,
                attempt=attempt,
                release_response=release,
                route_responses=routes,
                sitemap_response=sitemap,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            latest = SmokeReport(
                ok=False,
                checked_at=now_iso(),
                origin=origin.rstrip("/"),
                expected_commit=expected_commit,
                attempts=attempt,
                errors=[f"Canlı HTTP toplama hatası: {exc}"],
            )

        write_report(report_path, latest)
        if latest.ok:
            return latest
        if attempt < attempts:
            time.sleep(interval)

    assert latest is not None
    raise SnapshotValidationError(latest)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ALO186 İngilizce canlı yayını hosting modundan bağımsız ve tüm rotaları kapsayarak doğrular."
    )
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--expected-commit", default=os.getenv("GITHUB_SHA", "").strip())
    parser.add_argument("--github-token", default=os.getenv("GITHUB_TOKEN", ""))
    parser.add_argument("--attempts", type=int, default=36)
    parser.add_argument("--interval", type=float, default=15.0)
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("/tmp/alo186-live-english-report.json"),
    )
    args = parser.parse_args()

    if not args.expected_commit:
        parser.error("--expected-commit veya GITHUB_SHA zorunludur")
    if args.attempts < 1:
        parser.error("--attempts en az 1 olmalıdır")
    if args.interval < 0:
        parser.error("--interval negatif olamaz")

    try:
        report = run_live_smoke(
            origin=args.origin,
            repository=args.repository,
            expected_commit=args.expected_commit,
            github_token=args.github_token,
            attempts=args.attempts,
            interval=args.interval,
            timeout=args.timeout,
            report_path=args.report,
        )
    except SnapshotValidationError as exc:
        print(json.dumps(exc.report.to_json(), ensure_ascii=False))
        raise SystemExit(1) from exc

    print(json.dumps(report.to_json(), ensure_ascii=False))


if __name__ == "__main__":
    main()
