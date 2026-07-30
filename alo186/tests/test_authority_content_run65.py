from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY_PATH = ROOT / "alo186/deployment/routing-overlays/content-authority-run65.json"
PAGES = {
    "/haberler/harmonik-thdi-tdd-pcc-ieee-519-aktif-filtre": {
        "path": ROOT / "alo186/haberler/harmonik-thdi-tdd-pcc-ieee-519-aktif-filtre/index.html",
        "intent": ("THDi", "TDD", "PCC", "IEEE 519", "aktif harmonik filtre", "maksimum talep"),
        "sources": ("standards.ieee.org", "se.com", "eaton.com"),
        "separation": ("K-factor", "kompanzasyon rezonansı", "dV/dt"),
    },
    "/haberler/ges-panel-hotspot-bypass-diyot-termografi-iv-curve": {
        "path": ROOT / "alo186/haberler/ges-panel-hotspot-bypass-diyot-termografi-iv-curve/index.html",
        "intent": ("hotspot", "bypass diyot", "termografi", "I-V eğrisi", "junction box", "gölgelenme"),
        "sources": ("iec.ch", "nrel.gov"),
        "separation": ("AFCI", "MC4", "izolasyon direnci"),
    },
    "/haberler/ev-sarj-74-11-22-kw-wallbox-arac-onboard-charger": {
        "path": ROOT / "alo186/haberler/ev-sarj-74-11-22-kw-wallbox-arac-onboard-charger/index.html",
        "intent": ("7,4 kW", "11 kW", "22 kW", "wallbox", "onboard charger", "dinamik yük yönetimi"),
        "sources": ("iec.ch", "tesla.com", "abb.com"),
        "separation": ("RDC-DD", "Plug & Charge", "kablo ısınması"),
    },
}


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def main() -> None:
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    assert overlay["version"] == 116
    assert overlay["generatedAt"] == "2026-07-30"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    canonicals: set[str] = set()

    for route, contract in PAGES.items():
        path = contract["path"]
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        folded = html.casefold()
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)"', html)
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert title and description and h1 and canonical, route
        assert route in canonical.group(1)
        assert canonical.group(1).startswith("https://www.alo186.com/")
        assert html.count("<h1") == 1
        titles.add(strip_tags(title.group(1)))
        descriptions.add(description.group(1))
        h1s.add(strip_tags(h1.group(1)))
        canonicals.add(canonical.group(1))

        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")
        for schema_type in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema_type in html, (route, schema_type)
        assert html.count('"@type":"DefinedTerm"') >= 16, route
        assert html.count('"@type":"Question"') >= 5, route
        assert "<strong>Doğrudan cevap:</strong>" in html
        assert "Satın almama sınırı" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert html.count('href="/') >= 8, route
        assert "Son doğrulama: 30 Temmuz 2026" in html
        assert "/hesaplama/teknik-devir-kabul-paketi/" in html
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html

        for token in contract["intent"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for token in contract["separation"]:
            assert token.casefold() in folded, (route, token)

        for forbidden in (
            "garanti sonuç", "kesin çözüm", "hemen satın al", "stok tükeniyor",
            "alo186 yetkili servisidir", '"@type":"Product"', '"@type":"Offer"',
            "priceCurrency", "aggregateRating", "availability",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)

    established = {
        "/haberler/harmonikli-yukte-trafo-k-factor-derating-isinma",
        "/haberler/kompanzasyon-harmonik-rezonans-detuned-reaktor-secimi",
        "/haberler/ges-inverter-afci-dc-ark-hatasi-alarmi-kapatilir-mi",
        "/haberler/ges-mc4-konnektor-isinma-farkli-marka-krimp",
        "/hesaplama/ev-sarj-uygunluk/",
        "/haberler/ev-sarj-dinamik-yuk-yonetimi-ct-yonu",
        "/haberler/ev-sarj-kacak-akim-type-a-type-b-6ma-rdc-dd",
    }
    assert not established & set(PAGES)

    print(json.dumps({
        "ok": True,
        "routingVersion": 116,
        "pages": list(PAGES),
        "verifiedAt": "2026-07-30",
        "definedTermsPerPage": 16,
        "faqPerPage": 5,
        "purchaseBoundary": True,
        "canonicalCollision": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
