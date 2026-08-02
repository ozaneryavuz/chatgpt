from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SLUGS = (
    "jenerator-reverse-power-ansi-32r-motoring-ct-polarite-teshis",
    "ges-inverter-isolation-fault-riso-low-yagmur-sonrasi-toprak-hatasi-teshis",
    "bess-precharge-timeout-dc-bus-kontaktor-on-sarj-teshis",
)
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run122.json"


def between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def test_authority_content_run122() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 197
    assert overlay["generatedAt"] == "2026-08-02"
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

        schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        assert schemas
        for schema_payload in schemas:
            json.loads(schema_payload)
        for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema in html
        assert html.count('"@type":"DefinedTerm"') >= 10
        assert html.count('"@type":"Question"') == 5
        assert html.count('"acceptedAnswer"') == 5
        assert html.count("<details>") == 5
        assert "Son doğrulama: 2 Ağustos 2026" in html
        assert "Doğrudan cevap" in html
        assert "10 adımlık" in html
        assert "14 alan" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Bağımsızlık ve uygulama sınırı" in html
        assert html.count('href="/') >= 12
        assert "Kaynaklar" in html
        assert "�" not in html
        assert "accceptedAnswer" not in html
        assert routes[route]["source"] == f"alo186/haberler/{slug}/index.html"
        assert routes[route]["type"] == "article"
        for forbidden in ('"@type":"Product"', '"@type":"Offer"', "priceCurrency", "aggregateRating", "availability", "hemen satın al"):
            assert forbidden.casefold() not in folded

    assert len(titles) == len(descriptions) == len(h1s) == 3
    generator = (ROOT / f"alo186/haberler/{SLUGS[0]}/index.html").read_text(encoding="utf-8")
    pv = (ROOT / f"alo186/haberler/{SLUGS[1]}/index.html").read_text(encoding="utf-8")
    bess = (ROOT / f"alo186/haberler/{SLUGS[2]}/index.html").read_text(encoding="utf-8")
    for phrase in ("Reverse Power", "ANSI 32R", "motoring", "CT polaritesi", "faz eşleşmesi", "ISO 8528-12:2022"):
        assert phrase.casefold() in generator.casefold()
    for phrase in ("Isolation Fault", "Riso Low", "yağmur", "string", "izolasyon direnci", "IEC 62446-1"):
        assert phrase.casefold() in pv.casefold()
    for phrase in ("Precharge Timeout", "DC bus", "ön şarj direnci", "kontaktör", "RC", "IEC 62933-5-2:2025"):
        assert phrase.casefold() in bess.casefold()
    print("ALO186 içerik otoritesi run122: PASS")
