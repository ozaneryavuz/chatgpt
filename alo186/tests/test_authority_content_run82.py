from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run82.json"
PAGES = {
    "/haberler/santiye-elektrigi-gecici-baglanti-edas-basvuru-belgeleri": {
        "path": ROOT / "alo186/haberler/santiye-elektrigi-gecici-baglanti-edas-basvuru-belgeleri/index.html",
        "intent": ("Şantiye elektriği", "geçici bağlantı", "yapı ruhsatı", "bağlantı görüşü", "perakende satış sözleşmesi"),
        "sources": ("epdk.gov.tr", "ayedas.com.tr"),
        "separation": ("şantiye elektriği ve geçici bağlantıda izin–proje–bağlantı–sayaç zincirini", "güç artışı rehberi", "kaçak/usulsüz tüketim rehberi"),
        "boundary": "Belge tamamlanmadan ekipman satın almama sınırı",
        "cta": "/edas-bul/",
    },
    "/haberler/ups-paralel-n-plus-1-yuk-paylasimi-redundancy-kabul": {
        "path": ROOT / "alo186/haberler/ups-paralel-n-plus-1-yuk-paylasimi-redundancy-kabul/index.html",
        "intent": ("Paralel UPS", "N+1 yedeklilik", "yük paylaşımı", "bypass empedansı", "tek modül arızası"),
        "sources": ("iec.ch", "se.com", "eaton.com"),
        "separation": ("paralel UPS mimarisi, N+1 yedeklilik, yük paylaşımı ve tek modül arızası kabulünü", "kVA–kW rehberi", "ECO modu rehberi"),
        "boundary": "Sırf “yedek olsun” diye ikinci UPS almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/bess-grid-forming-grid-following-black-start-mikrogrid": {
        "path": ROOT / "alo186/haberler/bess-grid-forming-grid-following-black-start-mikrogrid/index.html",
        "intent": ("Grid-forming", "Grid-following", "Black start", "SoC rezervi", "karanlık başlangıç"),
        "sources": ("energy.gov", "nrel.gov"),
        "separation": ("BESS kontrol modları, ada liderliği ve karanlık tesisten black-start kabulünü", "AC/DC coupled retrofit rehberi", "VPP sözleşme rehberi"),
        "boundary": "“Grid-forming” etiketi için BESS satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 147
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
        "routingVersion": 147,
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
