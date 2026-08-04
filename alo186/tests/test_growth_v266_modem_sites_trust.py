#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "alo186"
POLICY = SITE / "deployment/affiliate_route_risk_policy_v266.json"
CONSOLIDATIONS = SITE / "deployment/content-consolidations.json"
SELECTOR = SITE / "amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/index.html"
CONFIG = SITE / "growth/live-drift/critical-pages-v266.json"
DRIFT_SCRIPT = SITE / "growth/live-drift/chatgpt_sites_live_drift.py"
COLD_TIMER = SITE / "hesaplama/kesinti-soguk-zincir-zamanlayici/index.html"
THERMOMETER = SITE / "amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/index.html"


class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.canonical = ""
        self.jsonld: list[str] = []
        self._jsonld = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value or "" for key, value in attrs}
        if tag.casefold() == "a":
            self.anchors.append(values)
        if tag.casefold() == "script":
            self.scripts.append(values)
            if values.get("type", "").casefold() == "application/ld+json":
                self._jsonld = True
                self._buffer = []
        if tag.casefold() == "link" and "canonical" in values.get("rel", "").casefold().split():
            self.canonical = values.get("href", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "script" and self._jsonld:
            self.jsonld.append("".join(self._buffer))
            self._jsonld = False

    def handle_data(self, data: str) -> None:
        if self._jsonld:
            self._buffer.append(data)


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def load_drift_module():
    name = "alo186_live_drift_v266_test"
    spec = importlib.util.spec_from_file_location(name, DRIFT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_fixture(root: Path, route: str, html: str) -> None:
    relative = route.strip("/")
    target = root / (relative or "index.html")
    if relative:
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def main() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    assert policy["version"] == 266
    assert policy["canonicalHost"] == "https://alo186.com"
    assert policy["affiliateProgram"]["merchant"] == "Amazon Türkiye"
    assert policy["affiliateProgram"]["tag"] == "alo186rehber-21"
    assert set(policy["affiliateProgram"]["requiredRel"]) == {"sponsored", "nofollow", "noopener"}
    assert policy["legacyMigrationQueue"] == []
    assert "modem-ont-mini-ups-yedekleme-secici" in policy["governedAffiliateRoutePatterns"]
    assert policy["trustRules"]["activeHazardCommerceClosed"] is True
    assert policy["trustRules"]["officialInstitutionImpressionForbidden"] is True
    assert policy["trustRules"]["personalDataCollectionForbidden"] is True
    assert policy["portfolioRules"]["legacyRoutesMigrateBeforeExpansion"] is True

    consolidation = policy["canonicalConsolidations"][0]
    assert consolidation["aliasPath"] == "/amazon-elektrik-urunleri/modem-mini-ups-secimi/"
    assert consolidation["canonicalPath"] == "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/"

    shared = json.loads(CONSOLIDATIONS.read_text(encoding="utf-8"))
    assert shared["version"] >= 11
    matches = [
        item for item in shared["consolidations"]
        if item["aliasPath"] == consolidation["aliasPath"]
    ]
    assert len(matches) == 1
    assert matches[0]["canonicalPath"] == consolidation["canonicalPath"]

    html = SELECTOR.read_text(encoding="utf-8")
    lowered = html.casefold()
    parser = Inspector()
    parser.feed(html)
    assert parser.canonical == "https://alo186.com/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/"
    for token in (
        "Amazon Gelir Ortağı açıklaması",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "30 günlük kısa kontrol",
        "90 günlük gerçek süre provası",
        "sponsored nofollow noopener",
        "alo186rehber-21",
        "112’yi arayın",
        "journey-events-v260.js",
        "reminder_downloaded",
    ):
        assert token.casefold() in lowered, token
    for forbidden in (
        "fetch(",
        "xmlhttprequest",
        "localstorage",
        "sessionstorage",
        "document.cookie",
        "garantilidir",
        "stokta",
    ):
        assert forbidden not in lowered, forbidden
    static_amazon = [
        item.get("href", "") for item in parser.anchors
        if "amazon.com.tr" in item.get("href", "").casefold()
    ]
    assert static_amazon == []
    assert any(item.get("src") == "/assets/journey-events-v260.js" for item in parser.scripts)

    blocks = [json.loads(raw) for raw in parser.jsonld]
    nodes = [node for block in blocks for node in walk(block) if isinstance(node, dict)]
    forbidden_schema = {
        "offers", "offer", "price", "priceCurrency", "availability",
        "aggregateRating", "review", "warranty", "delivery"
    }
    assert not any(forbidden_schema.intersection(node) for node in nodes)

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["version"] == 266
    assert len(config["pages"]) == 5
    pages = {item["id"]: item for item in config["pages"]}
    assert pages["homepage-critical-claim"]["priority"] == "P0"
    assert "on iş günlük başvuru süresi" in pages["homepage-critical-claim"]["forbiddenText"]
    assert pages["modem-ont-governed-selector"]["forbidDirectAmazonHref"] is True

    module = load_drift_module()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        fixture = root / "fixture"
        output = root / "output"
        stale_home = '''<!doctype html><html><head><title>ALO186</title><link rel="canonical" href="https://alo186.com/"></head><body><h1>ALO186</h1><p>ALO186 arıza kaydı alıyor mu?</p><p>Bağımsız bilgilendirme platformudur; EDAŞ veya kamu kurumu değildir.</p><p>EPDK tüketici bilgisinde on iş günlük başvuru süresi açıklanır.</p></body></html>'''
        stale_hub = '''<!doctype html><html><head><title>Ürün merkezi</title><link rel="canonical" href="https://alo186.com/amazon-elektrik-urunleri/"></head><body><h1>Ürünü değil teknik açığı seçin</h1><p>Mevcut sistem yeterliyse satın alma yok. Amazon satış ortaklığı. 96 ürün seçim yolu ve 50+ elektrik ürünü.</p><a href="https://www.amazon.com.tr/s?k=ups&tag=alo186rehber-21">Amazon</a></body></html>'''
        write_fixture(fixture, "/", stale_home)
        write_fixture(fixture, "/amazon-elektrik-urunleri/", stale_hub)
        write_fixture(fixture, "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/", html)
        write_fixture(fixture, "/hesaplama/kesinti-soguk-zincir-zamanlayici/", COLD_TIMER.read_text(encoding="utf-8"))
        write_fixture(fixture, "/amazon-elektrik-urunleri/buzdolabi-dondurucu-termometresi-secimi/", THERMOMETER.read_text(encoding="utf-8"))
        report = module.run(CONFIG, output, fixture)
        assert report["checked"] == 5
        assert report["driftCount"] == 2, report
        targets = {item["targetUrl"] for item in report["topActions"]}
        assert "https://alo186.com/" in targets
        assert "https://alo186.com/amazon-elektrik-urunleri/" in targets
        patch = json.loads((output / "sites-delta-patch-v259.json").read_text(encoding="utf-8"))
        assert patch["growthVersion"] == 266
        assert patch["status"] == "patch-required"
        assert patch["automaticPublishAllowed"] is False
        assert patch["connectedSitesWriteRequired"] is True
        assert len(patch["actions"]) == 2

    print(json.dumps({
        "ok": True,
        "policyVersion": policy["version"],
        "canonicalConsolidation": True,
        "modemSelector": "governed",
        "localRetestDays": [30, 90],
        "driftPages": len(config["pages"]),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
