from __future__ import annotations

import importlib.util
import json
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "alo186/content-ops/intentops_v214.py"
REGISTRY = ROOT / "alo186/content-ops/intent-opportunities-v214.json"
spec = importlib.util.spec_from_file_location("intentops_v214", MODULE)
intentops = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(intentops)


def test_registry_contract() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert data["version"] == 214
    assert abs(sum(data["scoringModel"].values()) - 1.0) < 1e-9
    assert len(data["opportunities"]) >= 6
    keys = [item["intentKey"] for item in data["opportunities"]]
    routes = [item["route"] for item in data["opportunities"]]
    assert len(keys) == len(set(keys))
    assert len(routes) == len(set(routes))
    findings = intentops.audit_registry(data)
    assert not [item for item in findings if item.level == "error"], findings
    scores = {item["intentKey"]: item["weightedScore"] for item in data["opportunities"]}
    assert scores["home-energy-storage-critical-load-plan"] >= 85
    assert scores["hotel-power-quality-loss-estimator"] >= 80
    assert scores["vpp-bess-revenue-readiness"] >= 75


def test_collision_guard() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    clone = dict(data["opportunities"][0])
    clone["intentKey"] = "collision-copy"
    clone["route"] = "/hesaplama/collision-copy/"
    data["opportunities"].append(clone)
    findings = intentops.audit_registry(data)
    assert any(item.code == "intent_collision" for item in findings)


def test_page_quality_contract() -> None:
    html = '''<!doctype html><html><head><title>Test</title>
    <script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"WebApplication","dateModified":"2026-08-02"},{"@type":"FAQPage"},{"@type":"BreadcrumbList"}]}</script>
    </head><body><h1>Araç</h1><section><h2>Doğrudan cevap</h2><p>Güvenlik riski için müdahale etmeyin.</p></section>
    <details><summary>1</summary><p>x</p></details><details><summary>2</summary><p>x</p></details><details><summary>3</summary><p>x</p></details>
    <a href="/a">a</a><a href="/b">b</a><a href="/c">c</a><a href="/d">d</a><a href="/e">e</a>
    <a href="https://example.org/one">s1</a><a href="https://example.net/two">s2</a>
    <script>window.dataLayer.push({event:'example_result'});</script></body></html>'''
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "index.html"
        page.write_text(html, encoding="utf-8")
        original = intentops.route_file
        intentops.route_file = lambda _route: page
        try:
            item = {"route": "/test/", "conversionEvents": ["example_result"]}
            guardrails = {
                "requireDirectAnswer": True,
                "minimumVisibleFaq": 3,
                "minimumInternalLinks": 5,
                "primarySourcesRequired": 2,
                "freshnessDays": 180,
                "requireSafetyBoundary": True,
                "requireConversionEvent": True,
            }
            findings = intentops.audit_page(item, guardrails, date(2026, 8, 2))
            assert not [finding for finding in findings if finding.level == "error"], findings
        finally:
            intentops.route_file = original


def test_forbidden_commercial_schema() -> None:
    html = '''<!doctype html><script type="application/ld+json">{"@context":"https://schema.org","@type":"Offer"}</script><h2>Doğrudan cevap</h2>güven risk'''
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "index.html"
        page.write_text(html, encoding="utf-8")
        original = intentops.route_file
        intentops.route_file = lambda _route: page
        try:
            findings = intentops.audit_page({"route": "/x/", "conversionEvents": []}, {
                "requireDirectAnswer": True, "minimumVisibleFaq": 0, "minimumInternalLinks": 0,
                "primarySourcesRequired": 0, "freshnessDays": 9999,
                "requireSafetyBoundary": True, "requireConversionEvent": False,
            }, date(2026, 8, 2))
            assert any(finding.code == "commercial_schema_forbidden" for finding in findings)
        finally:
            intentops.route_file = original


if __name__ == "__main__":
    test_registry_contract()
    test_collision_guard()
    test_page_quality_contract()
    test_forbidden_commercial_schema()
    print("ALO186 IntentOps v214: PASS")
