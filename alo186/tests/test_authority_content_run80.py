from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/content-authority-run80.json"
PAGES = {
    "/haberler/elektrik-gerilim-kalitesi-sikayeti-edas-bir-haftalik-olcum": {
        "path": ROOT / "alo186/haberler/elektrik-gerilim-kalitesi-sikayeti-edas-bir-haftalik-olcum/index.html",
        "intent": ("Bir haftalık ölçüm", "Gerilim çukuru", "Flicker", "Ölçüm noktası", "Teknik kalite dosyasında"),
        "sources": ("epdk.gov.tr", "iec.ch"),
        "separation": ("dağıtım bağlantı noktasındaki teknik kalite şikâyeti, bir haftalık ölçüm ve kanıt dosyasını", "kesinti tazminatı rehberi", "GES yüksek gerilim rehberi"),
        "boundary": "Regülatör veya UPS satın almama sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/jenerator-kisa-devre-akimi-sigorta-koruma-koordinasyonu": {
        "path": ROOT / "alo186/haberler/jenerator-kisa-devre-akimi-sigorta-koruma-koordinasyonu/index.html",
        "intent": ("Subtransient reaktans", "decrement eğrisi", "Minimum arıza akımını", "Zaman-akım eğrilerini", "ikincil enjeksiyon"),
        "sources": ("cat.com", "cummins.com"),
        "separation": ("jeneratör modundaki kısa devre akımı ve koruma cihazlarının zaman-akım koordinasyonunu", "jeneratör nötrü ve ATS rehberi", "düşük yük rehberi"),
        "boundary": "Şalteri büyütmeme ve ayarı kör değiştirmeme sınırı",
        "cta": "/hizmetler/elektrik-surekliligi/",
    },
    "/haberler/ev-sarj-plug-charge-iso-15118-sertifika-ocpp": {
        "path": ROOT / "alo186/haberler/ev-sarj-plug-charge-iso-15118-sertifika-ocpp/index.html",
        "intent": ("Plug & Charge", "Contract certificate", "V2G PKI", "Sertifika iptal", "OCPP ISO 15118 profili"),
        "sources": ("iso.org", "charin.global", "openchargealliance.org"),
        "separation": ("Plug & Charge sertifika, PKI ve arka uç yetkilendirme zincirini", "OCPP sürüm rehberi", "kWh ve fatura rehberi"),
        "boundary": "Yeni wallbox veya backend satın almama sınırı",
        "cta": "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
    },
}


def text_between(pattern: str, html: str) -> str:
    match = re.search(pattern, html, re.S | re.I)
    assert match, pattern
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert overlay["version"] == 144
    assert overlay["generatedAt"] == "2026-07-31"
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert set(routes) == set(PAGES)

    titles: set[str] = set()
    descriptions: set[str] = set()
    h1s: set[str] = set()
    for route, contract in PAGES.items():
        html = contract["path"].read_text(encoding="utf-8")
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
        assert html.count('"@type":"DefinedTerm"') >= 8
        assert html.count('"@type":"Question"') >= 5
        assert "Doğrudan cevap" in html
        assert contract["boundary"] in html
        assert html.count('href="/') >= 8
        assert "Son doğrulama: 31 Temmuz 2026" in html
        assert contract["cta"] in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Kaynaklar" in html
        for token in contract["intent"] + contract["separation"]:
            assert token.casefold() in folded, (route, token)
        for domain in contract["sources"]:
            assert domain in folded, (route, domain)
        for forbidden in (
            '"@type":"Product"',
            '"@type":"Offer"',
            "priceCurrency",
            "aggregateRating",
            "availability",
            "hemen satın al",
            "stok tükeniyor",
        ):
            assert forbidden.casefold() not in folded, (route, forbidden)
        assert routes[route]["type"] == "article"
        assert routes[route]["source"].endswith("/index.html")

    assert len(titles) == len(PAGES)
    assert len(descriptions) == len(PAGES)
    assert len(h1s) == len(PAGES)
    print(json.dumps({
        "ok": True,
        "routingVersion": 144,
        "pages": list(PAGES),
        "verifiedAt": "2026-07-31",
        "faqPerPage": 5,
        "definedTermsMinimum": 8,
        "canonicalCollision": False,
        "purchaseBoundary": True,
        "intentSeparation": True,
        "primarySourceOnly": True,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
