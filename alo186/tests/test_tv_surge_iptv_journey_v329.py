from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/tv-surge-iptv-journey-v329.json"
GUIDE = SITE / "haberler/elektrik-kesintisi-televizyona-zarar-verir-mi/index.html"
PLANNER = SITE / "hesaplama/televizyon-elektrik-kesintisi-koruma-hazirlik-plani/index.html"
SECTOR = SITE / "sektor-rehberi/otel-iptv-televizyon-elektrik-kesintisi-surekliligi/index.html"
EXISTING_SELECTOR = SITE / "amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/index.html"
ROUTES = {
    "/haberler/elektrik-kesintisi-televizyona-zarar-verir-mi/": GUIDE,
    "/hesaplama/televizyon-elektrik-kesintisi-koruma-hazirlik-plani/": PLANNER,
    "/sektor-rehberi/otel-iptv-televizyon-elektrik-kesintisi-surekliligi/": SECTOR,
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
    assert overlay["version"] == 329
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
        assert "amazon.com.tr" not in html.casefold()

    guide_visible = text(GUIDE.read_text(encoding="utf-8")).casefold()
    for required in (
        "sinyal yok",
        "type 3",
        "topraklama",
        "koaksiyel",
        "test ve ticaret kapalıdır",
        "satış ortaklığı bağlantısıdır",
    ):
        assert required.casefold() in guide_visible

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
    for sensitive in (
        "açık adres",
        "seri numarası",
        "wi-fi adı/parolası",
        "abonelik bilgisi",
    ):
        assert sensitive in planner_visible
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Form ve ticaret kapalı",
        "satış ortaklığı bağlantısıdır",
        "/amazon-elektrik-urunleri/akim-korumali-priz-yuk-uygunluk-secimi/",
    ):
        assert required in planner or required.casefold() in planner_visible

    sector_visible = text(SECTOR.read_text(encoding="utf-8")).casefold()
    for required in (
        "uçtan uca kabul matrisi",
        "headend",
        "jeneratör / ats",
        "aşırı gerilim / spd",
        "rack ups",
        "90 gün",
    ):
        assert required.casefold() in sector_visible

    selector = EXISTING_SELECTOR.read_text(encoding="utf-8")
    assert "Amazon Türkiye" in selector
    assert "satış ortaklığı" in selector.casefold()
    assert 'rel="sponsored' in selector
    assert "yeni ürün almayın" in text(selector).casefold()

    print(json.dumps({
        "ok": True,
        "routingVersion": 329,
        "newRoutes": list(ROUTES),
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "existingGatedAffiliateSelectorReused": True,
        "professionalOnlyHotelIptv": True,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "activeIncidentCommerceClosed": True,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
