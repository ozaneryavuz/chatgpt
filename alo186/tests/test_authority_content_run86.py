from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run86.json"
PAGES = {
    "/haberler/ark-flash-etiketi-incident-energy-ppe-risk-degerlendirmesi": {
        "path": ROOT / "alo186/haberler/ark-flash-etiketi-incident-energy-ppe-risk-degerlendirmesi/index.html",
        "intent": ("Ark flash", "Ark flaş", "Incident energy", "Arc-flash boundary", "Working distance", "IEEE 1584.2-2025"),
        "sources": ("standards.ieee.org", "osha.gov", "nfpa.org"),
        "separation": ("ark flaş hesabı, etiket verisi ve güvenli iş kararını", "AFDD–RCD–sigorta rehberi", "pano termografi rehberi"),
        "boundary": "Yalnız eski etiket değerine bakarak ark dayanımlı PPE satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/kompakt-salter-ir-tr-isd-tsd-ii-ig-ayar-anlami": {
        "path": ROOT / "alo186/haberler/kompakt-salter-ir-tr-isd-tsd-ii-ig-ayar-anlami/index.html",
        "intent": ("Ir", "tr", "Isd", "tsd", "Ii", "Ig", "I²t", "Trip unit"),
        "sources": ("iec.ch", "se.com", "productinfo.se.com"),
        "separation": ("elektronik trip unit ayarlarının kısa devre, kablo ve seçicilik hesabıyla kabulünü", "Jeneratör kısa devre rehberi", "RCD seçicilik rehberi"),
        "boundary": "Yalnız yük akımına veya fabrika ayarına bakarak şalter ayarı değiştirmeme sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/bess-izolasyon-izleme-imd-toprak-arizasi-alarmi": {
        "path": ROOT / "alo186/haberler/bess-izolasyon-izleme-imd-toprak-arizasi-alarmi/index.html",
        "intent": ("BESS", "Insulation monitoring device", "IMD", "Ground fault", "Insulation fault locator", "Leakage capacitance"),
        "sources": ("iec.ch", "productinfo.schneider-electric.com"),
        "separation": ("BESS DC izolasyon izleme, IMD/IFL ve ground fault alarm teşhisini", "GES Riso rehberi", "BESS kapasite/SoH rehberi"),
        "boundary": "Yalnız tek ohm ekranına bakarak IMD, rack veya PCS satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 151
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
        assert canonical.group(1) == f"https://alo186.com{route}"
        assert html.count("<h1") == 1
        assert 35 <= len(title) <= 100, (route, len(title))
        assert 100 <= len(description.group(1)) <= 190, (route, len(description.group(1)))
        titles.add(title)
        h1s.add(h1)
        descriptions.add(description.group(1))
        for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema in html, (route, schema)
        assert html.count('"@type":"DefinedTerm"') >= 8
        assert html.count('"@type":"Question"') >= 5
        assert "Doğrudan cevap" in html
        assert contract["boundary"] in html
        assert html.count('href="/') >= 8
        assert "Son doğrulama: 31 Temmuz 2026" in html
        assert contract["cta"] in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Kaynaklar" in html
        for token in contract["intent"] + contract["separation"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for forbidden in (
            '"@type":"Product"',
            '"@type":"Offer"',
            "priceCurrency",
            "aggregateRating",
            "availability",
            "hemen satın al",
            "stok tükeniyor",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 151,
        "pages": list(PAGES),
        "verifiedAt": "2026-07-31",
        "faqPerPage": 5,
        "definedTermsMinimum": 8,
        "canonicalCollision": False,
        "purchaseBoundary": True,
        "intentSeparation": True,
        "primarySourceOnly": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
