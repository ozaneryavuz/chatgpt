from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "ev": read("alo186/haberler/ev-sarj-gucu-dusuk-11kw-yerine-yavas-sarj/index.html"),
        "pv": read("alo186/haberler/ges-string-akimi-dusuk-mppt-farki-teshis/index.html"),
        "ups": read("alo186/haberler/ups-bypass-unavailable-out-of-tolerance-ne-demek/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-ev-string-bypass-v361.json"))
    expected = {
        "/haberler/ev-sarj-gucu-dusuk-11kw-yerine-yavas-sarj/",
        "/haberler/ges-string-akimi-dusuk-mppt-farki-teshis/",
        "/haberler/ups-bypass-unavailable-out-of-tolerance-ne-demek/",
    }
    assert routing["version"] == 361
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
        "on-board charger",
        "Dinamik Güç Yönetimi",
        "/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul/",
        "/haberler/ev-sarj-kablosu-fisi-konnektoru-isiniyor/",
        "OBC–EVSE–faz–yük–termal kanıt matrisi",
    ):
        assert required in ev

    pv = pages["pv"]
    for required in (
        "I-V eğrisi",
        "MPPT",
        "/haberler/ges-mc4-konnektor-capraz-eslestirme-krimp-kabul/",
        "/haberler/ges-inverter-izolasyon-hatasi-riso-low/",
        "Zaman–ışınım–string V/I–MPPT–I-V matrisi",
    ):
        assert required in pv

    ups = pages["ups"]
    for required in (
        "Bypass frequency out of tolerance",
        "Bypass phase missing",
        "Bypass phase sequence incorrect",
        "Inverter output is not in phase with bypass input",
        "/haberler/ups-bakim-bypass-geri-besleme-kilitleme-kabul-testi/",
        "Bypass V/Hz–faz–kesici–senkron matrisi",
    ):
        assert required in ups

    print({
        "ok": True,
        "version": 361,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "intent-separated / evidence-first / no-buy-first / professional-only energized work",
    })


if __name__ == "__main__":
    main()
