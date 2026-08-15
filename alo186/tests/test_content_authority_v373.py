from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"
ROUTING = ALO / "deployment/routing-overlays/content-authority-v373-vfd-spd-bess.json"

ARTICLES = {
    "vfd-surucu-kacak-akim-rolesi-atiyor-type-f-type-b": {
        "canonical": "https://alo186.com/haberler/vfd-surucu-kacak-akim-rolesi-atiyor-type-f-type-b",
        "sources": ("se.com", "webstore.iec.ch"),
        "needles": ("Tip F", "Tip B", "300 Hz", "EMC filtresi"),
    },
    "parafudr-kacak-akim-rolesi-atiyor-spd-rcd-sirasi": {
        "canonical": "https://alo186.com/haberler/parafudr-kacak-akim-rolesi-atiyor-spd-rcd-sirasi",
        "sources": ("dehn-international.com", "se.com", "webstore.iec.ch", "obo.global"),
        "needles": ("upstream", "darbe", "MCOV", "artık akım"),
    },
    "bess-izolasyon-hatasi-imd-toprak-arizasi-kabul": {
        "canonical": "https://alo186.com/haberler/bess-izolasyon-hatasi-imd-toprak-arizasi-kabul",
        "sources": ("webstore.iec.ch", "bender.de"),
        "needles": ("IEC 61557-8", "IEC 61557-9", "IMD", "IFLS"),
    },
}


def article_path(slug: str) -> Path:
    return ALO / "haberler" / slug / "index.html"


def ld_json_objects(html: str) -> list[dict]:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S | re.I)
    return [json.loads(block) for block in blocks]


class ContentAuthorityV373Tests(unittest.TestCase):
    def test_three_articles_exist_with_unique_seo_contract(self) -> None:
        for slug, spec in ARTICLES.items():
            path = article_path(slug)
            self.assertTrue(path.is_file(), path)
            html = path.read_text(encoding="utf-8")
            self.assertEqual(1, len(re.findall(r"<title>.*?</title>", html, flags=re.S | re.I)), slug)
            self.assertEqual(1, len(re.findall(r"<h1\b[^>]*>.*?</h1>", html, flags=re.S | re.I)), slug)
            self.assertEqual(1, html.count(f'<link rel="canonical" href="{spec["canonical"]}">'), slug)
            self.assertIn('name="description"', html, slug)
            self.assertIn("60 saniyelik karar", html, slug)

    def test_structured_data_and_visible_faq_exist(self) -> None:
        for slug in ARTICLES:
            html = article_path(slug).read_text(encoding="utf-8")
            payloads = ld_json_objects(html)
            self.assertTrue(payloads, slug)
            graph = payloads[0].get("@graph", [])
            types = {item.get("@type") for item in graph if isinstance(item, dict)}
            self.assertTrue({"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (slug, types))
            faq = next(item for item in graph if item.get("@type") == "FAQPage")
            self.assertGreaterEqual(len(faq.get("mainEntity", [])), 4, slug)
            visible_h3 = len(re.findall(r"<h3\b", html, flags=re.I))
            self.assertGreaterEqual(visible_h3, 4, slug)

    def test_primary_sources_and_claim_markers(self) -> None:
        for slug, spec in ARTICLES.items():
            html = article_path(slug).read_text(encoding="utf-8")
            for source in spec["sources"]:
                self.assertIn(source, html, (slug, source))
            for needle in spec["needles"]:
                self.assertIn(needle, html, (slug, needle))

    def test_contextual_internal_links(self) -> None:
        for slug in ARTICLES:
            html = article_path(slug).read_text(encoding="utf-8")
            hrefs = re.findall(r'href="(/[^"]+)"', html)
            contextual = [href for href in hrefs if href.startswith("/haberler/") or href.startswith("/elektrik-portali")]
            self.assertGreaterEqual(len(set(contextual)), 4, (slug, contextual))

    def test_no_commerce_on_high_risk_intents(self) -> None:
        forbidden = (
            "amazon.com.tr",
            "alo186rehber-21",
            '"@type":"Product"',
            '"@type":"Offer"',
            '"@type":"AggregateRating"',
            "priceCurrency",
        )
        for slug in ARTICLES:
            html = article_path(slug).read_text(encoding="utf-8")
            for needle in forbidden:
                self.assertNotIn(needle, html, (slug, needle))

    def test_professional_only_and_no_buy_first_contract(self) -> None:
        for slug in ARTICLES:
            html = article_path(slug).read_text(encoding="utf-8")
            self.assertIn("Professional-only", html, slug)
            self.assertRegex(html, r"satın almayın|satın alma", slug)

    def test_routing_overlay_is_exact_and_no_buy_first(self) -> None:
        data = json.loads(ROUTING.read_text(encoding="utf-8"))
        self.assertEqual(373, data["version"])
        self.assertEqual("2026-08-15", data["generatedAt"])
        expected = {spec["canonical"].removeprefix("https://alo186.com") for spec in ARTICLES.values()}
        actual = {route["canonicalPath"] for route in data["routes"]}
        self.assertEqual(expected, actual)
        self.assertEqual("no-buy-first", data["contentAuthority"]["commercialPolicy"])
        self.assertTrue(data["contentAuthority"]["sourceVerified"])
        self.assertTrue(data["contentAuthority"]["intentCollisionChecked"])

    def test_exact_title_h1_and_canonical_collision_guard(self) -> None:
        all_pages = list((ALO / "haberler").glob("*/index.html"))
        for slug, spec in ARTICLES.items():
            ours = article_path(slug).read_text(encoding="utf-8")
            title = re.search(r"<title>(.*?)</title>", ours, flags=re.S | re.I).group(1).strip()
            h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1\b[^>]*>(.*?)</h1>", ours, flags=re.S | re.I).group(1)).strip()
            title_hits = h1_hits = canonical_hits = 0
            for page in all_pages:
                html = page.read_text(encoding="utf-8", errors="ignore")
                if f"<title>{title}</title>" in html:
                    title_hits += 1
                match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, flags=re.S | re.I)
                if match and re.sub(r"<[^>]+>", "", match.group(1)).strip() == h1:
                    h1_hits += 1
                canonical_hits += html.count(f'<link rel="canonical" href="{spec["canonical"]}">')
            self.assertEqual(1, title_hits, (slug, title_hits))
            self.assertEqual(1, h1_hits, (slug, h1_hits))
            self.assertEqual(1, canonical_hits, (slug, canonical_hits))


if __name__ == "__main__":
    unittest.main()
