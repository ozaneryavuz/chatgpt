from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "ev": read("alo186/haberler/ev-sarj-uzatma-kablosu-kullanilir-mi/index.html"),
        "pv": read("alo186/haberler/ges-inverter-asiri-isiniyor-temperature-derating/index.html"),
        "gen": read("alo186/haberler/jenerator-mars-basiyor-ama-calismiyor-overcrank/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-v363-ev-extension-pv-thermal-gen-crank.json"))
    expected = {
        "/haberler/ev-sarj-uzatma-kablosu-kullanilir-mi/",
        "/haberler/ges-inverter-asiri-isiniyor-temperature-derating/",
        "/haberler/jenerator-mars-basiyor-ama-calismiyor-overcrank/",
    }
    assert routing["version"] == 363
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

    ev = pages["ev"]
    for required in (
        "uzatma kablosu",
        "Mobile Connector",
        "/haberler/ev-sarj-kablosu-fisi-konnektoru-isiniyor/",
        "/hesaplama/ev-sarj-gucu-suresi-elektrik-altyapi-uygunluk/",
        "EVSE–priz–mesafe–ısı kanıt paketi",
    ):
        assert required in ev

    pv = pages["pv"]
    for required in (
        "Temperature derating",
        "Sıcaklık–DC–AC–alarm matrisi",
        "/haberler/ges-string-akimi-dusuk-mppt-farki-teshis/",
        "/haberler/ges-inverter-izolasyon-hatasi-riso-low/",
        "Event 8003",
    ):
        assert required in pv

    gen = pages["gen"]
    for required in (
        "Overcrank",
        "Komut–crank–yakıt–alarm matrisi",
        "/haberler/jenerator-otomatikte-ama-elektrik-kesilince-calismiyor/",
        "/haberler/jenerator-yakit-kalitesi-su-mikrobiyal-kontaminasyon-kabul/",
        "karbon monoksit",
    ):
        assert required in gen

    print({
        "ok": True,
        "version": 363,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "intent-separated / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
