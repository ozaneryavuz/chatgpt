from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run83.json"
PAGES = {
    "/haberler/elektrik-faturasi-reaktif-enerji-enduktif-kapasitif-bedel": {
        "path": ROOT / "alo186/haberler/elektrik-faturasi-reaktif-enerji-enduktif-kapasitif-bedel/index.html",
        "intent": ("Reaktif enerji bedeli", "endüktif ve kapasitif oran", "3.8.0", "4.8.0", "kompanzasyon"),
        "sources": ("epdk.gov.tr", "enerjisa.com.tr"),
        "separation": ("reaktif enerji bedelini sayaç endeksi, oran, fatura ve kompanzasyon kanıtıyla", "kompanzasyon arızası rehberi", "fatura itirazı rehberi"),
        "boundary": "Ölçüm yapılmadan kompanzasyon ekipmanı satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/jenerator-ats-transfer-gecikmesi-retransfer-cooldown-ayari": {
        "path": ROOT / "alo186/haberler/jenerator-ats-transfer-gecikmesi-retransfer-cooldown-ayari/index.html",
        "intent": ("ATS transfer gecikmesi", "Engine start delay", "warm-up", "utility stabilization", "cooldown"),
        "sources": ("iec.ch", "se.com", "cat.com"),
        "separation": ("ATS zaman gecikmeleri, transfer–retransfer sırası ve olay zaman çizelgesi kabulünü", "jeneratör çıkış teşhisi rehberi", "jeneratör koruma koordinasyonu rehberi"),
        "boundary": "Süreleri rastgele kısaltmama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/jenerator-dizel-yakit-kirliligi-su-mikrop-fuel-polishing": {
        "path": ROOT / "alo186/haberler/jenerator-dizel-yakit-kirliligi-su-mikrop-fuel-polishing/index.html",
        "intent": ("Dizel yakıt", "serbest su", "mikrobiyal", "su separatörü", "fuel polishing"),
        "sources": ("cummins.com", "cat.com"),
        "separation": ("standby jeneratörde yakıt depolama, su, mikrop, tortu ve fuel polishing kabulünü", "wet stacking rehberi", "marş aküsü rehberi"),
        "boundary": "Analiz yapılmadan katkı, biyosit veya fuel polishing satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 148
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
        "routingVersion": 148,
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
