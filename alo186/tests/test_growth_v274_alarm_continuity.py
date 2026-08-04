from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-alarm-sistemi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/alarm-sistemi-elektrik-kesintisi-test-plani/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v274-alarm-continuity.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/alarm-continuity-v274.json"


class GrowthV274AlarmContinuityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_files_and_routes_exist(self) -> None:
        for path in (ARTICLE, TOOL, OVERLAY, DECISION):
            self.assertTrue(path.is_file(), path)
        self.assertEqual(self.overlay["version"], 274)
        routes = {item["canonicalPath"]: item for item in self.overlay["routes"]}
        self.assertEqual(
            set(routes),
            {
                "/haberler/elektrik-kesilince-alarm-sistemi-calisir-mi/",
                "/hesaplama/alarm-sistemi-elektrik-kesintisi-test-plani/",
            },
        )
        for route in routes.values():
            self.assertTrue((ROOT / route["source"]).is_file())

    def test_canonicals_use_single_host(self) -> None:
        expected = {
            self.article: "https://alo186.com/haberler/elektrik-kesilince-alarm-sistemi-calisir-mi/",
            self.tool: "https://alo186.com/hesaplama/alarm-sistemi-elektrik-kesintisi-test-plani/",
        }
        for html, canonical in expected.items():
            self.assertIn(f'<link rel="canonical" href="{canonical}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_answers_intent_without_fixed_runtime_or_commerce(self) -> None:
        required = (
            "Alarm sistemi kesintide çalışabilir",
            "panel, siren, sensör, internet/GSM haberleşmesi",
            "Acil sınır: ürün aramayın",
            "112",
            "Ajax Systems",
            "DSC",
            "4 Ağustos 2026",
            "tüketici affiliate kategorisine alınmamıştır",
            "Bağımsız bilgilendirme platformudur",
        )
        for text in required:
            self.assertIn(text, self.article)
        for fixed_claim in ("kesin 8 saat", "kesin 10 saat", "kesin 12 saat", "7–10 saat", "8–13 saat"):
            self.assertNotIn(fixed_claim, self.article)
        self.assertNotIn("amazon.com.tr", self.article.lower())
        self.assertLess(
            self.article.index("Acil sınır: ürün aramayın"),
            self.article.index("Affiliate ve hizmet sınırı"),
        )

    def test_tool_is_private_test_first_and_no_buy_first(self) -> None:
        required = (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli görünüyor — yeni ürün almayın",
            "Önce gerçek test yapın; ürün kararı vermeyin",
            "Profesyonel sistem: tüketici affiliate yolu kapalı",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "Yıllık profesyonel bakım",
            "no_buy_selected",
            "112",
        )
        for text in required:
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        self.assertNotRegex(
            self.tool,
            r"(?i)<input[^>]+(?:name|id)=[\"'](?:email|phone|address|alarm_code|subscription|serial|tc|tesisat|abonelik)",
        )
        for forbidden_call in (
            "fetch(",
            "XMLHttpRequest",
            "localStorage.",
            "sessionStorage.",
            "document.cookie",
        ):
            self.assertNotIn(forbidden_call, self.tool)
        self.assertIn("window.alo186AnalyticsConsent === true", self.tool)

    def test_affiliate_category_is_fail_closed(self) -> None:
        self.assertEqual(self.decision["version"], 274)
        self.assertEqual(self.decision["decision"], "professional-only")
        self.assertFalse(self.decision["conversionPolicy"]["consumerStoreLinks"])
        self.assertFalse(self.decision["conversionPolicy"]["directAmazonLinks"])
        self.assertTrue(self.decision["conversionPolicy"]["noBuyOutcomeRequired"])
        self.assertTrue(self.decision["conversionPolicy"]["noPriceStockRatingWarrantyClaims"])
        excluded = set(self.decision["excludedConsumerAffiliateClasses"])
        self.assertIn("model-specific alarm panel battery", excluded)
        self.assertIn("fire alarm control panel battery", excluded)
        self.assertIn("model-independent alarm UPS", excluded)
        repeat_days = {item["days"] for item in self.decision["repeatVisitReasons"]}
        self.assertEqual(repeat_days, {30, 90, 365})

    def test_schema_and_commercial_claims_are_fail_closed(self) -> None:
        self.assertIn('"@type":"Article"', self.article)
        self.assertIn('"@type":"FAQPage"', self.article)
        self.assertIn('"@type":"WebApplication"', self.tool)
        self.assertIn('"@type":"HowTo"', self.tool)
        for html in (self.article, self.tool):
            self.assertIsNone(
                re.search(
                    r'(?is)<a\b[^>]*\bhref\s*=\s*[\"\']https://(?:www\.)?amazon\.com\.tr[^>]*>',
                    html,
                )
            )
            for forbidden in (
                '"@type":"Product"',
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
