from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-elektrikli-arac-sarji-ne-olur/index.html"
TOOL = ROOT / "alo186/hesaplama/ev-sarj-istasyonu-elektrik-kesintisi-yeniden-baslatma-plani/index.html"
CALENDAR = ROOT / "alo186/hesaplama/planli-elektrik-kesintisi-takvim-hatirlatici/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v280-ev-outage-reminder.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/ev-charging-outage-v280.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


class EvOutageReminderV280Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.calendar = CALENDAR.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.policy = json.loads(POLICY.read_text(encoding="utf-8"))

    def test_routes_and_canonicals(self) -> None:
        expected = {
            "/haberler/elektrik-kesilince-elektrikli-arac-sarji-ne-olur/",
            "/hesaplama/ev-sarj-istasyonu-elektrik-kesintisi-yeniden-baslatma-plani/",
            "/hesaplama/planli-elektrik-kesintisi-takvim-hatirlatici/",
        }
        self.assertEqual(self.overlay["version"], 280)
        self.assertEqual({item["canonicalPath"] for item in self.overlay["routes"]}, expected)
        for html, path in (
            (self.article, "/haberler/elektrik-kesilince-elektrikli-arac-sarji-ne-olur/"),
            (self.tool, "/hesaplama/ev-sarj-istasyonu-elektrik-kesintisi-yeniden-baslatma-plani/"),
            (self.calendar, "/hesaplama/planli-elektrik-kesintisi-takvim-hatirlatici/"),
        ):
            self.assertIn(f'<link rel="canonical" href="https://alo186.com{path}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_is_model_specific_and_source_grounded(self) -> None:
        for text in (
            "davranış modele ve sisteme bağlıdır",
            "1–3 dakika",
            "Kabloyu zorlamayın",
            "Mevcut sistem üretici prosedürüne göre güvenli biçimde yeniden başlıyor",
            "EPDK Şarj@TR",
            "Tesla Energy Library",
            "Wallbox Help Center",
            "4 Ağustos 2026",
            "ALO186 EDAŞ, EPDK",
        ):
            self.assertIn(text, self.article)
        self.assertLess(self.article.index("Acil sınır: sistemi zorlamayın"), self.article.index("Kişisel verisiz yeniden başlatma planı"))
        self.assertNotIn("amazon.com.tr", self.article.lower())

    def test_restart_tool_is_private_no_buy_and_professional_only(self) -> None:
        for text in (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli — yeni ürün almayın",
            "Kabloyu zorlamayın",
            "Profesyonel süreklilik kapsamı gerekli",
            "Tüketici affiliate yolu kapalıdır",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "Yıllık profesyonel",
            "Teknik kapsam listesini indir",
        ):
            self.assertIn(text, self.tool)
        self.assertNotIn("amazon.com.tr", self.tool.lower())
        self.assertNotRegex(self.tool, r'(?i)<input[^>]+(?:name|id)=["\'](?:email|phone|address|serial|tc|tesisat|abonelik)')
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie"):
            self.assertNotIn(forbidden, self.tool)

    def test_calendar_is_local_official_recheck_and_repeat_visit(self) -> None:
        for text in (
            "canlı kesinti servisi değildir",
            "resmî EDAŞ duyurusunu yeniden kontrol",
            "TRIGGER:-PT1H",
            "TRIGGER;RELATED=END:PT30M",
            "BEGIN:VCALENDAR",
            "Bu sayfada affiliate veya mağaza bağlantısı yoktur",
            "ALO186 EDAŞ veya kamu kurumu değildir",
        ):
            self.assertIn(text, self.calendar)
        self.assertNotIn("amazon.com.tr", self.calendar.lower())
        self.assertNotRegex(self.calendar, r'(?i)<input[^>]+(?:name|id)=["\'](?:email|phone|address|serial|tc|tesisat|abonelik)')
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage.", "sessionStorage.", "document.cookie"):
            self.assertNotIn(forbidden, self.calendar)

    def test_fail_closed_governance(self) -> None:
        self.assertEqual(self.decision["decision"], "professional-only")
        self.assertEqual(self.decision["allowedConsumerAffiliateClasses"], [])
        policy = self.decision["conversionPolicy"]
        self.assertTrue(policy["directAffiliateLinksForbidden"])
        self.assertTrue(policy["noBuyOutcomeRequired"])
        self.assertTrue(policy["activeHazardCommerceClosed"])
        self.assertTrue(policy["personalDataCollectionForbidden"])
        self.assertTrue(policy["noPriceStockRatingWarrantyClaims"])
        self.assertTrue(policy["officialInstitutionImpressionForbidden"])
        self.assertTrue(policy["paidProfessionalServiceDisclosureRequired"])
        repeat_days = {item["days"] for item in self.decision["repeatVisitReasons"] if "days" in item}
        self.assertEqual(repeat_days, {30, 90, 365})
        professional = set(self.policy["professionalLeadOnlyRoutePatterns"])
        for pattern in (
            "elektrikli-arac-sarj-kesinti",
            "ev-sarj-istasyonu-kesinti",
            "wallbox-yedekleme",
            "evse-yedekleme",
            "sarj-istasyonu-surekliligi",
        ):
            self.assertIn(pattern, professional)

    def test_no_unverified_commerce_or_product_schema(self) -> None:
        for html in (self.article, self.tool, self.calendar):
            for forbidden in (
                '"@type":"Product"', '"@type":"Offer"', '"@type":"AggregateRating"',
                '"@type":"Review"', '"price":', '"priceCurrency":', '"availability":',
                '"aggregateRating":', '"warranty":',
            ):
                self.assertNotIn(forbidden, html)
            self.assertNotRegex(html, r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr[^>]*>')


if __name__ == "__main__":
    unittest.main()
