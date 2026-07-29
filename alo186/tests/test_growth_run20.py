from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest  # noqa: E402

ROUTES = {
    "/hesaplama/usb-c-sarj-zinciri-uygunluk/": "alo186/hesaplama/usb-c-sarj-zinciri-uygunluk/index.html",
    "/hesaplama/usb-c-urun-kabul-testi/": "alo186/hesaplama/usb-c-urun-kabul-testi/index.html",
    "/urun-bilgi-grafigi/usb-c-ekosistemi/": "alo186/urun-bilgi-grafigi/usb-c-ekosistemi/index.html",
}
FORBIDDEN = ["priceCurrency", "availability", "aggregateRating", "offers", "stokta", "garanti süresi", "resmî onaylı"]


def scripts(html: str) -> list[str]:
    return re.findall(r'<script(?![^>]+type=["\']application/ld\+json["\'])[^>]*>(.*?)</script>', html, re.I | re.S)


def main() -> None:
    manifest = load_effective_manifest(ROOT)
    assert manifest["version"] >= 71, manifest["version"]
    active = {item["canonicalPath"]: item for item in manifest["routes"]}
    for route, source in ROUTES.items():
        assert route in active, route
        assert active[route]["source"] == source
        assert (ROOT / source).is_file()

    chain = (ROOT / ROUTES["/hesaplama/usb-c-sarj-zinciri-uygunluk/"]).read_text(encoding="utf-8")
    acceptance = (ROOT / ROUTES["/hesaplama/usb-c-urun-kabul-testi/"]).read_text(encoding="utf-8")
    graph = (ROOT / ROUTES["/urun-bilgi-grafigi/usb-c-ekosistemi/"]).read_text(encoding="utf-8")

    for route, html in [(list(ROUTES)[0], chain), (list(ROUTES)[1], acceptance), (list(ROUTES)[2], graph)]:
        assert f'rel="canonical" href="https://www.alo186.com{route}"' in html
        assert html.count("<h1>") == 1
        assert "ALO186" in html and "bağımsız" in html.casefold()
        assert "satış ortaklığı" in html.casefold()
        assert "fiyat" in html.casefold() and "stok" in html.casefold() and "puan" in html.casefold()
        for token in FORBIDDEN:
            assert token.casefold() not in html.casefold(), (route, token)
        assert 'type="email"' not in html and 'type="tel"' not in html
        payloads = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
        assert payloads
        nodes = [node for payload in payloads for node in payload.get("@graph", [])]
        assert any(node.get("@type") == "BreadcrumbList" for node in nodes)
        assert not any(node.get("@type") in {"Offer", "AggregateRating"} for node in nodes)

    assert len(scripts(chain)) == 1
    assert len(scripts(acceptance)) == 1
    assert len(scripts(graph)) == 0
    for html in [chain, acceptance]:
        assert "localStorage" in html
        assert "kişisel verisiz" in html.casefold()
        assert "satın alma" in html.casefold()
        assert "sponsored" not in html.casefold(), "Araçlar doğrudan mağaza affiliate linki taşımamalı"
        assert "amazon.com.tr" not in html.casefold()

    assert "Mevcut zincir yeterli — satın alma yok" in chain
    assert "Isınma, yanık kokusu, erime" in chain
    assert "90 günlük yeniden kontrol" in chain
    assert "/akilli-urun-secimi?kategori=usb_c_charger" in chain
    assert "/akilli-urun-secimi?kategori=usb_c_cable" in chain

    assert "İlk başarısızlık yeni ürün kararı değildir" in acceptance
    assert "samefail" in acceptance
    assert "30 günlük tekrar" in acceptance
    assert "Aşırı sıcak, koku, erime" in acceptance

    assert "DefinedTermSet" in graph
    assert "usb_c_charger" in graph and "usb_c_cable" in graph and "powerbank" in graph
    for visible_node in ["1. Cihaz", "2. Protokol", "3. Adaptör", "4. Kablo", "5. Powerbank"]:
        assert visible_node in graph, visible_node
    assert "Mevcut zinciri test edin" in graph
    assert "amazon.com.tr" not in graph.casefold()

    injector = (DEPLOYMENT / "inject_growth_run20.py").read_text(encoding="utf-8")
    for token in ["growthRun20", "directAffiliateLinksAdded", "hazardCommerceClosed", "firstFailureCommerceClosed", "existingEquipmentNoBuyPreserved", "unverifiedCommercialFieldsUsed"]:
        assert token in injector

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "routes": list(ROUTES),
        "directAffiliateLinksAdded": 0,
        "hazardCommerceClosed": True,
        "firstFailureCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "rawPersonalDataCollected": False,
        "unverifiedCommercialFieldsUsed": [],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
