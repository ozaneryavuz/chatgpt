from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/aquarium-outage-journey-v323.json"
GUIDE = SITE / "haberler/elektrik-kesintisinde-akvaryum-baliklari-ne-yapilmali/index.html"
PLANNER = SITE / "hesaplama/akvaryum-elektrik-kesintisi-hazirlik-plani/index.html"
SELECTOR = SITE / "amazon-elektrik-urunleri/akvaryum-kesinti-hazirlik-secimi/index.html"
ROUTES = {
    "/haberler/elektrik-kesintisinde-akvaryum-baliklari-ne-yapilmali/": GUIDE,
    "/hesaplama/akvaryum-elektrik-kesintisi-hazirlik-plani/": PLANNER,
    "/amazon-elektrik-urunleri/akvaryum-kesinti-hazirlik-secimi/": SELECTOR,
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
    assert overlay["version"] == 323
    assert {r["canonicalPath"] for r in overlay["routes"]} == set(ROUTES)
    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        visible = text(html).casefold()
        assert f'https://alo186.com{route}' in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "edaş" in visible and "kamu kurumu" in visible
        assert "yeni ürün almayın" in visible
        assert not COMMERCIAL.intersection(types(schema(html)))
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible

    guide = pages[next(iter(ROUTES))]
    guide_visible = text(guide)
    assert "Tek bir güvenli saat yoktur" in guide
    assert "Aktif elektrik tehlikesinde test ve ticaret kapalıdır" in guide_visible
    assert "Amazon Türkiye bağlantıları satış ortaklığı bağlantısı" in guide_visible
    assert "amazon.com.tr" not in guide.casefold()

    planner = PLANNER.read_text(encoding="utf-8")
    planner_visible = text(planner)
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    for forbidden in ("fetch(", "xmlhttprequest", "sendbeacon", "localstorage.setitem", "sessionstorage.setitem"):
        assert forbidden not in planner.casefold()
    for required in ("new Blob", "URL.createObjectURL", "BEGIN:VCALENDAR", "30/90/365", "Form ve ticaret kapalı", "Mevcut hazırlık yeterli — yeni ürün almayın"):
        assert required in planner or required in planner_visible

    selector = SELECTOR.read_text(encoding="utf-8")
    selector_visible = text(selector).casefold()
    assert selector.count('class="gate"') == 8
    assert selector.count('rel="sponsored noopener"') == 2
    assert selector.count('amazon.com.tr') == 2
    assert selector.count('tag=alo186rehber-21') == 2
    assert "amazon türkiye satış ortaklığı açıklaması" in selector_visible
    assert "bağlantılar kapalı" in selector_visible
    assert "removeattribute('href')" in selector.casefold()
    assert "fiyat, stok, satıcı, puan, yorum, teslimat veya garanti" in selector_visible

    print(json.dumps({
        "ok": True,
        "routingVersion": 323,
        "newRoutes": list(ROUTES),
        "affiliateClasses": 2,
        "affiliateGateCount": 8,
        "initialMerchantLinksActive": 0,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
