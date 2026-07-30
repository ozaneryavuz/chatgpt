from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run55.json"

PAGES = {
    "/haberler/trafo-sahasinda-adim-dokunma-gerilimi-topraklama": {
        "path": ROOT / "alo186/haberler/trafo-sahasinda-adim-dokunma-gerilimi-topraklama/index.html",
        "intent": ("adım gerilimi", "dokunma gerilimi", "toprak potansiyel yükselmesi", "GPR", "transfer potansiyeli", "arıza akımı", "IEEE 81-2025"),
        "sources": ("standards.ieee.org", "webstore.iec.ch", "omicronenergy.com"),
        "separation": "trafo ve OG sahasında GPR, adım gerilimi, dokunma gerilimi, transfer potansiyeli, arıza akımı ve koruma açma süresini tek insan güvenliği kabul zincirinde doğrulamaktır",
    },
    "/haberler/jenerator-yakiti-day-tank-su-mikrobiyal-kirlenme-polishing": {
        "path": ROOT / "alo186/haberler/jenerator-yakiti-day-tank-su-mikrobiyal-kirlenme-polishing/index.html",
        "intent": ("day tank", "serbest su", "mikrobiyal kirlenme", "fuel polishing", "yakıt filtresi", "transfer pompası", "NFPA 110:2025"),
        "sources": ("link.nfpa.org", "cat.com", "donaldson.com"),
        "separation": "standby jeneratörde yakıt depolama, day tank transferi, serbest su, mikrobiyal kirlenme, fuel polishing, alarm zinciri ve yük altında yakıt güvenilirliğini birlikte doğrulamaktır",
    },
    "/haberler/vpp-talep-tarafi-katilimi-teias-2026-tesis-katilim-sartlari": {
        "path": ROOT / "alo186/haberler/vpp-talep-tarafi-katilimi-teias-2026-tesis-katilim-sartlari/index.html",
        "intent": ("5.000 MWh", "3 MW", "37,5 MW", "30–500 MW", "kontrol sayacı", "kapasite bedeli", "aktivasyon bedeli", "TEİAŞ"),
        "sources": ("teias.gov.tr", "webim.teias.gov.tr", "epdk.gov.tr"),
        "separation": "2026 TEİAŞ talep tarafı katılımında tüketim tesisi uygunluğu, toplayıcı portföy eşikleri, kapasite ve aktivasyon gelirleri, kritik saatler, kontrol sayacı ve sözleşme kanıtlarını tek katılım kararı içinde ayırmaktır",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 91, overlay["version"]
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
        assert html.count('"@type":"DefinedTerm"') >= 12, route
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
        "/haberler/topraklama-olcumunde-kazikli-pens-62-yuzde-yontemi",
        "/haberler/jenerator-yakit-tuketimi-litre-saat-yuk-faktoru",
        "/haberler/vpp-temel-tuketim-degeri-baseline-telemetri-uzlastirma",
        "/haberler/vpp-telemetri-kontrol-protokol-toplayici-hazirlik",
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
