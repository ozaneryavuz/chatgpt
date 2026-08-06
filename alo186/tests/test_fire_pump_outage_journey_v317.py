from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/fire-pump-outage-journey-v317.json"

ROUTES = {
    "/haberler/elektrik-kesilince-yangin-pompasi-calisir-mi/": SITE / "haberler/elektrik-kesilince-yangin-pompasi-calisir-mi/index.html",
    "/hesaplama/yangin-pompasi-elektrik-kesintisi-sureklilik-plani/": SITE / "hesaplama/yangin-pompasi-elektrik-kesintisi-sureklilik-plani/index.html",
    "/sektor-rehberi/otel-apartman-isletme-yangin-pompasi-surekliligi/": SITE / "sektor-rehberi/otel-apartman-isletme-yangin-pompasi-surekliligi/index.html",
}
MERCHANT_MARKERS = ("amazon.com.tr", "amzn.to", "alo186rehber-21")
COMMERCIAL_SCHEMA = {"Product", "Offer", "AggregateRating", "Review"}


def visible_text(html: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def schema_types(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        kind = value.get("@type")
        if isinstance(kind, str):
            found.add(kind)
        elif isinstance(kind, list):
            found.update(str(item) for item in kind)
        for child in value.values():
            found.update(schema_types(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_types(child))
    return found


def load_schema(html: str) -> object:
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(blocks) == 1
    return json.loads(blocks[0])


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 317
    assert overlay["generatedAt"] == "2026-08-06"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        folded = html.casefold()
        text = visible_text(html)
        text_folded = text.casefold()
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert all(marker not in folded for marker in MERCHANT_MARKERS)
        assert not COMMERCIAL_SCHEMA.intersection(schema_types(load_schema(html)))
        assert "yeni ürün alma" in text_folded or "satın almama sonucu" in text_folded
        assert "resmî kurum" in text_folded or "kamu kurumu" in text_folded
        assert "professional-only" in text_folded
        assert "fiyat" in text_folded and "stok" in text_folded

    guide = pages["/haberler/elektrik-kesilince-yangin-pompasi-calisir-mi/"]
    guide_text = visible_text(guide)
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(schema_types(load_schema(guide)))
    for required in (
        "Yangın pompasının kesintide çalışması",
        "Binada jeneratör var",
        "Aktif tehlikede ticaret kapalıdır",
        "genel elektrik sisteminden bağımsız",
        "/hesaplama/yangin-pompasi-elektrik-kesintisi-sureklilik-plani/",
        "/sektor-rehberi/otel-apartman-isletme-yangin-pompasi-surekliligi/",
    ):
        assert required in guide or required in guide_text, required

    planner = pages["/hesaplama/yangin-pompasi-elektrik-kesintisi-sureklilik-plani/"]
    planner_text = visible_text(planner)
    assert {"WebApplication", "BreadcrumbList", "ListItem"}.issubset(schema_types(load_schema(planner)))
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    lowered = planner.casefold()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "sendbeacon"):
        assert forbidden not in lowered
    for required in (
        "new Blob",
        "URL.createObjectURL",
        "BEGIN:VCALENDAR",
        "30/90/365",
        "Aktif yangında form ve ticaret kapalı",
        "Professional-only kabul ve düzeltici faaliyet gerekir",
        "Mevcut sistem proje ve gerçek görev testinde yeterliyse yeni ürün almayın",
        "Amazon Türkiye veya başka mağaza bağlantısı yoktur",
    ):
        assert required in planner, required
    assert "Ad, telefon, e-posta, adres" in planner_text
    assert "Seçimler sunucuya gönderilmez" in planner_text

    sector = pages["/sektor-rehberi/otel-apartman-isletme-yangin-pompasi-surekliligi/"]
    sector_text = visible_text(sector)
    assert {"Article", "BreadcrumbList", "ListItem"}.issubset(schema_types(load_schema(sector)))
    for required in (
        "Süreklilik ve kabul matrisi",
        "Gerçek kesinti ve otomatik başlatma görev kabul testi",
        "Enerji bağımsızlığı ve seçicilik incelemesi",
        "Bu sayfada Amazon Türkiye veya başka mağaza bağlantısı yoktur",
        "/kurumsal-elektrik-surekliligi-on-degerlendirme",
    ):
        assert required in sector or required in sector_text, required

    print(json.dumps({
        "ok": True,
        "routingVersion": 317,
        "newRoutes": list(ROUTES),
        "merchantLinksAdded": 0,
        "consumerAffiliateClasses": 0,
        "professionalOnly": True,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorage": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "activeFireCommerceClosed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
