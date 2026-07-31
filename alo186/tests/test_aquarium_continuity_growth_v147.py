#!/usr/bin/env python3
"""ALO186 aquarium continuity growth v147 release contract."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALCULATORS = [
    ROOT / "alo186/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-guvenligi/index.html",
    ROOT / "alo186/hesaplama/akvaryum-hava-motoru-yedek-guc-sure-uygunluk/index.html",
]
HUB = ROOT / "alo186/sektor-rehberi/akvaryum-elektrik-kesintisi-sureklilik-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/147-aquarium-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/aquarium-continuity-growth-v147-2026-07-31.md"
EXPECTED = {
    "/hesaplama/akvaryum-elektrik-kesintisi-oksijen-sicaklik-guvenligi/": CALCULATORS[0],
    "/hesaplama/akvaryum-hava-motoru-yedek-guc-sure-uygunluk/": CALCULATORS[1],
    "/sektor-rehberi/akvaryum-elektrik-kesintisi-sureklilik-merkezi/": HUB,
}


def fold(text: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(char)
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def inline_scripts(html: str) -> list[str]:
    return [body for attrs, body in re.findall(
        r"<script([^>]*)>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL
    ) if "application/ld+json" not in attrs.lower() and body.strip()]


def check_javascript(path: Path, html: str) -> None:
    node = shutil.which("node")
    require(node is not None, "Node.js is required")
    scripts = inline_scripts(html)
    require(scripts, f"No executable JavaScript: {path}")
    for index, script in enumerate(scripts, start=1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
            tmp.write(script)
            tmp_path = Path(tmp.name)
        try:
            result = subprocess.run([node, "--check", str(tmp_path)], text=True, capture_output=True)
            require(result.returncode == 0, f"JS failed in {path} #{index}: {result.stderr}")
        finally:
            tmp_path.unlink(missing_ok=True)


def check_common(path: Path, canonical: str) -> str:
    require(path.is_file(), f"Missing file: {path}")
    html = path.read_text(encoding="utf-8")
    lower = fold(html)
    require(f'href="https://alo186.com{canonical}"' in html, f"Canonical mismatch: {path}")
    require("bagımsız" in lower, f"Independent disclosure missing: {path}")
    require("veteriner" in lower and ("resmi kurum" in lower or "edas" in lower), f"Role boundary missing: {path}")
    require("fiyat" in lower and "stok" in lower and "puan" in lower and "garanti" in lower, f"Commercial guard missing: {path}")
    require("localstorage" not in lower and "sessionstorage" not in lower, f"Persistent storage found: {path}")
    for forbidden in ('"@type":"product"', '"@type":"offer"', "aggregaterating", '"availability"'):
        require(forbidden not in lower, f"Forbidden schema/token {forbidden}: {path}")
    check_javascript(path, html)
    return html


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    require(overlay.get("version") == 147, "Overlay version must be 147")
    require(overlay.get("generatedAt") == "2026-07-31", "Overlay date mismatch")
    routes = {item["canonicalPath"]: item for item in overlay.get("routes", [])}
    require(set(routes) == set(EXPECTED), f"Unexpected routes: {set(routes)}")
    for canonical, path in EXPECTED.items():
        require(routes[canonical]["source"] == str(path.relative_to(ROOT)), f"Source mismatch: {canonical}")

    safety = check_common(CALCULATORS[0], list(EXPECTED)[0])
    safety_lower = fold(safety)
    for phrase in ("yeni urun almayın", "yuzeyde", "hava yut", "aktif kesintide affiliate yolu kapalı", "evrensel"):
        require(phrase in safety_lower, f"Safety phrase missing: {phrase}")
    require("amazon.com.tr" not in safety_lower, "Emergency safety page must have no Amazon destination")
    require("merckvetmanual.com" in safety_lower and "okstate.edu" in safety_lower and "ifas.ufl.edu" in safety_lower,
            "Primary/authoritative sources missing")
    require("sensitive" in safety_lower and "commercial" in safety_lower, "Sensitive/commercial scope gate missing")

    runtime = check_common(CALCULATORS[1], list(EXPECTED)[1])
    runtime_lower = fold(runtime)
    require("yeni urun almayın" in runtime_lower, "Buy-nothing result missing")
    require("amazon satıs ortaklıgı" in runtime_lower, "Affiliate disclosure missing")
    require('rel="sponsored nofollow noopener"' in runtime, "Affiliate rel missing")
    require("amazon.com.tr/s?k=" in runtime_lower, "Only category search destination expected")
    require(all(f'id="{item}"' in runtime for item in ("need", "spec", "ad")), "Three confirmations missing")
    require("aktif kesintide ticari yol kapalı" in runtime_lower, "Active outage commerce block missing")
    require("dusuk yuk" in runtime_lower and "wh" in runtime_lower, "Low-load/Wh controls missing")
    require("pumpType==='none'" in runtime, "Affiliate must require missing pump")

    hub = check_common(HUB, list(EXPECTED)[2])
    hub_lower = fold(hub)
    require("amazon.com.tr" not in hub_lower, "Hub must not include Amazon")
    require('rel="sponsored nofollow noopener"' not in hub, "Hub must not include affiliate links")
    require("dogrudan affiliate baglantısı" in hub_lower, "No-direct-affiliate disclosure missing")
    require("kisisel veri" in hub_lower and "json" in hub_lower and "ics" in hub_lower, "Privacy/export controls missing")
    require(all(token in hub for token in ("7", "30", "90")), "Repeat intervals missing")

    audit = fold(AUDIT.read_text(encoding="utf-8"))
    for phrase in (
        "arama niyeti", "icerik boslugu", "kullanıcı yolculugu", "affiliate urun kategorileri",
        "donusum noktaları", "tekrar ziyaret nedenleri", "beklenen kullanıcı faydası", "beklenen gelir etkisi"
    ):
        require(phrase in audit, f"Audit section missing: {phrase}")

    print("ALO186 aquarium continuity growth v147 contract: PASS")


if __name__ == "__main__":
    main()
