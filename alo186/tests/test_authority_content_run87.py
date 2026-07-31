from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run87.json"
PAGES = {
    "/haberler/ev-sarj-fisi-kablosu-isinma-sicaklik-akim-dusurme-teshisi": {
        "path": ROOT / "alo186/haberler/ev-sarj-fisi-kablosu-isinma-sicaklik-akim-dusurme-teshisi/index.html",
        "intent": ("IEC 62752:2024", "IEC 62196-1:2025", "sıcaklık", "akım düşürme", "Mode 2", "IC-CPD"),
        "sources": ("iec.ch", "tesla.com"),
        "separation": ("şarj bağlantısındaki ısınma, temas direnci ve termal akım düşürmeyi", "RCD", "dinamik yük yönetimi"),
        "boundary": "Yalnız daha yüksek akımlı kablo veya wallbox satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/ups-aku-odasi-hidrojen-havalandirma-sarj-cihazi-guvenligi": {
        "path": ROOT / "alo186/haberler/ups-aku-odasi-hidrojen-havalandirma-sarj-cihazi-guvenligi/index.html",
        "intent": ("IEC 62485-2", "hidrojen", "havalandırma", "VRLA", "şarj cihazı", "gaz algılama"),
        "sources": ("iec.ch", "osha.gov"),
        "separation": ("sabit UPS akü odasında gaz oluşumu, havalandırma ve şarj arızası güvenliğini", "akü string", "lityum"),
        "boundary": "Yalnız oda metrekaresine bakarak fan veya gaz dedektörü satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/parafudr-tov-notr-kopmasi-surekli-asiri-gerilim-farki": {
        "path": ROOT / "alo186/haberler/parafudr-tov-notr-kopmasi-surekli-asiri-gerilim-farki/index.html",
        "intent": ("IEC 61643-11:2025", "TOV", "Uc", "MCOV", "nötr kopması", "sürekli aşırı gerilim"),
        "sources": ("iec.ch", "se.com"),
        "separation": ("geçici darbe ile uzun süreli aşırı gerilim ayrımını", "yedek sigorta", "gerilim kalitesi"),
        "boundary": "Yalnız daha yüksek Uc veya daha büyük kA değerli parafudr satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 152
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
        "routingVersion": 152,
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
