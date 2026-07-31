#!/usr/bin/env python3
"""ALO186 fridge and food-safety growth v146 release contract."""
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
    ROOT / "alo186/hesaplama/buzdolabi-dondurucu-kesinti-gida-guvenligi/index.html",
    ROOT / "alo186/hesaplama/buzdolabi-dondurucu-termometre-alarm-uygunluk/index.html",
]
HUB = ROOT / "alo186/sektor-rehberi/elektrik-kesintisi-buzdolabi-gida-guvenligi-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/146-fridge-food-safety-growth.json"
AUDIT = ROOT / "alo186/audits/fridge-food-safety-growth-v146-2026-07-31.md"
EXPECTED = {
    "/hesaplama/buzdolabi-dondurucu-kesinti-gida-guvenligi/": CALCULATORS[0],
    "/hesaplama/buzdolabi-dondurucu-termometre-alarm-uygunluk/": CALCULATORS[1],
    "/sektor-rehberi/elektrik-kesintisi-buzdolabi-gida-guvenligi-merkezi/": HUB,
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
    return [
        body
        for attrs, body in re.findall(
            r"<script([^>]*)>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL
        )
        if "application/ld+json" not in attrs.lower() and body.strip()
    ]


def check_javascript(path: Path, html: str) -> None:
    node = shutil.which("node")
    require(node is not None, "Node.js is required for inline JavaScript validation")
    scripts = inline_scripts(html)
    require(scripts, f"No executable inline JavaScript found: {path}")
    for index, script in enumerate(scripts, start=1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
            tmp.write(script)
            tmp_path = Path(tmp.name)
        try:
            result = subprocess.run(
                [node, "--check", str(tmp_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            require(
                result.returncode == 0,
                f"Inline JavaScript syntax failed in {path} script {index}: {result.stderr}",
            )
        finally:
            tmp_path.unlink(missing_ok=True)


def check_common(path: Path, canonical: str) -> str:
    require(path.is_file(), f"Missing published file: {path}")
    html = path.read_text(encoding="utf-8")
    lower = fold(html)
    require(
        f'href="https://alo186.com{canonical}"' in html,
        f"Canonical mismatch: {path}",
    )
    require("bagımsız" in lower, f"Independent-platform disclosure missing: {path}")
    require(
        "resmi kurum" in lower or "tarım ve orman bakanlıgı" in lower,
        f"Official-impression guard missing: {path}",
    )
    require(
        "fiyat" in lower and "stok" in lower and "puan" in lower,
        f"Commercial-data guard missing: {path}",
    )
    require(
        "localstorage" not in lower and "sessionstorage" not in lower,
        f"Persistent browser storage found: {path}",
    )
    for forbidden in ('"@type":"product"', '"@type":"offer"', "aggregaterating", '"availability"'):
        require(forbidden not in lower, f"Forbidden commercial schema/token {forbidden}: {path}")
    check_javascript(path, html)
    return html


def main() -> None:
    require(OVERLAY.is_file(), "Routing overlay is missing")
    require(AUDIT.is_file(), "Growth audit is missing")
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    require(overlay.get("version") == 146, "Routing overlay version must be 146")
    routes = {item["canonicalPath"]: item for item in overlay.get("routes", [])}
    require(set(routes) == set(EXPECTED), f"Unexpected route set: {set(routes)}")
    for canonical, path in EXPECTED.items():
        require(
            routes[canonical]["source"] == str(path.relative_to(ROOT)),
            f"Source mismatch for {canonical}",
        )

    for canonical, path in list(EXPECTED.items())[:2]:
        html = check_common(path, canonical)
        lower = fold(html)
        require("yeni urun almayın" in lower, f"Buy-nothing result missing: {path}")
        require("amazon satıs ortaklıgı" in lower, f"Visible affiliate disclosure missing: {path}")
        require('rel="sponsored nofollow noopener"' in html, f"Affiliate rel contract missing: {path}")
        require("amazon.com.tr/s?k=" in lower, f"Only category/search affiliate destination expected: {path}")
        require(
            'id="need"' in html and 'id="spec"' in html and 'id="ad"' in html,
            f"Three affiliate confirmations missing: {path}",
        )
        require("hazard" in lower or "flood" in lower, f"Fail-closed hazard input missing: {path}")
        require("scope" in lower, f"Scope gate missing: {path}")

    food_html = CALCULATORS[0].read_text(encoding="utf-8")
    food_lower = fold(food_html)
    for phrase in ("4 saat", "48 saat", "24 saat", "supheli gıdayı tatmayın", "aktif veya yeni bitmis kesintide"):
        require(phrase in food_lower, f"Food safety guard missing: {phrase}")
    require("anne sutu" in food_lower and "ilac" in food_lower and "ticari gıda" in food_lower,
            "Special cold-chain exclusions missing")
    require("fda" in food_lower and "cdc" in food_lower and "tarım ve orman" in food_lower,
            "Primary food-safety sources missing")

    thermo_html = CALCULATORS[1].read_text(encoding="utf-8")
    thermo_lower = fold(thermo_html)
    for phrase in ("0–4 °c", "-18 °c", "baglantısız", "bulut", "min/max"):
        require(phrase in thermo_lower, f"Thermometer task distinction missing: {phrase}")
    require("mevcut olcum duzeni yeterli" in thermo_lower, "Existing-equipment success result missing")
    require("ilac" in thermo_lower and "ticari gıda" in thermo_lower,
            "Medical/commercial scope exclusion missing")

    hub_html = check_common(HUB, "/sektor-rehberi/elektrik-kesintisi-buzdolabi-gida-guvenligi-merkezi/")
    hub_lower = fold(hub_html)
    require("amazon.com.tr" not in hub_lower, "Hub must not include a direct Amazon destination")
    require('rel="sponsored nofollow noopener"' not in hub_html, "Hub must not include affiliate links")
    require("kisisel veri" in hub_lower, "Hub personal-data statement missing")
    require("json" in hub_lower and "ics" in hub_lower, "Hub JSON/ICS repeat-test exports missing")
    require("7" in hub_html and "30" in hub_html and "90" in hub_html, "Hub repeat-test intervals missing")
    require("dogrudan affiliate baglantısı yoktur" in hub_lower, "Hub no-direct-affiliate disclosure missing")
    require("alo 174" in hub_lower and "edas" in hub_lower, "Official-channel separation missing")

    audit = fold(AUDIT.read_text(encoding="utf-8"))
    for phrase in (
        "arama niyeti",
        "icerik boslugu",
        "kullanıcı yolculugu",
        "affiliate urun kategorileri",
        "donusum noktaları",
        "tekrar ziyaret nedenleri",
        "beklenen kullanıcı faydası",
        "beklenen gelir etkisi",
    ):
        require(phrase in audit, f"Audit section missing: {phrase}")

    print("ALO186 fridge food-safety growth v146 contract: PASS")


if __name__ == "__main__":
    main()
