from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "rcd": read("alo186/haberler/kacak-akim-rolesi-kalkmiyor-reset-olmuyor/index.html"),
        "ev": read("alo186/haberler/ev-sarj-baslamiyor-wallbox-araca-bagli-ama-sarj-etmiyor/index.html"),
        "gen": read("alo186/haberler/elektrik-geldi-jenerator-durmuyor-ats-sebeke-algilama/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-v365-rcd-ev-gen.json"))
    expected = {
        "/haberler/kacak-akim-rolesi-kalkmiyor-reset-olmuyor/",
        "/haberler/ev-sarj-baslamiyor-wallbox-araca-bagli-ama-sarj-etmiyor/",
        "/haberler/elektrik-geldi-jenerator-durmuyor-ats-sebeke-algilama/",
    }
    assert routing["version"] == 365
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
        "RCCB/RCBO",
        "RCD reset–devre–belirti kanıt paketi",
        "/haberler/kacak-akim-rolesi-neden-atar/",
        "/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/",
        "/hesaplama/sigorta-kacak-akim-belirti-ayirici/",
    ):
        assert required in rcd

    ev = pages["ev"]
    for required in (
        "Wallbox araca bağlı",
        "Durum ışığı–araç talebi–ayar–hata kodu–kaynak matrisi",
        "/haberler/ev-sarj-gucu-dusuk-11kw-yerine-yavas-sarj/",
        "/haberler/ev-sarj-baslayinca-sigorta-kacak-akim-rolesi-atiyor/",
        "Tesla Türkiye",
    ):
        assert required in ev

    gen = pages["gen"]
    for required in (
        "utility sensing",
        "Şebeke dönüşü–ATS–retransfer–cooldown kanıt matrisi",
        "/haberler/jenerator-calisiyor-ama-elektrik-gelmiyor-ats-transfer-etmiyor/",
        "/haberler/jenerator-ats-3-kutup-4-kutup-notr-rcd-kabul-testi/",
        "N1/N2",
    ):
        assert required in gen

    print({
        "ok": True,
        "version": 365,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "intent-separated / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
