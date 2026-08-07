from __future__ import annotations

import tempfile
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DEPLOYMENT = ROOT / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build  # noqa: E402

HUB = ROOT / "kesintiye-hazirlik-atolyesi-v334" / "index.html"
ROBOTS = ROOT / "robots.txt"
COLD_GUIDE = ROOT / "haberler" / "elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir" / "index.html"
COLD_PLAN = ROOT / "hesaplama" / "buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani" / "index.html"
COLD_SELECTOR = ROOT / "amazon-elektrik-urunleri" / "buzdolabi-dondurucu-termometre-soguk-zincir-secimi" / "index.html"


class GrowthV334DiscoveryJourneyTest(unittest.TestCase):
    def test_robots_has_one_effective_sitemap(self):
        lines = [line.strip() for line in ROBOTS.read_text(encoding="utf-8").splitlines() if line.strip().lower().startswith("sitemap:")]
        self.assertEqual(["Sitemap: https://alo186.com/sitemap.xml"], lines)

    def test_hub_is_intent_first_and_has_no_direct_merchant(self):
        html = HUB.read_text(encoding="utf-8")
        for phrase in (
            "Sisteminiz yeterliyse yeni ürün almayın",
            "ALO186 resmî kurum değildir",
            "Arıza/ihbar kaydı almaz",
            "Bu merkezde doğrudan Amazon veya başka mağaza bağlantısı yoktur",
            "30 gün",
            "90 gün",
            "365 gün",
        ):
            self.assertIn(phrase, html)
        self.assertNotIn("amazon.com.tr", html.lower())
        self.assertNotIn("amzn.to", html.lower())
        self.assertNotIn("localStorage.", html)
        self.assertNotIn("sessionStorage.", html)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("XMLHttpRequest", html)

    def test_existing_cold_chain_journey_is_reused_not_duplicated(self):
        guide = COLD_GUIDE.read_text(encoding="utf-8")
        plan = COLD_PLAN.read_text(encoding="utf-8")
        selector = COLD_SELECTOR.read_text(encoding="utf-8")
        hub = HUB.read_text(encoding="utf-8")
        self.assertIn("4 saat", guide)
        self.assertIn("48 saat", guide)
        self.assertIn("24 saat", guide)
        self.assertIn("yeni ürün almayın", guide.lower())
        self.assertIn("kişisel veri", plan.lower())
        self.assertIn("satış ortaklığı", selector.lower())
        self.assertIn("alo186rehber-21", selector)
        self.assertIn('rel="sponsored nofollow noopener"', selector)
        self.assertIn("/haberler/elektrik-kesilince-buzdolabi-derin-dondurucu-ne-kadar-dayanir/", hub)
        self.assertIn("/hesaplama/buzdolabi-dondurucu-elektrik-kesintisi-gida-guvenligi-plani/", hub)
        self.assertIn("/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometre-soguk-zincir-secimi/", hub)

    def test_production_build_contains_hub_and_canonical_sitemap(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            release = build(REPO, out, "v334-test")
            hub = out / "kesintiye-hazirlik-atolyesi" / "index.html"
            self.assertTrue(hub.is_file())
            html = hub.read_text(encoding="utf-8")
            self.assertIn('href="https://alo186.com/kesintiye-hazirlik-atolyesi/"', html)
            self.assertNotIn("https://www.alo186.com", html)
            sitemap = (out / "sitemap.xml").read_text(encoding="utf-8")
            self.assertIn("https://alo186.com/kesintiye-hazirlik-atolyesi/", sitemap)
            robots = (out / "robots.txt").read_text(encoding="utf-8")
            self.assertEqual(1, sum(1 for line in robots.splitlines() if line.strip().lower().startswith("sitemap:")))
            self.assertGreaterEqual(int(release.get("routingVersion", 0)), 334)


if __name__ == "__main__":
    unittest.main()
