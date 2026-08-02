"""Canlı www→apex davranışı ile production builder sözleşmesinin ayrışmasını engeller."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import build_static_site  # noqa: E402
import smoke_live_routes  # noqa: E402
import smoke_static_site  # noqa: E402


# Kaynak manifest, üretilen artifact ve canlı yönlendirme aynı tek origin üzerinde kalmalıdır.
CANONICAL = "https://alo186.com"
LEGACY = "https://www.alo186.com"


def test_source_contract_uses_apex_and_redirects_www() -> None:
    manifest = json.loads((DEPLOYMENT / "routing-manifest.json").read_text(encoding="utf-8"))
    apache = (DEPLOYMENT / "apache-production.htaccess").read_text(encoding="utf-8")

    assert manifest["canonicalHost"] == CANONICAL
    assert build_static_site.CANONICAL_HOST == CANONICAL
    assert build_static_site.LEGACY_HOST == LEGACY
    assert smoke_static_site.CANONICAL_HOST == CANONICAL
    assert smoke_static_site.LEGACY_HOST == LEGACY
    assert smoke_live_routes.CANONICAL_HOST == CANONICAL
    assert smoke_live_routes.LEGACY_HOST == LEGACY
    assert "RewriteCond %{HTTP_HOST} !^alo186\\.com$ [NC]" in apache
    assert "RewriteRule ^ https://alo186.com%{REQUEST_URI} [R=301,L,NE]" in apache
    assert "RewriteRule ^ https://www.alo186.com%{REQUEST_URI}" not in apache
    assert 'Access-Control-Allow-Origin "https://alo186.com"' in apache


def test_no_test_hardcodes_legacy_www_for_sitemap() -> None:
    legacy_literals = (LEGACY, r"https:\/\/www\.alo186\.com")
    offenders: list[str] = []
    candidates = list((ROOT / "alo186").glob("**/test.js"))
    candidates.extend((ROOT / "alo186/tests").glob("test*.js"))
    candidates.extend((ROOT / "alo186/tests").glob("test*.py"))

    for candidate in sorted(set(candidates)):
        for line_number, line in enumerate(candidate.read_text(encoding="utf-8").splitlines(), start=1):
            if "sitemap" not in line.lower():
                continue
            if any(literal in line for literal in legacy_literals):
                offenders.append(f"{candidate.relative_to(ROOT)}:{line_number}")

    assert offenders == []


def test_full_production_bundle_contains_only_apex_canonicals(tmp_path: Path) -> None:
    output = tmp_path / "site"
    release = build_static_site.build(ROOT, output, "apex-contract-test")
    smoke = smoke_static_site.smoke(output, ROOT)

    assert release["canonicalHost"] == CANONICAL
    assert smoke["ok"] is True
    assert f"Sitemap: {CANONICAL}/sitemap.xml" in (output / "robots.txt").read_text(encoding="utf-8")
    assert LEGACY not in (output / "sitemap.xml").read_text(encoding="utf-8")

    leaked: list[str] = []
    for candidate in output.rglob("*"):
        if not candidate.is_file() or candidate.name == "checksums.sha256":
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY in text:
            leaked.append(candidate.relative_to(output).as_posix())
    assert leaked == []


def test_live_smoke_probes_www_then_accepts_apex(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_fetch(url: str, timeout: int = 20):
        calls.append(url)
        if url == LEGACY + "/":
            return 200, CANONICAL + "/", b"", {}, 0.01
        if url.endswith("/robots.txt"):
            body = f"Sitemap: {CANONICAL}/sitemap.xml".encode()
            return 200, url.replace(LEGACY, CANONICAL), body, {"content-type": "text/plain"}, 0.01
        if url.endswith("/sitemap.xml"):
            body = f"<loc>{CANONICAL}/</loc>".encode()
            return 200, url.replace(LEGACY, CANONICAL), body, {"content-type": "application/xml"}, 0.01
        if url.endswith("/tailwindcss"):
            return 200, url.replace(LEGACY, CANONICAL), b"", {"content-type": "text/css"}, 0.01
        if url.endswith("/404.html"):
            return 200, url.replace(LEGACY, CANONICAL), b"", {"content-type": "text/html"}, 0.01

        canonical = url.replace(LEGACY, CANONICAL)
        route_path = canonical.removeprefix(CANONICAL) or "/"
        route = next(item for item in smoke_live_routes.ROUTES if item[0] == route_path)
        html = (
            f"<html><head><title>{route[1]}</title>"
            f"<link rel=\"canonical\" href=\"{route[2]}\"></head>"
            "<body>Bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir. "
            "Cihaz hasarı başvurusu 30 gün içinde yapılır.</body></html>"
        ).encode()
        headers = {name: "present" for name in smoke_live_routes.REQUIRED_SECURITY_HEADERS}
        headers["content-type"] = "text/html"
        return 200, canonical, html, headers, 0.01

    monkeypatch.setattr(smoke_live_routes, "fetch", fake_fetch)
    result = smoke_live_routes.run(CANONICAL, check_assets=False)
    assert result["ok"] is True
    assert calls[0] == LEGACY + "/"
    assert result["results"][0]["path"] == "www-redirect"
