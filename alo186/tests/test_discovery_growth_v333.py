from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap-growth-v333.xml"
HUB = ROOT / "kesintiye-hazirlik-atolyesi" / "index.html"


class DiscoveryGrowthV333Test(unittest.TestCase):
    def test_robots_announces_v333_sitemap(self):
        text = ROBOTS.read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://alo186.com/sitemap-growth-v333.xml", text)

    def test_sitemap_is_valid_unique_and_recent(self):
        tree = ET.parse(SITEMAP)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [n.text.strip() for n in root.findall("sm:url/sm:loc", ns)]
        self.assertGreaterEqual(len(urls), 40)
        self.assertEqual(len(urls), len(set(urls)), "v333 sitemap contains duplicate URLs")
        self.assertTrue(all(u.startswith("https://") for u in urls))
        required = {
            "https://www.alo186.com/kesintiye-hazirlik-atolyesi",
            "https://alo186.com/haberler/elektrik-kesintisi-bilgisayara-zarar-verir-mi/",
            "https://alo186.com/haberler/elektrik-kesilince-gunes-panelleri-calisir-mi/",
            "https://alo186.com/haberler/elektrik-kesilince-pos-yazar-kasa-calisir-mi/",
            "https://alo186.com/haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/",
        }
        self.assertTrue(required.issubset(set(urls)))

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
