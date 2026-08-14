from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    pages = {
        "rcd": read("alo186/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/index.html"),
        "generator": read("alo186/haberler/jenerator-calisiyor-ama-elektrik-gelmiyor-ats-transfer-etmiyor/index.html"),
        "ups": read("alo186/haberler/ups-surekli-otuyor-bip-sesi-alarm-ne-anlama-gelir/index.html"),
    }
    routing = json.loads(read("alo186/deployment/routing-overlays/content-authority-symptom-triage-v346.json"))

    expected_routes = {
        "/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/",
        "/haberler/jenerator-calisiyor-ama-elektrik-gelmiyor-ats-transfer-etmiyor/",
        "/haberler/ups-surekli-otuyor-bip-sesi-alarm-ne-anlama-gelir/",
    }
    assert routing["version"] == 346
    assert {route["canonicalPath"] for route in routing["routes"]} == expected_routes
    assert len(routing["routes"]) == 3

    for name, page in pages.items():
        lowered = page.lower()
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
        assert '"@type":"Article"' in page
        assert '"@type":"FAQPage"' in page
        assert '"@type":"BreadcrumbList"' in page
        assert "Son doğrulama: 14 Ağustos 2026" in page
        assert "ALO186 resmî kurum değildir" in page
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert '"@type":"Review"' not in page
        assert "60 saniyelik karar" in page
        assert "Kaynaklar" in page
        assert "yeni ekipman satın" in lowered or "yeni ürün" in lowered or "satın" in lowered

    # RCD: do not encourage hazardous DIY fault injection.
    rcd = pages["rcd"]
    for required in (
        "nötr-toprak kısa devresi",
        "faz-toprak lamba deneyi",
        "açma akımı",
        "açma süresi",
        "/haberler/kacak-akim-rolesi-neden-surekli-atar",
        "/haberler/kacak-akim-toplam-kacak-butcesi-istenmeyen-acma-teshisi",
    ):
        assert required in rcd

    # Generator: engine-running must not be confused with actual load transfer.
    generator = pages["generator"]
    for required in (
        "Motor çalışması",
        "Jeneratör kaynağı kabulü",
        "ATS transfer komutu",
        "interlock",
        "/haberler/jenerator-ats-3-kutup-4-kutup-notr-rcd-kabul-testi",
        "/haberler/jenerator-yuk-bankasi-wet-stacking-dusuk-yuk-kabul-testi",
    ):
        assert required in generator

    # UPS: beep pattern is model-specific and active battery/fire symptoms close DIY path.
    ups = pages["ups"]
    for required in (
        "ses kodları modele göre değişir",
        "yük yüzdesini",
        "yanık kokusu",
        "rastgele reset",
        "/haberler/ups-aku-runtime-kalibrasyon-desarj-kapasite-kabul-testi",
        "/haberler/ups-giris-thdi-jenerator-uyumluluk-kabul-testi",
    ):
        assert required in ups

    print({
        "ok": True,
        "version": 346,
        "newRoutes": 3,
        "commercialLinks": 0,
        "structuredData": ["Article", "FAQPage", "BreadcrumbList"],
        "riskMode": "safety-first / no dangerous DIY",
    })


if __name__ == "__main__":
    main()
