from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "alo186/amazon-elektrik-urunleri"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/commercial-category-pages-v42.json"
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build  # noqa: E402
from inject_private_search import run as inject_private_search  # noqa: E402


ROUTES = {
    "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi": SOURCE_ROOT / "tasinabilir-guc-istasyonu-secimi/index.html",
    "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi": SOURCE_ROOT / "akilli-priz-enerji-olcer-secimi/index.html",
    "/amazon-elektrik-urunleri/ges-malzemeleri-secimi": SOURCE_ROOT / "ges-malzemeleri-secimi/index.html",
}
CONSUMER_HUB_ROUTES = {
    "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi",
    "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi",
}
TOOLS = {
    "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi": "/hesaplama/power-station-kapasite-eps-uygunluk/",
    "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi": "/hesaplama/akilli-priz-enerji-olcer-uygunluk/",
    "/amazon-elektrik-urunleri/ges-malzemeleri-secimi": "/hesaplama/gunes-paneli-power-station-uygunluk/",
}
AMAZON_HOSTS = {"amazon.com.tr", "www.amazon.com.tr"}


def text_of(html: str, tag: str) -> str:
    match = re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip()


def jsonld_types(html: str) -> set[str]:
    result: set[str] = set()

    def visit(value) -> None:
        if isinstance(value, dict):
            raw = value.get("@type")
            if isinstance(raw, str):
                result.add(raw)
            elif isinstance(raw, list):
                result.update(str(item) for item in raw)
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    for block in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        visit(json.loads(block))
    return result


def amazon_links(html: str) -> list[str]:
    links = re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>', html, re.I | re.S)
    return [value for value in links if urlsplit(value).hostname in AMAZON_HOSTS]


