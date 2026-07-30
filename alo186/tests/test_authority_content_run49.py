from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run49.json"

PAGES = {
    "/haberler/topraklama-olcumunde-kazikli-pens-62-yuzde-yontemi": {
        "path": ROOT / "alo186/haberler/topraklama-olcumunde-kazikli-pens-62-yuzde-yontemi/index.html",
        "intent": ("kazıklı", "pensli", "yüzde 62", "fall-of-potential", "IEC 61557-5"),
        "sources": ("webstore.iec.ch", "fluke.com", "megger.com"),
        "separation": "kazıklı fall-of-potential, yüzde 62, seçici ve pensli topraklama ölçüm yöntemlerinin hangi elektriksel büyüklüğü ölçtüğünü, hangi tesis geometrisinde geçerli olduğunu ve sonucun hangi kanıtlarla doğrulanacağını",
    },
    "/haberler/ges-zero-export-sifir-ihracat-ct-sayac-yonu": {
        "path": ROOT / "alo186/haberler/ges-zero-export-sifir-ihracat-ct-sayac-yonu/index.html",
        "intent": ("zero export", "CT", "PCC", "faz eşleşmesi", "IEC TS 62786-2"),
        "sources": ("manuals.sma.de", "huawei.com", "webstore.iec.ch", "epdk.gov.tr"),
        "separation": "zero export sisteminde PCC ölçüm noktası, CT/sayaç yönü, faz eşleşmesi, haberleşme, çoklu inverter kontrolü ve fail-safe saha kabulünün hangi testlerle doğrulanacağını",
    },
    "/haberler/ups-aku-odasi-havalandirma-hidrojen-riski-vrla": {
        "path": ROOT / "alo186/haberler/ups-aku-odasi-havalandirma-hidrojen-riski-vrla/index.html",
        "intent": ("VRLA", "hidrojen", "havalandırma", "şarj kilitlemesi", "IEC 62485-2"),
        "sources": ("webstore.iec.ch", "osha.gov", "enersys.com", "schneider-electric.com"),
        "separation": "VRLA ve diğer sabit akü kurulumlarında gaz emisyonu, havalandırma hesabı, klima-fan ayrımı, fan arızası, gaz algılama ve şarj kilitlemesinin hangi veriler ve saha testleriyle doğrulanacağını",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] >= 84, overlay["version"]
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES), routes

    titles: set[str] = set()
    h1s: set[str] = set()
    canonicals: set[str] = set()

    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("index.html")

        title = re.search(r"<title>(.*?)</title>", html, re.S)
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert title and h1 and canonical, route
        assert route in canonical.group(1), (route, canonical.group(1))
        assert canonical.group(1).startswith("https://alo186.com/"), canonical.group(1)
        titles.add(title.group(1))
        h1s.add(h1.group(1))
        canonicals.add(canonical.group(1))

        for schema_type in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema_type in html, (route, schema_type)
        assert html.count('"@type":"DefinedTerm"') >= 8, route
        assert html.count('"@type":"Question"') >= 4, route
        assert "<strong>Doğrudan cevap:</strong>" in html, route
        assert "Güvenlik sınırı:" in html or "Güvenlik ve mevzuat sınırı:" in html, route
        assert "Satın almama sınırı:" in html, route
        assert "Mevcut içerikten görev ayrımı" in html, route
        assert contract["separation"] in html, route
        assert html.count('href="/') >= 8, route
        assert "Teknik devir-kabul paketini aç" in html, route
        assert "Profesyonel ön değerlendirme" in html, route
        assert "Son doğrulama: 30 Temmuz 2026" in html, route

        lower = html.lower()
        for token in contract["intent"]:
            assert token.lower() in lower, (route, token)
        assert all(domain in lower for domain in contract["sources"]), (route, contract["sources"])

        for forbidden in (
            '"@type":"Product"',
            '"@type":"Offer"',
            "priceCurrency",
            "availability",
            "aggregateRating",
            'type="email"',
            'type="tel"',
            "amazon.com.tr",
            "son ürün",
            "hemen satın al",
        ):
            assert forbidden not in lower, (route, forbidden)

    assert len(titles) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)
    print(json.dumps({"routingVersion": overlay["version"], "routes": sorted(PAGES)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
