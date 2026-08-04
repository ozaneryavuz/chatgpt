from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "alo186/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-sureklilik-plani/index.html"
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-guvenlik-kamerasi-calisir-mi/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/kamera-nvr-ups-yedek-guc-secimi/index.html"
EVENTS = ROOT / "alo186/assets/journey-events-v260.js"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v268-cctv-continuity.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


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
    article = read(ARTICLE)
    selector = read(SELECTOR)
    events = read(EVENTS)
    overlay = json.loads(read(OVERLAY))
    policy = json.loads(read(POLICY))

    assert overlay["version"] == 268
    assert {item["canonicalPath"] for item in overlay["routes"]} == {
        "/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-sureklilik-plani/",
        "/haberler/elektrik-kesilince-guvenlik-kamerasi-calisir-mi/",
        "/amazon-elektrik-urunleri/kamera-nvr-ups-yedek-guc-secimi/",
    }
    assert "kamera-nvr-ups-yedek-guc" in policy["governedAffiliateRoutePatterns"]

    tool_graph = list(walk(jsonld(tool)))
    article_graph = list(walk(jsonld(article)))
    selector_graph = list(walk(jsonld(selector)))
    tool_types = {node.get("@type") for node in tool_graph if isinstance(node.get("@type"), str)}
    article_types = {node.get("@type") for node in article_graph if isinstance(node.get("@type"), str)}
    selector_types = {node.get("@type") for node in selector_graph if isinstance(node.get("@type"), str)}
    assert {"WebApplication", "HowTo", "HowToStep", "FAQPage", "BreadcrumbList"}.issubset(tool_types)
    assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(article_types)
    assert {"CollectionPage", "ItemList", "Product", "FAQPage", "BreadcrumbList"}.issubset(selector_types)
    assert sum(node.get("@type") == "HowToStep" for node in tool_graph) == 5
    assert sum(node.get("@type") == "Product" for node in selector_graph) == 3
    assert not ({"Offer", "AggregateRating", "Review"} & selector_types)

    schema = json.dumps(jsonld(tool) + jsonld(article) + jsonld(selector), ensure_ascii=False).casefold()
    for forbidden in ('"price"', '"pricecurrency"', '"availability"', '"offers"', '"aggregaterating"', '"review"', '"warranty"', '"delivery"'):
        assert forbidden not in schema, forbidden

    assert "amazon.com.tr" not in tool.casefold()
    assert "amazon.com.tr" not in article.casefold()
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
        "Satış ortaklığı açıklaması",
        "yeni ürün almayacağım",
        "fiyat, stok, satıcı puanı, ürün puanı, yorum, teslimat veya garanti",
        "Aktif tehlikede mağaza yolu kapalıdır",
        "Bağımsız bilgilendirme platformudur",
    ):
        assert phrase.casefold() in selector.casefold(), phrase
    assert selector.index("Satış ortaklığı açıklaması") < selector.index("data-affiliate-href")
    assert selector.index("Aktif tehlikede mağaza yolu kapalıdır") < selector.index("data-affiliate-href")

    for source in (tool, selector):
        lowered = source.casefold()
        assert 'type="email"' not in lowered
        assert 'type="tel"' not in lowered
        assert "xmlhttprequest" not in lowered
        assert "fetch(" not in lowered
        assert "localstorage" not in lowered
        assert "sessionstorage" not in lowered
        assert "/assets/journey-events-v260.js" in source
        assert "112" in source
        assert "resmî kurum" in source
        assert "30 gün" in source
        assert "90 gün" in source

    for required in (
        "NVR/DVR",
        "PoE",
        "router",
        "ONT",
        "W ve VA",
        "Mevcut UPS",
        "Schneider Electric",
        "Axis",
        "4 Ağustos 2026",
    ):
        assert required in tool or required in article or required in selector, required

    assert "/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-sureklilik-plani/" in article
    assert "/amazon-elektrik-urunleri/kamera-nvr-ups-yedek-guc-secimi/" in article
    assert '"dateModified":"2026-08-04"' in article
    assert "Son kaynak kontrolü: 4 Ağustos 2026" in article

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
        "articleIntentBridge": True,
        "monthlyAndQuarterlyReminders": True,
        "personalDataFields": 0,
        "unverifiedCommercialFields": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
