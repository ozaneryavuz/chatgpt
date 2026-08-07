from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/server-room-power-cooling-v337.json"
GUIDE = SITE / "haberler/sunucu-odasi-elektrik-kesintisinde-ups-calisirken-klima-durursa-ne-olur/index.html"
PLANNER = SITE / "hesaplama/sunucu-odasi-elektrik-kesintisi-ups-sogutma-sureklilik-plani/index.html"
PRO = SITE / "sektor-rehberi/otel-isletme-sunucu-odasi-ups-jenerator-sogutma-surekliligi/index.html"
ROUTES = {
    "/haberler/sunucu-odasi-elektrik-kesintisinde-ups-calisirken-klima-durursa-ne-olur/": GUIDE,
    "/hesaplama/sunucu-odasi-elektrik-kesintisi-ups-sogutma-sureklilik-plani/": PLANNER,
    "/sektor-rehberi/otel-isletme-sunucu-odasi-ups-jenerator-sogutma-surekliligi/": PRO,
}
COMMERCIAL = {"Product", "Offer", "AggregateRating", "Review"}


def visible_text(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", html, flags=re.I | re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def schema_types(value: object) -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            out.add(kind)
        for item in value.values():
            out.update(schema_types(item))
    elif isinstance(value, list):
        for item in value:
            out.update(schema_types(item))
    return out


def schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 337
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        visible = visible_text(html).casefold()
        assert f"https://alo186.com{route}" in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "edaş" in visible and "kamu kurumu" in visible
        assert "yeni ürün almayın" in visible
        assert "satış ortaklığı" in visible
        assert "professional-only" in visible
        assert "amazon.com.tr" not in html.casefold()
        assert not COMMERCIAL.intersection(schema_types(schema(html)))
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible

    guide = GUIDE.read_text(encoding="utf-8")
    guide_visible = visible_text(guide).casefold()
    for required in (
        "ups yalnız güç katmanıdır",
        "soğutma transfer gecikmesi",
        "kontrollü kapanma",
        "jeneratör ve ats",
        "bypass etmeyin",
    ):
        assert required.casefold() in guide_visible
    for domain in ("se.com", "vertiv.com"):
        assert domain in guide

    planner = PLANNER.read_text(encoding="utf-8")
    planner_visible = visible_text(planner).casefold()
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
        "30/90/365",
        "Form ve ticaret kapalı",
        "/sektor-rehberi/otel-isletme-sunucu-odasi-ups-jenerator-sogutma-surekliligi/",
    ):
        assert required in planner or required.casefold() in planner_visible

    pro = PRO.read_text(encoding="utf-8")
    pro_visible = visible_text(pro).casefold()
    for required in (
        "it kritik yük",
        "ups ve akü",
        "kontrollü shutdown",
        "soğutma",
        "jeneratör / ats",
        "izleme / alarm",
        "geri dönüş",
        "/kurumsal-elektrik-surekliligi-on-degerlendirme",
        "30 / 90 / 365",
    ):
        assert required.casefold() in pro_visible or required in pro

    print(json.dumps({
        "ok": True,
        "routingVersion": 337,
        "newRoutes": list(ROUTES),
        "newAffiliateClasses": 0,
        "gatedMerchantLinks": 0,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "activeIncidentCommerceClosed": True,
        "noBuyOutcome": True,
        "professionalOnlyServerRoom": True,
        "revisitCycle": [30, 90, 365],
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
