from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
OVERLAY = SITE / "deployment/routing-overlays/project-journey-v315.json"
HUB_ROUTE = "/elektrik-proje-karar-merkezi"
PLANNER_ROUTE = "/hesaplama/elektrik-proje-hazirlik-plani/"
HUB = SITE / "elektrik-proje-karar-merkezi/index.html"
PLANNER = SITE / "hesaplama/elektrik-proje-hazirlik-plani/index.html"
FIELD = SITE / "haberler/elektrik-odasi-safti-busbar-kablo-tavasi-yangin-durdurucu-detaylari/index.html"
COORDINATION = SITE / "haberler/elektrik-odalari-saft-busbar-kablo-tava-yangin-durdurucu-koordinasyonu/index.html"

PROJECT_LINKS = {
    "/haberler/peyzaj-dis-alan-elektrik-aydinlatma-priz-sulama-projesi",
    "/haberler/yangin-algilama-acil-anons-cctv-kartli-gecis-data-entegrasyon-projesi",
    "/haberler/elektrik-odalari-saft-busbar-kablo-tava-yangin-durdurucu-koordinasyonu",
    "/haberler/elektrik-odasi-safti-busbar-kablo-tavasi-yangin-durdurucu-detaylari",
    "/haberler/cati-ges-avan-uygulama-proje-dc-ac-koruma-kabul-raporu",
    "/haberler/elektrik-ihale-paketi-kesif-metraj-sartname-marka-listesi-butce",
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


def direct_answer_words(html: str) -> set[str]:
    match = re.search(
        r'<div\s+class=["\'][^"\']*\banswer\b[^"\']*["\'][^>]*>(.*?)</div>',
        html,
        re.I | re.S,
    )
    assert match
    text = visible_text(match.group(1)).casefold()
    stop = {
        "elektrik", "yangın", "kablo", "busbar", "doğrudan", "cevap",
        "sistem", "geçiş", "olarak", "birlikte", "kontrol",
    }
    return {
        token for token in re.findall(r"[a-zçğıöşü0-9]+", text)
        if len(token) > 4 and token not in stop
    }


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / max(1, len(left | right))


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 315
    assert overlay["generatedAt"] == "2026-08-06"
    assert {item["canonicalPath"] for item in overlay["routes"]} == {HUB_ROUTE, PLANNER_ROUTE}

    hub = HUB.read_text(encoding="utf-8")
    planner = PLANNER.read_text(encoding="utf-8")
    field = FIELD.read_text(encoding="utf-8")
    coordination = COORDINATION.read_text(encoding="utf-8")

    for route, html in ((HUB_ROUTE, hub), (PLANNER_ROUTE, planner)):
        assert '<meta name="viewport"' in html and "width=device-width" in html
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert all(marker not in html.casefold() for marker in MERCHANT_MARKERS)
        kinds = schema_types(load_schema(html))
        assert not COMMERCIAL_SCHEMA.intersection(kinds)

    assert {"CollectionPage", "ItemList", "BreadcrumbList", "ListItem"}.issubset(
        schema_types(load_schema(hub))
    )
    assert all(link in hub for link in PROJECT_LINKS)
    assert PLANNER_ROUTE in hub
    hub_text = visible_text(hub)
    assert "Tasarım ve disiplin koordinasyonu" in hub_text
    assert "Saha uygulaması ve kabul kaydı" in hub_text
    assert "30 gün" in hub_text and "90 gün" in hub_text and "365 gün" in hub_text
    assert "satış ortaklığı bağlantısı yoktur" in hub_text.casefold()
    assert "professional-only" in hub_text.casefold()
    assert "yeni ürün alma" in hub_text.casefold()
    assert "EDAŞ, TEDAŞ, EPDK veya başka bir kamu kuruluşu değildir" in hub_text

    planner_text = visible_text(planner)
    assert {"WebApplication", "BreadcrumbList", "ListItem"}.issubset(
        schema_types(load_schema(planner))
    )
    assert len(re.findall(r'data-weight="[23]"', planner)) == 10
    assert not re.search(r'<input[^>]+type=["\'](?:text|email|tel|file|hidden)["\']', planner, re.I)
    lowered = planner.casefold()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "sendbeacon"):
        assert forbidden not in lowered
    for required in (
        "new Blob", "URL.createObjectURL", "BEGIN:VCALENDAR", "30/90/365",
        "Aktif tehlikede planlama ve ticari yol kapalıdır",
        "Satın almama sonucu", "Yeni ürün almayın",
        "satış ortaklığı bağlantısı yoktur",
    ):
        assert required in planner
    assert "Ad, telefon, e-posta, adres" in planner_text
    assert "Seçimler sunucuya gönderilmez" in planner_text
    assert "EDAŞ veya kamu kurumu değildir" in planner_text

    field_text = visible_text(field)
    assert "Yangın Durdurucu Kablo Geçişi: Saha Kabulü" in field
    assert "Koordinasyon değil, saha kanıtı" in field_text
    assert HUB_ROUTE in field and PLANNER_ROUTE in field
    assert "/haberler/elektrik-odalari-saft-busbar-kablo-tava-yangin-durdurucu-koordinasyonu" in field
    assert "satış ortaklığı bağlantısı yoktur" in field_text.casefold()
    assert "yeni bir malzeme satın almayın" in field_text.casefold()
    assert "ALO186; EDAŞ, TEDAŞ, EPDK, EMO, GİB veya başka bir kamu kuruluşu değildir" in field_text
    assert {"Article", "FAQPage", "BreadcrumbList", "Question", "Answer"}.issubset(
        schema_types(load_schema(field))
    )

    field_words = direct_answer_words(field)
    coordination_words = direct_answer_words(coordination)
    overlap = jaccard(field_words, coordination_words)
    assert overlap < 0.45, overlap
    assert re.search(r"<h1[^>]*>Yangın durdurucu kablo geçişi saha kabulü", field, re.I)
    assert re.search(r"<h1[^>]*>Elektrik odaları ve şaft detayları nasıl koordine edilir", coordination, re.I)

    print(json.dumps({
        "ok": True,
        "routingVersion": 315,
        "newRoutes": [HUB_ROUTE, PLANNER_ROUTE],
        "intentSplit": {
            "coordination": "oda/şaft/güzergah rezervasyonu",
            "fieldAcceptance": "penetrasyon/etiket/fotograf/as-built",
            "directAnswerJaccard": round(overlap, 3),
        },
        "projectGuidesLinked": len(PROJECT_LINKS),
        "personalDataFields": 0,
        "networkSubmission": False,
        "browserStorage": False,
        "merchantLinksAdded": 0,
        "commercialSchemaAdded": False,
        "noBuyOutcome": True,
        "revisitCycle": [30, 90, 365],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
