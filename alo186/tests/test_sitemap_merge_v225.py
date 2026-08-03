from __future__ import annotations

import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import merge_sitemaps_v225 as sitemap_merge  # noqa: E402


class SitemapMergeV225Tests(unittest.TestCase):
    def write_sitemap(self, path: Path, urls: list[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        records = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
        path.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + records
            + "</urlset>",
            encoding="utf-8",
        )

    def urls(self, path: Path) -> list[str]:
        root = ET.parse(path).getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [str(node.text) for node in root.findall("s:url/s:loc", ns)]

    def test_merges_dedicated_urls_once_and_normalizes_www(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            sources = root / "source"
            self.write_sitemap(
                site / "sitemap.xml",
                ["https://alo186.com/", "https://alo186.com/shared/"],
            )
            self.write_sitemap(
                sources / "sitemap-electric-project-v200.xml",
                ["https://www.alo186.com/project/", "https://alo186.com/shared/"],
            )
            self.write_sitemap(
                sources / "sitemap-growth-v207.xml",
                ["https://alo186.com/growth-a/", "https://alo186.com/growth-b/"],
            )

            first = sitemap_merge.run(site, sources)
            self.assertEqual(first["importedUrlCount"], 3)
            self.assertEqual(first["afterUrlCount"], 5)
            self.assertTrue(first["unique"])
            urls = self.urls(site / "sitemap.xml")
            self.assertEqual(len(urls), len(set(urls)))
            self.assertIn("https://alo186.com/project/", urls)
            self.assertNotIn("https://www.alo186.com/project/", urls)

            second = sitemap_merge.run(site, sources)
            self.assertEqual(second["importedUrlCount"], 0)
            self.assertEqual(second["afterUrlCount"], 5)
            receipt = json.loads((site / "sitemap-merge-v225.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt, second)

    def test_rejects_external_or_non_https_url(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            sources = root / "source"
            self.write_sitemap(site / "sitemap.xml", ["https://alo186.com/"])
            self.write_sitemap(
                sources / "sitemap-electric-project-v200.xml",
                ["http://alo186.com/insecure/"],
            )
            self.write_sitemap(
                sources / "sitemap-growth-v207.xml",
                ["https://example.com/external/"],
            )
            with self.assertRaisesRegex(RuntimeError, "Canonical sitemap dışı URL"):
                sitemap_merge.run(site, sources)


if __name__ == "__main__":
    unittest.main()
