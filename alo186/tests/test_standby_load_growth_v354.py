from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    article = read("alo186/haberler/kapali-cihaz-elektrik-harcar-mi-bekleme-modu-standby-tuketimi/index.html")
    tool = read("alo186/hesaplama/bekleme-modu-standby-kwh-hesaplama/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/standby-load-growth-v354.json"))

    expected = {
        "/haberler/kapali-cihaz-elektrik-harcar-mi-bekleme-modu-standby-tuketimi/",
        "/hesaplama/bekleme-modu-standby-kwh-hesaplama/",
    }
    assert routing["version"] == 354
    assert len(routing["routes"]) == 2
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    for page in (article, tool):
        lowered = page.lower()
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in page
        assert '"@type":"BreadcrumbList"' in page
        assert "bağımsız" in lowered
        assert "resmî" in lowered
        assert "yeni ürün almayın" in lowered
        assert "fiyat" in lowered and "stok" in lowered and "puan" in lowered and "garanti" in lowered
        assert "amazon.com.tr" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "Review" not in page

    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    for required in (
        "Off mode",
        "Standby",
        "Networked standby",
        "No-buy-first karar sırası",
        "/hesaplama/bekleme-modu-standby-kwh-hesaplama/",
        "/hesaplama/elektrik-faturasi-kwh-gun-tuketim-karsilastirma/",
        "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/",
        "Bu rehberde doğrudan Amazon veya başka merchant bağlantısı yoktur",
        "Avrupa Komisyonu",
        "U.S. Department of Energy",
    ):
        assert required in article

    assert '"@type":"WebApplication"' in tool
    assert '"@type":"FAQPage"' in tool
    assert "type=\"text\"" not in tool
    assert "textarea" not in tool.lower()
    assert "localStorage" not in tool
    assert "sessionStorage" not in tool
    assert "XMLHttpRequest" not in tool
    assert "fetch(" not in tool
    for required in (
        "Ölçülmüş standby gücü",
        "30 güne normalize",
        "Bu sayfada merchant bağlantısı yoktur",
        "Koşullar tamamlanmıyorsa yeni ürün almayın",
        "7 gün sonra yeniden ölç",
        "30 gün sonra faturayla karşılaştır",
        "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi/",
    ):
        assert required in tool

    # Internal link only; merchant link remains owned by the existing gated selector.
    assert "amazon.com.tr" not in article.lower()
    assert "amazon.com.tr" not in tool.lower()

    print({
        "ok": True,
        "version": 354,
        "newRoutes": 2,
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "privacy": "local-only/no-storage/no-identifiers",
        "conversion": "existing-gated-energy-meter-selector-only",
    })


if __name__ == "__main__":
    main()
