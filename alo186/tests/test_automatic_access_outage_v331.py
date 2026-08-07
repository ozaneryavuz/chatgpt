from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/automatic-access-outage-v331.json"
GUIDE = SITE / "haberler/elektrik-kesilince-otomatik-kepenk-garaj-kapisi-nasil-acilir/index.html"
PLANNER = SITE / "hesaplama/otomatik-kapi-kepenk-elektrik-kesintisi-sureklilik-plani/index.html"
SECTOR = SITE / "sektor-rehberi/site-otel-isletme-otomatik-kapi-kepenk-kesinti-surekliligi/index.html"
ROUTES = {
    "/haberler/elektrik-kesilince-otomatik-kepenk-garaj-kapisi-nasil-acilir/": GUIDE,
    "/hesaplama/otomatik-kapi-kepenk-elektrik-kesintisi-sureklilik-plani/": PLANNER,
    "/sektor-rehberi/site-otel-isletme-otomatik-kapi-kepenk-kesinti-surekliligi/": SECTOR,
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
    assert overlay["version"] == 331
    assert {r["canonicalPath"] for r in overlay["routes"]} == set(ROUTES)
    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}

    for route, html in pages.items():
        visible = text(html).casefold()
        assert f"https://alo186.com{route}" in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "edaş" in visible and "kamu kurumu" in visible
        assert not COMMERCIAL.intersection(types(schema(html)))
        assert "amazon.com.tr" not in html.casefold()
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible

    guide_visible = text(GUIDE.read_text(encoding="utf-8")).casefold()
    for required in (
        "tek bir “manuel açma” yöntemi yoktur",
        "nice",
        "kaçış yolu kapılarının elle açılabilir",
        "yeni ürün almayın",
        "yeni amazon kategorisi açılmadı",
    ):
        assert required.casefold() in guide_visible

    planner = PLANNER.read_text(encoding="utf-8")
    planner_visible = text(planner).casefold()
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    for forbidden in ("fetch(", "xmlhttprequest", "sendbeacon", "localstorage.setitem", "sessionstorage.setitem"):
        assert forbidden not in planner.casefold()
    for required in (
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Form ve ticaret kapalı",
        "Professional-only",
        "yeni ürün almayın",
    ):
        assert required.casefold() in (planner + planner_visible).casefold()

    sector_visible = text(SECTOR.read_text(encoding="utf-8")).casefold()
    for required in (
        "professional-only kabul matrisi",
        "kaçış ve tahliye",
        "ups/akü",
        "jeneratör/ats",
        "tesis elektrik risk ön değerlendirmesini aç",
        "merchant bağlantısı",
    ):
        assert required.casefold() in sector_visible

    print(json.dumps({
        "ok": True,
        "routingVersion": 331,
        "newRoutes": list(ROUTES),
        "newAffiliateClasses": 0,
        "merchantLinks": 0,
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
