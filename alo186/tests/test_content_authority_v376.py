from __future__ import annotations

import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"
ROUTING = ALO / "deployment/routing-overlays/content-authority-v376-rcd-neutral-spd.json"

ARTICLES = {
    "kacak-akim-rolesi-tip-a-mi-tip-ac-mi": {
        "canonical": "https://alo186.com/haberler/kacak-akim-rolesi-tip-a-mi-tip-ac-mi",
        "sources": ("webstore.iec.ch", "hager.com"),
        "needles": ("Tip A", "Tip AC", "darbeli DC", "RCCB"),
    },
    "notr-toprak-birlestirilir-mi-rcd-pen-tn-tt": {
        "canonical": "https://alo186.com/haberler/notr-toprak-birlestirilir-mi-rcd-pen-tn-tt",
        "sources": ("webstore.iec.ch", "victronenergy.com"),
        "needles": ("PEN", "N-PE", "TN-S", "TT"),
    },
    "parafudr-baglanti-kablosu-50-cm-kisa-iletken-neden": {
        "canonical": "https://alo186.com/haberler/parafudr-baglanti-kablosu-50-cm-kisa-iletken-neden",
        "sources": ("webstore.iec.ch", "phoenixcontact.com"),
        "needles": ("0,5 m", "V-wiring", "Up", "L × di/dt"),
    },
}


def article_path(slug: str) -> Path:
    return ALO / "haberler" / slug / "index.html"


def ld_json_objects(html: str) -> list[dict]:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S | re.I)
    return [json.loads(block) for block in blocks]


def visible_h1(html: str) -> str:
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", html, flags=re.S | re.I)
    if not match:
        return ""
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def intent_tokens(text: str) -> set[str]:
    folded = unicodedata.normalize("NFKD", text.casefold())
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    tokens = set(re.findall(r"[a-z0-9]+", folded))
    stop = {
        "ve", "veya", "mi", "mu", "ne", "neden", "nasil", "icin", "ile", "bir", "bu",
        "da", "de", "nedir", "rehberi", "kabul", "hatasi", "alarmi", "alarm", "hata",
        "kac", "olmali", "dogru", "secimi",
    }
    return {token for token in tokens if token not in stop and len(token) > 1}


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return 0.0 if not union else len(left & right) / len(union)


class ContentAuthorityV376Tests(unittest.TestCase):
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
            self.assertGreaterEqual(len(re.findall(r"<h3\b", html, flags=re.I)), 4, slug)

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
            "amazon.com.tr", "alo186rehber-21", '"@type":"Product"', '"@type":"Offer"',
            '"@type":"AggregateRating"', "priceCurrency",
        )
        for slug in ARTICLES:
            html = article_path(slug).read_text(encoding="utf-8")
            for needle in forbidden:
                self.assertNotIn(needle, html, (slug, needle))

    def test_professional_only_and_no_buy_first_contract(self) -> None:
        for slug in ARTICLES:
            html = article_path(slug).read_text(encoding="utf-8")
            self.assertIn("Professional-only", html, slug)
            self.assertRegex(html, r"satın almayın|değiştirmeyin", slug)

    def test_routing_overlay_is_exact_and_no_buy_first(self) -> None:
        data = json.loads(ROUTING.read_text(encoding="utf-8"))
        self.assertEqual(376, data["version"])
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
            h1 = visible_h1(ours)
            title_hits = h1_hits = canonical_hits = 0
            for page in all_pages:
                html = page.read_text(encoding="utf-8", errors="ignore")
                if f"<title>{title}</title>" in html:
                    title_hits += 1
                if visible_h1(html) == h1:
                    h1_hits += 1
                canonical_hits += html.count(f'<link rel="canonical" href="{spec["canonical"]}">')
            self.assertEqual(1, title_hits, (slug, title_hits))
            self.assertEqual(1, h1_hits, (slug, h1_hits))
            self.assertEqual(1, canonical_hits, (slug, canonical_hits))

    def test_fuzzy_h1_intent_collision_guard(self) -> None:
        all_pages = list((ALO / "haberler").glob("*/index.html"))
        new_paths = {article_path(slug).resolve() for slug in ARTICLES}
        for slug in ARTICLES:
            ours = article_path(slug)
            ours_tokens = intent_tokens(visible_h1(ours.read_text(encoding="utf-8")))
            self.assertGreaterEqual(len(ours_tokens), 3, slug)
            collisions: list[tuple[float, str, str]] = []
            for page in all_pages:
                if page.resolve() in new_paths:
                    continue
                other_h1 = visible_h1(page.read_text(encoding="utf-8", errors="ignore"))
                score = jaccard(ours_tokens, intent_tokens(other_h1))
                if score >= 0.78:
                    collisions.append((score, page.parent.name, other_h1))
            self.assertFalse(collisions, (slug, sorted(collisions, reverse=True)[:5]))


if __name__ == "__main__":
    unittest.main()
