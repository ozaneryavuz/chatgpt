from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run88.json"
PAGES = {
    "/haberler/ups-jenerator-aku-sarj-akimi-giris-akim-limiti": {
        "path": ROOT / "alo186/haberler/ups-jenerator-aku-sarj-akimi-giris-akim-limiti/index.html",
        "intent": ("IEC 62040-3:2021", "akü şarj", "giriş akım limiti", "ramp-in", "jeneratör modu", "SoC"),
        "sources": ("iec.ch", "se.com"),
        "separation": ("kesinti sonrası UPS şarjının jeneratör giriş yüküne etkisini", "ATS süreleri", "akü string"),
        "boundary": "Yalnız UPS kVA'sına bakarak daha büyük jeneratör veya akü satın almayın",
    },
    "/haberler/ges-inverter-reaktif-guc-q-u-cosphi-p-volt-var-ayari": {
        "path": ROOT / "alo186/haberler/ges-inverter-reaktif-guc-q-u-cosphi-p-volt-var-ayari/index.html",
        "intent": ("IEC TS 62786-2:2026", "Q(U)", "cosφ(P)", "reaktif güç", "POI", "kompanzasyon"),
        "sources": ("iec.ch", "sma.de", "huawei.com", "epdk.gov.tr"),
        "separation": ("inverter reaktif güç ve şebeke destek ayarlarının POI'de kabulünü", "reaktif fatura", "zero-export"),
        "boundary": "Yalnız yüksek gerilim alarmına bakarak inverter, reaktör veya kompanzasyon ürünü almayın",
    },
    "/haberler/elektrik-faturasi-sayac-carpani-akim-trafosu-orani-hatasi": {
        "path": ROOT / "alo186/haberler/elektrik-faturasi-sayac-carpani-akim-trafosu-orani-hatasi/index.html",
        "intent": ("sayaç çarpanı", "akım trafosu", "CT/VT", "OSOS", "bir yıl", "hatalı faturalandırma"),
        "sources": ("epdk.gov.tr", "enerjisa.com.tr"),
        "separation": ("aktif/reaktif tüketimin sayaç çarpanı ve CT/VT oranıyla yeniden hesaplanmasını", "reaktif enerji rehberi", "fatura itirazı rehberi"),
        "boundary": "Tek fatura artışıyla sayaç, CT veya kompanzasyon ürünü satın almayın",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 153
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
        assert "/hizmetler/elektrik-surekliligi/" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Kaynaklar" in html
        for token in contract["intent"] + contract["separation"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for forbidden in (
            '"@type":"Product"', '"@type":"Offer"', "priceCurrency",
            "aggregateRating", "availability", "hemen satın al", "stok tükeniyor",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 153,
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
