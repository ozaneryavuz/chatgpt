from __future__ import annotations

import json
import re
import sys
import tempfile
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import build, load_effective_manifest  # noqa: E402
from generate_commerce_guides import generate, load  # noqa: E402
from inject_private_search import run as inject_private_search  # noqa: E402


AMAZON_HOSTS = {"amazon.com.tr", "www.amazon.com.tr"}
REQUIRED_REL = {"sponsored", "nofollow", "noopener"}
CURRENCY_PATTERN = re.compile(r"\b\d[\d.,]*\s*(?:₺|TL|TRY)\b", re.I)
ANCHOR_PATTERN = re.compile(r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>", re.I | re.S)
ATTR_PATTERN = re.compile(
    r"(?P<name>[a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
    re.S,
)


def attrs(raw: str) -> dict[str, str]:
    return {
        match.group("name").casefold(): unescape(match.group("value"))
        for match in ATTR_PATTERN.finditer(raw)
    }


def amazon_anchors(html: str) -> list[dict[str, str]]:
    result = []
    for match in ANCHOR_PATTERN.finditer(html):
        parsed = attrs(match.group("attrs"))
        host = urlsplit(parsed.get("href", "")).hostname
        if host in AMAZON_HOSTS:
            result.append(parsed)
    return result


def jsonld_types(html: str) -> set[str]:
    types: set[str] = set()

    def visit(value) -> None:
        if isinstance(value, dict):
            raw = value.get("@type")
            if isinstance(raw, str):
                types.add(raw)
            elif isinstance(raw, list):
                types.update(str(item) for item in raw)
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    for block in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        visit(json.loads(block))
    return types


def test_config_has_eight_distinct_high_intent_guides() -> None:
    config = load(ROOT)
    guides = config["guides"]
    assert len(guides) == 8
    assert len({item["slug"] for item in guides}) == 8
    assert len({item["category"] for item in guides}) == 8
    assert len({item["title"] for item in guides}) == 8
    assert len({item["h1"] for item in guides}) == 8
    assert sum(bool(item["affiliateEnabled"]) for item in guides) == 7
    assert sum(not bool(item["affiliateEnabled"]) for item in guides) == 1
    professional = next(item for item in guides if not item["affiliateEnabled"])
    assert professional["slug"] == "ges-malzemeleri"
    assert professional["affiliatePolicy"] == "professional_only"
    assert professional["amazonSearchQuery"] is None


def test_generated_pages_are_substantive_unique_and_transparent() -> None:
    config = load(ROOT)
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        release = generate(ROOT, output)
        assert release["guideCount"] == 8
        assert release["affiliateEnabledCount"] == 7
        assert release["professionalOnlyCount"] == 1
        assert release["staticPricesStored"] is False
        assert release["staticStockStored"] is False

        hub = (output / "urun-rehberleri/index.html").read_text(encoding="utf-8")
        assert 'rel="canonical" href="https://www.alo186.com/urun-rehberleri/"' in hub
        assert "Ticari şeffaflık" in hub
        assert "Fiyat ve stok gösterilmez" in hub
        assert not amazon_anchors(hub)

        titles: set[str] = set()
        descriptions: set[str] = set()
        for item in config["guides"]:
            path = output / "urun-rehberleri" / item["slug"] / "index.html"
            assert path.is_file(), path
            text = path.read_text(encoding="utf-8")
            title = re.search(r"<title>(.*?)</title>", text, re.S).group(1)
            description = re.search(r'<meta name="description" content="([^"]+)"', text).group(1)
            assert title not in titles
            assert description not in descriptions
            titles.add(title)
            descriptions.add(description)
            assert len(description) >= 110
            assert f'rel="canonical" href="https://www.alo186.com/urun-rehberleri/{item["slug"]}"' in text
            assert text.count("<h1>") == 1
            assert len(re.findall(r"<h2>", text)) >= 7
            assert "Yeni ürün almamanız gereken durumlar" in text
            assert "Mevcut ürün" in text
            assert "Fiyat, stok" in text or "fiyat, stok" in text
            assert not CURRENCY_PATTERN.search(text)
            schema_types = jsonld_types(text)
            assert {"Article", "FAQPage", "BreadcrumbList"} <= schema_types
            assert "Product" not in schema_types
            assert "Offer" not in schema_types
            assert text.count("<details>") >= 3
            assert item["toolPath"] in text
            assert item["productCenterPath"] in text

            links = amazon_anchors(text)
            if item["affiliateEnabled"]:
                assert len(links) == 1, (item["slug"], links)
                rel = {token.casefold() for token in links[0].get("rel", "").split()}
                assert REQUIRED_REL <= rel
                assert f'tag={config["affiliateTag"]}' in links[0]["href"]
                assert 'data-alo186-affiliate-gate="qualified"' in text
                assert text.count("data-commerce-check") == len(item["gateChecks"])
                assert "Reklam / satış ortaklığı" in text
                assert 'aria-disabled="true"' in text
            else:
                assert not links
                assert 'data-affiliate-policy="professional_only"' in text
                assert "doğrudan mağaza bağlantısı yok" in text


def test_tool_and_internal_routes_exist_in_effective_inventory() -> None:
    config = load(ROOT)
    manifest = load_effective_manifest(ROOT)
    routes = {item["canonicalPath"] for item in manifest["routes"]}
    for item in config["guides"]:
        assert item["toolPath"].split("?", 1)[0] in routes, item["toolPath"]
        assert item["productCenterPath"].split("?", 1)[0] in routes, item["productCenterPath"]
        for related in item["related"]:
            assert related["path"].split("?", 1)[0] in routes, related["path"]


def test_canonical_bundle_routes_sitemap_release_and_search_are_integrated() -> None:
    with tempfile.TemporaryDirectory() as directory:
        site = Path(directory) / "site"
        release = build(ROOT, site, "commerce-test")
        expected = {
            "/urun-rehberleri/",
            "/urun-rehberleri/powerbank-usb-c-pd",
            "/urun-rehberleri/akim-korumali-grup-priz",
            "/urun-rehberleri/modem-ont-mini-ups",
            "/urun-rehberleri/tasinabilir-guc-istasyonu",
            "/urun-rehberleri/sarjli-acil-aydinlatma",
            "/urun-rehberleri/fotoelektrik-duman-alarmi",
            "/urun-rehberleri/akilli-priz-enerji-olcer",
            "/urun-rehberleri/ges-malzemeleri",
        }
        routes = {item["canonicalPath"] for item in release["routes"]}
        assert expected <= routes
        assert release["routingVersion"] >= 41
        assert release["commerceGuideCount"] == 8
        assert release["commerceCollectionCount"] == 1
        assert release["commerceGuides"]["guideCount"] == 8
        assert release["commerceGuides"]["affiliateEnabledCount"] == 7
        assert release["commerceGuides"]["professionalOnlyCount"] == 1
        assert release["commerceGuides"]["staticPricesStored"] is False
        assert release["commerceGuides"]["staticStockStored"] is False
        assert release["commerceGuides"]["productCenterLinkInjected"] is True
        assert (site / "urun-rehberleri/commerce-guide.css").is_file()
        assert (site / "urun-rehberleri/commerce-guide.js").is_file()
        assert (site / "urun-rehberleri/commerce-release.json").is_file()
        for route in expected:
            assert (site / route.strip("/") / "index.html").is_file(), route
        sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
        for route in expected:
            assert f"https://www.alo186.com{route}" in sitemap
        product_center = (site / "akilli-urun-secimi/index.html").read_text(encoding="utf-8")
        assert "/urun-rehberleri/" in product_center
        assert "https://www.alo186.com/amazon-elektrik-urunleri" not in product_center

        search_result = inject_private_search(site, "")
        assert search_result["entryCount"] >= 89
        index = json.loads((site / "arama/search-index.json").read_text(encoding="utf-8"))
        commerce_entries = [
            row for row in index["entries"] if row["canonicalPath"].startswith("/urun-rehberleri")
        ]
        assert len(commerce_entries) == 9
        assert all(row["bucket"] == "collection" for row in commerce_entries)
        by_path = {row["canonicalPath"]: row for row in commerce_entries}
        assert by_path["/urun-rehberleri/"]["priority"] == 55
        for route in expected - {"/urun-rehberleri/"}:
            assert by_path[route]["priority"] == 45
        assert index["commercialRankingExcluded"] == [
            "price",
            "stock",
            "rating",
            "seller",
            "warranty",
            "affiliateCommission",
        ]
        assert all("price" not in row and "stock" not in row and "rating" not in row for row in commerce_entries)


def main() -> None:
    test_config_has_eight_distinct_high_intent_guides()
    test_generated_pages_are_substantive_unique_and_transparent()
    test_tool_and_internal_routes_exist_in_effective_inventory()
    test_canonical_bundle_routes_sitemap_release_and_search_are_integrated()
    print(json.dumps({"ok": True, "commercialGuides": 8, "collectionPages": 1}, ensure_ascii=False))


if __name__ == "__main__":
    main()
