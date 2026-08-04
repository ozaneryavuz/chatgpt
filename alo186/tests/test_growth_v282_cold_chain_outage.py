from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/index.html"
TOOL = ROOT / "alo186/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/index.html"
AFFILIATE = ROOT / "alo186/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v282-cold-chain-outage.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/cold-chain-outage-v282.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


class ColdChainOutageV282Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.affiliate = AFFILIATE.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_routes_and_canonicals(self) -> None:
        expected = {
            "/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/",
            "/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/",
            "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/",
        }
        self.assertEqual(self.overlay["version"], 282)
        self.assertEqual({item["canonicalPath"] for item in self.overlay["routes"]}, expected)
        for html, path in (
            (self.article, "/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/"),
            (self.tool, "/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/"),
            (self.affiliate, "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/"),
        ):
            self.assertIn(f'<link rel="canonical" href="https://alo186.com{path}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_is_source_grounded_and_conservative(self) -> None:
        for text in (
            "4, 24 ve 48 saat yalnız planlama sınırlarıdır",
            "Şüpheli gıdayı tatmayın",
            "buz kristali",
            "USDA FSIS",
            "U.S. FDA",
            "T.C. Tarım ve Orman Bakanlığı",
            "4 Ağustos 2026",
            "ALO186 EDAŞ, Tarım ve Orman Bakanlığı",
            "Mevcut çözüm yeterliyse yeni ürün almayın",
        ):
            self.assertIn(text, self.article)
        self.assertLess(self.article.index("Acil ve güvenlik sınırı"), self.article.index("Gelecek kesintiye hazırlık"))
        self.assertNotIn("amazon.com.tr", self.article.lower())

    def test_tool_is_private_no_buy_and_not_a_safety_guarantee(self) -> None:
        for text in (
            "mağaza bağlantısı yok",
            "Mevcut hazırlık yeterli — yeni ürün almayın",
            "4, 24 ve 48 saatlik resmî planlama bilgilerini",
            "Şüpheli gıdayı tatmayın",
            "Genel ev tipi süreleri kullanmayın",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "180",
        ):
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        self.assertNotRegex(self.tool, r'(?i)<input[^>]+(?:name|id)=["\'](?:email|phone|address|serial|tc|tesisat|abonelik)')
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie"):
            self.assertNotIn(forbidden, self.tool)

    def test_affiliate_is_locked_disclosed_and_no_buy_first(self) -> None:
        for text in (
            "Amazon Türkiye satış ortaklığı",
            "bağlantılar başlangıçta kilitlidir",
            "Çalışan buzdolabı/dondurucu termometrem",
            "Mevcut hazırlık yeterli — mağaza bağlantıları kapalı tutuldu",
            "4, 24 ve 48 saat bilgilerinin kesin garanti olmadığını",
            "alo186rehber-21",
            'rel="sponsored nofollow noopener"',
            "İlaç, tıbbi ürün, bebek besini",
        ):
            self.assertIn(text, self.affiliate)
        self.assertLess(self.affiliate.index("Satış ortaklığı açıklaması"), self.affiliate.index("Mağaza bağlantısı güven kapısı"))
        self.assertNotRegex(self.affiliate, r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr[^>]*>')

    def test_conditional_affiliate_governance(self) -> None:
        self.assertEqual(self.decision["decision"], "conditional-consumer-affiliate")
        self.assertEqual(self.decision["conversionPolicy"]["merchant"], "Amazon Türkiye")
        self.assertTrue(self.decision["conversionPolicy"]["linksLockedByDefault"])
        self.assertTrue(self.decision["conversionPolicy"]["activeOutageUrgencyCommerceClosed"])
        self.assertTrue(self.decision["conversionPolicy"]["noBuyOutcomeRequired"])
        self.assertTrue(self.decision["conversionPolicy"]["noPriceStockRatingWarrantyClaims"])
        self.assertEqual({item["days"] for item in self.decision["repeatVisitReasons"]}, {30, 90, 180})
        self.assertIn(
            "buzdolabi-dondurucu-termometre-soguk-zincir",
            self.policy["governedAffiliateRoutePatterns"],
        )

    def test_no_unverified_commerce_fields(self) -> None:
        for html in (self.article, self.tool, self.affiliate):
            for forbidden in (
                '"@type":"Offer"', '"@type":"AggregateRating"', '"@type":"Review"',
                '"price":', '"priceCurrency":', '"availability":', '"aggregateRating":',
                '"warranty":',
            ):
                self.assertNotIn(forbidden, html)
        for html in (self.article, self.tool):
            self.assertNotIn('"@type":"Product"', html)


if __name__ == "__main__":
    unittest.main()
