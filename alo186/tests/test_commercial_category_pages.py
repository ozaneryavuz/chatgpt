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
# Ürün merkezi genel kategori listesinden görev odaklı karar kartlarına
# dönüştürüldü. Hızla eskiyen sabit rota/rehber/model sayıları artık sözleşme
# değildir; kullanıcı görevi ve güncel teknik uygunluk görünür kalmalıdır.
HUB_ROUTES = {
    "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
    "/amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/",
    "/amazon-elektrik-urunleri/guvenlik-kamerasi-nvr-poe-ups-secici/",
    "/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/",
    "/amazon-elektrik-urunleri/cpap-yedek-guc-uygunluk-secici/",
    "/amazon-elektrik-urunleri/mobil-hotspot-4g-5g-yedek-internet-secici/",
    "/amazon-elektrik-urunleri/powerbank-usb-c-secimi",
    "/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi",
    "/amazon-elektrik-urunleri/tasinabilir-guc-istasyonu-secimi",
    "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi",
    "/amazon-elektrik-urunleri/kombi-ups-power-station-secimi",
    "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-gida-guvenligi-secici/",
}


def text_of(html: str, tag: str) -> str:
    match = re.search(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", match.group(1)))).strip()


def canonical_for(html: str, route: str) -> str:
    match = re.search(
        r'<link\b(?=[^>]*\brel=["\']canonical["\'])(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*>',
        html,
        re.I,
    )
    if not match:
        raise AssertionError(f"Canonical bulunamadı: {route}")
    canonical = match.group(1)
    parsed = urlsplit(canonical)
    if parsed.scheme != "https" or parsed.netloc not in {"alo186.com", "www.alo186.com"}:
        raise AssertionError(canonical)
    if (parsed.path.rstrip("/") or "/") != (route.rstrip("/") or "/"):
        raise AssertionError((canonical, route))
    if parsed.query or parsed.fragment:
        raise AssertionError(canonical)
    return canonical


def route_file(route: str) -> Path:
    return ROOT / "alo186" / route.strip("/") / "index.html"


class CommercialCategoryPagesTests(unittest.TestCase):
    def test_overlay_routes_all_five_unique_commercial_pages(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertGreaterEqual(overlay["version"], 41)
        self.assertEqual(overlay["generatedAt"], "2026-07-29")
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
            canonical_for(html, route)
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

    def test_hub_links_to_current_task_focused_routes(self) -> None:
        html = ROUTES["/amazon-elektrik-urunleri"].read_text(encoding="utf-8")
        for route in HUB_ROUTES:
            self.assertIn(f'href="{route}"', html)
            self.assertTrue(route_file(route).is_file(), route)
        self.assertGreaterEqual(html.count('class="card route-card"'), len(HUB_ROUTES))
        self.assertIn("Güncel karar rotaları", html)
        self.assertIn("Mevcut sistem yeterliyse satın alma yok", html)
        self.assertIn("Aktif tehlikede satış yolu kapalı", html)
        for stale_claim in ("18+ karar rotası", "9 özel rehber", "25 rehber", "152 model", "67 ürün seçim yolu"):
            self.assertNotIn(stale_claim, html)

    def test_direct_affiliate_links_are_freshness_gated_and_only_powerbank_is_direct(self) -> None:
        runtime = (SOURCE_ROOT / "commercial.js").read_text(encoding="utf-8")
        catalog = (ROOT / "alo186/urun-eslestirme/catalog.js").read_text(encoding="utf-8")
        self.assertIn("freshOnly: true", runtime)
        self.assertIn("verificationStatus", runtime)
        self.assertIn("category.mode === 'direct'", runtime)
        self.assertIn('rel="sponsored nofollow noopener"', runtime)
        self.assertIn("commercial_products_blocked", runtime)
        self.assertIn("const verificationMaxAgeDays=45", catalog)
        self.assertIn("id:'powerbank'", catalog)
        self.assertIn("mode:'direct'", catalog)
        self.assertIn("id:'surge_strip'", catalog)
        self.assertIn("id:'mini_ups'", catalog)
        self.assertNotIn("amazon.com.tr", ROUTES["/amazon-elektrik-urunleri/akim-korumali-grup-priz-secimi"].read_text(encoding="utf-8").lower())
        self.assertNotIn("amazon.com.tr", ROUTES["/amazon-elektrik-urunleri/modem-mini-ups-secimi"].read_text(encoding="utf-8").lower())
        self.assertNotIn("amazon.com.tr", ROUTES["/amazon-elektrik-urunleri/acil-aydinlatma-duman-alarmi"].read_text(encoding="utf-8").lower())

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
