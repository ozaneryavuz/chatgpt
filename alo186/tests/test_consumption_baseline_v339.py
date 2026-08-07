from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/consumption-baseline-v339.json"
DECISION = SITE / "deployment/affiliate-category-decisions/consumption-baseline-v339.json"
GUIDE = SITE / "haberler/elektrik-faturasi-neden-yuksek-kwh-gun-tuketim-artisi/index.html"
TOOL = SITE / "hesaplama/elektrik-faturasi-kwh-gun-tuketim-karsilastirma/index.html"
SELECTOR = SITE / "amazon-elektrik-urunleri/priz-tipi-enerji-olcer-secimi/index.html"
ROUTES = {
    "/haberler/elektrik-faturasi-neden-yuksek-kwh-gun-tuketim-artisi/": GUIDE,
    "/hesaplama/elektrik-faturasi-kwh-gun-tuketim-karsilastirma/": TOOL,
    "/amazon-elektrik-urunleri/priz-tipi-enerji-olcer-secimi/": SELECTOR,
}
COMMERCIAL_SCHEMA = {"Product", "Offer", "AggregateRating", "Review"}


def visible_text(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def schema_types(value: object) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            result.add(kind)
        for item in value.values():
            result.update(schema_types(item))
    elif isinstance(value, list):
        for item in value:
            result.update(schema_types(item))
    return result


def schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 339
    assert {r["canonicalPath"] for r in overlay["routes"]} == set(ROUTES)

    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["version"] == 339
    assert decision["newAffiliateClasses"] == 1
    assert decision["newMerchantLinks"] == 1
    assert decision["affiliateClass"] == "plug-in-energy-meter-wattmeter"
    assert "meter-purchase-will-reduce-bill" in decision["mustNotClaim"]
    assert "energy-audit" in decision["professionalOnly"]

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        assert f"https://alo186.com{route}" in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert not COMMERCIAL_SCHEMA.intersection(schema_types(schema(html)))
        visible = visible_text(html).casefold()
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible
        assert "kamu kurumu" in visible

    guide = pages[next(r for r in ROUTES if r.startswith("/haberler/"))]
    guide_visible = visible_text(guide).casefold()
    for required in ("kwh/gün", "gün sayısı", "yeni ürün almayın", "epdk", "etkb", "sayaç"):
        assert required.casefold() in guide_visible
    assert "lisans.epdk.gov.tr" in guide
    assert "enerji.gov.tr" in guide

    tool = TOOL.read_text(encoding="utf-8")
    tool_visible = visible_text(tool).casefold()
    for forbidden in ("fetch(", "xmlhttprequest", "sendbeacon", "localstorage", "sessionstorage"):
        assert forbidden not in tool.casefold()
    for required in ("WebApplication", "new Blob", "BEGIN:VCALENDAR", "kWh/gün", "yeni ürün almayın", "30 gün"):
        assert required in tool or required.casefold() in tool_visible
    assert "type=\"text\"" not in tool.casefold()
    assert "type=\"email\"" not in tool.casefold()
    assert "type=\"tel\"" not in tool.casefold()

    selector = SELECTOR.read_text(encoding="utf-8")
    selector_visible = visible_text(selector).casefold()
    assert selector.count('class="gate"') == 8
    assert selector.count('rel="sponsored noopener"') == 1
    assert selector.count("amazon.com.tr") == 1
    assert "tag=alo186rehber-21" in selector
    assert "data-merchant-url=" in selector
    assert "href=\"https://www.amazon.com.tr" not in selector
    for required in ("satış ortaklığı", "yeni ürün almayın", "sabit tesisat", "motor/kompresör", "uzatma", "mevcut güvenli ölçüm"):
        assert required.casefold() in selector_visible

    print(json.dumps({
        "ok": True,
        "routingVersion": 339,
        "newRoutes": list(ROUTES),
        "newAffiliateClasses": 1,
        "newMerchantLinks": 1,
        "merchantLinksTrustGated": True,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "noBuyOutcome": True,
        "unverifiedPriceStockRatingWarranty": 0,
        "monthlyRevisit": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
