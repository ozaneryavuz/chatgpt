from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-kombi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/index.html"
COMMERCE = ROOT / "alo186/amazon-elektrik-urunleri/kombi-ups-yedek-guc-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v272-boiler-trust.json"
DRIFT = ROOT / "alo186/growth/live-drift/sites-delta-v272-homepage-evergreen-canonical.json"


class GrowthV272BoilerTrustTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.commerce = COMMERCE.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.drift = json.loads(DRIFT.read_text(encoding="utf-8"))

    def test_files_and_routes_exist(self) -> None:
        for path in (ARTICLE, TOOL, COMMERCE, OVERLAY, DRIFT):
            self.assertTrue(path.is_file(), path)
        self.assertEqual(self.overlay["version"], 272)
        routes = {item["canonicalPath"]: item for item in self.overlay["routes"]}
        self.assertEqual(
            set(routes),
            {
                "/haberler/elektrik-kesilince-kombi-calisir-mi/",
                "/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/",
                "/amazon-elektrik-urunleri/kombi-ups-yedek-guc-secimi/",
            },
        )
        for route in routes.values():
            self.assertTrue((ROOT / route["source"]).is_file())

    def test_canonicals_use_single_host(self) -> None:
        expected = {
            self.article: "https://alo186.com/haberler/elektrik-kesilince-kombi-calisir-mi/",
            self.tool: "https://alo186.com/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/",
            self.commerce: "https://alo186.com/amazon-elektrik-urunleri/kombi-ups-yedek-guc-secimi/",
        }
        for html, canonical in expected.items():
            self.assertIn(f'<link rel="canonical" href="{canonical}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_answers_intent_and_preserves_emergency_boundary(self) -> None:
        required = (
            "Elektrik kesilince kombi normal olarak durur",
            "187 Doğal Gaz Acil",
            "112",
            "Elektrik gelince kombi kendiliğinden çalışır mı?",
            "Mevcut sistem kesintide hedef süreyi sağlıyorsa yeni UPS gerekir mi?",
            "4 Ağustos 2026",
            "Worcester Bosch",
            "Eaton",
            "EPDK",
            "T.C. Sağlık Bakanlığı",
            "Bağımsız bilgilendirme platformudur",
        )
        for text in required:
            self.assertIn(text, self.article)
        self.assertLess(
            self.article.index("Acil sınır: ürün düşünmeyin"),
            self.article.index("Satış ortaklığı açıklamalı seçiciyi aç"),
        )

    def test_tool_is_privacy_preserving_and_has_no_store_link(self) -> None:
        required = (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli — yeni ürün almayın",
            "ideal yük enerjisi",
            "187",
            "112",
            "professional",
            "30 günlük görsel kontrol",
            "90 günlük gerçek test",
            "BEGIN:VCALENDAR",
            "no_buy_selected",
        )
        for text in required:
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        self.assertNotRegex(self.tool, r"(?i)<input[^>]+(?:name|id)=[\"'](?:email|phone|address|tc|tesisat|abonelik)")
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "document.cookie"):
            self.assertNotIn(forbidden, self.tool)

    def test_commerce_is_safety_gated_and_disclosed_before_links(self) -> None:
        required = (
            "Satış ortaklığı açıklaması",
            "Amazon Türkiye bağlantıları satış ortaklığı bağlantısıdır",
            "Mevcut sistem kontrollü testte hedef süreyi ve güvenli yeniden başlamayı sağlıyor — yeni ürün almayacağım",
            "class=\"gate-check\"",
            "alo186rehber-21",
            "sponsored nofollow noopener",
            "affiliate_unlocked",
            "affiliate_clicked",
            "BEGIN:VCALENDAR",
            "187",
            "112",
        )
        for text in required:
            self.assertIn(text, self.commerce)
        self.assertLess(
            self.commerce.index("Satış ortaklığı açıklaması"),
            self.commerce.index("Kilitli Amazon Türkiye arama bağlantıları"),
        )
        self.assertEqual(self.commerce.count('class="button primary store-link"'), 3)
        self.assertEqual(self.commerce.count('aria-disabled="true"'), 3)
        self.assertIsNone(
            re.search(r'(?i)href\s*=\s*[\"\']https://www\.amazon\.com\.tr', self.commerce),
            "Amazon linkleri kaynak HTML içinde aktif href olarak bulunmamalı",
        )
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "document.cookie"):
            self.assertNotIn(forbidden, self.commerce)

    def test_schema_has_generic_product_classes_but_no_unverified_commercial_fields(self) -> None:
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

    def test_homepage_drift_patch_covers_current_and_cached_variants(self) -> None:
        self.assertEqual(self.drift["version"], 272)
        self.assertEqual(self.drift["priority"], "P0")
        matches = {item["match"] for item in self.drift["replacements"]}
        expected = {
            "25 rehberin tamamını gör",
            "26 rehberin tamamını gör",
            "10 rehberin tamamını gör",
            "152 modeli doğrulanmış ürün için seçim kartları",
            "154 modeli doğrulanmış ürün için seçim kartları",
            "50+ elektrik ürünü için Amazon seçim kartları",
            "https://www.alo186.com/elektrik-portali",
        }
        self.assertTrue(expected.issubset(matches))
        forbidden = set(self.drift["forbiddenAfterPatch"])
        self.assertIn("https://www.alo186.com/elektrik-portali", forbidden)
        self.assertIn("https://alo186.com/", self.drift["requiredAfterPatch"])
        self.assertTrue(self.drift["commercialConstraints"]["noBuyOutcomeRequired"])
        self.assertTrue(self.drift["institutionalConstraints"]["mustNotImplyEdasOrPublicAuthority"])


if __name__ == "__main__":
    unittest.main()
