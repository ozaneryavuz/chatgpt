from __future__ import annotations

import importlib.util
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "deployment/finalize_sitemap_uniqueness.py"
SPEC = importlib.util.spec_from_file_location("finalize_sitemap_uniqueness", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_site(root: Path, sitemap: str) -> Path:
    site = root / "site"
    site.mkdir()
    (site / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (site / "index.html").write_text("<!doctype html><title>ALO186</title>", encoding="utf-8")
    return site


def locs(site: Path) -> list[str]:
    root = ET.parse(site / "sitemap.xml").getroot()
    namespace = root.tag[1:].split("}", 1)[0] if root.tag.startswith("{") else ""
    ns = f"{{{namespace}}}" if namespace else ""
    return [node.text.strip() for node in root.findall(f"{ns}url/{ns}loc") if node.text]


def test_collapses_apex_and_www_preserving_first_node_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = write_site(
            Path(tmp),
            """<?xml version='1.0' encoding='utf-8'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.alo186.com/hesaplama/kesinti-hazirlik-envanteri/</loc><lastmod>2026-08-03</lastmod></url>
  <url><loc>https://alo186.com/hesaplama/kesinti-hazirlik-envanteri/</loc></url>
  <url><loc>https://alo186.com/hesaplama/elektrik-bakim-takvimi/</loc></url>
</urlset>
""",
        )
        report = MODULE.run(site)
        assert report["duplicateCountRemoved"] == 1
        assert locs(site) == [
            "https://alo186.com/hesaplama/kesinti-hazirlik-envanteri/",
            "https://alo186.com/hesaplama/elektrik-bakim-takvimi/",
        ]
        text = (site / "sitemap.xml").read_text(encoding="utf-8")
        assert "2026-08-03" in text
        first = (site / "sitemap.xml").read_bytes()
        MODULE.run(site)
        assert (site / "sitemap.xml").read_bytes() == first


def test_malformed_xml_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = write_site(Path(tmp), "<urlset><url><loc>https://alo186.com/</loc></urlset>")
        try:
            MODULE.run(site)
        except ET.ParseError:
            pass
        else:
            raise AssertionError("Bozuk sitemap fail-closed reddedilmeliydi")


if __name__ == "__main__":
    test_collapses_apex_and_www_preserving_first_node_metadata()
    test_malformed_xml_fails_closed()
    print("Final sitemap uniqueness tests passed.")
