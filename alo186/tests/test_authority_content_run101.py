from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SLUGS = (
    "elektrik-dalgalanmasi-cihaz-hasari-edas-basvurusu-30-gun-kanit",
    "ges-inverter-dusuk-izolasyon-direnci-riso-toprak-hatasi-string-teshis",
    "ups-inverter-inoperable-output-short-circuit-overload-teshis",
)
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run101.json"
CONSOLIDATIONS = ROOT / "alo186/deployment/content-consolidations.json"
OLD_DAMAGE_ROUTE = "/haberler/elektrik-dalgalanmasi-cihaz-hasari-edas-basvurusu-10-is-gunu-kanit"
NEW_DAMAGE_ROUTE = "/haberler/elektrik-dalgalanmasi-cihaz-hasari-edas-basvurusu-30-gun-kanit"
OLD_DAMAGE_PATH = ROOT / "alo186/haberler/elektrik-dalgalanmasi-cihaz-hasari-edas-basvurusu-10-is-gunu-kanit/index.html"


def between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def test_authority_content_run101() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 168
    assert overlay["generatedAt"] == "2026-08-01"
    assert len(overlay["routes"]) == 3
    assert "edas-basvurusu-10-is-gunu-kanit" not in json.dumps(overlay, ensure_ascii=False)
    assert not OLD_DAMAGE_PATH.exists()

    consolidation_data = json.loads(CONSOLIDATIONS.read_text(encoding="utf-8"))
    aliases = {
        item["aliasPath"]: item["canonicalPath"]
        for item in consolidation_data["consolidations"]
    }
    assert aliases[OLD_DAMAGE_ROUTE] == NEW_DAMAGE_ROUTE

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
            '"@type":"Product"',
            '"@type":"Offer"',
            "priceCurrency",
            "aggregateRating",
            "availability",
            "hemen satın al",
        ):
            assert forbidden.casefold() not in folded

    assert len(titles) == 3
    assert len(descriptions) == 3
    assert len(h1s) == 3

    edas = (ROOT / "alo186/haberler/elektrik-dalgalanmasi-cihaz-hasari-edas-basvurusu-30-gun-kanit/index.html").read_text(encoding="utf-8")
    ges = (ROOT / "alo186/haberler/ges-inverter-dusuk-izolasyon-direnci-riso-toprak-hatasi-string-teshis/index.html").read_text(encoding="utf-8")
    ups = (ROOT / "alo186/haberler/ups-inverter-inoperable-output-short-circuit-overload-teshis/index.html").read_text(encoding="utf-8")

    for phrase in ("30 gün içinde", "Madde 26/1", "teknik kalite ölçümü", "servis raporu", "gerekçeli cevap"):
        assert phrase.casefold() in edas.casefold()
    for obsolete in (
        "10 iş günlük EDAŞ başvurusu",
        "10 iş günü içinde ilgili dağıtım şirketine talepte",
        "10 iş günlük başvuru süresi",
        "10 iş günlük süreyi koruyun",
    ):
        assert obsolete.casefold() not in edas.casefold()
    assert "https://www.resmigazete.gov.tr/eskiler/2020/12/20201229M1-1.htm" in edas
    assert "https://www.resmigazete.gov.tr/eskiler/2025/10/20251023-5.htm" in edas
    for phrase in ("Low Insulation Resistance", "Riso", "DC+/PE", "nem", "string"):
        assert phrase.casefold() in ges.casefold()
    for phrase in ("Inverter Inoperable", "Output Short Circuit", "overload", "waveform", "power sharing"):
        assert phrase.casefold() in ups.casefold()

    print("ALO186 içerik otoritesi run101: PASS")
