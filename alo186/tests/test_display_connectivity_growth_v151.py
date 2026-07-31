#!/usr/bin/env python3
"""ALO186 display connectivity growth v151 release contract."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIT = ROOT / "alo186/hesaplama/hdmi-displayport-cozunurluk-yenileme-uygunluk/index.html"
DIAG = ROOT / "alo186/hesaplama/hdmi-displayport-sinyal-sorunu-kok-neden/index.html"
HUB = ROOT / "alo186/sektor-rehberi/goruntu-baglanti-kablo-test-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/151-display-connectivity-growth.json"
AUDIT = ROOT / "alo186/audits/display-connectivity-growth-v151-2026-07-31.md"
EXPECTED = {
    "/hesaplama/hdmi-displayport-cozunurluk-yenileme-uygunluk/": FIT,
    "/hesaplama/hdmi-displayport-sinyal-sorunu-kok-neden/": DIAG,
    "/sektor-rehberi/goruntu-baglanti-kablo-test-merkezi/": HUB,
}

def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def executable_scripts(html: str) -> list[str]:
    return [
        body for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", html, re.I | re.S)
        if "application/ld+json" not in attrs.lower() and body.strip()
    ]

def check_js(path: Path, html: str) -> None:
    node = shutil.which("node")
    require(node is not None, "Node.js required")
    scripts = executable_scripts(html)
    require(scripts, f"No executable JS: {path}")
    for index, script in enumerate(scripts, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
            tmp.write(script)
            tmp_path = Path(tmp.name)
        try:
            result = subprocess.run([node, "--check", str(tmp_path)], text=True, capture_output=True)
            require(result.returncode == 0, f"JS failed {path} #{index}: {result.stderr}")
        finally:
            tmp_path.unlink(missing_ok=True)

def check_common(path: Path, canonical: str) -> str:
    require(path.is_file(), f"Missing {path}")
    html = path.read_text(encoding="utf-8")
    lower = fold(html)
    require(f'href="https://alo186.com{canonical}"' in html, f"Canonical mismatch {path}")
    require("bagımsız" in lower or "bagimsiz" in lower, f"Independence missing {path}")
    require("resmi kurum" in lower, f"Official-role boundary missing {path}")
    for token in ("fiyat", "stok", "puan", "garanti"):
        require(token in lower, f"Commercial guard missing {token}: {path}")
    require("localstorage" not in lower and "sessionstorage" not in lower, f"Persistent storage found {path}")
    for forbidden in ('"@type":"product"', '"@type":"offer"', "aggregaterating", '"availability"'):
        require(forbidden not in lower, f"Forbidden schema {forbidden}: {path}")
    require('"@type":"faqpage"' in lower and '"@type":"breadcrumblist"' in lower, f"Structured data missing {path}")
    check_js(path, html)
    return html

def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    require(overlay.get("version") == 151, "Overlay version must be 151")
    require(overlay.get("generatedAt") == "2026-07-31", "Overlay date mismatch")
    routes = {item["canonicalPath"]: item for item in overlay.get("routes", [])}
    require(set(routes) == set(EXPECTED), f"Unexpected routes: {set(routes)}")
    for canonical, path in EXPECTED.items():
        require(routes[canonical]["source"] == str(path.relative_to(ROOT)), f"Source mismatch {canonical}")

    fit = check_common(FIT, list(EXPECTED)[0])
    fit_lower = fold(fit)
    for phrase in (
        "yeni kablo almadan once",
        "mevcut kablo hedefte kararlı calısıyor",
        "yeni urun almayın",
        "amazon satıs ortaklıgı",
        "hdmi licensing administrator",
        "vesa",
    ):
        require(phrase in fit_lower, f"Fit phrase missing: {phrase}")
    require('rel="sponsored nofollow noopener"' in fit, "Affiliate rel missing on fit")
    require("amazon.com.tr/s?k=" in fit_lower, "Affiliate category destination missing on fit")
    require(all(f'id="{item}"' in fit for item in ("need", "spec", "ad")), "Three confirmations missing on fit")
    require(all(token in fit for token in ("source", "display", "cableLabel", "altmode", "actual")), "Evidence gates missing on fit")
    require("4k 240 hz" in fit_lower and "ultra96" in fit_lower and "dp80" in fit_lower, "Current HDMI/DP classes missing")

    diag = check_common(DIAG, list(EXPECTED)[1])
    diag_lower = fold(diag)
    for phrase in (
        "belirtiyi dogrudan",
        "bilinen saglam kablo",
        "mevcut baglantı kararlı",
        "yeni urun almayın",
        "kablo kok nedeni guclu bicimde dogrulandı",
    ):
        require(phrase in diag_lower, f"Diagnostic phrase missing: {phrase}")
    require('rel="sponsored nofollow noopener"' in diag, "Affiliate rel missing on diagnostic")
    require("amazon.com.tr/s?k=" in diag_lower, "Affiliate category destination missing on diagnostic")
    require(all(f'id="{item}"' in diag for item in ("need", "spec", "ad")), "Three confirmations missing on diagnostic")
    require(all(token in diag for token in ("knownGood", "knownGoodSolved", "lowerMode", "otherPort", "direct")), "Diagnostic gates missing")
    require("ticari yol kapalıdır" in diag_lower, "Hazard commerce block missing")

    hub = check_common(HUB, list(EXPECTED)[2])
    hub_lower = fold(hub)
    require("amazon.com.tr" not in hub_lower, "Hub must not include Amazon")
    require('rel="sponsored nofollow noopener"' not in hub, "Hub must not include affiliate rel")
    require("dogrudan affiliate baglantısı yoktur" in hub_lower, "No-direct-affiliate disclosure missing")
    require("kisisel veri" in hub_lower and "json" in hub_lower and "ics" in hub_lower, "Privacy/export controls missing")
    require(all(token in hub for token in ('data-days="7"', 'data-days="30"', 'data-days="90"')), "Repeat intervals missing")
    require("localstorage" not in hub_lower and "sessionstorage" not in hub_lower, "Persistent storage found in hub")

    audit = fold(AUDIT.read_text(encoding="utf-8"))
    for phrase in (
        "arama niyeti", "icerik boslugu", "kullanıcı yolculugu", "affiliate urun kategorileri",
        "donusum noktaları", "tekrar ziyaret nedenleri", "beklenen kullanıcı faydası",
        "beklenen gelir etkisi", "uygulanan site gelistirmeleri"
    ):
        require(phrase in audit, f"Audit section missing {phrase}")

    print("ALO186 display connectivity growth v151 contract: PASS")

if __name__ == "__main__":
    main()
