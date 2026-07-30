from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run59.json"
PAGES = {
    "/haberler/elektrik-guc-artirimi-edas-tadilat-projesi-basvurusu": {
        "path": ROOT / "alo186/haberler/elektrik-guc-artirimi-edas-tadilat-projesi-basvurusu/index.html",
        "intent": ("güç artırımı", "bağlantı gücü", "tadilat projesi", "bağlantı görüşü", "kompanzasyon", "EDAŞ"),
        "sources": ("epdk.gov.tr", "ayedas.com.tr"),
    },
    "/haberler/jenerator-ats-3-kutuplu-4-kutuplu-notr-transferi-rcd": {
        "path": ROOT / "alo186/haberler/jenerator-ats-3-kutuplu-4-kutuplu-notr-transferi-rcd/index.html",
        "intent": ("3 kutuplu", "4 kutuplu", "solid neutral", "switched neutral", "N-PE", "RCD"),
        "sources": ("webstore.iec.ch", "se.com", "eaton.com"),
    },
    "/haberler/bess-round-trip-efficiency-yardimci-tuketim-ac-dc-verim": {
        "path": ROOT / "alo186/haberler/bess-round-trip-efficiency-yardimci-tuketim-ac-dc-verim/index.html",
        "intent": ("round-trip efficiency", "AC-AC", "yardımcı tüketim", "PCS", "HVAC", "ölçüm sınırı"),
        "sources": ("webstore.iec.ch", "nrel.gov"),
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 97
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    canonicals: set[str] = set()

    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
        folded = html.casefold()
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        description = re.search(r'<meta name="description" content="([^"]+)"', html)
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert title and description and h1 and canonical
        assert route in canonical.group(1)
        assert canonical.group(1).startswith("https://www.alo186.com/")
        titles.add(title.group(1))
        descriptions.add(description.group(1))
        h1s.add(h1.group(1))
        canonicals.add(canonical.group(1))
        for schema_type in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema_type in html
        assert html.count('"@type":"DefinedTerm"') >= 12
        assert html.count('"@type":"Question"') >= 5
        assert "<strong>Doğrudan cevap:</strong>" in html
        assert "Satın almama sınırı" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert html.count('href="/') >= 8
        assert "Son doğrulama: 30 Temmuz 2026" in html
        assert "/hesaplama/teknik-devir-kabul-paketi/" in html
        assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html
        for token in contract["intent"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for forbidden in ("garanti sonuç", "kesin çözüm", "hemen satın al", "stok tükeniyor", "ALO186 yetkili servisidir"):
            assert forbidden.casefold() not in folded

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)
    established = {
        "/haberler/elektrik-kesintisi-tazminati-edas-12-saat-yillik-kesinti",
        "/sektor-rehberi/elektrik-sayaci-arizasi",
        "/haberler/jenerator-yuk-siralama-load-shedding-motor-kalkisi",
        "/haberler/hibrit-inverter-backup-notr-toprak-bagi-rcd-atmasi",
        "/haberler/bess-augmentasyon-kapasite-kaybi-eol-kullanilabilir-enerji",
        "/haberler/bess-termal-kacak-off-gas-gaz-algilama-acil-durum",
    }
    assert not established & set(PAGES)
    print(json.dumps({"routingVersion": 97, "pages": list(PAGES), "verifiedAt": "2026-07-30"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
