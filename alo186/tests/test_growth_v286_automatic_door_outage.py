from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-otomatik-kapi-acilir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/otomatik-kapi-elektrik-kesintisi-cikis-plani/index.html"
PROFESSIONAL = ROOT / "alo186/sektor-rehberi/otomatik-kapi-erisim-kontrolu-kesinti-surekliligi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v286-automatic-door-outage.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/automatic-door-access-control-outage-v286.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


class AutomaticDoorOutageV286Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.professional = PROFESSIONAL.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_routes_and_canonicals(self) -> None:
        expected = {
            "/haberler/elektrik-kesilince-otomatik-kapi-acilir-mi/",
            "/hesaplama/otomatik-kapi-elektrik-kesintisi-cikis-plani/",
            "/sektor-rehberi/otomatik-kapi-erisim-kontrolu-kesinti-surekliligi/",
        }
        self.assertEqual(self.overlay["version"], 286)
        self.assertEqual({item["canonicalPath"] for item in self.overlay["routes"]}, expected)
        for html, path in (
            (self.article, "/haberler/elektrik-kesilince-otomatik-kapi-acilir-mi/"),
            (self.tool, "/hesaplama/otomatik-kapi-elektrik-kesintisi-cikis-plani/"),
            (self.professional, "/sektor-rehberi/otomatik-kapi-erisim-kontrolu-kesinti-surekliligi/"),
        ):
            self.assertIn(f'<link rel="canonical" href="https://alo186.com{path}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_is_conservative_and_source_grounded(self) -> None:
        for text in (
            "Fail-safe",
            "Fail-secure",
            "Kapıyı, kanadı, motoru ya da kilidi zorlamayın",
            "tüketici affiliate kapsamına alınmamıştır",
            "CIBSE",
            "Allegion",
            "Buckinghamshire Fire & Rescue",
            "5 Ağustos 2026",
            "ALO186 EDAŞ, itfaiye, kapı üreticisi veya kamu kurumu değildir",
        ):
            self.assertIn(text, self.article)
        self.assertLess(self.article.index("İnsan içeride kaldıysa"), self.article.index("Satın alma neden ilk adım değil?"))

    def test_tool_is_private_no_buy_and_professional_first(self) -> None:
        for text in (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli — yeni ürün almayın",
            "Professional-only kapsam",
            "Amazon veya başka mağaza bağlantısı yoktur",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "365",
        ):
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        self.assertNotRegex(self.tool, r'(?i)<input[^>]+(?:name|id)=["\'](?:email|phone|address|serial|tc|tesisat|abonelik)')
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie"):
            self.assertNotIn(forbidden, self.tool)

    def test_professional_route_has_no_consumer_commerce(self) -> None:
        for text in (
            "Bu sayfa ürün satışı yapmaz",
            "tüketici tipi UPS",
            "Affiliate ve resmî kurum açıklaması",
            "Amazon veya başka mağaza bağlantısı kullanılmaz",
            "Beklenen gelir modeli tüketici ürünü komisyonu değil",
        ):
            self.assertIn(text, self.professional)
        self.assertNotRegex(self.professional, r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr[^>]*>')

    def test_professional_only_governance(self) -> None:
        self.assertEqual(self.decision["decision"], "professional-lead-only")
        self.assertFalse(self.decision["consumerAffiliateDecision"]["allowed"])
        self.assertFalse(self.decision["conversionPolicy"]["merchantLinks"])
        self.assertTrue(self.decision["conversionPolicy"]["professionalScopeOnly"])
        self.assertTrue(self.decision["conversionPolicy"]["activeHazardCommerceClosed"])
        self.assertTrue(self.decision["conversionPolicy"]["noBuyOutcomeRequired"])
        self.assertEqual({item["days"] for item in self.decision["repeatVisitReasons"]}, {30, 90, 365})
        for pattern in ("otomatik-kapi", "erisim-kontrolu", "manyetik-kilit", "elektrikli-karsilik", "kartli-gecis"):
            self.assertIn(pattern, self.policy["professionalLeadOnlyRoutePatterns"])

    def test_no_unverified_commerce_or_product_schema(self) -> None:
        for html in (self.article, self.tool, self.professional):
            for forbidden in (
                '"@type":"Offer"', '"@type":"AggregateRating"', '"@type":"Review"',
                '"@type":"Product"', '"price":', '"priceCurrency":', '"availability":',
                '"aggregateRating":', '"warranty":',
            ):
                self.assertNotIn(forbidden, html)
            self.assertNotRegex(html, r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr')


if __name__ == "__main__":
    unittest.main()
