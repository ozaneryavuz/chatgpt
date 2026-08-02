from __future__ import annotations

import json
import re
import unittest
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "alo186/amazon-elektrik-urunleri"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/commercial-category-pages-v41.json"
ROUTES = {
    "/amazon-elektrik-urunleri": SOURCE_ROOT / "index.html",
    "/amazon-elektrik-urunleri/powerbank-usb-c-secimi": SOURCE_ROOT / "powerbank-usb-c-secimi/index.html",
    "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi": SOURCE_ROOT / "akim-korumali-grup-priz-secimi/index.html",
    "/amazon-elektrik-urunleri/modem-mini-ups-secimi": SOURCE_ROOT / "modem-mini-ups-secimi/index.html",
    "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi": SOURCE_ROOT / "acil-aydinlatma-duman-alarmi/index.html",
}
DIRECT_COMMERCIAL_ROUTES = {
    "/amazon-elektrik-urunleri",
    "/amazon-elektrik-urunleri/powerbank-usb-c-secimi",
}
EXPANSION_ROUTES = {
    "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi",
    "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi",
    "/amazon-elektrik-urunleri/ges-malzemeleri-secimi",
    "/amazon-elektrik-urunleri/kombi-ups-power-station-secimi",
    "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici",
}
CANONICAL_LINK = re.compile(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', re.I)


def normalized_path(value: str) -> str:
    path = urlsplit(value).path or "/"
    return path.rstrip("/") or "/"


def assert_source_canonical(test: unittest.TestCase, html: str, route: str) -> None:
    match = CANONICAL_LINK.search(html)
    test.assertIsNotNone(match, route)
    parsed = urlsplit(match.group(1))
    test.assertEqual(parsed.scheme, "https", route)
    test.assertIn(parsed.hostname, {"alo186.com", "www.alo186.com"}, route)
    test.assertEqual(normalized_path(match.group(1)), normalized_path(route), route)


def text_of(html: str, tag: str) -> str:
    match = re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip()


class CommercialCategoryPagesTests(unittest.TestCase):
    def test_overlay_routes_all_five_unique_commercial_pages(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertGreaterEqual(overlay["version"], 41)
        actual = {item["canonicalPath"]: item for item in overlay["routes"]}
        self.assertEqual(set(actual), set(ROUTES))
        self.assertEqual(actual["/amazon-elektrik-urunleri"]["type"], "collection")
        for route in set(ROUTES) - {"/amazon-elektrik-urunleri"}:
            self.assertEqual(actual[route]["type"], "commerce-guide")
        self.assertEqual(len({item["source"] for item in overlay["routes"]}), 5)

    def test_pages_have_unique_intent_canonical_and_visible_commercial_disclosure(self) -> None:
        titles: set[str] = set()
        headings: set[str] = set()
        runtime = (SOURCE_ROOT / "commercial.js").read_text(encoding="utf-8").lower()
        self.assertIn("kullanıcıya ek maliyet yansımaz", runtime)
        self.assertIn("fiyat, stok, satıcı", runtime)
        self.assertIn("normalizedisclosures", runtime)
        for route, path in ROUTES.items():
            html = path.read_text(encoding="utf-8")
            lower = html.lower()
            title = text_of(html, "title")
            h1 = text_of(html, "h1")
            self.assertTrue(title, route)
            self.assertTrue(h1, route)
            self.assertNotIn(title, titles)
            self.assertNotIn(h1, headings)
            titles.add(title)
            headings.add(h1)
            assert_source_canonical(self, html, route)
            self.assertIn('meta name="description"', html)
            self.assertIn("Reklam / satış ortaklığı", html)
            self.assertIn("application/ld+json", html)
            self.assertNotIn("en ucuz", lower)
            self.assertNotIn("garantili olarak öner", lower)
            self.assertNotRegex(lower, r"\b\d+[.,]?\d*\s*tl\b")
            if route in DIRECT_COMMERCIAL_ROUTES:
                self.assertIn("kullanıcıya ek maliyet yansımaz", lower)
                self.assertIn("fiyat", lower)
                self.assertIn("stok", lower)

    def test_hub_links_to_current_dedicated_pages_without_stale_count_fixture(self) -> None:
        html = ROUTES["/amazon-elektrik-urunleri"].read_text(encoding="utf-8")
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
        linked = {normalized_path(value) for value in hrefs if normalized_path(value).startswith("/amazon-elektrik-urunleri/")}
        required = {normalized_path(route) for route in (set(ROUTES) - {"/amazon-elektrik-urunleri"}) | EXPANSION_ROUTES}
        self.assertTrue(required <= linked, sorted(required - linked))
        self.assertGreaterEqual(html.count('class="card route-card"'), len(required))
        self.assertIn("Mevcut sistem yeterliyse satın alma yok", html)
        self.assertIn("Aktif tehlikede satış yolu kapalı", html)
        self.assertNotRegex(html, r"https://alo186\.com/amazon-elektrik-urunleri(?=[a-z0-9])")

    def test_direct_affiliate_links_are_freshness_gated_and_high_risk_categories_remain_closed(self) -> None:
        runtime = (SOURCE_ROOT / "commercial.js").read_text(encoding="utf-8")
        catalog = (ROOT / "alo186/urun-eslestirme/catalog.js").read_text(encoding="utf-8")
        for token in (
            "freshOnly: true",
            "verificationStatus",
            "category.mode === 'direct'",
            'rel="sponsored nofollow noopener"',
            "commercial_products_blocked",
        ):
            self.assertIn(token, runtime)
        self.assertIn("const verificationMaxAgeDays=45", catalog)
        for category in ("powerbank", "usb_c_charger", "usb_c_cable", "usb_c_hub", "display_cable"):
            self.assertRegex(catalog, re.compile(rf"id:'{category}'.*?mode:'direct'", re.S))
        for category in ("surge_strip", "generator", "inverter", "outlet_tester", "ev_cable", "ups_battery"):
            self.assertNotRegex(catalog, re.compile(rf"id:'{category}'.*?mode:'direct'", re.S))
        for route in (
            "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi",
            "/amazon-elektrik-urunleri/modem-mini-ups-secimi",
            "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi",
        ):
            self.assertNotIn("amazon.com.tr", ROUTES[route].read_text(encoding="utf-8").lower())

    def test_each_page_has_a_free_tool_before_or_beside_commercial_route(self) -> None:
        requirements = {
            "/amazon-elektrik-urunleri/powerbank-usb-c-secimi": "/hesaplama/powerbank-usb-c-uygunluk/",
            "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi": "/hesaplama/akim-korumali-grup-priz-uygunluk/",
            "/amazon-elektrik-urunleri/modem-mini-ups-secimi": "/hesaplama/modem-internet-yedekleme/",
            "/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi": "/hesaplama/acil-aydinlatma-sure-uygunluk/",
        }
        for route, tool in requirements.items():
            html = ROUTES[route].read_text(encoding="utf-8")
            self.assertIn(f'href="{tool}"', html)
            self.assertIn("/akilli-urun-secimi", html)
        emergency = ROUTES["/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi"].read_text(encoding="utf-8")
        self.assertIn("/hesaplama/duman-alarmi-yerlesim-bakim-uygunluk/", emergency)

    def test_pages_preserve_safety_and_no_purchase_boundaries(self) -> None:
        powerbank = ROUTES["/amazon-elektrik-urunleri/powerbank-usb-c-secimi"].read_text(encoding="utf-8").lower()
        surge = ROUTES["/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi"].read_text(encoding="utf-8").lower()
        mini_ups = ROUTES["/amazon-elektrik-urunleri/modem-mini-ups-secimi"].read_text(encoding="utf-8").lower()
        safety = ROUTES["/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi"].read_text(encoding="utf-8").lower()
        self.assertIn("yeni ürün almak gerekmeyebilir", powerbank)
        self.assertIn("pano tipi spd", surge)
        self.assertIn("gerilim veya polarite okunamıyor", mini_ups)
        self.assertIn("112 aranır", safety)
        self.assertIn("ürün satıcısı değildir", ROUTES["/amazon-elektrik-urunleri"].read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
