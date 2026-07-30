from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run64.json"
PAGES = {
    "/haberler/ges-inverter-afci-dc-ark-hatasi-alarmi-kapatilir-mi": {
        "path": ROOT / "alo186/haberler/ges-inverter-afci-dc-ark-hatasi-alarmi-kapatilir-mi/index.html",
        "intents": ("AFCI", "DC ark", "alarm kapatılır", "seri ark", "krimp", "manuel reset"),
        "sources": ("iec.ch", "sma.de", "huawei.com", "solaredge.com"),
        "separation": ("ges-mc4-konnektor-isinma", "ges-inverter-izolasyon-direnci", "anti-islanding"),
    },
    "/haberler/santiye-elektrigi-gecici-baglanti-edas-basvurusu": {
        "path": ROOT / "alo186/haberler/santiye-elektrigi-gecici-baglanti-edas-basvurusu/index.html",
        "intents": ("Şantiye elektriği", "geçici bağlantı", "yapı ruhsatı", "elektrik projesi", "kalıcı bağlantı", "enerji izni"),
        "sources": ("epdk.gov.tr", "ayedas.com.tr", "tedas.gov.tr"),
        "separation": ("elektrik-guc-artirimi", "elektrik-arizasinda-edas", "elektrik-faturasi-itiraz"),
    },
    "/haberler/kacak-akim-rolesi-selektivite-s-tipi-ust-alt-rcd": {
        "path": ROOT / "alo186/haberler/kacak-akim-rolesi-selektivite-s-tipi-ust-alt-rcd/index.html",
        "intents": ("RCD seçiciliği", "S tipi", "üst RCD", "alt RCD", "birlikte atar", "zaman gecikmesi"),
        "sources": ("iec.ch", "se.com"),
        "separation": ("kacak-akim-rolesi-ramp-testi", "kacak-akim-rolesi-neden-surekli-atar", "ev-sarj-kacak-akim"),
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 106
    assert overlay["generatedAt"] == "2026-07-30"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    canonicals: set[str] = set()

    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
        folded = html.casefold()
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)"', html)
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert title and description and h1 and canonical
        assert route in canonical.group(1)
        assert canonical.group(1).startswith("https://alo186.com/")
        assert html.count("<h1>") == 1
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")
        titles.add(title.group(1))
        descriptions.add(description.group(1))
        h1s.add(h1.group(1))
        canonicals.add(canonical.group(1))

        for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema in html
        assert html.count('"@type":"DefinedTerm"') >= 12
        assert html.count('"@type":"Question"') >= 5
        assert "<strong>Doğrudan cevap:</strong>" in html
        assert "Güvenlik sınırı" in html
        assert "Satın almama sınırı" in html
        assert "Son doğrulama: 30 Temmuz 2026" in html
        assert html.count('href="/') >= 8
        assert "/hesaplama/teknik-devir-kabul-paketi/" in html
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html
        for token in contract["intents"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for token in contract["separation"]:
            assert token in folded, (route, token)
        for forbidden in (
            "kesin çözüm", "garanti sonuç", "hemen satın al", "stok tükeniyor",
            "alo186 yetkili servisidir", '"@type":"Product"', '"@type":"Offer"'
        ):
            assert forbidden not in folded

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)

    established = {
        "/haberler/ges-mc4-konnektor-isinma-farkli-marka-krimp",
        "/haberler/ges-inverter-izolasyon-direnci-dusuk-hatasi",
        "/haberler/elektrik-guc-artirimi-edas-tadilat-projesi-basvurusu",
        "/haberler/kacak-akim-rolesi-ramp-testi-acma-akimi-suresi",
        "/haberler/kacak-akim-rolesi-neden-surekli-atar",
    }
    assert not established & set(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 106,
        "pages": list(PAGES),
        "definedTermsMinimum": 12,
        "faqMinimum": 5,
        "verifiedAt": "2026-07-30",
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
