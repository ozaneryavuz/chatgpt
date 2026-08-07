from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/basement-drainage-outage-v332.json"
GUIDE = SITE / "haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/index.html"
PLANNER = SITE / "hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/index.html"
SECTOR = SITE / "sektor-rehberi/apartman-otel-bodrum-drenaj-pompasi-kesinti-surekliligi/index.html"
ROUTES = {
    "/haberler/elektrik-kesilince-bodrum-drenaj-pompasi-calisir-mi/": GUIDE,
    "/hesaplama/bodrum-drenaj-pompasi-elektrik-kesintisi-su-baskini-plani/": PLANNER,
    "/sektor-rehberi/apartman-otel-bodrum-drenaj-pompasi-kesinti-surekliligi/": SECTOR,
}
COMMERCIAL_TYPES = {"Product", "Offer", "AggregateRating", "Review"}


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


def load_schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 332
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        visible = visible_text(html).casefold()
        assert f"https://alo186.com{route}" in html
        assert '<meta name="viewport"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert "edaş" in visible
        assert "kamu kurumu" in visible or "bağımsız bilgilendirme" in visible
        assert not COMMERCIAL_TYPES.intersection(schema_types(load_schema(html)))
        assert "amazon.com.tr" not in html.casefold()
        for word in ("fiyat", "stok", "puan", "garanti"):
            assert word in visible

    guide_visible = visible_text(pages[next(iter(ROUTES))]).casefold()
    for required in (
        "aktif su baskınında test veya alışveriş yapmayın",
        "yeni ürün almayın",
        "tek pompa “yedeklilik” değildir",
        "yüksek su alarmı",
        "merchant",
    ):
        assert required.casefold() in guide_visible

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
        "BEGIN:VCALENDAR",
        "Form ve ticari yol kapalı",
        "Professional-only",
        "Mevcut sistem yeterli — yeni ürün almayın",
        "mağaza bağlantısı yok",
    ):
        assert required.casefold() in (planner + planner_visible).casefold()

    sector_visible = visible_text(SECTOR.read_text(encoding="utf-8")).casefold()
    for required in (
        "professional-only",
        "sıfır tüketici affiliate",
        "görev-yedek pompalar",
        "jeneratör/ats",
        "yüksek su alarmı",
        "dönüşüm noktaları",
        "bakım sözleşmesi",
    ):
        assert required.casefold() in sector_visible

    print(json.dumps({
        "ok": True,
        "routingVersion": 332,
        "routes": list(ROUTES),
        "newAffiliateClasses": 0,
        "merchantLinks": 0,
        "commercialSchemaTypes": 0,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorageWrites": False,
        "activeFloodCommerceClosed": True,
        "noBuyOutcome": True,
        "professionalOnlyConversion": True,
        "unverifiedPriceStockRatingWarranty": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
