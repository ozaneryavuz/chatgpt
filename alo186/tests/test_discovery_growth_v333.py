from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap-growth-v333.xml"
HUB = ROOT / "kesintiye-hazirlik-atolyesi" / "index.html"


class DiscoveryGrowthV333Test(unittest.TestCase):
    def test_robots_announces_only_effective_canonical_sitemap(self):
        text = ROBOTS.read_text(encoding="utf-8")
        sitemap_lines = [line.strip() for line in text.splitlines() if line.strip().lower().startswith("sitemap:")]
        self.assertEqual(["Sitemap: https://alo186.com/sitemap.xml"], sitemap_lines)

    def test_v333_discovery_inventory_remains_valid_unique_and_recent(self):
        tree = ET.parse(SITEMAP)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [n.text.strip() for n in root.findall("sm:url/sm:loc", ns)]
        self.assertGreaterEqual(len(urls), 40)
        self.assertEqual(len(urls), len(set(urls)), "v333 sitemap contains duplicate URLs")
        self.assertTrue(all(u.startswith("https://") for u in urls))
        required_paths = (
            "/kesintiye-hazirlik-atolyesi",
            "/haberler/elektrik-kesintisi-bilgisayara-zarar-verir-mi/",
            "/haberler/elektrik-kesilince-gunes-panelleri-calisir-mi/",
            "/haberler/elektrik-kesilince-pos-yazar-kasa-calisir-mi/",
            "/haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/",
        )
        for path in required_paths:
            self.assertTrue(any(url.endswith(path) for url in urls), path)

    def test_hub_preserves_trust_and_no_buy(self):
        html = HUB.read_text(encoding="utf-8")
        required_phrases = [
            "Sisteminiz yeterliyse yeni ürün almayın",
            "Amazon Türkiye bağlantısı",
            "satış ortaklığı bağlantısı",
            "Fiyat, stok, puan veya garanti",
            "ALO186 resmî kurum değildir",
            "Arıza/ihbar kaydı almaz",
            "kişisel veri istemez",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, html)
        self.assertNotIn("amazon.com.tr", html.lower())
        self.assertNotIn("amzn.to", html.lower())
        self.assertNotRegex(html, r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating|Review)"')

    def test_hub_routes_intent_before_commerce(self):
        html = HUB.read_text(encoding="utf-8")
        representative_routes = [
            "/hesaplama/bilgisayar-nas-elektrik-kesintisi-hazirlik-plani/",
            "/hesaplama/televizyon-elektrik-kesintisi-koruma-hazirlik-plani/",
            "/hesaplama/ges-elektrik-kesintisi-yedekleme-hazirlik-plani/",
            "/sektor-rehberi/magaza-restoran-kafe-pos-yazar-kasa-kesinti-surekliligi/",
            "/sektor-rehberi/site-otel-isletme-otomatik-kapi-kepenk-kesinti-surekliligi/",
            "/hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/",
        ]
        for route in representative_routes:
            self.assertIn(f'href="{route}"', html)
        merchant_like = re.findall(r'href="([^"]*(?:amazon\.com|amzn\.to)[^"]*)"', html, flags=re.I)
        self.assertEqual([], merchant_like)


if __name__ == "__main__":
    unittest.main()
