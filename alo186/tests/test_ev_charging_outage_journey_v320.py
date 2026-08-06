from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/ev-charging-outage-journey-v320.json"

ROUTES = {
    "/haberler/elektrik-kesilince-elektrikli-arac-sarji-durur-mu/": SITE / "haberler/elektrik-kesilince-elektrikli-arac-sarji-durur-mu/index.html",
    "/hesaplama/elektrikli-arac-sarj-elektrik-kesintisi-hazirlik-plani/": SITE / "hesaplama/elektrikli-arac-sarj-elektrik-kesintisi-hazirlik-plani/index.html",
    "/sektor-rehberi/site-otel-isletme-elektrikli-arac-sarj-kesinti-surekliligi/": SITE / "sektor-rehberi/site-otel-isletme-elektrikli-arac-sarj-kesinti-surekliligi/index.html",
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
    assert overlay["version"] == 320
    assert overlay["generatedAt"] == "2026-08-06"
    assert {item["canonicalPath"] for item in overlay["routes"]} == set(ROUTES)

    pages = {route: path.read_text(encoding="utf-8") for route, path in ROUTES.items()}
    for route, html in pages.items():
        folded = html.casefold()
        text_folded = visible_text(html).casefold()
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert all(marker not in folded for marker in MERCHANT_MARKERS)
        assert not COMMERCIAL_SCHEMA.intersection(schema_types(load_schema(html)))
        assert "yeni ürün alma" in text_folded or "satın almama sonucu" in text_folded
        assert "resmî kurum" in text_folded or "epdk" in text_folded
        assert "professional-only" in text_folded
        assert "fiyat" in text_folded and "stok" in text_folded

    guide = pages["/haberler/elektrik-kesilince-elektrikli-arac-sarji-durur-mu/"]
    guide_text = visible_text(guide)
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(schema_types(load_schema(guide)))
    for required in (
        "Şarjın durması normaldir",
        "otomatik devam edeceğini varsaymayın",
        "Elektrikli araç evi otomatik olarak beslemez",
        "Yangın, duman veya can güvenliği riskinde ticaret ve test kapalıdır",
        "/hesaplama/elektrikli-arac-sarj-elektrik-kesintisi-hazirlik-plani/",
        "/sektor-rehberi/site-otel-isletme-elektrikli-arac-sarj-kesinti-surekliligi/",
    ):
        assert required in guide or required in guide_text, required

    planner = pages["/hesaplama/elektrikli-arac-sarj-elektrik-kesintisi-hazirlik-plani/"]
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
        "Yangın, duman, aşırı ısınma, su teması veya elektrik çarpması riskinde form ve ticaret kapalı",
        "Professional-only kabul ve düzeltici faaliyet gerekir",
        "Mevcut şarj kesintisi hazırlığı yeterli — yeni ürün almayın",
        "Amazon Türkiye veya başka mağaza bağlantısı yoktur",
    ):
        assert required in planner, required
    assert "Ad, telefon, e-posta, adres" in planner_text
    assert "Seçimler sunucuya gönderilmez" in planner_text

    sector = pages["/sektor-rehberi/site-otel-isletme-elektrikli-arac-sarj-kesinti-surekliligi/"]
    sector_text = visible_text(sector)
    assert {"Article", "BreadcrumbList", "ListItem"}.issubset(schema_types(load_schema(sector)))
    for required in (
        "Süreklilik ve kabul matrisi",
        "Gerçek kesinti ve enerji dönüşü görev/kabul testi",
        "Dinamik yük yönetimi",
        "Ağ, OCPP ve ödeme",
        "Bu sayfada Amazon Türkiye veya başka mağaza bağlantısı yoktur",
        "/kurumsal-elektrik-surekliligi-on-degerlendirme",
    ):
        assert required in sector or required in sector_text, required

    print(json.dumps({
        "ok": True,
        "routingVersion": 320,
        "newRoutes": list(ROUTES),
        "merchantLinksAdded": 0,
        "consumerAffiliateClasses": 0,
        "professionalOnly": True,
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorage": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
        "activeHazardCommerceClosed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
