from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/outage-lighting-journey-v330.json"
GUIDE = SITE / "haberler/elektrik-kesintisinde-mum-mu-el-feneri-mi/index.html"
PLANNER = SITE / "hesaplama/elektrik-kesintisi-acil-aydinlatma-hazirlik-plani/index.html"
SELECTOR = SITE / "amazon-elektrik-urunleri/elektrik-kesintisi-acil-aydinlatma-secimi/index.html"
ROUTES = {
    "/haberler/elektrik-kesintisinde-mum-mu-el-feneri-mi/": GUIDE,
    "/hesaplama/elektrik-kesintisi-acil-aydinlatma-hazirlik-plani/": PLANNER,
    "/amazon-elektrik-urunleri/elektrik-kesintisi-acil-aydinlatma-secimi/": SELECTOR,
}
COMMERCIAL = {"Product", "Offer", "AggregateRating", "Review"}


def text(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def types(value: object) -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            out.add(kind)
        for item in value.values():
            out.update(types(item))
    elif isinstance(value, list):
        for item in value:
            out.update(types(item))
    return out


def schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 330
    assert {r["canonicalPath"] for r in overlay["routes"]} == set(ROUTES)
    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}

    for route, html in pages.items():
        visible = text(html).casefold()
        assert f"https://alo186.com{route}" in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "edaş" in visible and "kamu kurumu" in visible
        assert "yeni ürün almayın" in visible
        assert not COMMERCIAL.intersection(types(schema(html)))
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible

    guide_visible = text(GUIDE.read_text(encoding="utf-8")).casefold()
    for required in (
        "mum yerine",
        "afad",
        "el feneri",
        "test ve ticaret kapalıdır",
        "satış ortaklığı bağlantısıdır",
    ):
        assert required.casefold() in guide_visible
    assert "amazon.com.tr" not in GUIDE.read_text(encoding="utf-8").casefold()

    planner = PLANNER.read_text(encoding="utf-8")
    planner_visible = text(planner).casefold()
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    for forbidden in (
        "fetch(",
        "xmlhttprequest",
        "sendbeacon",
        "localstorage.setitem",
        "sessionstorage.setitem",
    ):
        assert forbidden not in planner.casefold()
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/180",
        "Form ve ticaret kapalı",
        "satış ortaklığı bağlantısıdır",
        "/amazon-elektrik-urunleri/elektrik-kesintisi-acil-aydinlatma-secimi/",
    ):
        assert required in planner or required.casefold() in planner_visible
    assert "amazon.com.tr" not in planner.casefold()

    selector = SELECTOR.read_text(encoding="utf-8")
    selector_visible = text(selector).casefold()
    assert selector.count('class="gate"') == 8
    assert selector.count('rel="sponsored noopener"') == 2
    assert selector.count('data-merchant-url="https://www.amazon.com.tr/') == 2
    assert "sales ortaklığı" not in selector_visible
    assert "satış ortaklığı" in selector_visible
    for required in (
        "el feneri / baş feneri",
        "taşınabilir led fener",
        "professional-only",
        "aktif kesinti yok",
        "yeni ürün almayın",
        "30 günde",
        "90 günde",
        "180 günde",
    ):
        assert required.casefold() in selector_visible
    assert "href=\"https://www.amazon.com.tr/" not in selector.casefold()

    print(json.dumps({
        "ok": True,
        "routingVersion": 330,
        "newRoutes": list(ROUTES),
        "newAffiliateClasses": 2,
        "gatedMerchantLinks": 2,
        "affiliateGates": 8,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "activeIncidentCommerceClosed": True,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 180],
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
