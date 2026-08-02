from __future__ import annotations

import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import finalize_sitemap_v225 as sitemap_quality  # noqa: E402


PAGE = """<!doctype html><html lang="tr"><head>
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<title>Test</title></head><body><main><h1>Test</h1></main></body></html>"""


class SitemapQualityTests(unittest.TestCase):
    def write_page(self, root: Path, route: str, canonical: str, robots: str = "index,follow") -> None:
        target = root / route.strip("/") / "index.html" if route != "/" else root / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(PAGE.format(robots=robots, canonical=canonical), encoding="utf-8")

    def test_removes_alias_missing_duplicate_and_adds_home(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            self.write_page(site, "/", "https://alo186.com/")
            self.write_page(site, "/good/", "https://alo186.com/good/")
            self.write_page(site, "/alias/", "https://alo186.com/good/", "noindex,follow")
            (site / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://www.alo186.com/old.xml\n", encoding="utf-8")
            (site / "alo186-release.json").write_text(json.dumps({"commit": "abc"}), encoding="utf-8")
            (site / "pages-release.json").write_text(json.dumps({"basePath": ""}), encoding="utf-8")
            (site / "sitemap.xml").write_text(
                '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://www.alo186.com/good/</loc></url>'
                '<url><loc>https://alo186.com/good/</loc></url>'
                '<url><loc>https://alo186.com/alias/</loc></url>'
                '<url><loc>https://alo186.com/missing/</loc></url>'
                '</urlset>',
                encoding="utf-8",
            )
            report = sitemap_quality.run(site)
            tree = ET.parse(site / "sitemap.xml")
            ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = [item.text for item in tree.findall("s:url/s:loc", ns)]
            self.assertEqual(urls, ["https://alo186.com/", "https://alo186.com/good/"])
            self.assertEqual(report["removedNoindexCount"], 1)
            self.assertEqual(report["removedMissingCount"], 1)
            self.assertEqual(report["removedDuplicateCount"], 1)
            self.assertEqual(report["normalizedOriginCount"], 1)
            self.assertTrue(report["homepageAdded"])
            self.assertEqual((site / "robots.txt").read_text(encoding="utf-8"), sitemap_quality.ROBOTS_TEXT)
            for release_name in ("alo186-release.json", "pages-release.json"):
                payload = json.loads((site / release_name).read_text(encoding="utf-8"))
                self.assertEqual(payload["sitemapQualityV225"], report)

    def test_removes_indexable_url_with_different_canonical(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            self.write_page(site, "/", "https://alo186.com/")
            self.write_page(site, "/old/", "https://alo186.com/new/")
            (site / "robots.txt").write_text("", encoding="utf-8")
            (site / "sitemap.xml").write_text(
                '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://alo186.com/old/</loc></url></urlset>',
                encoding="utf-8",
            )
            report = sitemap_quality.run(site)
            self.assertEqual(report["removedNoncanonicalCount"], 1)
            self.assertIn("https://alo186.com/old/", report["removedNoncanonical"][0])


if __name__ == "__main__":
    unittest.main()
