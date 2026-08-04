from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-pelet-sobasi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/pelet-sobasi-elektrik-kesintisi-guvenli-kapanma-plani/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v276-pellet-stove-outage.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/pellet-stove-outage-v276.json"
RISK_POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


class GrowthV276PelletStoveOutageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.article = ARTICLE.read_text(encoding="utf-8")
        cls.tool = TOOL.read_text(encoding="utf-8")
        cls.overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.risk_policy = json.loads(RISK_POLICY.read_text(encoding="utf-8"))

    def test_routes_and_canonicals(self) -> None:
        self.assertEqual(self.overlay["version"], 276)
        routes = {item["canonicalPath"]: item for item in self.overlay["routes"]}
        expected = {
            "/haberler/elektrik-kesilince-pelet-sobasi-calisir-mi/",
            "/hesaplama/pelet-sobasi-elektrik-kesintisi-guvenli-kapanma-plani/",
        }
        self.assertEqual(set(routes), expected)
        for route in routes.values():
            self.assertTrue((ROOT / route["source"]).is_file())
        for html, path in (
            (self.article, "/haberler/elektrik-kesilince-pelet-sobasi-calisir-mi/"),
            (self.tool, "/hesaplama/pelet-sobasi-elektrik-kesintisi-guvenli-kapanma-plani/"),
        ):
            self.assertIn(f'<link rel="canonical" href="https://alo186.com{path}">', html)
            self.assertNotIn("https://www.alo186.com", html)

    def test_article_closes_unsafe_generic_ups_path(self) -> None:
        required = (
            "Çoğu pelet sobası elektrik olmadan normal çalışmaz",
            "küçük bir UPS yeter",
            "model bağımsız genellemeler güvenli değildir",
            "Mevcut üretici onaylı yedekleme güvenli kapanmayı",
            "U.S. EPA",
            "ComfortBilt",
            "CDC",
            "4 Ağustos 2026",
            "Bağımsız bilgilendirme platformudur",
            "112",
        )
        for text in required:
            self.assertIn(text, self.article)
        self.assertLess(
            self.article.index("Acil sınır: ürün aramayın"),
            self.article.index("Kişisel verisiz güvenli kapanma planı"),
        )
        for unsafe_claim in (
            "her pelet sobası güvenle söner",
            "her küçük UPS uygundur",
            "kesin çalışma süresi",
            "garantili kapanma",
        ):
            self.assertNotIn(unsafe_claim, self.article)

    def test_tool_is_private_fail_closed_and_no_buy_capable(self) -> None:
        required = (
            "mağaza bağlantısı yok",
            "Mevcut sistem yeterli görünüyor — yeni ürün almayın",
            "Profesyonel sistem: tüketici affiliate yolu kapalı",
            "Genel UPS uyumluluk kanıtı değildir",
            "Ürün, UPS ve bakım akışı kapalıdır",
            "BEGIN:VCALENDAR",
            "30 günlük",
            "90 günlük",
            "365 günlük",
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
        self.assertIn(
            "/amazon-elektrik-urunleri/pilli-karbonmonoksit-alarmi-secimi/",
            self.tool,
        )

    def test_no_direct_or_unverified_commerce(self) -> None:
        for html in (self.article, self.tool):
            self.assertNotRegex(
                html,
                r'(?is)<a\b[^>]*\bhref\s*=\s*["\']https://(?:www\.)?amazon\.com\.tr[^>]*>',
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
        self.assertIn('"@type":"Article"', self.article)
        self.assertIn('"@type":"WebApplication"', self.tool)
        self.assertIn('"@type":"HowTo"', self.tool)

    def test_decision_is_professional_only_with_safe_existing_crosslink(self) -> None:
        self.assertEqual(self.decision["version"], 276)
        self.assertEqual(
            self.decision["decision"],
            "professional-only-with-existing-low-risk-safety-crosslink",
        )
        policy = self.decision["conversionPolicy"]
        self.assertFalse(policy["directAffiliateLinksAllowed"])
        self.assertTrue(policy["activeHazardCommerceClosed"])
        self.assertTrue(policy["manufacturerManualRequired"])
        self.assertTrue(policy["authorizedServiceOrProfessionalReviewRequiredForBackupPower"])
        self.assertTrue(policy["noBuyOutcomeRequired"])
        self.assertTrue(policy["personalDataCollectionForbidden"])
        self.assertTrue(policy["noPriceStockRatingWarrantyClaims"])
        self.assertEqual(
            {item["days"] for item in self.decision["repeatVisitReasons"]},
            {30, 90, 365},
        )
        paths = self.decision["permittedConversionPaths"]
        safe_affiliate = [item for item in paths if item["type"] == "existing-low-risk-affiliate-guide"]
        self.assertEqual(len(safe_affiliate), 1)
        self.assertEqual(
            safe_affiliate[0]["route"],
            "/amazon-elektrik-urunleri/pilli-karbonmonoksit-alarmi-secimi/",
        )
        excluded = set(self.decision["excludedConsumerAffiliateClasses"])
        self.assertIn("model-independent pellet stove UPS", excluded)
        self.assertIn("pellet stove inverter", excluded)
        self.assertIn("generator or building transfer system", excluded)

    def test_central_risk_policy_marks_pellet_backup_professional_only(self) -> None:
        patterns = set(self.risk_policy["professionalLeadOnlyRoutePatterns"])
        self.assertIn("pelet-sobasi", patterns)
        self.assertIn("pelet-kazani", patterns)
        self.assertTrue(self.risk_policy["trustRules"]["activeHazardCommerceClosed"])
        self.assertTrue(self.risk_policy["affiliateProgram"]["disclosureBeforeLinkRequired"])
        self.assertTrue(self.risk_policy["affiliateProgram"]["noBuyOutcomeRequired"])


if __name__ == "__main__":
    unittest.main()
