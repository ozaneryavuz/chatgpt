from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run54.json"

PAGES = {
    "/haberler/ev-sarj-ocpp-internet-kesilirse-offline-calismasi": {
        "path": ROOT / "alo186/haberler/ev-sarj-ocpp-internet-kesilirse-offline-calismasi/index.html",
        "intent": ("OCPP", "internet kesildiğinde", "Authorization cache", "Local Authorization List", "offline yetkilendirme", "CSMS", "IEC 63584:2024"),
        "sources": ("openchargealliance.org", "webstore.iec.ch"),
        "separation": "OCPP'li şarj istasyonunda internet kesildiğinde aktif oturum, offline yetkilendirme, yerel veri tamponu, yeniden bağlantı ve CSMS uzlaştırmasını",
    },
    "/haberler/jenerator-yuk-siralama-load-shedding-motor-kalkisi": {
        "path": ROOT / "alo186/haberler/jenerator-yuk-siralama-load-shedding-motor-kalkisi/index.html",
        "intent": ("yük ekleme", "load shedding", "motor kalkış", "UPS walk-in", "gerilim-frekans toparlanması", "ATS", "NFPA 110:2025"),
        "sources": ("cat.com", "powersuite.cummins.com", "link.nfpa.org"),
        "separation": "ATS sonrasında yük ekleme sırasını, motor kalkışını, UPS walk-in'i, kapasite kaybında load shedding'i ve kontrollü yük geri almayı",
    },
    "/haberler/ges-string-voc-sogukta-artar-inverter-dc-gerilim-siniri": {
        "path": ROOT / "alo186/haberler/ges-string-voc-sogukta-artar-inverter-dc-gerilim-siniri/index.html",
        "intent": ("PV string", "Voc", "sıcaklık katsayısı", "tasarım minimum sıcaklığı", "maksimum DC", "MPPT", "IEC 62548-1:2023+A1:2025"),
        "sources": ("webstore.iec.ch", "manuals.sma.de", "fronius.com"),
        "separation": "PV string seri modül sayısını soğuk Voc, modül sıcaklık katsayısı, tasarım minimum sıcaklığı, inverter maksimum DC ve MPPT çalışma aralığı üzerinden doğrulamaktır",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 90, overlay["version"]
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
        assert "Teknik devir-kabul" in html, route
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html, route

        for token in contract["intent"]:
            assert token in html, (route, token)
        for domain in contract["sources"]:
            assert domain in html, (route, domain)

        forbidden = (
            "garanti sonuç",
            "kesin çözüm",
            "hemen satın al",
            "son ürün",
            "stok tükeniyor",
            "ALO186 yetkili servisidir",
        )
        lower = html.lower()
        for token in forbidden:
            assert token.lower() not in lower, (route, token)
        assert 'target="_blank" rel="noopener"' in html, route

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)

    established = (
        "/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-sayac-faz-eslesmesi",
        "/haberler/jenerator-yuk-bankasi-testi-nasil-yapilir",
        "/haberler/ges-zero-export-sifir-ihracat-ct-sayac-yonu",
        "/haberler/ges-mc4-konnektor-isinma-farkli-marka-krimp",
    )
    assert not set(established) & set(PAGES)

    print(json.dumps({
        "routingVersion": overlay["version"],
        "pages": list(PAGES),
        "articleCount": len(PAGES),
        "schema": ["Article", "FAQPage", "BreadcrumbList", "DefinedTerm"],
        "verifiedAt": "2026-07-30",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
