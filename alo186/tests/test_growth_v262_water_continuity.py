from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "alo186/hesaplama/hidrofor-elektrik-kesintisi-yedekleme-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/pilli-su-kacagi-alarmi-secimi/index.html"
EVENTS = ROOT / "alo186/assets/journey-events-v260.js"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v262-water-continuity.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def jsonld(source: str) -> list[object]:
    blocks = re.findall(
        r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
        flags=re.I | re.S,
    )
    assert blocks
    return [json.loads(block.strip()) for block in blocks]


def walk(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main() -> None:
    tool = read(TOOL)
    selector = read(SELECTOR)
    events = read(EVENTS)
    overlay = json.loads(read(OVERLAY))

    assert overlay["version"] == 262
    assert {item["canonicalPath"] for item in overlay["routes"]} == {
        "/hesaplama/hidrofor-elektrik-kesintisi-yedekleme-plani/",
        "/amazon-elektrik-urunleri/pilli-su-kacagi-alarmi-secimi/",
    }
    assert "https://alo186.com/hesaplama/hidrofor-elektrik-kesintisi-yedekleme-plani/" in tool
    assert "https://alo186.com/amazon-elektrik-urunleri/pilli-su-kacagi-alarmi-secimi/" in selector

    tool_graph = list(walk(jsonld(tool)))
    selector_graph = list(walk(jsonld(selector)))
    tool_types = {node.get("@type") for node in tool_graph if isinstance(node.get("@type"), str)}
    selector_types = {node.get("@type") for node in selector_graph if isinstance(node.get("@type"), str)}
    assert {"WebApplication", "HowTo", "HowToStep", "FAQPage", "BreadcrumbList"}.issubset(tool_types)
    assert {"CollectionPage", "ItemList", "Product", "FAQPage", "BreadcrumbList"}.issubset(selector_types)
    assert sum(node.get("@type") == "HowToStep" for node in tool_graph) == 5
    assert sum(node.get("@type") == "Product" for node in selector_graph) == 3
    assert not ({"Offer", "AggregateRating", "Review"} & selector_types)

    schema = json.dumps(jsonld(tool) + jsonld(selector), ensure_ascii=False).casefold()
    for forbidden in ('"price"', '"pricecurrency"', '"availability"', '"offers"', '"aggregaterating"', '"review"'):
        assert forbidden not in schema, forbidden

    for anchor in re.findall(r'<a\b[^>]*>', selector, flags=re.I):
        href = re.search(r'\shref="([^"]+)"', anchor, flags=re.I)
        assert not (href and "amazon.com.tr/" in href.group(1).casefold()), anchor
    locked_links = re.findall(r'<a\b[^>]*data-affiliate-href="([^"]+)"[^>]*>', selector, flags=re.I)
    assert len(locked_links) == 3
    assert all("amazon.com.tr/" in link and "tag=alo186rehber-21" in link for link in locked_links)
    for tag in re.findall(r'<a\b[^>]*data-affiliate-href="[^"]+"[^>]*>', selector, flags=re.I):
        rel = re.search(r'rel="([^"]+)"', tag, flags=re.I)
        assert rel
        assert {"sponsored", "nofollow", "noopener"}.issubset(set(rel.group(1).split()))
        assert 'aria-disabled="true"' in tag

    for phrase in (
        "Reklam / satış ortaklığı açıklaması",
        "Mevcut çözümüm yeterli — yeni ürün almayacağım",
        "Fiyat, stok, satıcı, teslimat, puan, yorum ve garanti",
        "ALO186 satıcı değildir",
    ):
        assert phrase in selector, phrase

    for source in (tool, selector):
        lowered = source.casefold()
        assert 'type="email"' not in lowered
        assert 'type="tel"' not in lowered
        assert "xmlhttprequest" not in lowered
        assert "fetch(" not in lowered
        assert "/assets/journey-events-v260.js" in source
        assert "ALO186" in source and "resmî kurum" in source

    assert "grundfos.com" in tool
    assert "epa.gov/watersense" in tool
    assert "epa.gov/watersense" in selector
    assert "yeni UPS, inverter veya jeneratör almayın" in tool
    assert "tüketici UPS’iyle seçilmemelidir" in tool
    assert "Su kaçağı alarmı onarım veya güvenlik garantisi değildir" in selector
    assert selector.index("Güvenlik sınırı") < selector.index("data-affiliate-href")

    assert "30 gün" in tool and "90 gün" in tool
    assert "30 gün" in selector and "90 gün" in selector
    for required_event in (
        "tool_started",
        "tool_completed",
        "no_buy_selected",
        "affiliate_unlocked",
        "affiliate_clicked",
        "reminder_downloaded",
    ):
        assert required_event in events

    print(json.dumps({
        "ok": True,
        "routes": len(overlay["routes"]),
        "productClasses": 3,
        "affiliateLinksLocked": len(locked_links),
        "professionalMotorGate": True,
        "personalDataFields": 0,
        "unverifiedCommercialFields": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
