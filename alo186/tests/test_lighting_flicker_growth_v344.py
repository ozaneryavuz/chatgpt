from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALO = ROOT / "alo186"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    guide = read("alo186/haberler/led-ampul-titriyor-isiklar-neden-titriyor/index.html")
    tool = read("alo186/hesaplama/aydinlatma-titreme-guvenlik-ayirici/index.html")
    tool_js = read("alo186/hesaplama/aydinlatma-titreme-guvenlik-ayirici/app.js")
    selector = read("alo186/amazon-elektrik-urunleri/led-ampul-uygunluk-secimi/index.html")
    selector_js = read("alo186/amazon-elektrik-urunleri/led-ampul-uygunluk-secimi/app.js")
    damage = read("alo186/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/lighting-flicker-growth-v344.json"))
    decision = json.loads(read("alo186/deployment/affiliate-category-decisions/lighting-flicker-growth-v344.json"))

    assert routing["version"] == 344
    assert len(routing["routes"]) == 3
    assert {r["canonicalPath"] for r in routing["routes"]} == {
        "/haberler/led-ampul-titriyor-isiklar-neden-titriyor/",
        "/hesaplama/aydinlatma-titreme-guvenlik-ayirici/",
        "/amazon-elektrik-urunleri/led-ampul-uygunluk-secimi/",
    }

    # Trust-critical deadline source is current in repository source, not only build-time rewritten.
    assert "Madde 26/1" in damage
    assert "30 gün" in damage
    for stale_claim in (
        "özel süre 10 iş günüdür",
        "zarar tarihinden itibaren 10 iş günü içinde",
        "hasar tazmini talebi için 10 iş günlük süre",
    ):
        assert stale_claim not in damage
    assert "önceki düzenlemeye ait süre anlatımı" in damage
    assert "ALO186 bağımsız bilgi platformudur" in damage

    # Search guide is non-commercial and routes risk before purchase.
    assert "amazon.com.tr" not in guide.lower()
    for required in (
        "Birden fazla oda",
        "yanık kokusu",
        "Dimmer",
        "/haberler/notr-kopmasi-nasil-anlasilir",
        "/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi",
        "/hesaplama/aydinlatma-titreme-guvenlik-ayirici/",
        "ALO186 resmî kurum değildir",
    ):
        assert required in guide

    # Privacy-safe, no-buy-first triage.
    lowered_tool = (tool + tool_js).lower()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage"):
        assert forbidden not in lowered_tool
    assert "Yeni ürün almayın" in tool_js
    assert "90" in tool_js and "BEGIN:VCALENDAR" in tool_js
    assert "/amazon-elektrik-urunleri/led-ampul-uygunluk-secimi/" in tool_js
    assert "multi_room" in tool_js and "whole_home" in tool_js

    # Exactly one low-risk affiliate class; merchant href does not exist in initial HTML.
    assert selector.count("data-gate") == 8
    assert 'href="https://www.amazon.com.tr' not in selector
    assert "Reklam / satış ortaklığı açıklaması" in selector
    assert "Fiyat, stok, satıcı, teslimat, puan, yorum ve garanti" in selector
    assert "yeni ürün almayın" in selector.lower()
    assert "https://www.amazon.com.tr/s?k=led+ampul&tag=alo186rehber-21" in selector_js
    assert "n===8" in selector_js
    assert "removeAttribute('href')" in selector_js
    assert "sponsored noopener" in selector_js

    forbidden_schema = ('"@type":"Product"', '"@type":"Offer"', 'AggregateRating', '"@type":"Review"')
    for token in forbidden_schema:
        assert token not in selector

    assert decision["newAffiliateClasses"] == 1
    assert decision["newMerchantLinks"] == 1
    assert decision["affiliateClass"] == "replaceable-led-bulb"
    assert "integrated-led-fixture-or-driver" in decision["blockedConsumerAffiliateClasses"]
    for claim in ("unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"):
        assert claim in decision["mustNotClaim"]

    print({
        "ok": True,
        "version": 344,
        "newRoutes": 3,
        "newAffiliateClasses": 1,
        "newMerchantLinks": 1,
        "deadlineSource": "30 days",
        "privacy": "no network or persistent browser storage",
    })


if __name__ == "__main__":
    main()
