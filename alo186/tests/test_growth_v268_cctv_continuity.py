from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "alo186/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-sureklilik-plani/index.html"
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-guvenlik-kamerasi-calisir-mi/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/kamera-nvr-ups-yedek-guc-secimi/index.html"
EVENTS = ROOT / "alo186/assets/journey-events-v260.js"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v268-cctv-continuity.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() == "a":
            self.anchors.append({key.casefold(): value or "" for key, value in attrs})


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
    assert {"WebApplication", "HowTo", "HowToStep", "BreadcrumbList"}.issubset(tool_types)
    assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(article_types)
    assert {"ItemList", "Product", "FAQPage", "BreadcrumbList"}.issubset(selector_types)
    assert sum(node.get("@type") == "HowToStep" for node in tool_graph) == 5
    assert sum(node.get("@type") == "Product" for node in selector_graph) == 2
    assert not ({"Offer", "AggregateRating", "Review"} & selector_types)

    schema = json.dumps(jsonld(tool) + jsonld(article) + jsonld(selector), ensure_ascii=False).casefold()
    for forbidden in ('"price"', '"pricecurrency"', '"availability"', '"offers"', '"aggregaterating"', '"review"', '"warranty"', '"delivery"'):
        assert forbidden not in schema, forbidden

    assert "amazon.com.tr" not in tool.casefold()
    assert "amazon.com.tr" not in article.casefold()
    parser = AnchorParser()
    parser.feed(selector)
    locked = [anchor for anchor in parser.anchors if anchor.get("id") in {"sdLink", "upsLink"}]
    assert len(locked) == 2
    for anchor in locked:
        assert not anchor.get("href")
        assert anchor.get("aria-disabled") == "true"
        assert {"sponsored", "nofollow", "noopener"}.issubset(set(anchor.get("rel", "").split()))

    for phrase in (
        "Satış ortaklığı açıklaması",
        "yeni ürün almayacağım",
        "Fiyat, stok, satıcı, puan, yorum, teslimat ve garanti",
        "mağaza yolu kapalıdır",
        "bağımsız bilgilendirme platformudur",
        "PoE",
        "NVR/DVR",
        "professional-only",
    ):
        assert phrase.casefold() in selector.casefold(), phrase
    assert selector.index("Satış ortaklığı açıklaması") < selector.index('id="sdLink"')
    assert selector.index("mağaza yolu kapalıdır") < selector.index('id="sdLink"')

    for source in (tool, selector):
        lowered = source.casefold()
        assert 'type="email"' not in lowered
        assert 'type="tel"' not in lowered
        assert "xmlhttprequest" not in lowered
        assert "fetch(" not in lowered
        assert "localstorage" not in lowered
        assert "sessionstorage" not in lowered
        assert "112" in source
        assert "bağımsız bilgilendirme platformudur" in lowered
        assert "edaş" in lowered

    for required in (
        "NVR/DVR",
        "PoE",
        "router",
        "microSD",
        "Mevcut sistem yeterli",
        "Axis",
        "5 Ağustos 2026",
    ):
        assert required in tool or required in article or required in selector, required

    assert "/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-sureklilik-plani/" in article
    assert "/amazon-elektrik-urunleri/kamera-nvr-ups-yedek-guc-secimi/" in article
    assert '"dateModified":"2026-08-05"' in article

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
        "legacyVersion": 268,
        "migratedTrustVersion": 299,
        "routes": len(overlay["routes"]),
        "productClasses": 2,
        "affiliateLinksLocked": len(locked),
        "measurementFirst": True,
        "privacyBoundary": True,
        "personalDataFields": 0,
        "unverifiedCommercialFields": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
