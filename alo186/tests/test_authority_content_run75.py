from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run75.json"
PAGES = {
    "/haberler/ev-sarj-faturasi-kwh-farki-arac-istasyon-sayaci": {
        "path": ROOT / "alo186/haberler/ev-sarj-faturasi-kwh-farki-arac-istasyon-sayaci/index.html",
        "intent": ("istasyon sayacı", "araç batarya yüzdesi", "TL/kWh", "OCPP oturum kaydı", "başlangıç-bitiş sayaç"),
        "sources": ("epdk.gov.tr", "openchargealliance.org", "energy.gov"),
        "separation": ("şarj oturumundaki sayaç, araç ekranı ve fatura kWh farkını", "elektrik faturası itirazı"),
        "boundary": "Yeni şarj cihazı almama sınırı",
    },
    "/haberler/bess-dc-izolasyon-hatasi-imd-toprak-ariza-yeri": {
        "path": ROOT / "alo186/haberler/bess-dc-izolasyon-hatasi-imd-toprak-ariza-yeri/index.html",
        "intent": ("IMD", "izolasyon direnci", "sistem kaçak kapasitesi", "kutup-toprak gerilimleri", "arıza yeri tespit"),
        "sources": ("iec.ch", "bender.de", "schneider-electric.com"),
        "separation": ("BESS DC izolasyon direnci, IMD alarmı ve arıza yeri tespitine", "BESS yangın planı"),
        "boundary": "IMD değiştirmeme sınırı",
    },
    "/haberler/isik-titremesi-flicker-pst-plt-gerilim-dalgalanmasi": {
        "path": ROOT / "alo186/haberler/isik-titremesi-flicker-pst-plt-gerilim-dalgalanmasi/index.html",
        "intent": ("Flicker", "Pst", "Plt", "hızlı gerilim değişimi", "Class A"),
        "sources": ("iec.ch", "epdk.gov.tr", "fluke.com"),
        "separation": ("görsel ışık titremesi, flicker, Pst ve Plt kanıtına", "gerilim çukuru rehberi"),
        "boundary": "Regülatör satın almama sınırı",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 137
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
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html
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
        "routingVersion": 137,
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
