from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "afci": read("alo186/haberler/ges-inverter-dc-arc-fault-afci-alarmi/index.html"),
        "oil": read("alo186/haberler/jenerator-low-oil-pressure-dusuk-yag-basinci-alarmi/index.html"),
        "fan": read("alo186/haberler/ups-fan-fault-fan-inoperable-alarmi/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-v368-afci-oil-fan.json"))
    expected = {
        "/haberler/ges-inverter-dc-arc-fault-afci-alarmi/",
        "/haberler/jenerator-low-oil-pressure-dusuk-yag-basinci-alarmi/",
        "/haberler/ups-fan-fault-fan-inoperable-alarmi/",
    }
    assert routing["version"] == 368
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

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

    afci = pages["afci"]
    for required in (
        "DC Arc Fault",
        "AFCI Check Failure",
        "Alarm–string–konnektör–termal kanıt matrisi",
        "/haberler/ges-mc4-konnektor-capraz-eslestirme-krimp-kabul/",
        "/haberler/ges-inverter-izolasyon-hatasi-riso-low/",
        "IEC 63027:2023",
    ):
        assert required in afci

    oil = pages["oil"]
    for required in (
        "Low Oil Pressure",
        "Alarm–yağ seviyesi–sızıntı–çalışma saati matrisi",
        "/haberler/jenerator-mars-basiyor-ama-calismiyor-overcrank/",
        "/haberler/jenerator-siyah-beyaz-mavi-duman-neden-atar/",
        "ISO 8528-13:2026",
    ):
        assert required in oil

    fan = pages["fan"]
    for required in (
        "Fan Inoperable",
        "Alarm–fan–sıcaklık–yük kanıt matrisi",
        "/haberler/ups-bypass-unavailable-out-of-tolerance-ne-demek/",
        "/haberler/ups-akusu-sisti-sicak-koku-var-ne-yapmali/",
        "IEC 62040-1",
    ):
        assert required in fan

    print({
        "ok": True,
        "version": 368,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "incident-intent / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
