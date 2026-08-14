from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "partial": read("alo186/haberler/evde-bazi-prizlerde-elektrik-var-bazilarinda-yok-faz-arizasi/index.html"),
        "ev": read("alo186/haberler/ev-sarj-baslayinca-sigorta-kacak-akim-rolesi-atiyor/index.html"),
        "neutral": read("alo186/haberler/notr-kablosu-isiniyor-ucuncu-harmonik-neden/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-intent-triage-v349.json"))

    expected_routes = {
        "/haberler/evde-bazi-prizlerde-elektrik-var-bazilarinda-yok-faz-arizasi/",
        "/haberler/ev-sarj-baslayinca-sigorta-kacak-akim-rolesi-atiyor/",
        "/haberler/notr-kablosu-isiniyor-ucuncu-harmonik-neden/",
    }
    assert routing["version"] == 349
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == expected_routes

    for name, page in pages.items():
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
        assert "satın" in lowered or "ürün almayın" in lowered

    partial = pages["partial"]
    for required in (
        "Tek oda veya tek devre",
        "Bina veya sokak etkisi",
        "186 / dağıtım şirketi",
        "pano kapağını açmayın",
        "/edas-bul",
        "/haberler/gerilim-dengesizligi-vuf-edas-teknik-kalite-olcum-dosyasi",
        "/haberler/gerilim-cukuru-yukselmesi-kisa-kesinti-edas-olay-kaydi",
    ):
        assert required in partial

    ev = pages["ev"]
    for required in (
        "hangi koruma attı",
        "RCD/RCBO",
        "hata kodu",
        "tekrar tekrar resetlemeyin",
        "/haberler/ev-sarj-kacak-akim-rcd-tip-b-rdc-dd-6ma-kabul",
        "/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-fail-safe-kabul",
        "/haberler/ev-sarj-notr-pen-kopmasi-dokunma-gerilimi-koruma-kabul",
    ):
        assert required in ev

    neutral = pages["neutral"]
    for required in (
        "gerçek RMS",
        "3., 9., 15.",
        "Gevşek/yüksek dirençli bağlantı",
        "evrensel kural değildir",
        "IEC 61000-4-30:2025",
        "/haberler/harmonikli-yuk-trafo-k-faktoru-derating-notr-termal-kabul",
        "/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-kabul-testi",
    ):
        assert required in neutral

    print({
        "ok": True,
        "version": 349,
        "newRoutes": 3,
        "commercialLinks": 0,
        "structuredData": ["Article", "FAQPage", "BreadcrumbList"],
        "riskMode": "safety-first / evidence-first / no-buy-first",
    })


if __name__ == "__main__":
    main()
