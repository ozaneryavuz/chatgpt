from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

import inject_ai_commerce_aeo_v250 as aeo  # noqa: E402
import inject_ai_commerce_breadcrumb_v250 as breadcrumb  # noqa: E402

EXPECTED_AGENTS = (
    "OAI-SearchBot",
    "GPTBot",
    "ChatGPT-User",
    "PerplexityBot",
    "ClaudeBot",
    "Claude-SearchBot",
    "Bytespider",
    "Google-Extended",
)


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def schema_types(text: str) -> set[str]:
    types: set[str] = set()
    for raw in re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        text,
        re.IGNORECASE | re.DOTALL,
    ):
        payload = json.loads(raw.replace("<\\/", "</"))
        types.update(breadcrumb.collect_types(payload))
    return types


def public_link(base_path: str, value: str) -> str:
    """Return the final HTML link expected after Pages preparation.

    Fragment-only deep links remain local to the current document and must not
    receive a repository base path. Root-relative routes receive the project
    prefix only in the `/chatgpt` artifact.
    """
    if value.startswith("#"):
        return value
    if base_path and value.startswith("/"):
        return f"{base_path}{value}"
    return value


def validate_final_site(site: Path, base_path: str) -> None:
    report = json.loads(
        (site / aeo.VALIDATION_TARGET).read_text(encoding="utf-8")
    )
    assert report["ok"] is True
    assert report["version"] == 250
    assert report["routeCount"] == 6
    assert report["itemListCount"] == 6
    assert report["productEntityCount"] == 18
    assert report["faqPageCount"] == 6
    assert report["verifiedOfferCount"] == 0
    assert report["emittedOfferCount"] == 0
    assert report["offerPolicy"] == "fail-closed"
    assert report["staticPrerendered"] is True
    assert report["javascriptRequiredForCoreRecommendations"] is False
    assert report["directAmazonLinkCount"] == report["annotatedAmazonLinkCount"]
    assert report["failures"] == []

    manifest = aeo.load_manifest(ROOT)
    seen_ids: set[str] = set()
    for route in manifest["routes"]:
        path = site / route["file"]
        assert path.is_file(), route["file"]
        text = path.read_text(encoding="utf-8")
        assert text.count(aeo.MARKER) == 1
        assert text.count(breadcrumb.MARKER) == 1
        assert 'data-rendering="static-prerender"' in text
        assert "<table" in text and "<tbody" in text
        assert text.count('class="alo186-ai-commerce-v250__card"') == 3
        assert text.count(aeo.SCHEMA_MARKER) == 1
        for product in route["products"]:
            assert f'id="{product["id"]}"' in text
            assert product["id"] not in seen_ids
            seen_ids.add(product["id"])
        for faq in route.get("faq", []):
            assert f'id="{faq["id"]}"' in text
            expected_link = public_link(base_path, faq["linkUrl"])
            assert f'href="{expected_link}"' in text

        match = re.search(
            rf'<script\b[^>]*{re.escape(aeo.SCHEMA_MARKER)}[^>]*>(.*?)</script>',
            text,
            re.IGNORECASE | re.DOTALL,
        )
        assert match
        payload = json.loads(match.group(1).replace("<\\/", "</"))
        graph = payload["@graph"]
        item_list = next(node for node in graph if node["@type"] == "ItemList")
        assert item_list["numberOfItems"] == 3
        assert len(item_list["itemListElement"]) == 3
        for item in item_list["itemListElement"]:
            product = item["item"]
            assert product["@type"] == "Product"
            assert "offers" not in product
            assert product["url"].startswith("https://alo186.com")
            assert len(product["additionalProperty"]) == 4
            assert "isRelatedTo" in product
        assert any(node["@type"] == "FAQPage" for node in graph)
        assert "BreadcrumbList" in schema_types(text)

    product_graph_path = site / breadcrumb.PRODUCT_GRAPH_ROUTE
    product_graph_text = product_graph_path.read_text(encoding="utf-8")
    assert product_graph_text.count(breadcrumb.MARKER) == 1
    product_types = schema_types(product_graph_text)
    assert {"Product", "Brand", "ItemList", "BreadcrumbList"}.issubset(product_types)
    assert "Offer" not in product_types
    for token in ("ASIN", "MPN", "additionalProperty"):
        assert token in product_graph_text

    release = json.loads((site / "alo186-release.json").read_text(encoding="utf-8"))
    breadcrumb_report = release["aiCommerceBreadcrumbV250"]
    assert breadcrumb_report["ok"] is True
    assert breadcrumb_report["breadcrumbRouteCount"] == 7
    assert breadcrumb_report["productGraph"]["offerEmitted"] is False

    css_href = (
        f"{base_path}/{aeo.STYLE_TARGET.as_posix()}"
        if base_path
        else f"/{aeo.STYLE_TARGET.as_posix()}"
    )
    first_target = site / manifest["routes"][0]["file"]
    assert css_href in first_target.read_text(encoding="utf-8")

    llms = (site / "llms.txt").read_text(encoding="utf-8")
    for token in (
        "## Resmî ve güvenlik kanalları",
        "## Teknik çözüm ve ekipman rehberleri",
        "## Sorundan ürüne karar ankrajları",
        "## Ticari ve yapılandırılmış veri politikası",
        "alo186rehber-21",
        "priceValidUntil",
    ):
        assert token in llms, token

    robots = (site / "robots.txt").read_text(encoding="utf-8")
    for agent in EXPECTED_AGENTS:
        assert f"User-agent: {agent}" in robots, agent
    for path in (
        "/haberler/",
        "/hesaplama/",
        "/urun-rehberleri/",
        "/amazon-elektrik-urunleri/",
        "/rehber/",
        "/urunler/",
    ):
        assert f"Allow: {path}" in robots

    for safety_path in (
        "acil-numaralar/index.html",
        "en/emergency-numbers-turkey/index.html",
        "en/electricity-outage-turkey/index.html",
    ):
        path = site / safety_path
        if path.is_file():
            assert aeo.MARKER not in path.read_text(encoding="utf-8")


