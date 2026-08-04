from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesintisinde-telefon-nasil-sarj-edilir/index.html"
TOOL = ROOT / "alo186/hesaplama/telefon-elektrik-kesintisi-sarj-plani/index.html"
COMMERCE = ROOT / "alo186/amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v279-phone-outage.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/phone-outage-v279.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


class PhoneOutageV279Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.commerce = COMMERCE.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_routes_and_canonicals(self) -> None:
        expected = {
            "/haberler/elektrik-kesintisinde-telefon-nasil-sarj-edilir/",
            "/hesaplama/telefon-elektrik-kesintisi-sarj-plani/",
            "/amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/",
        }
        self.assertEqual(self.overlay["version"], 279)
        self.assertEqual({item["canonicalPath"] for item in self.overlay["routes"]}, expected)
        for html, path in (
            (self.article, "/haberler/elektrik-kesintisinde-telefon-nasil-sarj-edilir/"),
            (self.tool, "/hesaplama/telefon-elektrik-kesintisi-sarj-plani/"),
            (self.commerce, "/amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/"),
        ):
            self.assertIn(f'<link rel="canonical" href="https://alo186.com{path}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_is_save_first_and_source_grounded(self) -> None:
        for text in (
            "yeni powerbank almak ilk adım değildir",
            "Mevcut telefon pili hedef süreyi karşılıyorsa yeni ürün almayın",
            "Apple Support",
            "Google Pixel Help",
            "FAA PackSafe",
            "4 Ağustos 2026",
            "112",
            "ALO186 EDAŞ, kamu kurumu",
        ):
            self.assertIn(text, self.article)
        self.assertLess(self.article.index("Acil sınır: şarj etmeyin"), self.article.index("Güvenlik kapılı seçiciyi aç"))

    def test_tool_is_private_test_first_and_no_store(self) -> None:
        for text in (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli — yeni ürün almayın",
            "Önce mevcut powerbanki gerçek kullanımda test edin",
            "Tek kritik iletişim kanalı: tüketici affiliate yolu kapalı",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
        ):
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie"):
            self.assertNotIn(forbidden, self.tool)
        self.assertNotRegex(self.tool, r'(?i)<input[^>]+(?:name|id)=["\'](?:email|phone|address|serial|tc|tesisat|abonelik)')

    def test_commerce_starts_locked_and_discloses(self) -> None:
        self.assertIn("Amazon Türkiye satış ortaklığı", self.commerce)
        self.assertIn("Mevcut telefon pili veya güvenli powerbank gerçek testte hedef süreyi sağlıyor", self.commerce)
        self.assertEqual(self.commerce.count('aria-disabled="true"'), 2)
        self.assertEqual(self.commerce.count('rel="sponsored nofollow noopener"'), 2)
        self.assertIn("alo186rehber-21", self.commerce)
        self.assertNotRegex(self.commerce, r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr[^>]*>')
        self.assertLess(self.commerce.index("Satış ortaklığı açıklaması"), self.commerce.index("Mağaza bağlantısı güven kapısı"))

    def test_fail_closed_governance(self) -> None:
        self.assertEqual(self.decision["decision"], "conditional-consumer-affiliate")
        policy = self.decision["conversionPolicy"]
        self.assertTrue(policy["linksLockedByDefault"])
        self.assertTrue(policy["disclosureBeforeLinkRequired"])
        self.assertTrue(policy["noBuyOutcomeRequired"])
        self.assertTrue(policy["activeHazardCommerceClosed"])
        self.assertTrue(policy["personalDataCollectionForbidden"])
        self.assertTrue(policy["noPriceStockRatingWarrantyClaims"])
        self.assertEqual({item["days"] for item in self.decision["repeatVisitReasons"]}, {30, 90})
        self.assertIn("telefon-powerbank-kablo", self.policy["governedAffiliateRoutePatterns"])

    def test_no_unverified_commerce_schema(self) -> None:
        self.assertEqual(self.commerce.count('"@type":"Product"'), 2)
        for html in (self.article, self.tool, self.commerce):
            for forbidden in (
                '"@type":"Offer"', '"@type":"AggregateRating"', '"@type":"Review"',
                '"price":', '"priceCurrency":', '"availability":', '"aggregateRating":', '"warranty":',
            ):
                self.assertNotIn(forbidden, html)


if __name__ == "__main__":
    unittest.main()
