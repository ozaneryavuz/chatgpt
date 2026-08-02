from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

DEPLOYMENT = Path(__file__).resolve().parents[1] / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

import audit_live_origin_v225 as audit  # noqa: E402


HEALTHY_HTML = """<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="ALO186 bağımsız teknik bilgi sayfası.">
<meta name="robots" content="index,follow,max-image-preview:large">
<title>ALO186 teknik kalite</title>
<link rel="canonical" href="{canonical}">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"ALO186"}}</script>
</head><body>
<a class="skip-link" href="#main">İçeriğe geç</a>
<main id="main"><h1>ALO186 teknik kalite</h1><p>Bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir.</p></main>
</body></html>"""


class LiveOriginQualityTests(unittest.TestCase):
    def result(self, url: str, *, status: int = 200, body: str = "", headers: dict[str, str] | None = None, final_url: str | None = None, redirects=None):
        return audit.FetchResult(
            requested_url=url,
            final_url=final_url or url,
            status=status,
            headers=headers or {"content-type": "text/html; charset=utf-8"},
            body=body.encode("utf-8"),
            elapsed_ms=10,
            redirects=list(redirects or []),
        )

    def healthy_fetcher(self, url: str, timeout: float = 20.0, max_bytes: int = 5_000_000, follow_redirects: bool = True):
        del timeout, max_bytes
        parsed = audit.urllib.parse.urlsplit(url)
        clean_url = audit.urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        if clean_url == "https://www.alo186.com/" and not follow_redirects:
            return self.result(clean_url, status=308, headers={"location": "https://alo186.com/", "content-type": "text/html"})
        if clean_url.endswith("/pages-release.json"):
            return self.result(clean_url, status=404, headers={"content-type": "application/json"})
        if clean_url.endswith("/robots.txt"):
            return self.result(clean_url, body="User-agent: *\nAllow: /\nSitemap: https://alo186.com/sitemap.xml\n", headers={"content-type": "text/plain"})
        if clean_url.endswith("/sitemap.xml"):
            urls = ["https://alo186.com/", *(f"https://alo186.com{route}" for route in audit.CRITICAL_ROUTES if route != "/")]
            body = '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>"
            return self.result(clean_url, body=body, headers={"content-type": "application/xml"})
        route = parsed.path or "/"
        canonical = "https://alo186.com/" if route == "/" else f"https://alo186.com{route}"
        return self.result(clean_url, body=HEALTHY_HTML.format(canonical=canonical), headers={"content-type": "text/html; charset=utf-8"})

    def test_healthy_live_origin_contract(self):
        with mock.patch.object(audit, "fetch", side_effect=self.healthy_fetcher):
            report = audit.run(
                origin="https://alo186.com",
                expected_commit="",
                timeout=1,
                workers=2,
                max_sitemap_urls=50,
                mobile_lighthouse=None,
                desktop_lighthouse=None,
            )
        self.assertTrue(report.ok)
        self.assertEqual(report.successful_critical_routes, len(audit.CRITICAL_ROUTES))
        self.assertEqual(report.sitemap_url_count, len(audit.CRITICAL_ROUTES))
        self.assertEqual(report.internal_broken_count, 0)
        self.assertFalse(any(issue.severity in {"P0", "P1"} for issue in report.issues))

    def test_sitemap_noindex_is_p1(self):
        def noindex_fetcher(url: str, timeout: float = 20.0, max_bytes: int = 5_000_000, follow_redirects: bool = True):
            result = self.healthy_fetcher(url, timeout, max_bytes, follow_redirects)
            if audit.urllib.parse.urlsplit(url).path == "/arama/":
                result.body = HEALTHY_HTML.format(canonical="https://alo186.com/arama/").replace("index,follow", "noindex,follow").encode("utf-8")
            return result

        with mock.patch.object(audit, "fetch", side_effect=noindex_fetcher):
            report = audit.run(
                origin="https://alo186.com",
                expected_commit="",
                timeout=1,
                workers=2,
                max_sitemap_urls=50,
                mobile_lighthouse=None,
                desktop_lighthouse=None,
            )
        self.assertFalse(report.ok)
        self.assertTrue(any(issue.code in {"critical_noindex", "sitemap_noindex"} and issue.severity == "P1" for issue in report.issues))

    def test_www_redirect_must_be_permanent_and_apex(self):
        report = audit.Report(version=225, checked_at=audit.utc_now(), origin="https://alo186.com", expected_commit="")
        with mock.patch.object(audit, "fetch", return_value=self.result("https://www.alo186.com/", status=302, headers={"location": "https://alo186.com/"})):
            audit.audit_www_redirect(report, 1)
        self.assertTrue(any(issue.code == "www_redirect_not_permanent" for issue in report.issues))

    def test_lighthouse_thresholds_and_lab_field_separation(self):
        payload = {
            "finalDisplayedUrl": "https://alo186.com/",
            "categories": {
                "performance": {"score": 0.93},
                "accessibility": {"score": 1.0},
                "best-practices": {"score": 0.96},
                "seo": {"score": 1.0},
            },
            "audits": {
                "largest-contentful-paint": {"numericValue": 2100},
                "cumulative-layout-shift": {"numericValue": 0.02},
                "total-blocking-time": {"numericValue": 120},
                "speed-index": {"numericValue": 2200},
                "total-byte-weight": {"numericValue": 430000},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "desktop.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            report = audit.Report(version=225, checked_at=audit.utc_now(), origin="https://alo186.com", expected_commit="")
            audit.audit_lighthouse(report, None, path)
        self.assertEqual(len(report.lighthouse), 1)
        self.assertFalse(report.field_core_web_vitals_available)
        self.assertFalse(any(issue.severity in {"P0", "P1"} for issue in report.issues))

    def test_brittle_count_is_warning_not_publication_failure(self):
        page = HEALTHY_HTML.format(canonical="https://alo186.com/").replace("</main>", "<p>152 modeli doğrulanmış ürün için seçim kartları</p></main>")
        report = audit.Report(version=225, checked_at=audit.utc_now(), origin="https://alo186.com", expected_commit="")
        response = self.result("https://alo186.com/", body=page)
        parsed = audit.audit_page(report, "https://alo186.com", "/", response)
        self.assertIsNotNone(parsed)
        self.assertTrue(any(issue.code == "brittle_visible_count" and issue.severity == "P2" for issue in report.issues))


if __name__ == "__main__":
    unittest.main()
