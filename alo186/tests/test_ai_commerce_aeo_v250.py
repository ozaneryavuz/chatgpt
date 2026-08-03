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
            assert f'href="{faq["linkUrl"]}"' in text

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
        assert any(node["@type"] == "FAQPage" for node in graph)

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
        "Offer yalnız",
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
                "robotsAiAgents": list(EXPECTED_AGENTS),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
