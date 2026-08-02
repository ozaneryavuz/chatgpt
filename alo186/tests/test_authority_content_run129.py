#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "harmonic": ROOT / "haberler/notr-iletken-asiri-akim-triplen-harmonik-led-ups-ofis-otel-teshis/index.html",
    "generator": ROOT / "haberler/jenerator-wet-stacking-dusuk-yuk-siyah-duman-egzoz-yaglanma-teshis/index.html",
    "ev": ROOT / "haberler/ev-sarj-tip-b-rcd-rdc-dd-6ma-dc-kacak-akim-koruma-secimi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/content-authority-run129.json"


def extract_jsonld(text: str) -> dict:
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
    assert match, "JSON-LD missing"
    return json.loads(match.group(1))


def test_pages_exist_and_have_unique_canonicals() -> None:
    canonicals: list[str] = []
    titles: list[str] = []
    for path in PAGES.values():
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", text, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
        assert "<!doctype html>" in text.lower()
        assert title and canonical
        assert canonical.group(1).startswith("https://alo186.com/")
        titles.append(title.group(1))
        canonicals.append(canonical.group(1))
    assert len(set(titles)) == 3
    assert len(set(canonicals)) == 3


def test_aeo_schema_and_user_value_contract() -> None:
    for path in PAGES.values():
        text = path.read_text(encoding="utf-8")
        data = extract_jsonld(text)
        types = {item.get("@type") for item in data["@graph"]}
        assert {"Article", "FAQPage", "BreadcrumbList"} <= types
        article = next(item for item in data["@graph"] if item.get("@type") == "Article")
        faq = next(item for item in data["@graph"] if item.get("@type") == "FAQPage")
        assert len(article["about"]) >= 12
        assert len(article["citation"]) >= 5
        assert article["speakable"]["@type"] == "SpeakableSpecification"
        assert len(faq["mainEntity"]) == 5
        assert text.count("<details>") == 5
        assert all(term in text for term in ["Doğrudan cevap", "10 adımlık", "14 alan", "Mevcut içerikten görev ayrımı", "Dönüşüm çağrısı"])
        assert text.count('href="/') >= 12
        assert text.count("https://") >= 5
        assert "Product" not in text
        assert '"Offer"' not in text
        assert "AggregateRating" not in text
        assert not re.search(r"�|Ã|Ä|Å|Â", text)


def test_topic_specific_fail_closed_guards() -> None:
    harmonic = PAGES["harmonic"].read_text(encoding="utf-8")
    assert all(term in harmonic for term in ["Enerjili tesiste nötr iletkeni", "triplen", "gerçek RMS"])
    generator = PAGES["generator"].read_text(encoding="utf-8")
    assert all(term in generator for term in ["Egzoz hattını kapatmayın", "load bank", "wet stacking"])
    ev = PAGES["ev"].read_text(encoding="utf-8")
    assert all(term in ev for term in ["RCD, RDC-DD", "6 mA DC", "IEC 62955"])


def test_routing_overlay() -> None:
    data = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert data["version"] == 207
    assert data["generatedAt"] == "2026-08-02"
    assert len(data["routes"]) == 3
    for route in data["routes"]:
        assert route["path"].startswith("/haberler/")
        assert (ROOT / route["file"]).exists()
    assert data["qualityGate"].endswith("test_authority_content_run129.py")


if __name__ == "__main__":
    test_pages_exist_and_have_unique_canonicals()
    test_aeo_schema_and_user_value_contract()
    test_topic_specific_fail_closed_guards()
    test_routing_overlay()
    print("content authority run129: PASS")
