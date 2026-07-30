from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run67.json"
PAGES = {
    "/haberler/kacak-akim-rolesi-ramp-testi-acma-suresi-test-dugmesi-farki": {
        "path": ROOT / "alo186/haberler/kacak-akim-rolesi-ramp-testi-acma-suresi-test-dugmesi-farki/index.html",
        "intent": ("Ramp testi", "açma süresi", "0,5×", "test düğmesi", "IEC 61557-6"),
        "sources": ("iec.ch", "fluke.com"),
        "separation": ("ölçü cihazıyla doğrulama", "topraklama"),
    },
    "/haberler/ges-mc4-konnektor-uyumsuzluk-krimp-isinma-termal-kontrol": {
        "path": ROOT / "alo186/haberler/ges-mc4-konnektor-uyumsuzluk-krimp-isinma-termal-kontrol/index.html",
        "intent": ("çapraz eşleştirme", "krimp", "temas direnci", "termografi", "aynı üretici"),
        "sources": ("iec.ch", "nrel.gov", "staubli.com"),
        "separation": ("PV kablo konnektörü", "AFCI"),
    },
    "/haberler/ups-aku-kapasite-testi-empedans-ic-direnc-farki": {
        "path": ROOT / "alo186/haberler/ups-aku-kapasite-testi-empedans-ic-direnc-farki/index.html",
        "intent": ("kapasite testi", "empedans", "baseline", "deşarj testi", "IEEE 1188-2025"),
        "sources": ("ieee.org", "megger.com", "fluke.com"),
        "separation": ("ohmik trend", "gerçek kapasite"),
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 123
    assert overlay["generatedAt"] == "2026-07-31"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
        folded = html.casefold()
        title = text_between(r"<title>(.*?)</title>", html)
        h1 = text_between(r"<h1>(.*?)</h1>", html)
        description = re.search(r'<meta name="description" content="([^"]+)"', html)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert description and canonical
        assert route in canonical.group(1)
        assert html.count("<h1") == 1
        titles.add(title)
        h1s.add(h1)
        descriptions.add(description.group(1))
        for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema in html, (route, schema)
        assert html.count('"@type":"DefinedTerm"') >= 8
        assert html.count('"@type":"Question"') >= 5
        assert "Doğrudan cevap" in html
        assert "Satın almama sınırı" in html
        assert html.count('href="/') >= 8
        assert "Son doğrulama: 31 Temmuz 2026" in html
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html
        assert "Mevcut rehberlerden görev ayrımı" in html
        for token in contract["intent"] + contract["separation"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for forbidden in (
            '"@type":"Product"', '"@type":"Offer"', "priceCurrency", "aggregateRating",
            "garanti sonuç", "kesin sonuç", "hemen satın al", "stok tükeniyor",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 123,
        "pages": list(PAGES),
        "verifiedAt": "2026-07-31",
        "faqPerPage": 5,
        "definedTermsMinimum": 8,
        "canonicalCollision": False,
        "purchaseBoundary": True,
        "intentSeparation": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
