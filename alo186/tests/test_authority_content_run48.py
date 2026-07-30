from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run48.json"

PAGES = {
    "/haberler/banyoda-espotansiyel-kusaklama-rcd-topraklama": {
        "path": ROOT / "alo186/haberler/banyoda-espotansiyel-kusaklama-rcd-topraklama/index.html",
        "intent": ("eşpotansiyel kuşaklama", "RCD", "metal boru", "PE sürekliliği", "IEC 60364-7-701"),
        "sources": ("iec.ch", "electrical.theiet.org"),
        "separation": "banyo ve duş alanında RCD, ana kuşaklama, ek eşpotansiyel kuşaklama, metal boru sınıflandırması ve PE sürekliliğinin hangi kanıtlarla birlikte değerlendirileceğini",
    },
    "/haberler/ups-aku-kapasite-testi-self-test-desarj-farki": {
        "path": ROOT / "alo186/haberler/ups-aku-kapasite-testi-self-test-desarj-farki/index.html",
        "intent": ("kapasite testi", "self-test", "iç direnç", "kontrollü deşarj", "IEEE 1188-2025"),
        "sources": ("standards.ieee.org", "eaton.com", "vertiv.com"),
        "separation": "UPS self-test, iç direnç/conductance trendi, gerçek runtime ve kontrollü deşarj kapasite testinin hangi kanıtları sağladığını ve nasıl birlikte yorumlanacağını",
    },
    "/haberler/ges-mc4-konnektor-isinma-farkli-marka-krimp": {
        "path": ROOT / "alo186/haberler/ges-mc4-konnektor-isinma-farkli-marka-krimp/index.html",
        "intent": ("MC4", "cross-mating", "krimp", "temas direnci", "IEC 62852", "IEC 62548-1"),
        "sources": ("iec.ch", "staubli.com"),
        "separation": "PV MC4 tipi konnektörde farklı marka çapraz eşleşme, yanlış krimp, temas direnci, su/mekanik etki ve termal anomali kanıtlarının nasıl ayrılacağını",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] >= 83, overlay["version"]
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
