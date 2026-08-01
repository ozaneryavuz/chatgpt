from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run92.json"
PAGES = {
    "/haberler/inverter-dc-bus-overvoltage-frenleme-direnci-yavaslama-rampi": {
        "path": ROOT / "alo186/haberler/inverter-dc-bus-overvoltage-frenleme-direnci-yavaslama-rampi/index.html",
        "intent": ("DC bus overvoltage", "rejeneratif enerji", "yavaşlama rampası", "frenleme direnci", "fren kıyıcı"),
        "sources": ("se.com",),
        "separation": ("motor yavaşlarken DC baraya dönen enerji", "dV/dt ve sinüs filtre rehberi", "THDi–TDD rehberi"),
        "boundary": "Yavaşlama rampası, yük ataleti ve frenleme enerjisi ölçülmeden fren direnci veya daha büyük sürücü satın almayın",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/ats-kontak-yapismasi-konum-uyusmazligi-mekanik-kilit-testi": {
        "path": ROOT / "alo186/haberler/ats-kontak-yapismasi-konum-uyusmazligi-mekanik-kilit-testi/index.html",
        "intent": ("kontak yapışması", "konum uyuşmazlığı", "yardımcı kontak", "mekanik kilit", "double-throw"),
        "sources": ("iec.ch", "se.com"),
        "separation": ("ana güç kontağı ile konum geri bildirimi", "ATS zamanlama rehberi", "reverse power rehberi"),
        "boundary": "Ana kontak konumu ve yardımcı kontak geri bildirimi doğrulanmadan ATS kontrolörü veya transfer mekanizması satın almayın",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/monofazeden-trifazeye-gecis-edas-proje-sayac-guc-degisimi": {
        "path": ROOT / "alo186/haberler/monofazeden-trifazeye-gecis-edas-proje-sayac-guc-degisimi/index.html",
        "intent": ("monofazeden trifazeye", "bağlantı görüşü", "tadilat projesi", "trifaze sayaç", "faz dengesi"),
        "sources": ("epdk.gov.tr", "ayedas.com.tr", "tedas.gov.tr"),
        "separation": ("faz sayısının değiştirilmesi", "güç artışı rehberi", "şantiye bağlantısı rehberi"),
        "boundary": "Dağıtım bağlantı görüşü ve onaylı tadilat projesi olmadan sayaç, ana sigorta veya faz sayısını değiştirmeyin",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 158
    assert overlay["generatedAt"] == "2026-08-01"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    for route, contract in PAGES.items():
        path = contract["path"]
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        folded = html.casefold()
        title = text_between(r"<title>(.*?)</title>", html)
        h1 = text_between(r"<h1>(.*?)</h1>", html)
        description = re.search(r'<meta name="description" content="([^"]+)"', html)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        assert description and canonical
        assert canonical.group(1) == f"https://alo186.com{route}"
        assert html.count("<h1") == 1
        assert 35 <= len(title) <= 100, (route, len(title))
        assert 100 <= len(description.group(1)) <= 190, (route, len(description.group(1)))
        titles.add(title)
        h1s.add(h1)
        descriptions.add(description.group(1))

        for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
            assert schema in html, (route, schema)
        assert html.count('"@type":"DefinedTerm"') >= 10
        assert html.count('"@type":"Question"') == 5
        assert html.count("<details>") == 5
        assert "Doğrudan cevap" in html
        assert "10 adımlık" in html
        assert "14 alan" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert contract["boundary"] in html
        assert contract["cta"] in html
        assert html.count('href="/') >= 8
        assert "Son doğrulama: 1 Ağustos 2026" in html
        assert "Kaynaklar" in html

        for token in contract["intent"] + contract["separation"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for forbidden in (
            '"@type":"Product"', '"@type":"Offer"', "priceCurrency",
            "aggregateRating", "availability", "hemen satın al", "stok tükeniyor",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)

        assert routes[route]["type"] == "article"
        assert routes[route]["source"] == str(path.relative_to(ROOT))

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 158,
        "pages": list(PAGES),
        "verifiedAt": "2026-08-01",
        "faqPerPage": 5,
        "definedTermsMinimum": 10,
        "canonicalCollision": False,
        "purchaseBoundary": True,
        "intentSeparation": True,
        "primarySourceOnly": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
