from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
ROUTES = (
    "/hesaplama/elektrik-kesintisi-tazminat-kontrolu/",
    "/hesaplama/ges-kesinti-yedekleme-mimarisi/",
    "/hesaplama/ev-sarj-kacak-akim-koruma-secici/",
)


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def source_contracts() -> None:
    run21 = (DEPLOYMENT / "inject_growth_run21.py").read_text(encoding="utf-8")
    boiler = (DEPLOYMENT / "inject_boiler_continuity_growth.py").read_text(encoding="utf-8")
    intent = (DEPLOYMENT / "inject_intent_tools_run135.py").read_text(encoding="utf-8")
    guard = (DEPLOYMENT / "guard_commerce_routes_v3.py").read_text(encoding="utf-8")
    overlay = json.loads((DEPLOYMENT / "routing-overlays/216-intent-tools-run135.json").read_text(encoding="utf-8"))

    for text, name in ((run21, "growth_run21"), (boiler, "boiler_continuity")):
        assert 'entry = f"<url><loc>{CANONICAL}</loc></url>"' in text, name
        assert 'f"<url><loc>{CANONICAL}</loc></urlset>"' not in text, name
        assert "ET.fromstring(updated)" in text, name
        assert 'CANONICAL = "https://alo186.com" + ROUTE' in text, name
    assert 'ET.parse(site / "sitemap.xml")' in run21

    outage = (ROOT / "alo186/hesaplama/elektrik-kesintisi-tazminat-kontrolu/index.html").read_text(encoding="utf-8")
    for token in (
        "const rawHours=input.value.trim()",
        "rawHours===''?Number.NaN:Number(rawHours)",
        "rawHours===''||!Number.isFinite(hours)||hours<0||hours>8760",
        "30 gün",
    ):
        assert token in outage, token
    assert "on iş günü" not in outage.casefold()

    for token in (
        "import inject_private_search as private_search",
        "private_search.run(site, base_path)",
        'data-alo186-intent-tools-run135="true"',
        "searchIndexGenerated",
        "sitemapWellFormed",
        "harden_outage_input",
    ):
        assert token in intent, token
    assert "import inject_intent_tools_run135 as intent_tools" in guard
    assert "intent_tools.inject(resolved, base_path)" in guard
    assert 'result["intentToolsRun135"]' in guard

    assert overlay["version"] == 216
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)
    assert overlay["trust"]["emptyInputFailClosed"] is True
    assert overlay["trust"]["searchIndexRequired"] is True
    assert overlay["trust"]["sitemapWellFormedRequired"] is True


def chained_sitemap_contract() -> None:
    sys.path.insert(0, str(DEPLOYMENT))
    run21 = load("p0_growth_run21", DEPLOYMENT / "inject_growth_run21.py")
    boiler = load("p0_boiler_continuity", DEPLOYMENT / "inject_boiler_continuity_growth.py")
    with tempfile.TemporaryDirectory(prefix="alo186-p0-sitemap-") as folder:
        site = Path(folder)
        sitemap = site / "sitemap.xml"
        sitemap.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <url><loc>https://alo186.com/</loc></url>\n'
            '</urlset>\n',
            encoding="utf-8",
        )
        for _ in range(2):
            run21.append_sitemap(site)
            boiler.append_sitemap(site)
            ET.parse(sitemap)
        text = sitemap.read_text(encoding="utf-8")
        assert text.count(run21.CANONICAL) == 1
        assert text.count(boiler.CANONICAL) == 1
        assert "https://www.alo186.com" not in text


def artifact_contracts(site: Path, base_path: str) -> None:
    sys.path.insert(0, str(DEPLOYMENT))
    intent = load("p0_intent_tools", DEPLOYMENT / "inject_intent_tools_run135.py")
    result = intent.validate(site.resolve(), base_path)
    assert result["ok"] is True
    assert result["sitemapWellFormed"] is True
    assert set(result["routes"]) == set(ROUTES)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    source_contracts()
    chained_sitemap_contract()
    if args.site:
        artifact_contracts(args.site, args.base_path)
    print(json.dumps({
        "ok": True,
        "version": 216,
        "sitemapWriters": 2,
        "intentRoutes": list(ROUTES),
        "emptyInputFailClosed": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
