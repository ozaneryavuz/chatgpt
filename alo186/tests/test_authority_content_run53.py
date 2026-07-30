from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run53.json"

PAGES = {
    "/haberler/jenerator-odasi-havalandirma-radyator-hava-debisi-egzoz-karsi-basinci": {
        "path": ROOT / "alo186/haberler/jenerator-odasi-havalandirma-radyator-hava-debisi-egzoz-karsi-basinci/index.html",
        "intent": ("radyatör hava debisi", "dış statik basınç", "sıcak hava geri dönüşü", "negatif basınç", "egzoz karşı basıncı", "Cummins T-030", "NFPA 110:2025"),
        "sources": ("powersuite.cummins.com", "link.nfpa.org"),
        "separation": "jeneratör odası havalandırmasını; radyatör hava debisi, dış statik basınç, sıcak hava geri dönüşü, oda basıncı, motor yanma havası ve egzoz karşı basıncı üzerinden doğrulamayı",
    },
    "/haberler/kacak-akim-rolesi-toplam-kacak-akim-emc-filtre-ups-surucu": {
        "path": ROOT / "alo186/haberler/kacak-akim-rolesi-toplam-kacak-akim-emc-filtre-ups-surucu/index.html",
        "intent": ("toplam kaçak akım bütçesi", "EMI/EMC filtreleri", "Y kapasitörleri", "ortak-mod akımı", "UPS transferi", "Type B", "devre bölümlendirmesi"),
        "sources": ("webstore.iec.ch", "se.com"),
        "separation": "kaçak akım rölesinin cihaz sayısı arttıkça açmasını; toplam kaçak akım bütçesi, EMI/EMC filtreleri, UPS ve sürücü ortak-mod akımları, geçici darbeler ve devre bölümlendirmesi üzerinden açıklamayı",
    },
    "/haberler/bess-augmentasyon-kapasite-kaybi-eol-kullanilabilir-enerji": {
        "path": ROOT / "alo186/haberler/bess-augmentasyon-kapasite-kaybi-eol-kullanilabilir-enerji/index.html",
        "intent": ("BESS augmentasyonu", "EOL kullanılabilir enerji", "oversizing", "yeni-eski rack", "PCS oranı", "IEC TS 62933-2-3:2025", "augmentasyon tetikleyicisi"),
        "sources": ("webstore.iec.ch", "atb.nrel.gov"),
        "separation": "BESS kapasite augmentasyonunu; EOL kullanılabilir enerji taahhüdü, ilk gün oversizing, kademeli rack ekleme, yeni-eski batarya uyumu, PCS oranı ve yeniden kabul testi üzerinden planlamayı",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 89, overlay["version"]
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
        "/haberler/jenerator-yuk-bankasi-testi-nasil-yapilir",
        "/haberler/kacak-akim-rolesi-ramp-testi-acma-akimi-suresi",
        "/haberler/bess-soc-soh-kullanilabilir-enerji-kapasite-testi",
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
