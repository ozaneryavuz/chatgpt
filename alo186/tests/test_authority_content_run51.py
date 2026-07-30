from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run51.json"

PAGES = {
    "/haberler/elektrik-kesintisi-tazminati-edas-12-saat-yillik-kesinti": {
        "path": ROOT / "alo186/haberler/elektrik-kesintisi-tazminati-edas-12-saat-yillik-kesinti/index.html",
        "intent": ("12 saati", "yıllık kesinti tazminatı", "Nisan ayından", "dağıtım bedellerinden", "15 iş günü", "10 iş günü"),
        "sources": ("epdk.gov.tr", "cimer.gov.tr"),
        "separation": "elektrik kesintisi tazminatında yıllık bildirimsiz kesinti sınırı, 12 saati aşan tek kesinti, otomatik fatura mahsubu, kayıt doğrulama ve EPDK şikâyet yolunun nasıl ayrılacağını",
    },
    "/haberler/toprak-hata-cevrim-empedansi-zs-ze-topraklama-direnci-farki": {
        "path": ROOT / "alo186/haberler/toprak-hata-cevrim-empedansi-zs-ze-topraklama-direnci-farki/index.html",
        "intent": ("Zs", "Ze", "R1+R2", "PEFC", "otomatik açma", "IEC 61557-3"),
        "sources": ("webstore.iec.ch", "electrical.theiet.org", "fluke.com"),
        "separation": "topraklama elektrodu direnci ile Zs/Ze hata çevrim empedansını, R1+R2 ile otomatik açma doğrulamasını ve canlı test sınırlarını birbirinden ayırmayı",
    },
    "/haberler/parafudr-baglanti-kablosu-50-cm-up-koruma-seviyesi": {
        "path": ROOT / "alo186/haberler/parafudr-baglanti-kablosu-50-cm-up-koruma-seviyesi/index.html",
        "intent": ("50 cm", "Up", "endüktif gerilim", "V bağlantı", "IEC 60364-5-53", "IEC 61643-12"),
        "sources": ("webstore.iec.ch", "se.com"),
        "separation": "parafudrın etiket Up değerini tesisattaki etkin koruma seviyesinden ayırmayı; bağlantı iletkeni uzunluğu, endüktif gerilim, 50 cm yerleşim, V bağlantı ve pano kabul ölçütlerini",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 87, overlay["version"]
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES), routes

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    canonicals: set[str] = set()

    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")

        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)"', html)
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert title and description and h1 and canonical, route
        assert route in canonical.group(1), (route, canonical.group(1))
        assert canonical.group(1).startswith("https://alo186.com/"), canonical.group(1)
        titles.add(title.group(1))
        descriptions.add(description.group(1))
        h1s.add(h1.group(1))
        canonicals.add(canonical.group(1))

        for schema_type in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema_type in html, (route, schema_type)
        assert html.count('"@type":"DefinedTerm"') >= 8, route
        assert html.count('"@type":"Question"') >= 5, route
        assert "<strong>Doğrudan cevap:</strong>" in html, route
        assert "Satın almama sınırı:" in html, route
        assert "Mevcut içerikten görev ayrımı" in html, route
        assert contract["separation"] in html, route
        assert html.count('href="/') >= 8, route
        assert "Son doğrulama: 30 Temmuz 2026" in html, route
        assert 'href="/hesaplama/teknik-devir-kabul-paketi/"' in html, route

        lower = html.casefold()
        for token in contract["intent"]:
            assert token.casefold() in lower, (route, token)
        assert all(domain in lower for domain in contract["sources"]), (route, contract["sources"])

        for forbidden in (
            '"@type":"product"',
            '"@type":"offer"',
            "pricecurrency",
            "availability",
            "aggregaterating",
            'type="email"',
            'type="tel"',
            "amazon.com.tr",
            "son ürün",
            "hemen satın al",
            "garantili tazminat",
        ):
            assert forbidden not in lower, (route, forbidden)

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)

    all_html = "\n".join(contract["path"].read_text(encoding="utf-8").casefold() for contract in PAGES.values())
    assert all_html.count("elektrik kesintisi tazminatı nasıl alınır") == 2  # Article headline + H1
    assert all_html.count("toprak hata çevrim empedansı nedir") == 2
    assert all_html.count("parafudr bağlantı kablosu neden kısa olmalı") == 2

    print(json.dumps({
        "routingVersion": overlay["version"],
        "routes": sorted(PAGES),
        "articles": len(PAGES),
        "uniqueTitles": len(titles),
        "uniqueDescriptions": len(descriptions),
        "directStoreLinks": 0,
        "sourceVerifiedAt": "2026-07-30",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
