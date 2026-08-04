from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-klima-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/elektrik-kesintisinde-sicak-hava-serinleme-plani/index.html"
COMMERCE = ROOT / "alo186/amazon-elektrik-urunleri/sarjli-fan-termometre-elektrik-kesintisi-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v273-heat-outage.json"


class GrowthV273HeatOutageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.commerce = COMMERCE.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))

    def test_files_and_routes_exist(self) -> None:
        for path in (ARTICLE, TOOL, COMMERCE, OVERLAY):
            self.assertTrue(path.is_file(), path)
        self.assertEqual(self.overlay["version"], 273)
        routes = {item["canonicalPath"]: item for item in self.overlay["routes"]}
        self.assertEqual(
            set(routes),
            {
                "/haberler/elektrik-kesilince-klima-calisir-mi/",
                "/hesaplama/elektrik-kesintisinde-sicak-hava-serinleme-plani/",
                "/amazon-elektrik-urunleri/sarjli-fan-termometre-elektrik-kesintisi-secimi/",
            },
        )
        for route in routes.values():
            self.assertTrue((ROOT / route["source"]).is_file())

    def test_canonicals_use_single_host(self) -> None:
        expected = {
            self.article: "https://alo186.com/haberler/elektrik-kesilince-klima-calisir-mi/",
            self.tool: "https://alo186.com/hesaplama/elektrik-kesintisinde-sicak-hava-serinleme-plani/",
            self.commerce: "https://alo186.com/amazon-elektrik-urunleri/sarjli-fan-termometre-elektrik-kesintisi-secimi/",
        }
        for html, canonical in expected.items():
            self.assertIn(f'<link rel="canonical" href="{canonical}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_answers_intent_and_keeps_health_boundary_first(self) -> None:
        required = (
            "Elektrik kesilince standart klima durur",
            "112",
            "32 °C",
            "Samsung Türkiye",
            "Dünya Sağlık Örgütü",
            "T.C. Sağlık Bakanlığı",
            "4 Ağustos 2026",
            "Bağımsız bilgilendirme platformudur",
            "Klimaya yedek güç neden genel tüketici ürünü değildir?",
        )
        for text in required:
            self.assertIn(text, self.article)
        self.assertLess(
            self.article.index("Acil sınır: alışveriş yapmayın"),
            self.article.index("Güvenlik kapılı seçiciyi aç"),
        )
        self.assertNotIn("amazon.com.tr", self.article.lower())

    def test_tool_is_private_no_store_and_prefers_no_buy(self) -> None:
        required = (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli — yeni ürün almayın",
            "32 °C ihtiyat sınırı",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "no_buy_selected",
            "professional",
            "112",
        )
        for text in required:
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        self.assertNotRegex(
            self.tool,
            r"(?i)<input[^>]+(?:name|id)=[\"'](?:email|phone|address|tc|tesisat|abonelik)",
        )
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "document.cookie"):
            self.assertNotIn(forbidden, self.tool)

    def test_commerce_is_disclosed_safety_gated_and_starts_locked(self) -> None:
        required = (
            "Satış ortaklığı açıklaması",
            "Amazon Türkiye bağlantıları satış ortaklığı bağlantısıdır",
            "Mevcut çözümüm yeterli — yeni ürün almayacağım",
            'class="gate-check"',
            "alo186rehber-21",
            "sponsored nofollow noopener",
            "affiliate_unlocked",
            "affiliate_clicked",
            "BEGIN:VCALENDAR",
            "32 °C",
            "112",
        )
        for text in required:
            self.assertIn(text, self.commerce)
        self.assertLess(
            self.commerce.index("Satış ortaklığı açıklaması"),
            self.commerce.index("Üç sınıfın gerçek görevi"),
        )
        self.assertEqual(self.commerce.count('class="button primary store-link"'), 3)
        locked = re.findall(
            r'<a\b[^>]*class="button primary store-link"[^>]*aria-disabled="true"',
            self.commerce,
        )
        self.assertEqual(len(locked), 3)
        self.assertIsNone(
            re.search(
                r'(?is)<a\b[^>]*\bhref\s*=\s*[\"\']https://www\.amazon\.com\.tr[^>]*>',
                self.commerce,
            ),
            "Amazon bağlantıları kaynak HTML anchorlarında aktif href taşımamalı",
        )
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "document.cookie"):
            self.assertNotIn(forbidden, self.commerce)

    def test_schema_and_commercial_claims_are_fail_closed(self) -> None:
        self.assertEqual(self.commerce.count('"@type":"Product"'), 3)
        for html in (self.article, self.tool, self.commerce):
            for forbidden in (
                '"@type":"Offer"',
                '"@type":"AggregateRating"',
                '"@type":"Review"',
                '"price":',
                '"priceCurrency":',
                '"availability":',
                '"aggregateRating":',
                '"warranty":',
            ):
                self.assertNotIn(forbidden, html)


if __name__ == "__main__":
    unittest.main()
