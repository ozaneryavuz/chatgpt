from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run89.json"
PAGES = {
    "/haberler/kacak-akim-rolesi-ortak-notr-npe-koprusu-yanlis-acma": {
        "path": ROOT / "alo186/haberler/kacak-akim-rolesi-ortak-notr-npe-koprusu-yanlis-acma/index.html",
        "intent": ("ortak nötr", "yanlış nötr barası", "N-PE köprüsü", "test düğmesi", "faz-nötr eşleşmesi"),
        "sources": ("iec.ch", "hager.com"),
        "separation": ("RCD sonrası yanlış nötr yollarını ve N-PE köprüsünü", "RCD ramp testi rehberi", "toplam sızıntı rehberi"),
        "boundary": "Daha yüksek mA'lı RCD veya gecikmeli tip satın almadan önce kablolamayı doğrulayın",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/ev-sarj-control-pilot-proximity-pilot-kilit-arizasi": {
        "path": ROOT / "alo186/haberler/ev-sarj-control-pilot-proximity-pilot-kilit-arizasi/index.html",
        "intent": ("Control Pilot", "Proximity Pilot", "kablo kilidi", "OCPP", "kontaktör"),
        "sources": ("iec.ch", "ti.com", "phoenixcontact.com"),
        "separation": ("temel analog el sıkışma, kablo kodu ve soket kilidi", "Plug & Charge rehberi", "fiş-kablo ısınma rehberi"),
        "boundary": "Hata katmanı kanıtlanmadan kablo, wallbox veya backend aboneliği değiştirmeyin",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/elektrik-sayaci-muhur-kirik-fiziksel-hasar-edas-bildirimi": {
        "path": ROOT / "alo186/haberler/elektrik-sayaci-muhur-kirik-fiziksel-hasar-edas-bildirimi/index.html",
        "intent": ("mühürsüz", "mührü kırık", "başvuru numarası", "saha tutanağı", "sayaca müdahale"),
        "sources": ("ayedas.com.tr", "epdk.gov.tr"),
        "separation": ("mühürsüz/kırık mühür ve fiziksel sayaç hasarının bildirim-kanıt sürecini", "sayaç ısınma rehberi", "kaçak/usulsüz tüketim tutanağı rehberi"),
        "boundary": "Sayaç, mühür veya “tamir” hizmeti satın almayın",
        "cta": "/edas-bul",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 154
    assert overlay["generatedAt"] == "2026-08-01"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    for route, contract in PAGES.items():
        path = contract["path"]
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
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
        assert html.count('"@type":"DefinedTerm"') >= 10
        assert html.count('"@type":"Question"') == 5
        assert html.count("<details>") == 5
        assert "Doğrudan cevap" in html
        assert "10 adımlık" in html
        assert "14 alan" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert contract["boundary"] in html
        assert contract["cta"] in html
        assert html.count('href="/') >= 8
        assert "Son doğrulama: 1 Ağustos 2026" in html
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
        assert routes[route]["source"] == str(path.relative_to(ROOT))

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 154,
        "pages": list(PAGES),
        "verifiedAt": "2026-08-01",
        "faqPerPage": 5,
        "definedTermsMinimum": 10,
        "canonicalCollision": False,
        "purchaseBoundary": True,
        "intentSeparation": True,
        "primarySourceOnly": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
