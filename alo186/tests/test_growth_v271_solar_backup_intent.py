#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"

ARTICLE = ALO / "haberler/elektrik-kesilince-gunes-paneli-calisir-mi/index.html"
TOOL = ALO / "hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/index.html"
ROUTING = ALO / "deployment/routing-overlays/growth-v271-solar-backup-intent.json"


def read(path: Path) -> str:
    assert path.exists(), f"Eksik dosya: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def assert_schema_types(html: str, types: tuple[str, ...], label: str) -> None:
    for schema_type in types:
        assert f'"@type":"{schema_type}"' in html or f'"@type": "{schema_type}"' in html, (
            f"{label}: {schema_type} schema eksik"
        )


def assert_safe(html: str, label: str) -> None:
    lowered = html.casefold()
    assert not re.search(r'href=["\'][^"\']*amazon\.', lowered), f"{label}: statik Amazon href bulundu"
    for token in ('"@type":"offer"', '"@type": "offer"', "aggregaterating", '"@type":"review"'):
        assert token not in lowered, f"{label}: yasak ticari schema bulundu: {token}"
    for token in ("localstorage", "sessionstorage", "xmlhttprequest", "fetch("):
        assert token not in lowered, f"{label}: gereksiz veri/ağ yüzeyi bulundu: {token}"
    for personal in ('type="email"', 'type="tel"', 'name="email"', 'name="phone"', 'name="address"'):
        assert personal not in lowered, f"{label}: kişisel veri alanı bulundu: {personal}"
    assert "bağımsız" in lowered and "kamu kurumu" in lowered, f"{label}: bağımsızlık açıklaması eksik"
    assert "112" in html, f"{label}: acil güvenlik sınırı eksik"


def main() -> None:
    article = read(ARTICLE)
    tool = read(TOOL)

    assert '<link rel="canonical" href="https://alo186.com/haberler/elektrik-kesilince-gunes-paneli-calisir-mi/">' in article
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/">' in tool

    assert_schema_types(article, ("Article", "HowTo", "FAQPage", "BreadcrumbList"), "article")
    assert_schema_types(tool, ("WebApplication", "HowTo", "FAQPage", "BreadcrumbList"), "tool")

    assert_safe(article, "article")
    assert_safe(tool, "tool")

    for token in (
        "anti-islanding",
        "Standart on-grid güneş sistemi",
        "Akü tek başına yeterli değildir",
        "Mevcut sistem gerçek testte hedefi sağlıyorsa yeni ürün almayın",
        "/hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/",
        "/isletme-surekliligi",
    ):
        assert token in article, f"Makale güven/niyet ifadesi eksik: {token}"

    for source in (
        "https://solar.huawei.com/id/products/sun2000-3-4-5-6ktl-l1/specs/",
        "https://www.fronius.com/tr-tr/turkey/gunes-enerjisi/kurulumcular-ve-partnerler/urunler-ve-hizmetler/ozellikler/fronius-acil-guec-modu",
        "https://manuals.sma.de/BU-STPH-xP63x/en-US/16824414475.html",
    ):
        assert source in article, f"Birincil kaynak eksik: {source}"

    for token in (
        "Bu sayfada mağaza veya Amazon bağlantısı yoktur",
        "Fiyat, stok, puan veya garanti bilgisi kullanılmaz",
        "Mevcut sistem yeterli: yeni ürün almayın",
        "professional_only",
        "life_safety_professional",
        "journey-events-v260.js",
        "text/calendar",
        "text/plain",
        "90 günlük kesinti tatbikatı",
        "Yıllık profesyonel kontrol",
        "ges-yedek-guc-on-degerlendirme-kapsami.txt",
    ):
        assert token in tool, f"Araç güven/dönüşüm ifadesi eksik: {token}"

    assert "alo186rehber-21" not in article and "alo186rehber-21" not in tool
    assert "Product" not in article and '"@type":"Product"' not in tool

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 271
    routes = {item["canonicalPath"]: item for item in routing["routes"]}
    expected = {
        "/haberler/elektrik-kesilince-gunes-paneli-calisir-mi/": "article",
        "/hesaplama/ges-elektrik-kesintisi-yedek-guc-uygunluk-kontrolu/": "tool",
    }
    assert set(routes) == set(expected)
    for path, route_type in expected.items():
        assert routes[path]["type"] == route_type
        assert (ROOT / routes[path]["source"]).exists(), f"Routing source eksik: {path}"

    print(json.dumps({
        "ok": True,
        "routes": sorted(expected),
        "directAmazonLinks": 0,
        "productSchemas": 0,
        "personalDataFields": 0,
        "repeatVisitIntervals": [30, 90, 365],
        "conversion": "professional_scope_download",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
