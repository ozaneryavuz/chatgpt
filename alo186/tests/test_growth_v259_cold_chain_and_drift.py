#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIMER = ROOT / "alo186/hesaplama/kesinti-soguk-zincir-zamanlayici/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/growth-v259-cold-chain.json"
CONFIG = ROOT / "alo186/growth/live-drift/critical-pages-v259.json"
SCRIPT = ROOT / "alo186/growth/live-drift/chatgpt_sites_live_drift.py"


class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.inputs: list[dict[str, str]] = []
        self.canonical = ""
        self.jsonld: list[str] = []
        self._jsonld = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value or "" for key, value in attrs}
        if tag == "a":
            self.links.append(values)
        if tag == "input":
            self.inputs.append(values)
        if tag == "link" and "canonical" in values.get("rel", "").casefold().split():
            self.canonical = values.get("href", "")
        if tag == "script" and values.get("type", "").casefold() == "application/ld+json":
            self._jsonld = True
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._jsonld:
            self.jsonld.append("".join(self._buffer))
            self._jsonld = False

    def handle_data(self, data: str) -> None:
        if self._jsonld:
            self._buffer.append(data)


def inspect(path: Path) -> tuple[str, Inspector, list[object]]:
    html = path.read_text(encoding="utf-8")
    parser = Inspector()
    parser.feed(html)
    blocks = [json.loads(item) for item in parser.jsonld]
    return html, parser, blocks


def walk(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def write_fixture(root: Path, url_path: str, html: str) -> None:
    target = root / url_path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def load_drift_module():
    name = "alo186_live_drift_v259"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    timer_html, timer_parser, timer_jsonld = inspect(TIMER)
    selector_html, selector_parser, selector_jsonld = inspect(SELECTOR)

    assert timer_parser.canonical == "https://alo186.com/hesaplama/kesinti-soguk-zincir-zamanlayici/"
    for token in ("yaklaşık 4 saat", "yaklaşık 24 saat", "yaklaşık 48 saat", "Şüpheli gıdayı tatmayın", "30 dakika", "60 dakika"):
        assert token.casefold() in timer_html.casefold(), token
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "document.cookie"):
        assert forbidden not in timer_html.casefold(), forbidden
    assert not any(item.get("type", "").casefold() in {"email", "tel"} for item in timer_parser.inputs)
    assert not any("amazon.com.tr" in item.get("href", "").casefold() for item in timer_parser.links)
    timer_types = {str(node.get("@type")) for block in timer_jsonld for node in walk(block) if isinstance(node, dict) and "@type" in node}
    assert {"WebApplication", "FAQPage", "BreadcrumbList"}.issubset(timer_types)

    assert selector_parser.canonical == "https://alo186.com/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/"
    for token in ("satış ortaklığı açıklaması", "kullanıcıya ek maliyet yansımaz", "Mevcut çözümüm yeterli", "sponsored nofollow noopener", "alo186rehber-21"):
        assert token.casefold() in selector_html.casefold(), token
    for forbidden in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "document.cookie"):
        assert forbidden not in selector_html.casefold(), forbidden
    assert not any(item.get("type", "").casefold() in {"email", "tel"} for item in selector_parser.inputs)
    amazon_links = [item for item in selector_parser.links if "amazon.com.tr" in (item.get("href", "") + item.get("data-affiliate-url", "")).casefold()]
    assert len(amazon_links) == 1
    amazon = amazon_links[0]
    assert not amazon.get("href"), "Amazon link must be locked without static href"
    assert "amazon.com.tr" in amazon.get("data-affiliate-url", "")
    assert "tag=alo186rehber-21" in amazon.get("data-affiliate-url", "")
    assert set(amazon.get("rel", "").split()) == {"sponsored", "nofollow", "noopener"}

    schema_nodes = [node for block in selector_jsonld for node in walk(block) if isinstance(node, dict)]
    schema_types = {str(node.get("@type")) for node in schema_nodes if node.get("@type")}
    assert {"Product", "ItemList", "CollectionPage", "FAQPage", "BreadcrumbList"}.issubset(schema_types)
    forbidden_schema_keys = {"offers", "offer", "price", "priceCurrency", "availability", "aggregateRating", "review", "warranty"}
    assert not any(forbidden_schema_keys.intersection(node) for node in schema_nodes)

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    routes = {item["canonicalPath"]: item for item in overlay["routes"]}
    assert routes["/hesaplama/kesinti-soguk-zincir-zamanlayici/"]["type"] == "tool"
    assert routes["/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/"]["type"] == "commerce-guide"

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert len(config["pages"]) == 3
    assert config["pages"][0]["priority"] == "P0"

    module = load_drift_module()
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        fixture = temp / "fixture"
        output = temp / "out"
        stale_hub = '''<!doctype html><html><head><title>Eski merkez</title><link rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri/"></head><body><h1>Ürünü değil teknik açığı seçin</h1><p>Mevcut sistem yeterliyse satın alma yok. Amazon satış ortaklığı. 96 ürün seçim yolu ve 154 doğrulanmış ASIN.</p><a href="https://www.amazon.com.tr/s?k=ups&tag=alo186rehber-21">Amazon</a></body></html>'''
        write_fixture(fixture, "/amazon-elektrik-urunleri/", stale_hub)
        write_fixture(fixture, "/hesaplama/kesinti-soguk-zincir-zamanlayici/", timer_html)
        write_fixture(fixture, "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/", selector_html)
        report = module.run(CONFIG, output, fixture)
        assert report["checked"] == 3
        assert report["driftCount"] == 1, report
        assert report["topActions"][0]["targetUrl"].endswith("/amazon-elektrik-urunleri/")
        patch = json.loads((output / "sites-delta-patch-v259.json").read_text(encoding="utf-8"))
        assert patch["status"] == "patch-required"
        assert patch["automaticPublishAllowed"] is False
        assert patch["connectedSitesWriteRequired"] is True
        assert patch["actions"][0]["acceptance"]["removeDirectAmazonHrefsBeforeTechnicalGate"] is True

        healthy_hub = '''<!doctype html><html><head><title>Ürün merkezi</title><link rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri/"></head><body><h1>Ürünü değil, doğrulanmış teknik açığı seçin</h1><p>Mevcut sistem yeterliyse satın alma yok. Amazon satış ortaklığı.</p><a href="/hesaplama/">Önce hesapla</a></body></html>'''
        write_fixture(fixture, "/amazon-elektrik-urunleri/", healthy_hub)
        clean = module.run(CONFIG, temp / "clean", fixture)
        assert clean["driftCount"] == 0, clean

    print(json.dumps({"ok": True, "routes": len(routes), "driftFixture": "passed", "affiliateGate": "passed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
