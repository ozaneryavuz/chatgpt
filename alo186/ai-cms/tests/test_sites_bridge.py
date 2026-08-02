from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "sites_bridge.py"
SPEC = importlib.util.spec_from_file_location("sites_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


def policy() -> dict:
    return {
        "canonicalHost": "https://alo186.com",
        "minimumQualityScore": 85,
        "forbiddenPublicSchemaTypes": ["Person", "ProfilePage", "Product", "Offer"],
        "requiredPublicDisclosures": [
            "ALO186 bağımsız bilgilendirme platformudur",
            "AI destekli taslak insan editör onayıyla yayımlanmıştır",
        ],
    }


def record(slug: str = "ornek-insan-onayli-icerik") -> dict:
    return {
        "schemaVersion": 1,
        "id": "cms_0123456789abcdef",
        "slug": slug,
        "state": "published",
        "title": "İnsan Onaylı Örnek İçerik Başlığı",
        "h1": "İnsan onaylı örnek içerik nasıl değerlendirilir?",
        "description": "Bu örnek açıklama, ChatGPT Sites köprüsünün metadata ve insan onayı sözleşmesini güvenli biçimde test etmek için yeterli uzunluktadır.",
        "editorial": {
            "humanReviewRequired": True,
            "approvedBy": "ozaneryavuz",
            "approvedAt": "2026-08-02T20:00:00Z",
            "publishedAt": "2026-08-02T20:05:00Z",
            "approvalPr": 999,
        },
        "seo": {
            "canonicalPath": f"/haberler/{slug}",
            "robots": "index,follow,max-image-preview:large",
        },
        "quality": {
            "score": 92,
            "minimumRequired": 85,
            "checks": {"sources": True},
        },
    }


def canonical_html(value: dict, extra_type: str | None = None) -> str:
    types = ["Article", "FAQPage", "BreadcrumbList"]
    if extra_type:
        types.append(extra_type)
    canonical = "https://alo186.com" + value["seo"]["canonicalPath"]
    return f'''<!doctype html><html lang="tr"><head><title>{value["title"]}</title><meta name="description" content="{value["description"]}"><link rel="canonical" href="{canonical}"><script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":types})}</script></head><body data-ai-cms-id="{value["id"]}"><h1>{value["h1"]}</h1><p>ALO186 bağımsız bilgilendirme platformudur</p><p>AI destekli taslak insan editör onayıyla yayımlanmıştır</p></body></html>'''


class SitesBridgeTests(unittest.TestCase):
    def test_valid_published_record_builds_preview_only_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            slug = "ornek-insan-onayli-icerik"
            value = record(slug)
            (root / "alo186/ai-cms/content").mkdir(parents=True)
            (root / "alo186/haberler" / slug).mkdir(parents=True)
            (root / "alo186/ai-cms/policy.json").write_text(json.dumps(policy()), encoding="utf-8")
            (root / "alo186/ai-cms/content" / f"{slug}.json").write_text(json.dumps(value), encoding="utf-8")
            (root / "alo186/haberler" / slug / "index.html").write_text(canonical_html(value), encoding="utf-8")
            package, _, _ = bridge.build_package(repo=root, slug=slug, source_commit="abcdef1", generated_at="2026-08-02T20:10:00Z")
            self.assertFalse(package["operation"]["publish"])
            self.assertFalse(package["reviewPolicy"]["automaticDeployAllowed"])
            self.assertTrue(package["reviewPolicy"]["humanPreviewRequired"])
            self.assertEqual(package["siteSlug"], "alo186")
            self.assertEqual(package["operation"]["canonicalUrl"], f"https://alo186.com/haberler/{slug}")

    def test_review_state_is_rejected(self) -> None:
        value = record()
        value["state"] = "review"
        with self.assertRaisesRegex(bridge.BridgeError, "yalnız published"):
            bridge.validate_published_record(record=value, canonical_html=canonical_html(value), policy=policy(), slug=value["slug"])

    def test_forbidden_schema_type_is_rejected_recursively(self) -> None:
        value = record()
        with self.assertRaisesRegex(bridge.BridgeError, "yasak schema tipi: Offer"):
            bridge.validate_published_record(record=value, canonical_html=canonical_html(value, "Offer"), policy=policy(), slug=value["slug"])

    def test_invalid_deployment_url_receipt_is_rejected(self) -> None:
        package = {
            "siteSlug": "alo186",
            "target": "chatgpt-sites",
            "sourceCommit": "abcdef1",
            "packageHash": "a" * 64,
            "operation": {
                "contentId": "cms_0123456789abcdef",
                "contentRecordSha256": "b" * 64,
                "canonicalHtmlSha256": "c" * 64,
                "canonicalUrl": "https://alo186.com/haberler/ornek-insan-onayli-icerik",
            },
        }
        receipt = {
            "schemaVersion": 1,
            "siteSlug": "alo186",
            "target": "chatgpt-sites",
            "sourceCommit": "abcdef1",
            "packageHash": "a" * 64,
            "contentId": "cms_0123456789abcdef",
            "contentRecordSha256": "b" * 64,
            "canonicalHtmlSha256": "c" * 64,
            "canonicalUrl": "https://alo186.com/haberler/ornek-insan-onayli-icerik",
            "deploymentUrl": "not a url",
            "publishedAt": "2026-08-02T20:20:00Z",
            "liveVerified": True,
            "verification": {
                "httpStatus": 200,
                "canonicalMatched": True,
                "titleMatched": True,
                "h1Matched": True,
                "structuredDataPresent": True,
                "platformConfirmed": True,
            },
        }
        with self.assertRaisesRegex(bridge.BridgeError, "deploymentUrl"):
            bridge.validate_receipt(receipt, package)

    def test_valid_receipt_is_accepted(self) -> None:
        package = {
            "siteSlug": "alo186",
            "target": "chatgpt-sites",
            "sourceCommit": "abcdef1",
            "packageHash": "a" * 64,
            "operation": {
                "contentId": "cms_0123456789abcdef",
                "contentRecordSha256": "b" * 64,
                "canonicalHtmlSha256": "c" * 64,
                "canonicalUrl": "https://alo186.com/haberler/ornek-insan-onayli-icerik",
            },
        }
        receipt = {
            "schemaVersion": 1,
            "siteSlug": "alo186",
            "target": "chatgpt-sites",
            "sourceCommit": "abcdef1",
            "packageHash": "a" * 64,
            "contentId": "cms_0123456789abcdef",
            "contentRecordSha256": "b" * 64,
            "canonicalHtmlSha256": "c" * 64,
            "canonicalUrl": "https://alo186.com/haberler/ornek-insan-onayli-icerik",
            "deploymentUrl": "https://alo186.com/haberler/ornek-insan-onayli-icerik",
            "publishedAt": "2026-08-02T20:20:00Z",
            "liveVerified": True,
            "verification": {
                "httpStatus": 200,
                "canonicalMatched": True,
                "titleMatched": True,
                "h1Matched": True,
                "structuredDataPresent": True,
                "platformConfirmed": True,
            },
        }
        bridge.validate_receipt(receipt, package)


if __name__ == "__main__":
    unittest.main()