def main() -> None:
    manifest = aeo.load_manifest(ROOT)
    assert manifest["offerPolicy"]["mode"] == "fail-closed"
    assert manifest["offerPolicy"]["verifiedOffers"] == []
    assert len(manifest["routes"]) == 6
    assert sum(len(route["products"]) for route in manifest["routes"]) == 18
    assert len(
        {
            product["id"]
            for route in manifest["routes"]
            for product in route["products"]
        }
    ) == 18

    with tempfile.TemporaryDirectory(prefix="alo186-ai-commerce-v250-") as folder:
        root = Path(folder)
        canonical = root / "canonical"
        run(
            [
                sys.executable,
                "alo186/deployment/build_static_site.py",
                "--output",
                str(canonical),
                "--commit",
                "ai-commerce-v250-test",
            ]
        )
        validate_final_site(canonical, "")

        second = aeo.apply_ai_commerce_aeo(ROOT, canonical)
        assert second["injectedRouteCount"] == 0
        assert second["alreadyInjectedRouteCount"] == 6
        assert second["verifiedOfferCount"] == 0
        assert second["emittedOfferCount"] == 0
        breadcrumb_second = breadcrumb.apply(canonical)
        assert breadcrumb_second["injected"] == 0
        assert breadcrumb_second["alreadyPresent"] == 7
        validate_final_site(canonical, "")

        for name, base_path in (("custom", ""), ("project", "/chatgpt")):
            site = root / name
            shutil.copytree(canonical, site)
            run(
                [
                    sys.executable,
                    "alo186/deployment/prepare_github_pages.py",
                    "--site",
                    str(site),
                    "--base-path",
                    base_path,
                    "--repository",
                    "ozaneryavuz/chatgpt",
                    "--commit",
                    "ai-commerce-v250-test",
                ]
            )
            validate_final_site(site, base_path)

    print(
        json.dumps(
            {
                "ok": True,
                "version": 250,
                "routeCount": 6,
                "productEntityCount": 18,
                "verifiedOfferCount": 0,
                "staticPrerendered": True,
                "deepLinksUnique": True,
                "breadcrumbRouteCount": 7,
                "verifiedProductGraph": True,
                "robotsAiAgents": list(EXPECTED_AGENTS),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
