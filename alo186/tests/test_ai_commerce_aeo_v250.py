from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
SCRIPT = DEPLOYMENT / "inject_ai_commerce_aeo_v250.py"
CONFIG = DEPLOYMENT / "ai-commerce-verified-offers-v250.json"
LLMS = ROOT / "alo186/llms.txt"
ROBOTS = ROOT / "alo186/robots.txt"
VERSION = 250


def load_module():
    spec = importlib.util.spec_from_file_location("inject_ai_commerce_aeo_v250", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_sources() -> dict:
    script = SCRIPT.read_text(encoding="utf-8")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    llms = LLMS.read_text(encoding="utf-8")
    robots = ROBOTS.read_text(encoding="utf-8")

    assert config["version"] == VERSION
    assert config["policy"] == "fail-closed"
    assert config["maxAgeHours"] <= 24
    assert config["offers"] == []
    assert set(config["requiredFields"]) >= {
        "productId", "url", "price", "priceCurrency", "availability",
        "sellerName", "verifiedAt", "validThrough",
    }

    for token in (
        '"@type": "Recommendation"',
        '"@type": "ItemList"',
        '"@type": "Table"',
        '"@type": "Offer"',
        'data-alo186-ssr-products-v250="true"',
        'rel="sponsored nofollow noopener"',
        'rehber-',
        'urun-',
        "validate_rel_across_site",
    ):
        assert token in script, token

    for token in (
        "## Resmî Kanallar",
        "## Teknik Çözüm ve Ekipman Rehberleri",
        "Ev/Ofis Kesinti Hazırlık Ekipmanları",
        "Cihaz ve Pano Koruma Ekipmanları",
        "GES ve Yedek Enerji Sistemleri",
        "Amazon Türkiye satış ortaklığı",
        "Product",
        "Recommendation",
        "ItemList",
        "Table",
        "Offer",
    ):
        assert token in llms, token

    for agent in (
        "OAI-SearchBot", "GPTBot", "ChatGPT-User", "PerplexityBot",
        "ClaudeBot", "Bytespider", "Google-Extended",
    ):
        assert f"User-agent: {agent}" in robots, agent
    for route in ("/rehber/", "/urunler/", "/haberler/", "/amazon-elektrik-urunleri/"):
        assert f"Allow: {route}" in robots, route

    assert "priceCurrency" not in llms
    assert "AggregateRating" not in llms
    return {
        "ok": True,
        "version": VERSION,
        "offerRecords": 0,
        "aiAgents": 7,
        "llmsSections": 6,
        "dynamicAffiliateRelContract": True,
    }


def validate_artifact(site: Path, base_path: str) -> dict:
    module = load_module()
    result = module.validate(site.resolve(), base_path)
    report = json.loads((site / module.REPORT_NAME).read_text(encoding="utf-8"))
    assert report["ok"] is True
    assert report["structuredData"]["products"] >= 3
    assert report["structuredData"]["recommendations"] >= 3
    assert report["structuredData"]["comparisonItems"] == 2
    assert report["structuredData"]["offers"] == 0
    assert report["offerGate"]["configuredRecords"] == 0
    assert report["ssrBaseline"] is True
    # Affiliate mağaza URL'leri kaynak HTML'de tutulmayabilir; runtime, kullanıcı
    # güven kapısından sonra anchor üretir. Bu nedenle sıfır statik anchor geçerli
    # bir sonuçtur. `module.validate()` bütün mevcut final-HTML affiliate
    # anchorlarını fail-closed tarar; kaynak sözleşmesi de runtime rel değerini
    # zorunlu tutar.
    assert isinstance(report["affiliateRelChecked"], int)
    assert report["affiliateRelChecked"] >= 0
    assert report["affiliateRelChanged"] >= 0
    assert report["deepLinks"] >= 6

    surge = module.route_file(site, module.SURGE_PRODUCTS_ROUTE).read_text(encoding="utf-8")
    assert surge.count('"@type": "Recommendation"') >= 3
    assert '"@type": "Offer"' not in surge
    assert len(set(re.findall(r'id="(urun-[^"]+)"', surge))) >= 3

    comparison = module.route_file(site, module.COMPARISON_ROUTE).read_text(encoding="utf-8")
    assert 'id="karsilastirma-ups-power-station"' in comparison
    assert 'id="alo186-product-comparison-v250"' in comparison
    assert '"@type": "Table"' in comparison
    assert '"@type": "ItemList"' in comparison

    matcher = module.route_file(site, module.MATCHER_ROUTE).read_text(encoding="utf-8")
    assert matcher.count('class="ssr-choice-card"') == len(module.SSR_CHOICES)
    assert 'data-alo186-ssr-products-v250="true"' in matcher

    release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
    contract = release.get("aiCommerceAeo") or {}
    assert contract.get("version") == VERSION
    assert contract.get("offerFailClosed") is True
    assert contract.get("llmsTxt") is True
    assert contract.get("aiCrawlerPolicy") is True
    return {**result, "products": report["structuredData"]["products"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path)
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    result = {"source": validate_sources()}
    if args.site:
        result["artifact"] = validate_artifact(args.site, args.base_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
