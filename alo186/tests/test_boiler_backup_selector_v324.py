from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "hesaplama" / "kombi-elektrik-kesintisi-yedek-guc-uygunluk"
CANONICAL = "/hesaplama/kombi-elektrik-kesintisi-yedek-guc-uygunluk/"


def main() -> None:
    html_path = ROUTE / "index.html"
    css_path = ROUTE / "styles.css"
    app_path = ROUTE / "app.js"
    test_path = ROUTE / "app.test.js"
    overlay_path = ROOT / "deployment" / "routing-overlays" / "085-boiler-backup-selector.json"
    common_path = ROOT / "hesaplama" / "common.js"

    for path in (html_path, css_path, app_path, test_path, overlay_path, common_path):
        assert path.is_file(), path

    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    app = app_path.read_text(encoding="utf-8")
    common = common_path.read_text(encoding="utf-8")
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))

    assert html.count("<h1") == 1
    assert "Kombi Elektrik Kesintisi ve Yedek Güç Uygunluk Testi" in html
    assert f'<link rel="canonical" href="https://alo186.com{CANONICAL}">' in html
    assert "Satış ortaklığı açıklaması" in html
    assert "Amazon satış ortaklığı bağlantılarıdır" in html
    assert "doğrudan Amazon bağlantısı yoktur" in html
    assert "187" in html and "112" in html
    assert "yeni ürün almayın sonucu" in html.casefold()
    assert "doğal gaz dağıtım şirketi, EDAŞ, kamu kurumu" in html
    assert "aggregateRating" not in html
    assert '"@type":"Product"' not in html
    assert '"@type":"Offer"' not in html

    blocks = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S | re.I)
    assert blocks
    types: set[str] = set()
    for block in blocks:
        payload = json.loads(block)
        for node in payload.get("@graph", [payload]):
            if isinstance(node, dict) and isinstance(node.get("@type"), str):
                types.add(node["@type"])
    assert {"WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"} <= types

    for forbidden in (
        "amazon.com.tr/",
        "localStorage",
        "sessionStorage",
        "fetch(",
        "XMLHttpRequest",
        "navigator.geolocation",
        "type=\"email\"",
        "type=\"tel\"",
        "<textarea",
    ):
        assert forbidden not in app
    assert "emergency_gas" in app
    assert "no_electrical_solution" in app
    assert "no_buy" in app
    assert "qualified_gap" in app
    assert "active_event" in app
    assert "Amazon satış ortaklığı bağlantılarıdır" in app
    assert "90*24*60*60*1000" in app

    assert "@media(max-width:620px)" in css
    assert "minmax(0,1fr)" in css

    assert overlay["version"] == 85
    route = overlay["routes"][0]
    assert route["canonicalPath"] == CANONICAL
    assert route["type"] == "calculator"
    assert route["source"].endswith("/index.html")

    assert CANONICAL in common
    assert "data-alo186-boiler-backup-card" in common
    counts = [int(value) for value in re.findall(r"(\d+) çekirdek araç", common)]
    assert counts and max(counts) >= 39

    print("Kombi yedek güç kaynak, güven, affiliate ve hub entegrasyon sözleşmeleri başarılı.")


if __name__ == "__main__":
    main()
