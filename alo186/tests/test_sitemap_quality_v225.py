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
import smoke_static_site as static_smoke  # noqa: E402


PAGE = """<!doctype html><html lang="tr"><head>
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<title>Test</title></head><body><main><h1>Test</h1>{body}</main></body></html>"""


class SitemapQualityTests(unittest.TestCase):
    def write_page(
        self,
        root: Path,
        route: str,
        canonical: str,
        robots: str = "index,follow",
        body: str = "",
    ) -> None:
        target = root / route.strip("/") / "index.html" if route != "/" else root / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            PAGE.format(robots=robots, canonical=canonical, body=body),
            encoding="utf-8",
        )

    def test_smoke_preserves_manifest_terminal_slash(self):
        self.assertEqual(static_smoke.normalize_route_path("/hesaplama/"), "/hesaplama/")
        self.assertEqual(static_smoke.normalize_route_path("/hesaplama"), "/hesaplama")
        self.assertEqual(
            static_smoke.expected_canonical_for_route("/hesaplama/", {}),
            "https://alo186.com/hesaplama/",
        )

    def test_smoke_accepts_only_declared_alias_canonicals(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            deployment = repo / "alo186/deployment"
            deployment.mkdir(parents=True)
            (deployment / "content-consolidations.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "consolidations": [
                            {
                                "intentKey": "declared-alias",
                                "aliasPath": "/haberler/eski-rehber",
                                "canonicalPath": "/haberler/guncel-rehber",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            aliases = static_smoke.load_declared_alias_canonicals(repo)
            self.assertEqual(
                aliases,
                {"/haberler/eski-rehber": "https://alo186.com/haberler/guncel-rehber"},
            )
            self.assertEqual(
                static_smoke.expected_canonical_for_route("/haberler/eski-rehber", aliases),
                "https://alo186.com/haberler/guncel-rehber",
            )
            self.assertEqual(
                static_smoke.expected_canonical_for_route("/haberler/baska-rehber", aliases),
                "https://alo186.com/haberler/baska-rehber",
            )

    def test_smoke_rejects_duplicate_alias_declarations(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            deployment = repo / "alo186/deployment"
            deployment.mkdir(parents=True)
            item = {
                "intentKey": "declared-alias",
                "aliasPath": "/haberler/eski-rehber",
                "canonicalPath": "/haberler/guncel-rehber",
            }
            (deployment / "content-consolidations.json").write_text(
                json.dumps({"version": 1, "consolidations": [item, item]}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "Yinelenen alias"):
                static_smoke.load_declared_alias_canonicals(repo)

    def test_removes_alias_missing_duplicate_and_adds_home(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            self.write_page(site, "/", "https://alo186.com/")
            self.write_page(site, "/good/", "https://alo186.com/good/")
            self.write_page(site, "/alias/", "https://alo186.com/good/", "noindex,follow")
            (site / "robots.txt").write_text(
                "User-agent: *\nAllow: /\nSitemap: https://www.alo186.com/old.xml\n",
                encoding="utf-8",
            )
            (site / "alo186-release.json").write_text(
                json.dumps({"commit": "abc"}), encoding="utf-8"
            )
            (site / "pages-release.json").write_text(
                json.dumps({"basePath": ""}), encoding="utf-8"
            )
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
            self.assertEqual(report["aliasLinkRewriteCount"], 0)
            self.assertEqual(report["remainingAliasHrefCount"], 0)
            self.assertTrue(report["homepageAdded"])
            self.assertEqual(
                (site / "robots.txt").read_text(encoding="utf-8"),
                sitemap_quality.ROBOTS_TEXT,
            )
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

    def test_rewrites_internal_alias_hrefs_to_canonical_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            voltage_alias = "/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi/"
            voltage_target = "/haberler/priz-gerilimi-neden-220-volttan-farkli-olabilir/"
            battery_alias = "/haberler/lifepo4-batarya-sogukta-sarj-edilir-mi/"
            battery_target = "/haberler/lifepo4-bataryalar-kisin-sarj-edilir-mi/"

            self.write_page(
                site,
                "/",
                "https://alo186.com/",
                body=(
                    f'<a href="{battery_alias}?src=home#cold">Batarya</a>'
                    f'<a href="https://www.alo186.com{voltage_alias}">Gerilim</a>'
                ),
            )
            self.write_page(
                site,
                voltage_target,
                "https://alo186.com" + voltage_target,
            )
            self.write_page(
                site,
                battery_target,
                "https://alo186.com" + battery_target,
            )
            for alias, target in (
                (voltage_alias, voltage_target),
                (battery_alias, battery_target),
            ):
                alias_file = site / alias.strip("/") / "index.html"
                alias_file.parent.mkdir(parents=True, exist_ok=True)
                alias_file.write_text(
                    PAGE.format(
                        robots="noindex,follow",
                        canonical="https://alo186.com" + target,
                        body=sitemap_quality.ALIAS_MARKER,
                    ),
                    encoding="utf-8",
                )

            urls = ["/", voltage_target, battery_target, voltage_alias, battery_alias]
            records = "".join(
                f"<url><loc>https://alo186.com{route}</loc></url>" for route in urls
            )
            (site / "sitemap.xml").write_text(
                '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + records
                + "</urlset>",
                encoding="utf-8",
            )

            report = sitemap_quality.run(site)
            homepage = (site / "index.html").read_text(encoding="utf-8")
            self.assertNotIn(voltage_alias, homepage)
            self.assertNotIn(battery_alias, homepage)
            self.assertIn(battery_target + "?src=home#cold", homepage)
            self.assertIn("https://alo186.com" + voltage_target, homepage)
            self.assertEqual(report["aliasLinkRewriteCount"], 2)
            self.assertEqual(report["aliasLinkTouchedPageCount"], 1)
            self.assertEqual(report["remainingAliasHrefCount"], 0)
            self.assertEqual(report["removedAliasCount"], 2)

            second = sitemap_quality.run(site)
            self.assertEqual(second["aliasLinkRewriteCount"], 0)
            self.assertEqual(second["remainingAliasHrefCount"], 0)


if __name__ == "__main__":
    unittest.main()
