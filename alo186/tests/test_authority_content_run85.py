from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run85.json"
PAGES = {
    "/haberler/jenerator-blok-isitici-jacket-water-heater-dusuk-sogutma-suyu-sicakligi": {
        "path": ROOT / "alo186/haberler/jenerator-blok-isitici-jacket-water-heater-dusuk-sogutma-suyu-sicakligi/index.html",
        "intent": ("Blok ısıtıcısı", "Jacket water heater", "Düşük soğutma suyu sıcaklığı", "termosifon dolaşımı", "soğuk marş"),
        "sources": ("cat.com", "cummins.com"),
        "separation": ("jeneratörün hazır bekleme sıcaklığı, blok ısıtıcısı beslemesi ve soğuk marş yolunu", "marş aküsü rehberi", "AVR/ATS çıkış rehberi"),
        "boundary": "Yalnız düşük sıcaklık alarmına bakarak ısıtıcı satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/bess-kapasite-testi-soh-kullanilabilir-enerji-augmentation-kabul": {
        "path": ROOT / "alo186/haberler/bess-kapasite-testi-soh-kullanilabilir-enerji-augmentation-kabul/index.html",
        "intent": ("BESS kapasite testi", "Kullanılabilir enerji", "State of Health", "Round-trip efficiency", "Augmentation"),
        "sources": ("iec.ch", "energy.gov", "nrel.gov"),
        "separation": ("BESS'in sahadaki kullanılabilir enerji, SoH ve kapasite takviyesi kabulünü", "AC/DC coupled rehberi", "grid-forming ve black start rehberi"),
        "boundary": "Yalnız BMS SoH yüzdesine bakarak augmentation satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/v2g-v2h-v2b-cift-yonlu-sarj-iso-15118-20-ocpp-2-1": {
        "path": ROOT / "alo186/haberler/v2g-v2h-v2b-cift-yonlu-sarj-iso-15118-20-ocpp-2-1/index.html",
        "intent": ("V2G", "V2H", "V2B", "ISO 15118-20", "OCPP 2.1", "Bidirectional power transfer"),
        "sources": ("iso.org", "openchargealliance.org", "epdk.gov.tr"),
        "separation": ("çift yönlü enerji akışı, tesis bağlantısı, sayaç, koruma ve ticari kabulü", "Plug & Charge rehberi", "dinamik yük yönetimi rehberi"),
        "boundary": "Yalnız “ISO 15118 destekli” etiketiyle çift yönlü şarj cihazı satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 150
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
        "routingVersion": 150,
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
