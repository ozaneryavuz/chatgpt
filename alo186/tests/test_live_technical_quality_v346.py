from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = "https://alo186.com"
SITEMAP = f"{CANONICAL}/sitemap.xml"
LEGACY_HANDOVER = "/hizmetler/teknik-devir-kabul-paketi"
HANDOVER_TARGET = "/kurumsal-elektrik-surekliligi-on-degerlendirme"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def sitemap_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip().lower().startswith("sitemap:")]


source_robots = (ROOT / "alo186/robots.txt").read_text(encoding="utf-8")
assert sitemap_lines(source_robots) == [f"Sitemap: {SITEMAP}"], sitemap_lines(source_robots)

source_htaccess = (ROOT / "alo186/deployment/apache-production.htaccess").read_text(encoding="utf-8")
redirect_rule = (
    "RewriteRule ^hizmetler/teknik-devir-kabul-paketi/?$ "
    f"{CANONICAL}{HANDOVER_TARGET} [R=301,L,NE]"
)
assert redirect_rule in source_htaccess
assert source_htaccess.index(redirect_rule) < source_htaccess.index("RewriteCond %{HTTP_HOST}")

with tempfile.TemporaryDirectory(prefix="alo186-live-quality-v346-") as folder:
    artifact = Path(folder) / "artifact"
    run([
        sys.executable,
        "alo186/deployment/build_static_site.py",
        "--output",
        str(artifact),
        "--commit",
        "live-quality-v346-test",
    ])

    robots = (artifact / "robots.txt").read_text(encoding="utf-8")
    assert sitemap_lines(robots) == [f"Sitemap: {SITEMAP}"], sitemap_lines(robots)
    for stale_name in (
        "sitemap-electric-project-v200.xml",
        "sitemap-growth-v207.xml",
        "sitemap-growth-v311.xml",
        "sitemap-growth-v312.xml",
        "sitemap-growth-v313.xml",
        "sitemap-growth-v333.xml",
    ):
        assert stale_name not in robots

    sitemap_path = artifact / "sitemap.xml"
    assert sitemap_path.is_file()
    tree = ET.parse(sitemap_path)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [node.text.strip() for node in tree.findall(".//sm:loc", ns) if node.text]
    assert locs
    assert len(locs) == len(set(locs)), "Sitemap yinelenen canonical URL taşıyor"
    assert all(url.startswith(CANONICAL + "/") for url in locs)
    assert not any("www.alo186.com" in url for url in locs)
    assert CANONICAL + HANDOVER_TARGET in locs
    assert CANONICAL + LEGACY_HANDOVER not in locs

    target = artifact / HANDOVER_TARGET.strip("/") / "index.html"
    assert target.is_file(), target
    html = target.read_text(encoding="utf-8")
    canonical = re.findall(r'<link\b[^>]*rel=["\'][^"\']*canonical[^"\']*["\'][^>]*href=["\']([^"\']+)', html, re.I)
    if not canonical:
        canonical = re.findall(r'<link\b[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\'][^"\']*canonical', html, re.I)
    assert canonical == [CANONICAL + HANDOVER_TARGET], canonical

    lowered = html.casefold()
    assert "kamu kurumu değildir" in lowered or "resmî kurum" in lowered
    assert "kişisel veri" in lowered
    for forbidden in (
        'type="email"',
        "type='email'",
        'type="tel"',
        "type='tel'",
        'name="email"',
        'name="phone"',
        'name="address"',
        'name="tc"',
        'name="tckn"',
    ):
        assert forbidden not in lowered, forbidden

    artifact_htaccess = (artifact / ".htaccess").read_text(encoding="utf-8")
    assert redirect_rule in artifact_htaccess

print({
    "ok": True,
    "canonicalSitemapDirectives": 1,
    "uniqueSitemapUrls": True,
    "legacyHandoverRedirect": 301,
    "redirectTarget": CANONICAL + HANDOVER_TARGET,
    "legacyRouteInSitemap": False,
    "personalDataFieldsAdded": 0,
})
