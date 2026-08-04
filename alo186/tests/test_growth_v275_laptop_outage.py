from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesintisinde-laptop-nasil-sarj-edilir/index.html"
TOOL = ROOT / "alo186/hesaplama/laptop-elektrik-kesintisi-sarj-uygunluk-plani/index.html"
COMMERCE = ROOT / "alo186/amazon-elektrik-urunleri/laptop-usb-c-pd-powerbank-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v275-laptop-outage.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/laptop-outage-v275.json"


class GrowthV275LaptopOutageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.commerce = COMMERCE.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_routes_and_canonicals(self) -> None:
        self.assertEqual(self.overlay["version"], 275)
        routes = {item["canonicalPath"]: item for item in self.overlay["routes"]}
        expected = {
            "/haberler/elektrik-kesintisinde-laptop-nasil-sarj-edilir/",
            "/hesaplama/laptop-elektrik-kesintisi-sarj-uygunluk-plani/",
            "/amazon-elektrik-urunleri/laptop-usb-c-pd-powerbank-secimi/",
        }
        self.assertEqual(set(routes), expected)
        for route in routes.values():
            self.assertTrue((ROOT / route["source"]).is_file())
        for html, path in (
            (self.article, "/haberler/elektrik-kesintisinde-laptop-nasil-sarj-edilir/"),
            (self.tool, "/hesaplama/laptop-elektrik-kesintisi-sarj-uygunluk-plani/"),
            (self.commerce, "/amazon-elektrik-urunleri/laptop-usb-c-pd-powerbank-secimi/"),
        ):
            self.assertIn(f'<link rel="canonical" href="https://alo186.com{path}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_is_test_first_and_source_grounded(self) -> None:
        required = (
            "Kesintide laptopu şarj etmek mümkündür",
            "USB-C görünümü tek başına",
            "Mevcut batarya hedef süreyi sağlıyorsa yeni ürün almayın",
            "Dell Support",
            "Apple Support",
            "FAA PackSafe",
            "4 Ağustos 2026",
            "Bağımsız bilgilendirme platformudur",
            "112",
        )
        for text in required:
            self.assertIn(text, self.article)
        self.assertLess(
            self.article.index("Acil sınır: şarj etmeyin"),
            self.article.index("Yalnız gerçek eksikte ürün sınıfı"),
        )
        for claim in ("kesin bir kez tam şarj", "kesin 8 saat", "garantili çalışma süresi"):
            self.assertNotIn(claim, self.article)

    def test_tool_is_private_and_no_buy_first(self) -> None:
        required = (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli görünüyor — yeni ürün almayın",
            "Önce gerçek test yapın; ürün kararı vermeyin",
            "Profesyonel sistem: tüketici affiliate yolu kapalı",
            "Ham enerji ihtiyacı",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "no_buy_selected",
            "window.alo186AnalyticsConsent === true",
        )
        for text in required:
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        for forbidden_call in (
            "fetch(",
            "XMLHttpRequest",
            "localStorage.",
            "sessionStorage.",
            "document.cookie",
        ):
            self.assertNotIn(forbidden_call, self.tool)
        self.assertNotRegex(
            self.tool,
            r'(?i)<input[^>]+(?:name|id)=["\'](?:email|phone|address|serial|tc|tesisat|abonelik)',
        )

    def test_commerce_is_locked_and_disclosed(self) -> None:
        self.assertIn("Amazon Türkiye satış ortaklığı", self.commerce)
        self.assertIn(
            "Mevcut çözümüm gerçek testte hedef süreyi sağlıyor — yeni ürün almayacağım",
            self.commerce,
        )
        self.assertIn('aria-disabled="true"', self.commerce)
        self.assertIn('rel="sponsored nofollow noopener"', self.commerce)
        self.assertIn("alo186rehber-21", self.commerce)
        self.assertIn("affiliate_unlocked", self.commerce)
        self.assertIn("affiliate_clicked", self.commerce)
        self.assertIn(
            "USB-C Power Delivery üzerinden şarj kabul ettiği üretici kılavuzunda doğrulandı",
            self.commerce,
        )
        self.assertNotRegex(
            self.commerce,
            r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr[^>]*>',
        )
        self.assertLess(
            self.commerce.index("Satış ortaklığı açıklaması"),
            self.commerce.index("Mağaza bağlantısı güven kapısı"),
        )

    def test_decision_is_fail_closed(self) -> None:
        self.assertEqual(self.decision["version"], 275)
        self.assertEqual(self.decision["decision"], "conditional-consumer-affiliate")
        policy = self.decision["conversionPolicy"]
        self.assertTrue(policy["linksLockedByDefault"])
        self.assertTrue(policy["disclosureBeforeLinkRequired"])
        self.assertTrue(policy["noBuyOutcomeRequired"])
        self.assertTrue(policy["activeHazardCommerceClosed"])
        self.assertTrue(policy["personalDataCollectionForbidden"])
        self.assertTrue(policy["noPriceStockRatingWarrantyClaims"])
        self.assertEqual({item["days"] for item in self.decision["repeatVisitReasons"]}, {30, 90})
        excluded = set(self.decision["excludedConsumerAffiliateClasses"])
        self.assertIn("model-independent DC barrel trigger cable", excluded)
        self.assertIn("critical medical or business continuity power source", excluded)

    def test_schema_and_unverified_commercial_fields_are_forbidden(self) -> None:
        self.assertIn('"@type":"Article"', self.article)
        self.assertIn('"@type":"WebApplication"', self.tool)
        self.assertIn('"@type":"HowTo"', self.tool)
        self.assertIn('"@type":"ItemList"', self.commerce)
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
