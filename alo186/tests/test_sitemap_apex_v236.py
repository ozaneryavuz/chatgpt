from __future__ import annotations

import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186" / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

import normalize_sitemap_apex_v236 as normalizer  # noqa: E402

NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def _write(site: Path, locations: list[str]) -> None:
    root = ET.Element(f"{{{NS}}}urlset")
    for location in locations:
        node = ET.SubElement(root, f"{{{NS}}}url")
        ET.SubElement(node, f"{{{NS}}}loc").text = location
        ET.SubElement(node, f"{{{NS}}}lastmod").text = "2026-08-03"
    ET.ElementTree(root).write(site / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def test_www_routes_are_normalized_and_deduplicated() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        _write(site, [
            "https://alo186.com/hesaplama/elektrik-planim/",
            "https://www.alo186.com/hesaplama/elektrik-planim/",
            "https://www.alo186.com/hesaplama/elektrik-kesintisi-kiti/",
        ])
        result = normalizer.normalize(site)
        assert result["normalizedWwwCount"] == 1
        assert result["duplicateCountRemoved"] == 1
        locations = [
            (node.text or "").strip()
            for node in ET.parse(site / "sitemap.xml").getroot().findall(".//{*}loc")
        ]
        assert locations == [
            "https://alo186.com/hesaplama/elektrik-planim/",
            "https://alo186.com/hesaplama/elektrik-kesintisi-kiti/",
        ]
        assert normalizer.normalize(site)["changed"] is False


def test_unknown_origin_is_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        _write(site, ["https://example.com/hesaplama/"])
        try:
            normalizer.normalize(site)
        except RuntimeError as exc:
            assert "origin izinli değil" in str(exc)
        else:
            raise AssertionError("Unknown sitemap origin must fail closed")


if __name__ == "__main__":
    test_www_routes_are_normalized_and_deduplicated()
    test_unknown_origin_is_rejected()
    print("ALO186 sitemap apex v236: PASS")
