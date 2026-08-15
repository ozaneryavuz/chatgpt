from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-asansor-ne-olur-mahsur-kalinca-ne-yapmali/index.html"
CALC = ROOT / "alo186/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-kontrolu/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/site-otel-asansor-elektrik-kesintisi-kurtarma-surekliligi/index.html"
ROUTES = ROOT / "alo186/deployment/routing-overlays/elevator-outage-safety-v368.json"
COMMERCE = ROOT / "alo186/content/commerce/elevator-outage-safety-v368.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def main() -> None:
    pages = [read(ARTICLE), read(CALC), read(SECTOR)]
    combined = "\n".join(pages)
    low = combined.casefold()

    # Safety-first: entrapment must never become a DIY or commerce journey.
    for required in (
        "kapıları zorlamayın",
        "kendi başınıza çık",
        "112",
        "alarm",
        "interkom",
        "yetkili servis",
        "affiliate",
        "bağımsız bilgilendirme platformudur",
    ):
        assert required.casefold() in low, required

    # No merchant surface or fabricated commerce metadata in this safety cluster.
    for forbidden in (
        "amazon.com.tr",
        "amzn.to",
        "pricecurrency",
        '"@type":"product"',
        '"@type":"offer"',
        "aggregaterating",
    ):
        assert forbidden not in low, forbidden

    # Calculator remains categorical and local-only.
    calc = pages[1].casefold()
    for forbidden in (
        "fetch(",
        "xmlhttprequest",
        "localstorage",
        "sessionstorage",
        "navigator.geolocation",
        "<textarea",
        'type="text"',
        'type="email"',
        'type="tel"',
    ):
        assert forbidden not in calc, forbidden
    assert "blob([body]" in calc
    assert "mevzuat tarihi değildir" in calc
    assert "yeni ürün almayın" in calc

    commerce = json.loads(read(COMMERCE))
    assert commerce["version"] == 368
    assert commerce["independentPlatform"] is True
    assert commerce["officialInstitutionImpersonation"] is False
    assert commerce["affiliateEligible"] is False
    assert commerce["newAffiliateCategories"] == 0
    assert commerce["merchantLinks"] == 0
    assert commerce["noBuyFirst"] is True
    assert set(commerce["prohibitedUnverifiedFields"]) == {"price", "stock", "rating", "warranty"}
    assert "elevator-ARD" in commerce["blockedProductClasses"]
    assert "generator-ATS-elevator-integration-acceptance" in commerce["professionalConversionClasses"]

    routing = json.loads(read(ROUTES))
    assert routing["version"] == 368
    expected = {
        "/haberler/elektrik-kesilince-asansor-ne-olur-mahsur-kalinca-ne-yapmali/",
        "/hesaplama/asansor-elektrik-kesintisi-kurtarma-hazirlik-kontrolu/",
        "/sektor-rehberi/site-otel-asansor-elektrik-kesintisi-kurtarma-surekliligi/",
    }
    assert {route["canonicalPath"] for route in routing["routes"]} == expected
    assert len({route["source"] for route in routing["routes"]}) == 3

    print({
        "ok": True,
        "version": 368,
        "routes": sorted(expected),
        "newAffiliateCategories": 0,
        "merchantLinks": 0,
        "personalDataFields": 0,
    })


if __name__ == "__main__":
    main()
