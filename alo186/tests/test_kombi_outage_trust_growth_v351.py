from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_all(page: str, values: tuple[str, ...]) -> None:
    lowered = page.lower()
    for value in values:
        assert value.lower() in lowered, value


def main() -> None:
    article = read("alo186/haberler/elektrik-kesilince-kombi-calisir-mi-elektrik-gelince-ne-yapmali/index.html")
    tool = read("alo186/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-kontrol/index.html")
    b2b = read("alo186/sektor-rehberi/site-otel-kombi-kazan-elektrik-kesintisi-isitma-surekliligi/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/kombi-outage-trust-growth-v351.json"))

    expected = {
        "/haberler/elektrik-kesilince-kombi-calisir-mi-elektrik-gelince-ne-yapmali/",
        "/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-kontrol/",
        "/sektor-rehberi/site-otel-kombi-kazan-elektrik-kesintisi-isitma-surekliligi/",
    }
    assert routing["version"] == 351
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    for page in (article, tool, b2b):
        lowered = page.lower()
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
        assert '"@type":"BreadcrumbList"' in page
        assert "ALO186" in page
        assert "resmî kurum" in page or "kamu kurumu" in page
        assert "yeni ürün almayın" in lowered
        assert "fiyat" in lowered and "stok" in lowered and "puan" in lowered and "garanti" in lowered
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "Review" not in page

    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    require_all(article, (
        "60 saniyelik karar",
        "Evrensel reset sayısı",
        "Doğal Gaz Acil 187",
        "UPS, regülatör veya jeneratör neden otomatik önerilmez",
        "/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-kontrol/",
        "DemirDöküm",
        "Vaillant",
        "Enerya",
    ))

    assert '"@type":"WebApplication"' in tool
    assert '"@type":"FAQPage"' in tool
    assert 'type="text"' not in tool
    assert "textarea" not in tool.lower()
    assert "localStorage" not in tool
    assert "sessionStorage" not in tool
    assert "XMLHttpRequest" not in tool
    assert "fetch(" not in tool
    require_all(tool, (
        "Gaz kokusu, karbonmonoksit alarmı",
        "Evinizde elektrik geri geldi mi?",
        "kendi marka/model kullanım kılavuzunuza",
        "Bu araçta affiliate bağlantısı yoktur",
        "Doğal Gaz Acil 187",
        "30 gün sonra kontrol",
        "Isıtma sezonu öncesi 180 gün",
    ))

    assert '"@type":"Article"' in b2b
    assert '"@type":"FAQPage"' in b2b
    require_all(b2b, (
        "uçtan uca kabul matrisi",
        "Jeneratör / ATS",
        "BMS / alarm / personel",
        "Professional-only gelir modeli",
        "Bu sayfada merchant bağlantısı yoktur",
        "ısıtma sezonu",
        "/kurumsal-elektrik-surekliligi-on-degerlendirme",
    ))

    print({
        "ok": True,
        "version": 351,
        "newRoutes": 3,
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "privacy": "categorical/local-only/no-storage",
        "riskMode": "gas-and-electric-safety-first / manual-first / no-buy-first",
    })


if __name__ == "__main__":
    main()
