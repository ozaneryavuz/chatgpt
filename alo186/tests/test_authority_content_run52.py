from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run52.json"

PAGES = {
    "/haberler/harmonik-thdi-tdd-thdv-pcc-olcum-farki": {
        "path": ROOT / "alo186/haberler/harmonik-thdi-tdd-thdv-pcc-olcum-farki/index.html",
        "intent": ("THDi", "TDD", "THDv", "PCC", "I<sub>L</sub>", "I<sub>SC</sub>", "IEEE 519-2022"),
        "sources": ("standards.ieee.org", "webstore.iec.ch", "eaton.com", "se.com"),
        "separation": "THDi, TDD ve THDv göstergelerini; PCC ölçüm noktası, maksimum talep akımı I<sub>L</sub>, kısa devre oranı ve IEEE 519 uygunluk kanıtı üzerinden birbirinden ayırmayı",
    },
    "/haberler/ups-backfeed-korumasi-bakim-bypass-interlock-guvenli-izolasyon": {
        "path": ROOT / "alo186/haberler/ups-backfeed-korumasi-bakim-bypass-interlock-guvenli-izolasyon/index.html",
        "intent": ("backfeed", "bakım bypassı", "shunt trip", "yardımcı kontak", "SKRU", "Kirk key", "IEC 62040-1"),
        "sources": ("webstore.iec.ch", "productinfo.se.com"),
        "separation": "UPS backfeed korumasını statik ve bakım bypassından ayırmayı; haricî ayırıcı, shunt trip, yardımcı kontak, mekanik interlock ve çok kaynaklı güvenli izolasyon kabulünü",
    },
    "/haberler/elektrik-baglanti-gucu-yuzde-20-artarsa-guc-artirimi-edas-basvurusu": {
        "path": ROOT / "alo186/haberler/elektrik-baglanti-gucu-yuzde-20-artarsa-guc-artirimi-edas-basvurusu/index.html",
        "intent": ("bağlantı gücü", "yüzde 20", "güç artırımı", "bağlantı görüşü", "talep gücü", "tadilat projesi", "EDAŞ"),
        "sources": ("epdk.gov.tr", "tuketici.epdk.gov.tr", "tedas.gov.tr"),
        "separation": "mesken dışı tesiste bağlantı gücünün yüzde 20'den fazla artmasını; kurulu güç, gerçek talep, EDAŞ bağlantı görüşü, tadilat projesi, dağıtım kapasitesi ve kabul kanıtı üzerinden yönetmeyi",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 88, overlay["version"]
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
        "/haberler/k-faktor-trafo-harmonik-yuklerde-nasil-secilir",
        "/haberler/ups-epo-rpo-acil-kapatma-nasil-calisir",
        "/haberler/ev-sarj-rcd-tip-b-rdc-dd-6ma-farki",
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
