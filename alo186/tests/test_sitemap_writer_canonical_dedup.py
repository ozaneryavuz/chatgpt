from __future__ import annotations

import importlib
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

WRITER_MODULES = [
    importlib.import_module("inject_growth_run9"),
    importlib.import_module("inject_growth_run11"),
    importlib.import_module("inject_growth_run12"),
    importlib.import_module("inject_growth_run15"),
]
CANONICAL_ORIGIN = "https://alo186.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
AFFECTED_ROUTES = tuple(
    dict.fromkeys(route for module in WRITER_MODULES for route in module.ROUTES.values())
)

assert len(AFFECTED_ROUTES) == 12
assert {
    "/hesaplama/cihaz-hasari-basvuru-takibi/",
    "/hesaplama/ev-elektrik-guvenligi-kontrolu/",
    "/hesaplama/karbonmonoksit-alarmi-jenerator-guvenligi/",
    "/hesaplama/elektrik-kesintisi-dayaniklilik-plani/",
    "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
    "/hesaplama/ges-aylik-uretim-saglik-gunlugu/",
    "/hesaplama/power-station-gunes-paneli-uygunluk/",
    "/hesaplama/duman-co-alarmi-bakim-gunlugu/",
    "/hesaplama/jenerator-ats-test-gunlugu/",
    "/hesaplama/ev-sarj-kablosu-saglik-gunlugu/",
}.issubset(AFFECTED_ROUTES)


def seed_sitemap(path: Path) -> None:
    ET.register_namespace("", SITEMAP_NS)
    root = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    home = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
    ET.SubElement(home, f"{{{SITEMAP_NS}}}loc").text = f"{CANONICAL_ORIGIN}/"

    for index, route in enumerate(AFFECTED_ROUTES):
        canonical = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(canonical, f"{{{SITEMAP_NS}}}loc").text = f"{CANONICAL_ORIGIN}{route}"
        ET.SubElement(canonical, f"{{{SITEMAP_NS}}}lastmod").text = f"2026-08-{index + 1:02d}"

        legacy = ET.SubElement(root, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(legacy, f"{{{SITEMAP_NS}}}loc").text = f"https://www.alo186.com{route}"
        ET.SubElement(legacy, f"{{{SITEMAP_NS}}}priority").text = "0.1"

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def sitemap_rows(path: Path) -> list[tuple[str, str | None, str | None]]:
    root = ET.parse(path).getroot()
    ns = {"sm": SITEMAP_NS}
    rows = []
    for node in root.findall("sm:url", ns):
        loc = node.findtext("sm:loc", namespaces=ns)
        rows.append(
            (
                loc or "",
                node.findtext("sm:lastmod", namespaces=ns),
                node.findtext("sm:priority", namespaces=ns),
            )
        )
    return rows


for artifact_name in ("custom-domain", "project-path"):
    with tempfile.TemporaryDirectory(prefix=f"alo186-{artifact_name}-") as temporary:
        site = Path(temporary)
        sitemap = site / "sitemap.xml"
        seed_sitemap(sitemap)

        for writer in WRITER_MODULES:
            writer.append_sitemap(site)

        first_bytes = sitemap.read_bytes()
        ET.parse(sitemap)
        rows = sitemap_rows(sitemap)
        locations = [row[0] for row in rows]

        assert not any("https://www.alo186.com" in location for location in locations)
        assert not any("/chatgpt/" in location for location in locations)
        for index, route in enumerate(AFFECTED_ROUTES):
            canonical = f"{CANONICAL_ORIGIN}{route}"
            assert locations.count(canonical) == 1, (artifact_name, canonical)
            row = next(item for item in rows if item[0] == canonical)
            assert row[1] == f"2026-08-{index + 1:02d}"
            assert row[2] is None

        for writer in WRITER_MODULES:
            writer.append_sitemap(site)

        assert sitemap.read_bytes() == first_bytes
        ET.parse(sitemap)

with tempfile.TemporaryDirectory(prefix="alo186-invalid-sitemap-") as temporary:
    path = Path(temporary) / "sitemap.xml"
    path.write_text("<urlset><url>", encoding="utf-8")
    try:
        WRITER_MODULES[0].append_sitemap(path.parent)
    except ET.ParseError:
        pass
    else:
        raise AssertionError("Bozuk sitemap fail-closed reddedilmedi")

print(
    {
        "ok": True,
        "writers": [module.__name__ for module in WRITER_MODULES],
        "canonicalOrigin": CANONICAL_ORIGIN,
        "routeCount": len(AFFECTED_ROUTES),
        "customDomain": True,
        "projectPath": True,
        "idempotent": True,
        "malformedXmlFailsClosed": True,
    }
)
