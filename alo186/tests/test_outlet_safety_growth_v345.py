from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    guide = read("alo186/haberler/priz-isiniyor-cizirti-yanik-kokusu-ne-yapmali/index.html")
    tool = read("alo186/hesaplama/priz-fis-elektrik-guvenlik-belirti-ayirici/index.html")
    tool_js = read("alo186/hesaplama/priz-fis-elektrik-guvenlik-belirti-ayirici/app.js")
    hub = read("alo186/ev-elektrik-guvenlik-kontrol-merkezi/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/outlet-safety-growth-v345.json"))
    decision = json.loads(read("alo186/deployment/affiliate-category-decisions/outlet-safety-growth-v345.json"))

    assert routing["version"] == 345
    assert {r["canonicalPath"] for r in routing["routes"]} == {
        "/haberler/priz-isiniyor-cizirti-yanik-kokusu-ne-yapmali/",
        "/hesaplama/priz-fis-elektrik-guvenlik-belirti-ayirici/",
        "/ev-elektrik-guvenlik-kontrol-merkezi/",
    }

    # Search guide is safety-first and not commercial.
    assert "amazon.com.tr" not in guide.lower()
    for required in (
        "Olağandışı sıcak",
        "cızırtı",
        "yanık kokusu",
        "Affiliate kapalı",
        "/hesaplama/priz-fis-elektrik-guvenlik-belirti-ayirici/",
        "/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/",
        "ALO186 resmî kurum değildir",
    ):
        assert required in guide

    # Privacy-safe, no-buy-first triage with local retention reminders.
    lowered = (tool + tool_js + hub).lower()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage"):
        assert forbidden not in lowered
    assert "yeni ürün almayın" in (tool + tool_js).lower()
    assert "BEGIN:VCALENDAR" in tool_js
    for days in ("30", "90", "365"):
        assert days in tool and days in hub
    assert "Ticari yolu kapatın" in tool_js
    assert "affiliate ürün bağlantısı açılmaz" in tool_js
    assert "/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/" in tool_js

    # Hub is a recurring safety center, not a merchant catalog.
    assert "amazon.com.tr" not in hub.lower()
    assert "yeni affiliate kategorisi açılmadı" in hub.lower()
    for path in (
        "/hesaplama/priz-fis-elektrik-guvenlik-belirti-ayirici/",
        "/hesaplama/aydinlatma-titreme-guvenlik-ayirici/",
        "/hesaplama/gerilim-koruma-cozum-secici/",
        "/fatura-ve-sayac-kontrol-merkezi/",
    ):
        assert path in hub

    # No new affiliate class or merchant link; fixed-installation tools are blocked.
    assert decision["newAffiliateClasses"] == 0
    assert decision["newMerchantLinks"] == 0
    blocked = set(decision["blockedConsumerAffiliateClasses"])
    assert {"wall-outlet-or-switch", "socket-wiring-tester", "non-contact-voltage-detector", "breaker-or-rcd"} <= blocked
    for claim in ("unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"):
        assert claim in decision["mustNotClaim"]

    forbidden_schema = ('"@type":"Product"', '"@type":"Offer"', 'AggregateRating', '"@type":"Review"')
    for page in (guide, tool, hub):
        for token in forbidden_schema:
            assert token not in page

    print({
        "ok": True,
        "version": 345,
        "newRoutes": 3,
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "retention": "local 30/90/365 ICS",
        "privacy": "no network or persistent browser storage",
    })


if __name__ == "__main__":
    main()
