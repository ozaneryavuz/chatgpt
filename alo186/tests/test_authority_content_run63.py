from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run63.json"
PAGES = {
    "/haberler/elektrik-kesintisi-tazminati-otomatik-odeme-12-saat": {
        "path": ROOT / "alo186/haberler/elektrik-kesintisi-tazminati-otomatik-odeme-12-saat/index.html",
        "intent": ("Elektrik kesintisi tazminatı", "otomatik ödeme", "12 saat", "ESÜRE", "ESAYI", "on iş günü"),
        "sources": ("epdk.gov.tr",),
    },
    "/haberler/parafudr-tip-1-tip-2-tip-3-koordinasyonu": {
        "path": ROOT / "alo186/haberler/parafudr-tip-1-tip-2-tip-3-koordinasyonu/index.html",
        "intent": ("Tip 1", "Tip 2", "Tip 3", "Iimp", "enerji koordinasyonu", "yedek sigorta"),
        "sources": ("webstore.iec.ch", "se.com", "dehn-international.com"),
    },
    "/haberler/ges-panel-hot-spot-bypass-diyot-string-uyumsuzlugu": {
        "path": ROOT / "alo186/haberler/ges-panel-hot-spot-bypass-diyot-string-uyumsuzlugu/index.html",
        "intent": ("hot spot", "bypass diyot", "string uyumsuzluğu", "termografi", "I-V", "EL"),
        "sources": ("webstore.iec.ch", "nrel.gov"),
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 101
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
        "/haberler/elektrik-kesintisi-cihaz-hasari-edas-basvurusu",
        "/haberler/anlik-elektrik-kesintisi-tekrar-kapama-recloser-edas-kaydi",
        "/haberler/parafudr-yedek-sigorta-scpd-nasil-secilir",
        "/haberler/parafudr-kirmizi-gosterge-kartus-degisimi-yedek-sigorta",
        "/haberler/ges-pid-potansiyel-induklu-bozulma-anti-pid-teshis",
        "/haberler/ges-inverter-afci-dc-ark-hatasi",
    }
    assert not established & set(PAGES)
    print(json.dumps({"routingVersion": 101, "pages": list(PAGES), "verifiedAt": "2026-07-30"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
