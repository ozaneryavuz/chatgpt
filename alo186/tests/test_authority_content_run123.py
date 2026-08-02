#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "afci": ROOT / "haberler/ges-inverter-afci-dc-arc-fault-seri-ark-alarmi-teshis/index.html",
    "resonance": ROOT / "haberler/kompanzasyon-harmonik-rezonans-kondansator-reaktor-asiri-akim-teshis/index.html",
    "outage": ROOT / "haberler/edas-12-saati-asan-elektrik-kesintisi-tazminati-odeme-kontrolu/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/content-authority-run123.json"

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
        assert len(faq["mainEntity"]) == 5
        assert text.count("<details>") == 5
        assert "Doğrudan cevap" in text
        assert "10 adımlık" in text
        assert "14 alan" in text
        assert "Mevcut içerikten görev ayrımı" in text
        assert text.count('href="/') >= 12
        assert text.count("https://") >= 5
        assert "Product" not in text
        assert '"Offer"' not in text
        assert "AggregateRating" not in text
        assert not re.search(r"�|Ã|Ä|Å|Â", text)

def test_topic_specific_fail_closed_guards() -> None:
    afci = PAGES["afci"].read_text(encoding="utf-8")
    assert all(term in afci for term in ["IEC 63027", "AFCI’yi bypass etmeyin", "Konnektör üretici ve tam tip"])
    resonance = PAGES["resonance"].read_text(encoding="utf-8")
    assert all(term in resonance for term in ["h ≈ √", "Detuned reaktör", "deşarj doğrulaması"])
    outage = PAGES["outage"].read_text(encoding="utf-8")
    assert all(term in outage for term in ["12 saati aşan", "mücbir sebep", "cihaz hasarı"])
    assert "kesin ödeme" in outage.lower()

def test_routing_overlay() -> None:
    data = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert data["version"] == 199
    assert len(data["routes"]) == 3
    for route in data["routes"]:
        assert route["path"].startswith("/haberler/")
        assert (ROOT / route["file"]).exists()
    assert data["qualityGate"].endswith("test_authority_content_run123.py")

if __name__ == "__main__":
    test_pages_exist_and_have_unique_canonicals()
    test_aeo_schema_and_user_value_contract()
    test_topic_specific_fail_closed_guards()
    test_routing_overlay()
    print("content authority run123: PASS")
