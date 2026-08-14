from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "rcd": read("alo186/haberler/yagmurda-kacak-akim-rolesi-atiyor-nem-izolasyon-arizasi/index.html"),
        "evrain": read("alo186/haberler/yagmurda-elektrikli-arac-sarj-edilir-mi-su-girisi/index.html"),
        "meter": read("alo186/haberler/elektrik-sayaci-ekrani-kapali-arizali-ne-yapmali/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-weather-meter-v357.json"))
    expected = {
        "/haberler/yagmurda-kacak-akim-rolesi-atiyor-nem-izolasyon-arizasi/",
        "/haberler/yagmurda-elektrikli-arac-sarj-edilir-mi-su-girisi/",
        "/haberler/elektrik-sayaci-ekrani-kapali-arizali-ne-yapmali/",
    }

    assert routing["version"] == 357
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == expected
    assert len({route["source"] for route in routing["routes"]}) == 3

    for page in pages.values():
        lowered = page.lower()
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
        assert '"@type":"Article"' in page
        assert '"@type":"FAQPage"' in page
        assert '"@type":"BreadcrumbList"' in page
        assert "Son doğrulama: 15 Ağustos 2026" in page
        assert "60 saniyelik karar" in page
        assert "Kaynaklar" in page
        assert "ALO186 bağımsız" in page
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "priceCurrency" not in page

    rcd = pages["rcd"]
    for required in (
        "RCD'yi köprülemeyin",
        "izolasyon direnci",
        "kuru ve yağışlı dönem",
        "IEC 61557-2",
        "/haberler/kacak-akim-rolesi-neden-atar/",
        "/haberler/kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi/",
        "yeni RCD satın almak yerine",
    ):
        assert required in rcd

    evrain = pages["evrain"]
    for required in (
        "su girişi",
        "extreme weather",
        "doğrudan su püskürtülmemesini",
        "IEC 62196-1:2025",
        "/haberler/ev-sarj-baslayinca-sigorta-kacak-akim-rolesi-atiyor/",
        "/haberler/ev-sarj-kablosu-fisi-konnektoru-isiniyor/",
        "ürün değiştirmeyin",
    ):
        assert required in evrain

    meter = pages["meter"]
    for required in (
        "mühür",
        "dağıtım şirketi",
        "sayaç kontrolü",
        "Madde 51",
        "/haberler/elektrik-sayaci-nasil-okunur-t0-t1-t2-t3-endeks/",
        "/fatura-ve-sayac-kontrol-merkezi/",
        "Kontrol sonucu gelmeden",
    ):
        assert required in meter

    print({
        "ok": True,
        "version": 357,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "weather-event / no-buy-first / official-process-first",
    })


if __name__ == "__main__":
    main()
