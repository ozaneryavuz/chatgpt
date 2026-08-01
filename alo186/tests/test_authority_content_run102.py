from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SLUGS = (
    "elektrik-kesintisi-tazminati-12-saat-yillik-esure-esayi-sorgulama",
    "kacak-akim-rolesi-ramp-testi-acma-akimi-suresi-yorumlama",
    "notr-asiri-isinma-ucuncu-harmonik-triplen-harmonik-teshis",
)
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run102.json"


def between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def test_authority_content_run102() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 169
    assert overlay["generatedAt"] == "2026-08-01"
    assert len(overlay["routes"]) == 3
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    titles, descriptions, h1s = set(), set(), set()

    for slug in SLUGS:
        page = ROOT / "alo186/haberler" / slug / "index.html"
        assert page.is_file(), page
        html = page.read_text(encoding="utf-8")
        folded = html.casefold()
        route = f"/haberler/{slug}"
        title = between(r"<title>(.*?)</title>", html)
        h1 = between(r"<h1>(.*?)</h1>", html)
        desc = re.search(r'<meta name="description" content="([^"]+)"', html)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert desc and canonical
        assert canonical.group(1) == f"https://alo186.com{route}"
        assert html.count("<h1>") == 1
        assert 35 <= len(title) <= 100
        assert 100 <= len(desc.group(1)) <= 190
        titles.add(title)
        descriptions.add(desc.group(1))
        h1s.add(h1)
        for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema in html
        assert html.count('"@type":"DefinedTerm"') >= 10
        assert html.count('"@type":"Question"') == 5
        assert html.count("<details>") == 5
        assert "Son doğrulama: 1 Ağustos 2026" in html
        assert "Doğrudan cevap" in html
        assert "10 adımlık" in html
        assert "Teknik dosyada bulunması gereken 14 alan" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Bağımsızlık ve uygulama sınırı" in html
        assert html.count('href="/') >= 12
        assert "Kaynaklar" in html
        assert routes[route]["source"] == f"alo186/haberler/{slug}/index.html"
        assert routes[route]["type"] == "article"
        for forbidden in (
            '"@type":"Product"', '"@type":"Offer"', "priceCurrency",
            "aggregateRating", "availability", "hemen satın al",
        ):
            assert forbidden.casefold() not in folded

    assert len(titles) == 3
    assert len(descriptions) == 3
    assert len(h1s) == 3

    outage = (ROOT / f"alo186/haberler/{SLUGS[0]}/index.html").read_text(encoding="utf-8")
    rcd = (ROOT / f"alo186/haberler/{SLUGS[1]}/index.html").read_text(encoding="utf-8")
    neutral = (ROOT / f"alo186/haberler/{SLUGS[2]}/index.html").read_text(encoding="utf-8")

    for phrase in ("12 saati", "ESÜRE", "ESAYI", "başvuru olmaksızın", "mahsup"):
        assert phrase.casefold() in outage.casefold()
    for phrase in ("ramp testi", "0,5×", "1×", "5×", "180°", "selektif"):
        assert phrase.casefold() in rcd.casefold()
    for phrase in ("triplen", "3.", "9.", "15.", "true-RMS", "nötr koruması"):
        assert phrase.casefold() in neutral.casefold()

    print("ALO186 içerik otoritesi run102: PASS")
