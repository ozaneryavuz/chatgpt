from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    guide = read("alo186/haberler/kacak-akim-rolesi-neden-atar/index.html")
    tool = read("alo186/hesaplama/sigorta-kacak-akim-belirti-ayirici/index.html")
    tool_js = read("alo186/hesaplama/sigorta-kacak-akim-belirti-ayirici/app.js")
    hub = read("alo186/ev-elektrik-guvenlik-kontrol-merkezi/index.html")
    routing = json.loads(read("alo186/deployment/routing-overlays/protection-trip-growth-v347.json"))
    decision = json.loads(read("alo186/deployment/affiliate-category-decisions/protection-trip-growth-v347.json"))

    assert routing["version"] == 347
    assert {r["canonicalPath"] for r in routing["routes"]} == {
        "/haberler/kacak-akim-rolesi-neden-atar/",
        "/hesaplama/sigorta-kacak-akim-belirti-ayirici/",
    }

    # Search guide distinguishes protection functions without DIY panel steps or commerce.
    assert "amazon.com.tr" not in guide.lower()
    for required in (
        "Aşırı akım koruması",
        "Artık akım koruması",
        "RCBO",
        "daha büyük amperli",
        "Affiliate kapalı",
        "/hesaplama/sigorta-kacak-akim-belirti-ayirici/",
        "/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/",
        "ALO186 resmî kurum değildir",
    ):
        assert required in guide
    for forbidden_phrase in (
        "nötr ile toprağı köprüleyin",
        "korumayı devre dışı bırakın ve kullanın",
        "daha büyük sigorta takın",
    ):
        assert forbidden_phrase not in guide.lower()

    # Privacy-safe, no-buy-first triage with local retention reminders.
    lowered = (tool + tool_js + hub).lower()
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage"):
        assert forbidden not in lowered
    assert "yeni ürün almayın" in lowered
    assert "BEGIN:VCALENDAR" in tool_js
    for days in ("30", "90", "365"):
        assert days in tool and days in hub
    assert "Ticari yolu kapatın" in tool_js
    assert "affiliate yolu kapalıdır" in tool_js
    assert "/haberler/kacak-akim-rolesi-neden-atar/" in tool_js
    assert "/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/" in tool_js

    # Retention hub routes protection-trip intent to the new no-commerce tool.
    assert "/hesaplama/sigorta-kacak-akim-belirti-ayirici/" in hub
    assert "MCB · RCD/RCCB · RCBO" in hub
    assert "yeni cihaz, tadilat, nem olayı veya tekrar eden koruma açması" in hub
    assert "amazon.com.tr" not in hub.lower()

    # Fixed protection stays professional-only; commerce metadata is explicitly blocked.
    assert decision["newAffiliateClasses"] == 0
    assert decision["newMerchantLinks"] == 0
    blocked = set(decision["blockedConsumerAffiliateClasses"])
    assert {"mcb-or-circuit-breaker", "rcd-or-rccb", "rcbo", "distribution-board-component"} <= blocked
    for claim in ("unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"):
        assert claim in decision["mustNotClaim"]

    forbidden_schema = ('"@type":"Product"', '"@type":"Offer"', 'AggregateRating', '"@type":"Review"')
    for page in (guide, tool, hub):
        for token in forbidden_schema:
            assert token not in page

    assert '"@type":"Article"' in guide
    assert '"@type":"FAQPage"' in guide
    assert '"@type":"BreadcrumbList"' in guide
    assert '"@type":"WebApplication"' in tool

    print({
        "ok": True,
        "version": 347,
        "newRoutes": 2,
        "newAffiliateClasses": 0,
        "newMerchantLinks": 0,
        "retention": "local 30/90/365 ICS plus event-triggered revisit",
        "privacy": "no network or persistent browser storage",
        "fixedProtection": "professional-only",
    })


if __name__ == "__main__":
    main()
