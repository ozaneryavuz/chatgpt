from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run50.json"

PAGES = {
    "/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-faz-eslesmesi": {
        "path": ROOT / "alo186/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-faz-eslesmesi/index.html",
        "intent": ("dinamik yük yönetimi", "CT", "faz eşleşmesi", "haberleşme", "IEC 60364-7-722"),
        "sources": ("webstore.iec.ch", "energylibrary.tesla.com", "productinfo.se.com"),
        "separation": "EV şarj dinamik yük yönetiminde ölçüm noktası, CT/sayaç yönü, faz eşleşmesi, ana besleme limiti, haberleşme ve fail-safe davranışın hangi saha testleriyle doğrulanacağını",
    },
    "/haberler/hibrit-inverter-backup-notr-toprak-bagi-rcd-atmasi": {
        "path": ROOT / "alo186/haberler/hibrit-inverter-backup-notr-toprak-bagi-rcd-atmasi/index.html",
        "intent": ("backup", "nötr-toprak", "ground relay", "RCD", "IEC 60364-8-82", "IEC 63552"),
        "sources": ("webstore.iec.ch", "victronenergy.com"),
        "separation": "hibrit inverter backup ve ada modunda kaynak referansı, nötr-toprak bağı, ground relay, nötr anahtarlama, RCD koruması ve transfer sırasının hangi belgeler ve saha testleriyle doğrulanacağını",
    },
    "/haberler/jenerator-mars-akusu-sarj-cihazi-on-isitici-start-hazirligi": {
        "path": ROOT / "alo186/haberler/jenerator-mars-akusu-sarj-cihazi-on-isitici-start-hazirligi/index.html",
        "intent": ("marş aküsü", "charger", "yardımcı AC", "jacket water heater", "overcrank", "NFPA 110"),
        "sources": ("nfpa.org", "cummins.com", "generac.com", "cat.com"),
        "separation": "standby jeneratörün kesintide ilk marş hazırlığında akü, charger, yardımcı AC besleme, kablo gerilim düşümü, ön ısıtıcı, kontrol alarmı ve transfer başlangıcının hangi ölçümlerle doğrulanacağını",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] >= 85, overlay["version"]
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
