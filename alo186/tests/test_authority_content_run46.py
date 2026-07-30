from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run46.json"

PAGES = {
    "/haberler/ges-rapid-shutdown-dc-izolator-afci-farki": {
        "path": ROOT / "alo186/haberler/ges-rapid-shutdown-dc-izolator-afci-farki/index.html",
        "intent": ("rapid shutdown", "DC izolatör", "AFCI", "anti-islanding", "IEC 63257"),
        "sources": ("iec.ch", "solaredge.com", "manuals.sma.de"),
        "separation": "acil durumda DC gerilimin hangi cihaz ve sınırlar içinde gerçekten düşürüldüğünü",
    },
    "/haberler/bess-soc-soh-kullanilabilir-enerji-kapasite-testi": {
        "path": ROOT / "alo186/haberler/bess-soc-soh-kullanilabilir-enerji-kapasite-testi/index.html",
        "intent": ("SoC", "SoH", "kullanılabilir enerji", "round-trip", "IEC 62933-2-1"),
        "sources": ("iec.ch", "nrel.gov", "sandia.gov"),
        "separation": "ekrandaki SoC/SoH değerinin gerçek kullanılabilir enerji, güç, verim ve saha sağlık testiyle nasıl doğrulanacağını",
    },
    "/haberler/vpp-temel-tuketim-degeri-baseline-telemetri-uzlastirma": {
        "path": ROOT / "alo186/haberler/vpp-temel-tuketim-degeri-baseline-telemetri-uzlastirma/index.html",
        "intent": ("VPP", "temel tüketim değeri", "baseline", "telemetri", "uzlaştırma"),
        "sources": ("epdk.gov.tr", "teias.gov.tr"),
        "separation": "temel tüketim değeri, aktivasyon, telemetri, gerçekleşen sapma ve uzlaştırmanın denetlenebilir bir gelir kanıtına nasıl dönüştürüleceğini",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] >= 81, overlay["version"]
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
        assert any(domain in lower for domain in contract["sources"]), (route, contract["sources"])

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
