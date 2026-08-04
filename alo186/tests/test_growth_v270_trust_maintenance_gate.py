#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"

ARTICLE = ALO / "haberler/elektrik-kesilince-otomatik-kapi-kepenk-garaj-kapisi-nasil-acilir/index.html"
GATE_TOOL = ALO / "hesaplama/otomatik-kapi-kepenk-elektrik-kesintisi-acil-plani/index.html"
MAINT_TOOL = ALO / "hesaplama/elektrik-kesintisi-ekipman-test-ve-bakim-plani/index.html"
ROUTING = ALO / "deployment/routing-overlays/growth-v270-trust-maintenance-gate.json"
DRIFT = ALO / "growth/live-drift/critical-pages-v270.json"
PATCH = ALO / "growth/live-drift/sites-delta-v270-homepage-evergreen.json"


def read(path: Path) -> str:
    assert path.exists(), f"Eksik dosya: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def assert_no_unsafe_commerce(html: str, label: str) -> None:
    lowered = html.lower()
    assert not re.search(r'href=["\'][^"\']*amazon\.', lowered), f"{label}: statik Amazon href bulundu"
    for token in ('"@type":"offer"', '"@type": "offer"', 'aggregaterating', '"@type":"review"'):
        assert token not in lowered, f"{label}: yasak ticari schema bulundu: {token}"
    for token in ("localstorage", "sessionstorage", "xmlhttprequest", "fetch("):
        assert token not in lowered, f"{label}: gereksiz veri/ağ yüzeyi bulundu: {token}"
    for personal in ('type="email"', 'type="tel"', 'name="email"', 'name="phone"', 'name="address"'):
        assert personal not in lowered, f"{label}: kişisel veri alanı bulundu: {personal}"


def assert_schema_types(html: str, types: tuple[str, ...], label: str) -> None:
    for schema_type in types:
        assert f'"@type":"{schema_type}"' in html or f'"@type": "{schema_type}"' in html, (
            f"{label}: {schema_type} schema eksik"
        )


def main() -> None:
    article = read(ARTICLE)
    gate = read(GATE_TOOL)
    maintenance = read(MAINT_TOOL)

    assert '<link rel="canonical" href="https://alo186.com/haberler/elektrik-kesilince-otomatik-kapi-kepenk-garaj-kapisi-nasil-acilir/">' in article
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/otomatik-kapi-kepenk-elektrik-kesintisi-acil-plani/">' in gate
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/elektrik-kesintisi-ekipman-test-ve-bakim-plani/">' in maintenance

    assert_schema_types(article, ("Article", "HowTo", "FAQPage", "BreadcrumbList"), "article")
    assert_schema_types(gate, ("WebApplication", "HowTo", "BreadcrumbList"), "gate tool")
    assert_schema_types(maintenance, ("WebApplication", "HowTo", "FAQPage", "BreadcrumbList"), "maintenance tool")

    for html, label in ((article, "article"), (gate, "gate tool"), (maintenance, "maintenance tool")):
        assert_no_unsafe_commerce(html, label)
        assert "Bağımsız" in html and "kamu kurumu değildir" in html, f"{label}: bağımsızlık açıklaması eksik"
        assert "112" in html, f"{label}: acil güvenlik sınırı eksik"
        assert "fiyat" not in html.lower() or "fiyat" in maintenance.lower(), "beklenmeyen fiyat iddiası"

    assert "Mevcut sistem güvenli çalışıyorsa yeni ürün almayın" in article
    assert "Mevcut güvenli düzen yeterliyse yeni ürün satın almayacağım" in gate
    assert "Mevcut çözüm hedefi sağlıyorsa yeni ürün almayacağım" in maintenance
    assert "Bu sayfada mağaza veya Amazon bağlantısı yoktur" in maintenance
    assert "90 günlük gerçek kesinti testi" in maintenance
    assert "90 günlük kesinti tatbikatı" in gate
    assert "text/calendar" in gate and "text/calendar" in maintenance
    assert "journey-events-v260.js" in gate and "journey-events-v260.js" in maintenance

    for source in (
        "https://www.hse.gov.uk/work-equipment-machinery/powered-gates/safety.htm",
        "https://www.hse.gov.uk/safetybulletins/poweredgates.htm",
        "https://www.geze.com.tr/",
    ):
        assert source in article, f"Birincil kaynak eksik: {source}"

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 270
    routes = {item["canonicalPath"]: item for item in routing["routes"]}
    expected = {
        "/haberler/elektrik-kesilince-otomatik-kapi-kepenk-garaj-kapisi-nasil-acilir/": "article",
        "/hesaplama/otomatik-kapi-kepenk-elektrik-kesintisi-acil-plani/": "tool",
        "/hesaplama/elektrik-kesintisi-ekipman-test-ve-bakim-plani/": "tool",
    }
    assert set(routes) == set(expected)
    for path, route_type in expected.items():
        assert routes[path]["type"] == route_type
        assert (ROOT / routes[path]["source"]).exists(), f"Routing source eksik: {path}"

    drift = json.loads(read(DRIFT))
    assert drift["version"] == 270
    pages = {item["id"]: item for item in drift["pages"]}
    assert pages["homepage-evergreen-commercial-trust"]["url"] == "https://alo186.com/"
    assert pages["www-alias-evergreen-commercial-trust"]["url"] == "https://www.alo186.com/"
    forbidden_home = set(pages["homepage-evergreen-commercial-trust"]["forbiddenText"])
    for stale in (
        "154 modeli doğrulanmış",
        "154 doğrulanmış ASIN",
        "50+ elektrik ürünü",
        "10 rehberin tamamını gör",
        "26 rehberin tamamını gör",
        "on iş günlük başvuru süresi",
    ):
        assert stale in forbidden_home, f"Ana sayfa drift yasağı eksik: {stale}"
    assert pages["equipment-maintenance-journey"]["forbidDirectAmazonHref"] is True
    assert pages["powered-gate-outage-tool"]["forbidDirectAmazonHref"] is True

    patch = json.loads(read(PATCH))
    assert patch["version"] == 270 and patch["priority"] == "P0"
    matches = {item["match"] for item in patch["replacements"]}
    assert "154 modeli doğrulanmış ürün için seçim kartları" in matches
    assert "EPDK tüketici bilgisinde on iş günlük başvuru süresi açıklanır." in matches
    assert patch["commercialConstraints"]["noPriceStockRatingWarrantyClaims"] is True
    assert patch["commercialConstraints"]["noBuyOutcomeRequired"] is True
    assert patch["institutionalConstraints"]["mustNotImplyEdasOrPublicAuthority"] is True

    # Qualifying gaps may route only to existing internal governed selectors; no marketplace URL here.
    for internal_path in (
        "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
        "/amazon-elektrik-urunleri/kamera-nvr-ups-yedek-guc-secimi/",
        "/amazon-elektrik-urunleri/akvaryum-pilli-usb-hava-motoru-secimi/",
        "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/",
        "/amazon-elektrik-urunleri/pilli-karbonmonoksit-alarmi-secimi/",
        "/amazon-elektrik-urunleri/pilli-su-kacagi-alarmi-secimi/",
    ):
        assert internal_path in maintenance, f"Güvenli kategori rotası eksik: {internal_path}"

    print(json.dumps({
        "ok": True,
        "routes": sorted(expected),
        "homepageStaleClaimsBlocked": len(forbidden_home),
        "directAmazonLinks": 0,
        "personalDataFields": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
