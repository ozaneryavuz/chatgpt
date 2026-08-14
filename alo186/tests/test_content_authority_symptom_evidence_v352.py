from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "ne": read("alo186/haberler/notr-toprak-arasi-voltaj-kac-volt-olmali/index.html"),
        "evheat": read("alo186/haberler/ev-sarj-kablosu-fisi-konnektoru-isiniyor/index.html"),
        "genset": read("alo186/haberler/jenerator-yuk-alinca-voltaj-frekans-dusuyor/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-symptom-evidence-v352.json"))
    expected = {
        "/haberler/notr-toprak-arasi-voltaj-kac-volt-olmali/",
        "/haberler/ev-sarj-kablosu-fisi-konnektoru-isiniyor/",
        "/haberler/jenerator-yuk-alinca-voltaj-frekans-dusuyor/",
    }
    assert routing["version"] == 352
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    for page in pages.values():
        lowered = page.lower()
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
        assert '"@type":"Article"' in page
        assert '"@type":"FAQPage"' in page
        assert '"@type":"BreadcrumbList"' in page
        assert "Son doğrulama: 14 Ağustos 2026" in page
        assert "60 saniyelik karar" in page
        assert "Kaynaklar" in page
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "ALO186 bağımsız" in page

    ne = pages["ne"]
    for required in (
        "Türkiye için evrensel kabul sınırı değildir",
        "DIY köprüleme yapmayın",
        "faz-nötr V",
        "nötr-toprak V",
        "/haberler/notr-kablosu-isiniyor-ucuncu-harmonik-neden/",
        "/haberler/inverter-eps-backup-notr-toprak-rcd-kabul-testi",
        "IEC 60364-8-82:2022+AMD1:2026",
    ):
        assert required in ne

    evheat = pages["evheat"]
    for required in (
        "neresi ısınıyor?",
        "Kabloyu suyla/buzla soğutmak",
        "IEC 62196-1:2025",
        "üç kırmızı",
        "/haberler/ev-sarj-baslayinca-sigorta-kacak-akim-rolesi-atiyor/",
        "/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul",
        "Kablo almadan önce sıcaklığın kaynağını doğrulayın",
    ):
        assert required in evheat

    genset = pages["genset"]
    for required in (
        "Gerilim düşümü ile frekans düşümü aynı şey değildir",
        "ISO 8528-5:2025",
        "başlangıç kVA",
        "AVR / alternatör",
        "Evrensel “%X düşerse arızalı” kuralı kullanılmaz",
        "/haberler/jenerator-yuk-bankasi-wet-stacking-dusuk-yuk-kabul-testi",
        "/haberler/ups-giris-thdi-jenerator-uyumluluk-kabul-testi",
    ):
        assert required in genset

    print({
        "ok": True,
        "version": 352,
        "routes": 3,
        "merchantLinks": 0,
        "schemas": ["Article", "FAQPage", "BreadcrumbList"],
        "policy": "evidence-first / no-buy-first / professional-only for energized work",
    })


if __name__ == "__main__":
    main()
