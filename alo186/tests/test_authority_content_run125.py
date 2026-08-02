#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "vpp": ROOT / "haberler/vpp-telemetri-stale-data-zaman-damgasi-sayac-mutabakat-teshis/index.html",
    "pv": ROOT / "haberler/ges-string-current-mismatch-dc-sigorta-mppt-akim-farki-teshis/index.html",
    "hvil": ROOT / "haberler/bess-hvil-open-high-voltage-interlock-service-disconnect-teshis/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/content-authority-run125.json"


def extract_jsonld(text: str) -> dict:
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
    assert match, "JSON-LD missing"
    return json.loads(match.group(1))


def test_pages_exist_and_have_unique_canonicals() -> None:
    canonicals = []
    titles = []
    for path in PAGES.values():
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        assert "<!doctype html>" in text.lower()
        title = re.search(r"<title>(.*?)</title>", text, re.S)
        canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
        assert title and canonical
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
        assert "Doğrudan cevap" in text
        assert "10 adımlık" in text
        assert "14 alan" in text
        assert "Mevcut içerikten görev ayrımı" in text
        assert "Dönüşüm çağrısı" in text
        assert text.count('href="/') >= 12
        assert text.count("https://") >= 5
        assert "Product" not in text
        assert '"Offer"' not in text
        assert "AggregateRating" not in text
        assert not re.search(r"�|Ã|Ä|Å|Â", text)


def test_topic_specific_fail_closed_guards() -> None:
    vpp = PAGES["vpp"].read_text(encoding="utf-8")
    assert all(term in vpp for term in ["Stale veriyi canlı kabul ederek dispatch etmeyin", "kalite bayrağı", "gelir sayacı"])
    pv = PAGES["pv"].read_text(encoding="utf-8")
    assert all(term in pv for term in ["PV konnektörünü yük altında açmayın", "String–MPPT haritasını", "I-V eğrisi"])
    hvil = PAGES["hvil"].read_text(encoding="utf-8")
    assert all(term in hvil for term in ["HVIL devresini köprülemeyin", "gerilim yokluğu", "kontaktör açma süresi"])


def test_routing_overlay() -> None:
    data = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert data["version"] == 202
    assert len(data["routes"]) == 3
    for route in data["routes"]:
        assert route["path"].startswith("/haberler/")
        assert (ROOT / route["file"]).exists()
    assert data["qualityGate"].endswith("test_authority_content_run125.py")


if __name__ == "__main__":
    test_pages_exist_and_have_unique_canonicals()
    test_aeo_schema_and_user_value_contract()
    test_topic_specific_fail_closed_guards()
    test_routing_overlay()
    print("content authority run125: PASS")
