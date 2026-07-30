from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run56.json"

PAGES = {
    "/haberler/ges-pid-potansiyel-induklu-bozulma-anti-pid-teshis": {
        "path": ROOT / "alo186/haberler/ges-pid-potansiyel-induklu-bozulma-anti-pid-teshis/index.html",
        "intent": ("potansiyel indüklü bozulma", "PID-shunting", "PID-polarization", "anti-PID", "I-V eğrisi", "elektrolüminesans", "IEC TS 62804-1:2025"),
        "sources": ("webstore.iec.ch", "research-hub.nrel.gov", "info.support.huawei.com"),
        "separation": "PV üretim kaybında PID şüphesini kirlenme, gölgelenme, mikroçatlak, bağlantı ve izolasyon arızalarından ayırmak; modül kanıtı, I-V/EL teşhisi ve üretici onaylı anti-PID kararını tek kabul zincirinde doğrulamaktır",
    },
    "/haberler/bess-termal-kacak-off-gas-gaz-algilama-acil-durum": {
        "path": ROOT / "alo186/haberler/bess-termal-kacak-off-gas-gaz-algilama-acil-durum/index.html",
        "intent": ("off-gas", "termal kaçak", "UL 9540A", "NFPA 855", "LEL", "uzaktan erişilebilir gaz izleme", "sebep-sonuç matrisi"),
        "sources": ("link.nfpa.org", "taiwan.ul.com", "fsri.org", "sandia.gov"),
        "separation": "BESS kapasite, SoH veya UL 9540/9540A genel açıklamasını tekrar etmeden; off-gas, duman, sıcaklık, havalandırma, patlama kontrolü ve uzaktan alarmı model bazlı sebep–sonuç kabulünde doğrulamaktır",
    },
    "/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32r": {
        "path": ROOT / "alo186/haberler/jenerator-ters-guc-reverse-power-alarmi-ansi-32r/index.html",
        "intent": ("reverse power", "ANSI 32R", "motoring", "prime mover", "governor", "CT polaritesi", "kW paylaşımı", "IEEE C37.102-2023"),
        "sources": ("standards.ieee.org", "documentation.deif.com", "woodward.com", "selinc.com"),
        "separation": "paralel jeneratörde ters aktif gücü; prime mover tork kaybı, governor/yakıt sorunu, CT faz-yön hatası, kW paylaşımı ve koruma ayarından ayırarak olay kaydıyla doğrulamaktır",
    },
}


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 93, overlay["version"]
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES), routes

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    canonicals: set[str] = set()

    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
        folded_html = html.casefold()
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
            assert token.casefold() in folded_html, (route, token)
        for domain in contract["sources"]:
            assert domain.casefold() in folded_html, (route, domain)

        forbidden = (
            "garanti sonuç",
            "kesin çözüm",
            "hemen satın al",
            "son ürün",
            "stok tükeniyor",
            "ALO186 yetkili servisidir",
        )
        for token in forbidden:
            assert token.casefold() not in folded_html, (route, token)
        assert 'target="_blank" rel="noopener"' in html, route

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    assert len(canonicals) == len(PAGES)

    established = (
        "/haberler/ges-mc4-konnektor-isinma-farkli-marka-krimp",
        "/haberler/bess-soc-soh-kullanilabilir-enerji-kapasite-testi",
        "/haberler/jenerator-yuk-siralama-load-shedding-motor-kalkisi",
        "/haberler/jenerator-yakiti-day-tank-su-mikrobiyal-kirlenme-polishing",
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
