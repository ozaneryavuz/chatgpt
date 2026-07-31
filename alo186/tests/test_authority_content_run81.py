from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run81.json"
PAGES = {
    "/haberler/jenerator-mars-akusu-sarj-cihazi-bosaliyor-start-arizasi": {
        "path": ROOT / "alo186/haberler/jenerator-mars-akusu-sarj-cihazi-bosaliyor-start-arizasi/index.html",
        "intent": ("Marş aküsü", "şarj beslemesi", "krank gerilimi", "Parazitik akım", "ilk deneme"),
        "sources": ("generac.com", "cat.com"),
        "separation": ("marş aküsü, şarj beslemesi ve start devresinin kabulünü", "çalışıyor fakat elektrik vermiyor rehberi", "düşük yük rehberi"),
        "boundary": "Aküyü ölçmeden değiştirmeme sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/asansor-elektrik-kesintisi-ard-ups-jenerator-kurtarma": {
        "path": ROOT / "alo186/haberler/asansor-elektrik-kesintisi-ard-ups-jenerator-kurtarma/index.html",
        "intent": ("Automatic Rescue Operation", "ARD", "en yakın kata", "iki yönlü alarm", "kurtarma tatbikatı"),
        "sources": ("iso.org", "bsigroup.com", "otis.com", "eur-lex.europa.eu"),
        "separation": ("elektrik kesintisinde yolcunun güvenli tahliyesi, ARD ve bina yedek kaynağı kabulünü", "genel jeneratör rehberi", "kesinti tazminatı rehberi"),
        "boundary": "Haricî UPS veya jeneratörü doğrudan bağlamama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/ups-eco-modu-double-conversion-yuksek-verimlilik-kabul": {
        "path": ROOT / "alo186/haberler/ups-eco-modu-double-conversion-yuksek-verimlilik-kabul/index.html",
        "intent": ("ECO modu", "çift çevrim", "statik bypass", "transfer süresi", "eConversion"),
        "sources": ("iec.ch", "se.com", "vertiv.com", "eaton.com"),
        "separation": ("UPS çalışma modu, verim ve transfer kabulünü", "bypass senkronizasyon rehberi", "kVA–kW seçim rehberi"),
        "boundary": "Sırf verim etiketi için UPS değiştirmeme sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 145
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
        "routingVersion": 145,
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