class CommercialCategoryExpansionTests(unittest.TestCase):
    def test_overlay_adds_three_unique_non_overlapping_intents(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertGreaterEqual(overlay["version"], 42)
        self.assertEqual(overlay["generatedAt"], "2026-07-29")
        actual = {item["canonicalPath"]: item for item in overlay["routes"]}
        self.assertEqual(set(actual), set(ROUTES))
        self.assertEqual(len({item["source"] for item in actual.values()}), 3)
        for route, row in actual.items():
            self.assertEqual(row["type"], "commerce-guide", route)
            self.assertTrue((ROOT / row["source"]).is_file(), row["source"])

    def test_pages_are_substantive_unique_and_do_not_publish_unverified_commerce_data(self) -> None:
        titles: set[str] = set()
        headings: set[str] = set()
        descriptions: set[str] = set()
        for route, path in ROUTES.items():
            html = path.read_text(encoding="utf-8")
            lower = html.lower()
            title = text_of(html, "title")
            h1 = text_of(html, "h1")
            description_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.I)
            self.assertIsNotNone(description_match, route)
            description = description_match.group(1)
            self.assertNotIn(title, titles)
            self.assertNotIn(h1, headings)
            self.assertNotIn(description, descriptions)
            titles.add(title)
            headings.add(h1)
            descriptions.add(description)
            self.assertGreaterEqual(len(description), 120, route)
            self.assertIn(f'<link rel="canonical" href="https://www.alo186.com{route}">', html)
            self.assertEqual(html.count("<h1>"), 1, route)
            self.assertGreaterEqual(len(re.findall(r"<h2>", html)), 6, route)
            self.assertGreaterEqual(html.count("<details>"), 3, route)
            self.assertIn("Reklam / satış ortaklığı" if "ges-malzemeleri" not in route else "Ticari şeffaflık", html)
            self.assertIn("ürün satıc", lower)
            self.assertIn("fiyat", lower)
            if "ges-malzemeleri" not in route:
                self.assertIn("stok", lower)
            else:
                self.assertIn("mağaza bağlantısı göstermez", lower)
            self.assertNotRegex(lower, r"\b\d+[.,]?\d*\s*(?:tl|₺|try)\b")
            self.assertNotIn("en ucuz", lower)
            self.assertNotIn("en iyi ürün", lower)
            self.assertNotIn("garanti edilir", lower)
            types = jsonld_types(html)
            self.assertIn("Article", types)
            self.assertIn("FAQPage", types)
            self.assertNotIn("Product", types)
            self.assertNotIn("Offer", types)
            self.assertEqual(amazon_links(html), [], route)

    def test_free_tool_and_no_purchase_boundary_precede_product_center(self) -> None:
        for route, path in ROUTES.items():
            html = path.read_text(encoding="utf-8")
            self.assertIn(TOOLS[route], html)
            self.assertTrue(
                any(term in html for term in ("Satın almama", "satın almamanız", "sipariş vermeyin")),
                route,
            )
        power = ROUTES["/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi"].read_text(encoding="utf-8")
        smart = ROUTES["/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi"].read_text(encoding="utf-8")
        ges = ROUTES["/amazon-elektrik-urunleri/ges-malzemeleri-secimi"].read_text(encoding="utf-8")
        runtime = (SOURCE_ROOT / "commercial.js").read_text(encoding="utf-8")
        self.assertIn('data-category="power_station"', power)
        self.assertIn('data-category="smart_plug"', smart)
        self.assertIn("data-product-center", power)
        self.assertIn("data-product-center", smart)
        for html in (power, smart):
            self.assertIn("doğrudan Amazon bağlantısı gösterilmez", html)
            self.assertTrue("doğrulanmış ürün" in html.casefold() or "doğrulanmış ürün kartı" in html.casefold())
        self.assertIn('data-commercial-scope="professional-only"', ges)
        self.assertIn("doğrudan Amazon veya başka mağaza bağlantısı göstermez", ges)
        self.assertNotIn("data-product-center", ges)
        self.assertIn("if (professionalOnly) return;", runtime)

    def test_catalog_keeps_new_consumer_categories_tool_first(self) -> None:
        catalog = (ROOT / "alo186/urun-eslestirme/catalog.js").read_text(encoding="utf-8")
        for category in ("power_station", "smart_plug"):
            pattern = re.compile(
                rf"\{{id:'{category}'.*?mode:'guide'.*?affiliatePolicy:'after_tool'",
                re.S,
            )
            self.assertRegex(catalog, pattern)
        self.assertNotRegex(catalog, re.compile(r"id:'(?:power_station|smart_plug)'.*?mode:'direct'", re.S))

    def test_hub_inventory_matches_visible_cards_without_stale_fixture(self) -> None:
        hub = (SOURCE_ROOT / "index.html").read_text(encoding="utf-8")
        guide_links = re.findall(
            r'href="(/amazon-elektrik-urunleri/[^"?#]+)"',
            hub,
            re.I,
        )
        unique = set(guide_links)
        self.assertGreaterEqual(len(unique), 7, sorted(unique))
        self.assertEqual(hub.count('class="card route-card"'), len(unique))
        self.assertIn("teknik açığı", hub)
        self.assertIn("mevcut güvenli sistem", hub)
        self.assertTrue(CONSUMER_HUB_ROUTES <= unique, sorted(unique))
        self.assertNotIn("/amazon-elektrik-urunleri/ges-malzemeleri-secimi", unique)
        self.assertNotIn("/urun-rehberleri/", hub)
        stale_display = re.search(r"(\d+) özel rehber", hub)
        if stale_display:
            self.assertEqual(int(stale_display.group(1)), len(unique), sorted(unique))

    def test_production_bundle_sitemap_and_private_search_include_expansion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory) / "site"
            release = build(ROOT, site, "commercial-expansion-test")
            routes = {row["canonicalPath"] for row in release["routes"]}
            self.assertGreaterEqual(release["routingVersion"], 42)
            self.assertTrue(set(ROUTES) <= routes)
            sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
            for route in ROUTES:
                self.assertTrue((site / route.strip("/") / "index.html").is_file(), route)
                self.assertIn(f"https://alo186.com{route}", sitemap)

            result = inject_private_search(site, "")
            self.assertGreaterEqual(result["entryCount"], 90)
            index = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
            entries = {row["canonicalPath"]: row for row in index["entries"]}
            for route in ROUTES:
                self.assertIn(route, entries)
                self.assertEqual(entries[route]["priority"], 45)
                self.assertEqual(entries[route]["bucket"], "collection")
                self.assertFalse(entries[route]["featured"])
                for forbidden in ("price", "stock", "rating", "seller", "warranty", "affiliateCommission"):
                    self.assertNotIn(forbidden, entries[route])
            self.assertEqual(
                index["commercialRankingExcluded"],
                ["price", "stock", "rating", "seller", "warranty", "affiliateCommission"],
            )


if __name__ == "__main__":
    unittest.main()