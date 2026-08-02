from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
ROUTES = (
    "/hesaplama/elektrik-kesintisi-tazminat-kontrolu/",
    "/hesaplama/ges-kesinti-yedekleme-mimarisi/",
    "/hesaplama/ev-sarj-kacak-akim-koruma-secici/",
)
PAGES = tuple(ROOT / "alo186" / route.strip("/") / "index.html" for route in ROUTES)
OVERLAY = ROOT / "alo186/deployment/routing-overlays/214-intent-tools-run135.json"
INJECTOR = ROOT / "alo186/deployment/inject_intent_tools_run135.py"
GUARD = ROOT / "alo186/deployment/guard_commerce_routes_v3.py"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def source_contracts() -> None:
    texts = [read(path) for path in PAGES]
    for path, html in zip(PAGES, texts, strict=True):
        for token in (
            'name="description"',
            'rel="canonical"',
            '"@type":"WebApplication"',
            '"@type":"FAQPage"',
            '"@type":"BreadcrumbList"',
            'Doğrudan cevap',
            'Son kaynak doğrulama: 2 Ağustos 2026',
        ):
            assert token in html, (path, token)
        for forbidden in (
            '"@type":"Product"',
            '"@type":"Offer"',
            '"@type":"AggregateRating"',
            'amazon.com.tr',
            'alo186rehber-21',
            'priceCurrency',
            'availability',
        ):
            assert forbidden not in html, (path, forbidden)

    compensation, pv_backup, ev_rcd = texts
    for token in (
        '12 saati',
        '30 gün',
        'Hizmet Kalitesi Yönetmeliğinin 26 ncı maddesine göre',
        'aria-invalid',
        '/edas-bul',
        'input.value.trim()',
    ):
        assert token in compensation, token
    assert re.search(r"rawHours\s*===\s*''\s*\?\s*Number\.NaN", compensation), "blank hours fail-closed"
    assert re.search(r"hours\s*>\s*8760", compensation), "8760-hour upper bound"
    assert 'on iş günü' not in compensation.casefold()

    for token in (
        'anti-islanding',
        "pv==='unknown'",
        'Önce inverter modelini ve topolojiyi doğrulayın',
        'Hibrit etiketi yeterli değildir',
        'geri besleme yapmayın',
    ):
        assert token in pv_backup, token
    assert re.search(r"hours\s*<\s*0\.5\s*\|\|\s*hours\s*>\s*72", pv_backup), "0.5-72 hour range"

    for token in (
        'IEC 62752',
        'IEC 62955',
        'Mode 2: IC-CPD + üst tesisat Tip A adayı',
        'Mode 3: Tip A + doğrulanmış 6 mA DC RDC-DD adayı',
        "mode==='unknown'",
        "external==='none'",
        'yalnız standart Tip AC',
        'ayrı devre',
    ):
        assert token in ev_rcd, token

    overlay = json.loads(read(OVERLAY))
    assert overlay['version'] >= 214
    assert {item['canonicalPath'] for item in overlay['routes']} == set(ROUTES)
    assert all(item['type'] == 'tool' for item in overlay['routes'])
    assert overlay['trust']['productOfferSchema'] is False
    assert overlay['trust']['directAffiliateLinks'] is False

    injector = read(INJECTOR)
    for token in (
        'data-alo186-intent-tools-run135="true"',
        'TARGET = Path("hesaplama/index.html")',
        'pages-release.json',
        'intentToolsRun135',
        'directMarketplaceLinks',
        'recompute_checksums',
    ):
        assert token in injector, token
    for route in ROUTES:
        assert route in injector, route
    assert 'amazon.com' not in injector.casefold()

    guard = read(GUARD)
    assert 'import inject_intent_tools_run135 as intent_tools' in guard
    assert 'intent_tools.inject(resolved, base_path)' in guard
    assert 'result["intentToolsRun135"]' in guard


def artifact_contracts(site: Path, base_path: str) -> None:
    base_path = "" if not base_path or base_path == "/" else "/" + base_path.strip("/")
    for route in ROUTES:
        assert (site / route.strip("/") / "index.html").is_file(), route

    sitemap_root = ET.parse(site / "sitemap.xml").getroot()
    sitemap_paths = {
        urlsplit(loc.text or "").path.rstrip("/") + "/"
        for loc in sitemap_root.findall(".//{*}loc")
        if loc.text
    }
    for route in ROUTES:
        assert route.rstrip("/") + "/" in sitemap_paths, route

    search = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
    active = {item.get("canonicalPath", "").rstrip("/") + "/" for item in search["entries"]}
    for route in ROUTES:
        assert route.rstrip("/") + "/" in active, route

    hub = (site / "hesaplama/index.html").read_text(encoding="utf-8")
    assert hub.count('data-alo186-intent-tools-run135="true"') == 3
    for route in ROUTES:
        expected = f'{base_path}{route}' if base_path else route
        assert f'href="{expected}"' in hub, expected
    match = re.search(r"(\d+)\s+çekirdek araç", hub)
    assert match and int(match.group(1)) >= 52

    release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
    contract = release["intentToolsRun135"]
    assert contract["version"] >= 214
    assert contract["toolCount"] == 3
    assert contract["directMarketplaceLinks"] == 0
    assert contract["personalDataCollected"] is False
    assert contract["failClosed"] is True
    expected_routes = [f"{base_path}{route}" if base_path else route for route in ROUTES]
    assert [item.rstrip("/") + "/" for item in contract["routes"]] == [
        item.rstrip("/") + "/" for item in expected_routes
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    source_contracts()
    if args.site:
        artifact_contracts(args.site.resolve(), args.base_path)
    print("ALO186 intent tools run135 source and artifact contracts: PASS")


if __name__ == "__main__":
    main()
