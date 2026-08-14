from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "ups": read("alo186/haberler/ups-elektrik-var-ama-akuden-calisiyor/index.html"),
        "riso": read("alo186/haberler/ges-inverter-izolasyon-hatasi-riso-low/index.html"),
        "pe": read("alo186/haberler/toprak-hattinda-akim-var-kacak-akim-neden/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-ups-riso-pe-v359.json"))
    expected = {
        "/haberler/ups-elektrik-var-ama-akuden-calisiyor/",
        "/haberler/ges-inverter-izolasyon-hatasi-riso-low/",
        "/haberler/toprak-hattinda-akim-var-kacak-akim-neden/",
    }

    assert routing["version"] == 359
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

    ups = pages["ups"]
    for required in (
        "input voltage",
        "input frequency",
        "on-battery",
        "transfer aralığını rastgele genişletmeyin",
        "FA156546",
        "/haberler/ups-giris-thdi-jenerator-uyumluluk-kabul-testi/",
        "yeni akü satın almak kök nedeni çözmez",
    ):
        assert required in ups

    riso = pages["riso"]
    for required in (
        "Isolation Fault",
        "Riso Low",
        "string bazlı izolasyon",
        "IEC 60364-7-712:2025",
        "IEC 62446-1",
        "/haberler/ges-panel-bypass-diyot-sicak-nokta-termal-iv-teshis/",
        "yeni panel almak gereksizdir",
    ):
        assert required in riso

    pe = pages["pe"]
    for required in (
        "toprağı sökmeyin",
        "faz ve nötr birlikte penslendiğinde",
        "IEC 61557-13:2023",
        "/haberler/kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi/",
        "gereksiz RCD veya topraklama malzemesi satın almayın",
    ):
        assert required in pe

    print({
        "ok": True,
        "version": 359,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "symptom-first / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
