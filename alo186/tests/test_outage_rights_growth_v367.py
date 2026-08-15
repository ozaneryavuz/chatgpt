from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    article = read("alo186/haberler/elektrik-kesintisi-tazminati-nasil-alinir/index.html")
    calc = read("alo186/hesaplama/elektrik-kesintisi-tazminat-on-kontrolu/index.html")
    hub = read("alo186/elektrik-kesintisi-haklari-merkezi/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/outage-rights-v367.json"))
    commerce = json.loads(read("alo186/content/commerce/outage-rights-v367.json"))

    expected = {
        "/haberler/elektrik-kesintisi-tazminati-nasil-alinir/",
        "/hesaplama/elektrik-kesintisi-tazminat-on-kontrolu/",
        "/elektrik-kesintisi-haklari-merkezi/",
    }
    assert routing["version"] == 367
    assert {route["canonicalPath"] for route in routing["routes"]} == expected
    assert len({route["source"] for route in routing["routes"]}) == 3

    assert commerce["affiliateEligible"] is False
    assert commerce["newAffiliateCategories"] == 0
    assert commerce["merchantLinks"] == 0
    assert commerce["noBuyFirst"] is True
    assert commerce["prohibitedUnverifiedFields"] == ["price", "stock", "rating", "warranty"]

    pages = (article, calc, hub)
    for page in pages:
        lowered = page.lower()
        assert "alo186 bağımsız" in lowered
        assert "amazon.com.tr" not in lowered
        assert "amzn.to" not in lowered
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert "AggregateRating" not in page
        assert "priceCurrency" not in page
        assert "https://www.alo186.com" not in page

    assert '<link rel="canonical" href="https://alo186.com/haberler/elektrik-kesintisi-tazminati-nasil-alinir/">' in article
    assert "12 saati aşan" in article
    assert "/hesaplama/elektrik-kesintisi-sure-gunlugu/" in article
    assert "/hesaplama/kesinti-gunlugu/" not in article
    assert "Ürün veya affiliate önerisi yok" in article
    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    assert '"@type":"BreadcrumbList"' in article

    assert '<link rel="canonical" href="https://alo186.com/hesaplama/elektrik-kesintisi-tazminat-on-kontrolu/">' in calc
    assert '"@type":"WebApplication"' in calc
    assert "Bu araç tazminat hesaplamaz" in calc
    assert "12 saati aşan" in calc
    for forbidden in ("fetch(", "localStorage", "sessionStorage", "geolocation"):
        assert forbidden not in calc

    assert '<link rel="canonical" href="https://alo186.com/elektrik-kesintisi-haklari-merkezi/">' in hub
    assert '"@type":"CollectionPage"' in hub
    assert '"@type":"ItemList"' in hub
    assert "Bu merkez neden affiliate içermez?" in hub
    assert "/hesaplama/elektrik-kesintisi-sure-gunlugu/" in hub
    assert "/haberler/elektrik-kesintisi-cihaz-hasari-tazminat-edas-basvuru/" in hub

    print({
        "ok": True,
        "version": 367,
        "routes": 3,
        "merchantLinks": 0,
        "newAffiliateCategories": 0,
        "policy": "official-source-first / no-buy-first / privacy-first / non-governmental",
    })


if __name__ == "__main__":
    main()
