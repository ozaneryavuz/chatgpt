from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run78.json"
PAGES = {
    "/haberler/kacak-usulsuz-elektrik-tespit-tutanagi-itiraz-sureci": {
        "path": ROOT / "alo186/haberler/kacak-usulsuz-elektrik-tespit-tutanagi-itiraz-sureci/index.html",
        "intent": ("Kaçak tüketim", "Usulsüz tüketim", "kayıtlı başvuru", "Mühür numaraları", "OSOS/yük profili"),
        "sources": ("epdk.gov.tr",),
        "separation": ("kaçak/usulsüz tespit tutanağının teknik kanıt ve başvuru dosyasını", "fatura itiraz rehberi", "güç artışı rehberi"),
        "boundary": "Hızlı ödeme veya parça değiştirme sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/ev-sarj-tip-a-tip-b-rcd-6ma-dc-rdcdd-secimi": {
        "path": ROOT / "alo186/haberler/ev-sarj-tip-a-tip-b-rcd-6ma-dc-rdcdd-secimi/index.html",
        "intent": ("RCD Tip A", "RCD Tip B", "RDC-DD 6 mA DC", "DC körleşme", "Gerçek araçla şarj edin"),
        "sources": ("iec.ch", "se.com"),
        "separation": ("EV şarj devresindeki AC/DC artık akım koruma mimarisini", "open-PEN ve topraklama rehberi", "RCD ramp testi rehberi"),
        "boundary": "Gereksiz Tip B satın almama sınırı",
        "cta": "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
    },
    "/haberler/ges-dc-ac-orani-inverter-clipping-oversizing-kabul": {
        "path": ROOT / "alo186/haberler/ges-dc-ac-orani-inverter-clipping-oversizing-kabul/index.html",
        "intent": ("DC/AC oranı", "İnverter clipping", "MPPT akımını", "Yıllık clipping enerjisini", "1–5 dakikalık DC/AC"),
        "sources": ("nrel.gov",),
        "separation": ("PV dizi gücü ile inverter AC gücünün boyutlandırılması ve clipping kaybını", "AC/DC coupled batarya rehberi", "PID/LID/LeTID rehberi"),
        "boundary": "Daha büyük inverter veya batarya almama sınırı",
        "cta": "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 142
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
        "routingVersion": 142,
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
