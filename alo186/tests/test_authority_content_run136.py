#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "storage": ROOT / "hesaplama/ev-enerji-depolama-kritik-yuk-plani/index.html",
    "hotel": ROOT / "hesaplama/otel-guc-kalitesi-kayip-hesabi/index.html",
    "vpp": ROOT / "hesaplama/bess-vpp-gelir-hazirligi/index.html",
}
EVENTS = {
    "storage": ("home_storage_plan_result", "storage_plan_download"),
    "hotel": ("hotel_power_quality_loss_result", "hotel_power_quality_report_download"),
    "vpp": ("vpp_readiness_result", "vpp_readiness_report_download"),
}
OVERLAY = ROOT / "deployment/routing-overlays/content-authority-run136.json"


def extract_jsonld(text: str) -> dict:
    match = re.search(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', text, re.I | re.S)
    assert match, "JSON-LD missing"
    return json.loads(match.group(1))


def schema_types(payload: dict) -> set[str]:
    graph = payload.get("@graph") if isinstance(payload.get("@graph"), list) else [payload]
    return {str(item.get("@type")) for item in graph if isinstance(item, dict)}


def test_pages() -> None:
    canonicals: set[str] = set()
    titles: set[str] = set()
    for key, path in PAGES.items():
        assert path.is_file(), path
        text = path.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        canonical = re.search(r'<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"', text, re.I)
        assert title and canonical
        assert len(re.findall(r"<h1\b", text, re.I)) == 1
        assert canonical.group(1).startswith("https://alo186.com/hesaplama/")
        titles.add(title.group(1).strip())
        canonicals.add(canonical.group(1))
        types = schema_types(extract_jsonld(text))
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= types
        assert "Doğrudan cevap" in text
        assert re.search(r"güven|tehlike|kritik sınır|yanlış yatırım", text, re.I)
        assert text.count("<details>") >= 4
        assert len(set(re.findall(r'href="(/[^"#?]+)', text))) >= 7
        assert len(re.findall(r'href="https?://', text)) >= 4
        assert "Son kaynak doğrulama: 2 Ağustos 2026" in text
        assert all(event in text for event in EVENTS[key])
        assert not re.search(r'"@type"\s*:\s*"(?:Product|Offer|AggregateRating)"', text)
        assert "amazon.com.tr" not in text.lower()
        assert "alo186rehber-21" not in text
        assert not re.search(r"�|Ã|Ä|Å|Â", text)
        test_file = path.with_name("test.js")
        assert test_file.is_file()
        subprocess.run(["node", str(test_file)], cwd=ROOT.parent, check=True)
    assert len(titles) == 3
    assert len(canonicals) == 3


def test_overlay() -> None:
    data = json.loads(OVERLAY.read_text(encoding="utf-8"))
    assert data["version"] == 218
    assert data["generatedAt"] == "2026-08-02"
    assert len(data["routes"]) == 3
    expected = {
        "/hesaplama/ev-enerji-depolama-kritik-yuk-plani/",
        "/hesaplama/otel-guc-kalitesi-kayip-hesabi/",
        "/hesaplama/bess-vpp-gelir-hazirligi/",
    }
    assert {route["path"] for route in data["routes"]} == expected
    for route in data["routes"]:
        assert route["path"] == route["canonicalPath"]
        assert route["source"] == "alo186/" + route["file"]
        assert (ROOT / route["file"]).is_file()
        assert route["type"] in {"calculator", "business-tool"}
        assert len(route["intent"]) > 80
    assert data["qualityGate"].endswith("test_authority_content_run136.py")


if __name__ == "__main__":
    test_pages()
    test_overlay()
    print("content authority run136: PASS")
