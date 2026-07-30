from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run47.json"

PAGES = {
    "/haberler/kacak-akim-rolesi-ramp-testi-acma-akimi-suresi": {
        "path": ROOT / "alo186/haberler/kacak-akim-rolesi-ramp-testi-acma-akimi-suresi/index.html",
        "intent": ("ramp testi", "açma akımı", "açma süresi", "0,5×", "IEC 61557-6"),
        "sources": ("iec.ch", "fluke.com", "se.com"),
        "separation": "RCD ramp testindeki açma akımı ile açma süresi, non-trip testi, test dalga şekli ve tesisat koruma kanıtlarının nasıl birlikte yorumlanacağını",
    },
    "/haberler/gerilim-kalitesi-sikayeti-class-a-olcum-edas-basvuru": {
        "path": ROOT / "alo186/haberler/gerilim-kalitesi-sikayeti-class-a-olcum-edas-basvuru/index.html",
        "intent": ("Class A", "Class S", "EDAŞ", "15 iş günü", "IEC 61000-4-30"),
        "sources": ("iec.ch", "epdk.gov.tr"),
        "separation": "gerilim olayının EDAŞ başvurusunda tekrarlanabilir ölçüm, olay günlüğü, ölçüm noktası ve yazılı kayıtla nasıl kanıtlanacağını",
    },
    "/haberler/ev-sarj-fisi-kablosu-neden-isinir": {
        "path": ROOT / "alo186/haberler/ev-sarj-fisi-kablosu-neden-isinir/index.html",
        "intent": ("temas direnci", "Type 2", "ısınma", "IEC 62196-1", "IEC 61851-1"),
        "sources": ("iec.ch", "tesla.com"),
        "separation": "şarj fişi, priz, Type 2 konnektörü veya kablodaki ısınmanın temas direnci, tesisat, akım, çevre ve termal koruma kanıtlarıyla nasıl ayrılacağını",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] >= 82, overlay["version"]
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
        assert html.count('href="/') >= 6, route
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
        ):
            assert forbidden not in html, (route, forbidden)

    assert len(titles) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)
    print(json.dumps({"routingVersion": overlay["version"], "routes": sorted(PAGES)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
