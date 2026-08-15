from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "smoke": read("alo186/haberler/jenerator-siyah-beyaz-mavi-duman-neden-atar/index.html"),
        "charge": read("alo186/haberler/inverter-akuyu-sarj-etmiyor-charge-disabled-bms/index.html"),
        "night": read("alo186/haberler/ges-inverter-gece-elektrik-tuketir-mi-night-consumption/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-smoke-charge-night-v360.json"))
    expected = {
        "/haberler/jenerator-siyah-beyaz-mavi-duman-neden-atar/",
        "/haberler/inverter-akuyu-sarj-etmiyor-charge-disabled-bms/",
        "/haberler/ges-inverter-gece-elektrik-tuketir-mi-night-consumption/",
    }

    assert routing["version"] == 360
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

    smoke = pages["smoke"]
    for required in (
        "Renk bir belirti; teşhis değildir",
        "wet stacking",
        "duman veya ateş",
        "/haberler/jenerator-yuk-alinca-voltaj-frekans-dusuyor/",
        "/haberler/jenerator-yakit-kalitesi-su-mikrobiyal-kontaminasyon-kabul/",
        "Duman–yük–sıcaklık kabul matrisi",
    ):
        assert required in smoke

    charge = pages["charge"]
    for required in (
        "charge disabled",
        "allow-to-charge",
        "charge current",
        "/haberler/inverter-yuk-baglayinca-kapaniyor-overload-low-battery/",
        "Kaynak–izin–akım–SoC matrisi",
        "BMS'yi köprülemeyin",
    ):
        assert required in charge

    night = pages["night"]
    for required in (
        "night consumption",
        "Q on Demand 24/7",
        "DATCOM",
        "/fatura-ve-sayac-kontrol-merkezi/",
        "/haberler/ges-inverter-reaktif-guc-cos-phi-qv-kabul-testi/",
        "Model–mod–gece kWh matrisi",
    ):
        assert required in night

    print({
        "ok": True,
        "version": 360,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "intent-separated / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
