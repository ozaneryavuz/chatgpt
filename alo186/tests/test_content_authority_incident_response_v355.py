from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "evlock": read("alo186/haberler/ev-sarj-kablosu-kilitli-kaldi-fis-cikmiyor/index.html"),
        "genset": read("alo186/haberler/jenerator-otomatikte-ama-elektrik-kesilince-calismiyor/index.html"),
        "upsbattery": read("alo186/haberler/ups-akusu-sisti-sicak-koku-var-ne-yapmali/index.html"),
    }
    routing = json.loads(
        read("alo186/deployment/routing-overlays/content-authority-incident-response-v355.json")
    )
    expected = {
        "/haberler/ev-sarj-kablosu-kilitli-kaldi-fis-cikmiyor/",
        "/haberler/jenerator-otomatikte-ama-elektrik-kesilince-calismiyor/",
        "/haberler/ups-akusu-sisti-sicak-koku-var-ne-yapmali/",
    }

    assert routing["version"] == 355
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

    evlock = pages["evlock"]
    for required in (
        "kabloyu zorlamayın",
        "manuel bırakma",
        "yalnız araç aktif şarj etmiyorken",
        "turuncu yüksek gerilim",
        "Ford Support",
        "/haberler/ev-sarj-kablosu-fisi-konnektoru-isiniyor/",
        "/hesaplama/ev-sarj-gucu-suresi-elektrik-altyapi-uygunluk/",
        "yeni kablo almadan önce",
    ):
        assert required in evlock

    genset = pages["genset"]
    for required in (
        "AUTO/Ready",
        "Hiç marş yok",
        "ATS start kontaklarını köprülemek",
        "start komutu",
        "T1 yardımcı beslemesi",
        "/haberler/jenerator-calisiyor-ama-elektrik-gelmiyor-ats-transfer-etmiyor/",
        "/haberler/jenerator-aku-sarj-cihazi-blok-isitici-hazirlik-kabul",
        "7 zaman damgası",
    ):
        assert required in genset

    upsbattery = pages["upsbattery"]
    for required in (
        "Şişme / kabin deformasyonu",
        "şebekeden ayrılmış olsa bile",
        "şişmiş aküyü tornavida ile kanırtmayın",
        "IEC 62040-1",
        "14 July 2026",
        "/haberler/ups-aku-runtime-kalibrasyon-desarj-kapasite-kabul-testi",
        "/haberler/ups-surekli-otuyor-bip-sesi-alarm-ne-anlama-gelir/",
        "yeni akü siparişinden önce",
    ):
        assert required in upsbattery

    print(
        {
            "ok": True,
            "version": 355,
            "routes": 3,
            "merchantLinks": 0,
            "schemas": ["Article", "FAQPage", "BreadcrumbList"],
            "policy": "incident-first / no-buy-first / professional-only for energized or damaged systems",
        }
    )


if __name__ == "__main__":
    main()
