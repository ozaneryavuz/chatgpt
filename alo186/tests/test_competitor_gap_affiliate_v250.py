#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "alo186/deployment/build_static_site.py"
SMOKE = ROOT / "alo186/deployment/smoke_static_site.py"
SCHEMA_MARKER = 'data-alo186-competitor-gap-schema-v250="true"'
SSR_MARKER = 'data-alo186-affiliate-ssr-v250="true"'
SMART_MARKER = 'data-alo186-smart-affiliate-v250="true"'
GATE_MARKER = 'data-alo186-affiliate-gate-v250="true"'
AFFILIATE_TAG = "alo186rehber-21"
FORBIDDEN_SCHEMA_KEYS = {
    "offer", "offers", "aggregaterating", "review", "reviews", "price",
    "pricecurrency", "availability", "seller", "shippingdetails",
    "hasmerchantreturnpolicy",
}
REQUIRED_CRAWLERS = (
    "OAI-SearchBot", "GPTBot", "PerplexityBot", "ClaudeBot",
    "Bytespider", "Google-Extended",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    parser.add_argument("--bundle", type=Path)
    return parser.parse_args()


def plain_html(source: str) -> str:
    source = re.sub(
        r"<(?:script|style|noscript)\b[^>]*>.*?</(?:script|style|noscript)\s*>",
        " ", source, flags=re.I | re.S,
    )
    source = re.sub(r"<[^>]+>", " ", source, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(source)).strip()


def marked_jsonld(source: str) -> list[dict[str, Any]]:
    blocks = re.findall(
        r'<script\b(?=[^>]*type=["\']application/ld\+json["\'])'
        r'(?=[^>]*data-alo186-competitor-gap-schema-v250=["\']true["\'])'
        r'[^>]*>(.*?)</script\s*>',
        source,
        flags=re.I | re.S,
    )
    assert blocks, "v250 işaretli JSON-LD bloğu bulunamadı"
    return [json.loads(block) for block in blocks]


def node_types(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        node_type = value.get("@type")
        if isinstance(node_type, str):
            found.append(node_type)
        elif isinstance(node_type, list):
            found.extend(str(item) for item in node_type)
        for child in value.values():
            found.extend(node_types(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(node_types(child))
    return found


def forbidden_keys(value: Any) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_SCHEMA_KEYS:
                result.add(str(key))
            result.update(forbidden_keys(child))
    elif isinstance(value, list):
        for child in value:
            result.update(forbidden_keys(child))
    return result


def assert_rel(source: str, anchor_id: str) -> None:
    anchor = re.search(
        rf'<a\b(?=[^>]*\bid=["\']{re.escape(anchor_id)}["\'])([^>]*)>',
        source,
        flags=re.I | re.S,
    )
    assert anchor, anchor_id
    attributes = anchor.group(1)
    rel = re.search(r'\brel=["\']([^"\']+)["\']', attributes, flags=re.I)
    assert rel, (anchor_id, "rel eksik")
    rel_tokens = set(rel.group(1).casefold().split())
    assert {"sponsored", "nofollow", "noopener"}.issubset(rel_tokens), (
        anchor_id, rel_tokens,
    )
    href = re.search(r'\bhref=["\']([^"\']+)["\']', attributes, flags=re.I)
    assert href and href.group(1).startswith("https://www.amazon.com.tr/"), anchor_id
    assert f"tag={AFFILIATE_TAG}" in html.unescape(href.group(1)), anchor_id


def assert_location_page(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8", errors="strict")
    payloads = marked_jsonld(source)
    all_types = set(node_types(payloads))
    expected = {"Organization", "Service", "GovernmentService", "ItemList", "Question"}
    assert expected.issubset(all_types), (path, sorted(all_types))
    assert not forbidden_keys(payloads), (path, forbidden_keys(payloads))

    graphs = [
        node for payload in payloads
        for node in payload.get("@graph", [])
        if isinstance(node, dict)
    ]
    organizations = [node for node in graphs if node.get("@type") == "Organization"]
    government = [node for node in graphs if node.get("@type") == "GovernmentService"]
    services = [node for node in graphs if node.get("@type") == "Service"]
    assert len(organizations) == 1, (path, organizations)
    assert len(government) == 1 and "112" in json.dumps(government[0], ensure_ascii=False), path
    assert len(services) == 1 and "186" in json.dumps(services[0], ensure_ascii=False), path
    assert organizations[0].get("@type") != "GovernmentService", path
    return all_types


def validate_bundle(bundle: Path) -> dict[str, Any]:
    release = json.loads((bundle / "alo186-release.json").read_text(encoding="utf-8"))
    report = release["competitorGapAffiliateV250"]
    assert report["version"] == 250
    assert report["schemaContractValidation"]["status"] == "passed"
    assert report["schemaContractValidation"]["jsonLdParseErrors"] == 0
    assert report["schemaContractValidation"]["criticalContractErrors"] == 0

    cities = sorted((bundle / "il").glob("*/index.html"))
    edas_pages = sorted((bundle / "dagitim-sirketleri").glob("*/index.html"))
    assert len(cities) >= 81, len(cities)
    assert len(edas_pages) >= 21, len(edas_pages)
    assert report["cityAndEdasSchema"]["cityPages"] == len(cities)
    assert report["cityAndEdasSchema"]["edasPages"] == len(edas_pages)
    assert report["cityAndEdasSchema"]["privateEdasTypedAsGovernment"] is False

    location_types: set[str] = set()
    for path in cities + edas_pages:
        location_types.update(assert_location_page(path))

    selector = bundle / "amazon-elektrik-urunleri/kombi-yedek-enerji-urun-secici/index.html"
    guide = bundle / "hesaplama/kombi-elektrik-kesintisi-ups-guc-istasyonu-uygunlugu/index.html"
    assert selector.is_file() and guide.is_file()
    selector_source = selector.read_text(encoding="utf-8", errors="strict")
    guide_source = guide.read_text(encoding="utf-8", errors="strict")
    assert SSR_MARKER in selector_source
    assert GATE_MARKER in selector_source
    assert "Kesintide kombi nasıl korunur?" in plain_html(selector_source)
    assert "Amazon Gelir Ortağı açıklaması" in plain_html(selector_source)
    assert selector_source.count('data-affiliate-locked="true"') == 3
    for anchor_id in ("urun-ups-3000va", "urun-guc-istasyonu-eps", "urun-enerji-olcer"):
        assert_rel(selector_source, anchor_id)
    assert 'aria-disabled="true"' in selector_source
    assert 'tabindex="-1"' in selector_source
    assert "approved.checked" in selector_source
    assert "!existing.checked" in selector_source
    assert "!hazard.checked" in selector_source
    assert "gates.every" in selector_source

    for path, source in ((selector, selector_source), (guide, guide_source)):
        payloads = marked_jsonld(source)
        all_types = set(node_types(payloads))
        assert {"Question", "HowTo", "HowToStep", "ItemList", "Product"}.issubset(all_types), (
            path, sorted(all_types),
        )
        assert node_types(payloads).count("Product") == 3, path
        assert not forbidden_keys(payloads), (path, forbidden_keys(payloads))
        serialized = json.dumps(payloads, ensure_ascii=False)
        assert "3000 VA sabit öneri değildir" in serialized, path
        assert "Mevcut model onaylı güvenli sistem ihtiyacı karşılıyorsa" in serialized, path

    smart_targets = {
        "haberler/ups-online-line-interactive-offline-farki/index.html": "urun-kesintisiz-guc-kaynagi",
        "haberler/parafudr-gerilim-koruma-rolesi-farki/index.html": "urun-asiri-gerilim-korumasi",
    }
    for relative, anchor_id in smart_targets.items():
        source = (bundle / relative).read_text(encoding="utf-8", errors="strict")
        assert SMART_MARKER in source, relative
        assert "Aktif tehlikede" in plain_html(source), relative
        assert_rel(source, anchor_id)

    robots = (bundle / "robots.txt").read_text(encoding="utf-8")
    for crawler in REQUIRED_CRAWLERS:
        assert re.search(
            rf"User-agent:\s*{re.escape(crawler)}\s*(?:\r?\n)+Allow:\s*/(?:\s|$)",
            robots,
            flags=re.I,
        ), crawler
    assert "Sitemap: https://alo186.com/sitemap.xml" in robots

    portal = next(
        path for path in (
            bundle / "elektrik-portali/index.html",
            bundle / "index.html",
        ) if path.is_file()
    )
    portal_visible = plain_html(portal.read_text(encoding="utf-8", errors="strict"))
    assert "ALO186 Akıllı Yol" in portal_visible
    assert "Kişisel hazırlık kontrolü" in portal_visible

    assert report["serverRenderedSource"]["smartPathVisibleWithoutJavaScript"] is True
    assert report["serverRenderedSource"]["personalPreparationVisibleWithoutJavaScript"] is True
    assert report["kombiHowToProductFusion"]["linksVisibleWithoutJavaScript"] is True
    assert report["kombiHowToProductFusion"]["linksClickableWithoutSafetyGate"] is False
    assert report["kombiHowToProductFusion"]["fixed3000VaRecommendation"] is False
    assert report["kombiHowToProductFusion"]["offerPublished"] is False
    assert report["kombiHowToProductFusion"]["aggregateRatingPublished"] is False

    return {
        "version": 250,
        "status": "passed",
        "bundle": str(bundle),
        "cityPagesValidated": len(cities),
        "edasPagesValidated": len(edas_pages),
        "locationSchemaTypes": sorted(location_types),
        "kombiSchemaTypes": ["Question", "HowTo", "HowToStep", "ItemList", "Product"],
        "serverRenderedAffiliateLinks": 3,
        "smartAffiliateGuideLinks": len(smart_targets),
        "explicitAiCrawlers": list(REQUIRED_CRAWLERS),
        "jsonLdParseErrors": 0,
        "criticalContractErrors": 0,
        "forbiddenCommercialSchemaFields": [],
        "richResultsCaveat": "Valid Schema.org markup does not guarantee a Google rich result; HowTo is not a current Google rich-result type and generic Product nodes intentionally omit Offer/price/stock/rating.",
    }


def main() -> None:
    args = parse_args()
    if args.bundle:
        args.bundle.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, str(BUILD), "--output", str(args.bundle), "--commit", "v250-test"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, str(SMOKE), "--bundle", str(args.bundle)],
            cwd=ROOT,
            check=True,
        )
        result = validate_bundle(args.bundle)
    else:
        with tempfile.TemporaryDirectory(prefix="alo186-v250-") as temp:
            bundle = Path(temp) / "site"
            subprocess.run(
                [sys.executable, str(BUILD), "--output", str(bundle), "--commit", "v250-test"],
                cwd=ROOT,
                check=True,
            )
            subprocess.run(
                [sys.executable, str(SMOKE), "--bundle", str(bundle)],
                cwd=ROOT,
                check=True,
            )
            result = validate_bundle(bundle)
            result["bundle"] = "temporary"

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
