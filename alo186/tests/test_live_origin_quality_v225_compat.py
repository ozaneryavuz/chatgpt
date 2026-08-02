from __future__ import annotations

import sys
import unittest
from pathlib import Path

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import audit_live_origin_v225_compat as compat  # noqa: E402
import verify_live_origin as hosting  # noqa: E402


class HostingAwareRouteTests(unittest.TestCase):
    def test_chatgpt_sites_uses_published_sites_routes(self):
        routes = compat.routes_for_mode(hosting.SITES_MODE)
        self.assertEqual(routes, tuple(hosting.CRITICAL_SITES_ROUTES))
        self.assertIn("/karar-motoru", routes)
        self.assertIn("/dagitim-sirketleri", routes)
        self.assertNotIn("/edas-bul/", routes)

    def test_github_pages_and_unknown_use_pages_routes(self):
        self.assertEqual(compat.routes_for_mode(hosting.PAGES_MODE), compat.PAGES_ROUTES)
        self.assertEqual(compat.routes_for_mode(hosting.UNKNOWN_MODE), compat.PAGES_ROUTES)
        self.assertIn("/edas-bul/", compat.PAGES_ROUTES)
        self.assertIn("/urun-bilgi-grafigi/", compat.PAGES_ROUTES)


if __name__ == "__main__":
    unittest.main()
