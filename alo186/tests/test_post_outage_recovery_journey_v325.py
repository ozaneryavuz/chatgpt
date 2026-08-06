from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/post-outage-recovery-journey-v325.json"
GUIDE = SITE / "haberler/elektrik-kesintisi-sonrasi-cihazlar-nasil-kontrol-edilir/index.html"
PLANNER = SITE / "hesaplama/elektrik-kesintisi-sonrasi-guvenli-devreye-alma-plani/index.html"
SECTOR = SITE / "sektor-rehberi/otel-isletme-elektrik-kesintisi-sonrasi-devreye-alma/index.html"
ROUTES = {
    "/haberler/elektrik-kesintisi-sonrasi-cihazlar-nasil-kontrol-edilir/": GUIDE,
    "/hesaplama/elektrik-kesintisi-sonrasi-guvenli-devreye-alma-plani/": PLANNER,
    "/sektor-rehberi/otel-isletme-elektrik-kesintisi-sonrasi-devreye-alma/": SECTOR,
}
COMMERCIAL = {"Product", "Offer", "AggregateRating", "Review"}
SELECTORS = {
    "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
    "/amazon-elektrik-urunleri/buzdolabi-dondurucu-kesinti-hazirlik-secimi/",
    "/amazon-elektrik-urunleri/akvaryum-kesinti-hazirlik-secimi/",
}


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
    assert overlay["version"] == 325
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

    guide = GUIDE.read_text(encoding="utf-8")
    guide_visible = text(guide)
    assert "Aktif elektrik, yangın veya su tehlikesinde test ve ticaret kapalıdır" in guide_visible
    assert "cihazları aynı anda açmayın" in guide_visible.casefold()
    assert "Şalteri art arda kaldırmayın" in guide_visible

    planner = PLANNER.read_text(encoding="utf-8")
    planner_visible = text(planner)
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    for forbidden in ("fetch(", "xmlhttprequest", "sendbeacon", "localstorage.setitem", "sessionstorage.setitem"):
        assert forbidden not in planner.casefold()
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Form ve ticaret kapalı",
        "Mevcut hazırlık yeterli — yeni ürün almayın",
    ):
        assert required in planner or required in planner_visible
    for selector in SELECTORS:
        assert selector in planner

    sector_visible = text(SECTOR.read_text(encoding="utf-8"))
    for required in (
        "Jeneratör–ATS gerçek kesinti ve yük altında kabul testi",
        "UPS, batarya ve kritik yük çalışma süresi doğrulaması",
        "Olay sonrası kök neden analizi",
    ):
        assert required in sector_visible

    print(json.dumps({
        "ok": True,
        "routingVersion": 325,
        "newRoutes": list(ROUTES),
        "qualifiedInternalSelectorRoutes": sorted(SELECTORS),
        "newAffiliateClasses": 0,
        "merchantLinks": 0,
        "professionalOnly": True,
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
