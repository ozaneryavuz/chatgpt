from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run58.json"
PAGES = {
    "/haberler/ev-sarj-plug-and-charge-iso-15118-sertifika-hatasi": {
        "path": ROOT / "alo186/haberler/ev-sarj-plug-and-charge-iso-15118-sertifika-hatasi/index.html",
        "intent": ("Plug & Charge", "ISO 15118-20", "sözleşme sertifikası", "V2G PKI", "EVCC", "SECC"),
        "sources": ("iso.org", "charin.global"),
    },
    "/haberler/ges-inverter-anti-islanding-ada-calismasi-koruma-testi": {
        "path": ROOT / "alo186/haberler/ges-inverter-anti-islanding-ada-calismasi-koruma-testi/index.html",
        "intent": ("anti-islanding", "istemsiz ada", "IEC 62116:2014", "yeniden bağlanma", "EDAŞ kabulü", "grid rölesi"),
        "sources": ("webstore.iec.ch", "epdk.gov.tr", "manuals.fronius.com"),
    },
    "/haberler/harmonikli-yukte-trafo-k-factor-derating-isinma": {
        "path": ROOT / "alo186/haberler/harmonikli-yukte-trafo-k-factor-derating-isinma/index.html",
        "intent": ("K-factor", "derating", "harmonik kayıp", "nötr akımı", "IEEE C57.110", "K-rated trafo"),
        "sources": ("standards.ieee.org", "se.com"),
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 95
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
        "/haberler/ev-sarj-ocpp-internet-kesilirse-offline-calismasi",
        "/haberler/elektrikli-arac-sarj-olmuyor-wallbox-neden-baslamiyor",
        "/haberler/ges-elektrik-kesintisinde-calisir-mi",
        "/haberler/ges-zero-export-sifir-ihracat-ct-sayac-yonu",
        "/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler",
        "/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur",
    }
    assert not established & set(PAGES)
    print(json.dumps({"routingVersion": 95, "pages": list(PAGES), "verifiedAt": "2026-07-30"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
