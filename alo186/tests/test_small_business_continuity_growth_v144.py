#!/usr/bin/env python3
"""ALO186 small-business continuity growth v144 release contract."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALCULATORS = [
    ROOT / "alo186/hesaplama/isletme-pos-okc-modem-yedek-guc-uygunluk/index.html",
    ROOT / "alo186/hesaplama/kucuk-isletme-kritik-yuk-oncelik-ve-kesinti-suresi/index.html",
]
HUB = ROOT / "alo186/sektor-rehberi/kucuk-isletme-elektrik-kesintisi-sureklilik-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/144-small-business-continuity.json"
AUDIT = ROOT / "alo186/audits/small-business-continuity-growth-v144-2026-07-31.md"
EXPECTED = {
    "/hesaplama/isletme-pos-okc-modem-yedek-guc-uygunluk/": CALCULATORS[0],
    "/hesaplama/kucuk-isletme-kritik-yuk-oncelik-ve-kesinti-suresi/": CALCULATORS[1],
    "/sektor-rehberi/kucuk-isletme-elektrik-kesintisi-sureklilik-merkezi/": HUB,
}


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
    lower = html.lower()
    require(
        f'href="https://alo186.com{canonical}"' in html,
        f"Canonical mismatch: {path}",
    )
    require("bağımsız" in lower, f"Independent-platform disclosure missing: {path}")
    require("resmî kurum" in lower or "edaş" in lower, f"Official-impression guard missing: {path}")
    require("fiyat" in lower and "stok" in lower and "puan" in lower, f"Commercial-data guard missing: {path}")
    require("localstorage" not in lower and "sessionstorage" not in lower, f"Persistent browser storage found: {path}")
    for forbidden in ('"@type":"product"', '"@type":"offer"', "aggregaterating", '"availability"'):
        require(forbidden not in lower, f"Forbidden commercial schema/token {forbidden}: {path}")
    check_javascript(path, html)
    return html


def main() -> None:
    require(OVERLAY.is_file(), "Routing overlay is missing")
    require(AUDIT.is_file(), "Growth audit is missing")
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    require(overlay.get("version") == 144, "Routing overlay version must be 144")
    routes = {item["canonicalPath"]: item for item in overlay.get("routes", [])}
    require(set(routes) == set(EXPECTED), f"Unexpected route set: {set(routes)}")
    for canonical, path in EXPECTED.items():
        require(routes[canonical]["source"] == str(path.relative_to(ROOT)), f"Source mismatch for {canonical}")

    calculator_html = []
    for canonical, path in list(EXPECTED.items())[:2]:
        html = check_common(path, canonical)
        calculator_html.append(html)
        lower = html.lower()
        require("yeni ürün almayın" in lower, f"Buy-nothing success result missing: {path}")
        require("amazon satış ortaklığı" in lower, f"Visible affiliate disclosure missing: {path}")
        require('rel="sponsored nofollow noopener"' in html, f"Affiliate rel contract missing: {path}")
        require("amazon.com.tr/s?k=" in lower, f"Only category/search affiliate destination expected: {path}")
        require('id="need"' in html and 'id="spec"' in html and 'id="ad"' in html, f"Three affiliate confirmations missing: {path}")
        require("hazard" in lower and "scope" in lower, f"Fail-closed safety inputs missing: {path}")

    hub_html = check_common(HUB, "/sektor-rehberi/kucuk-isletme-elektrik-kesintisi-sureklilik-merkezi/")
    hub_lower = hub_html.lower()
    require("amazon.com.tr" not in hub_lower, "Hub must not include a direct Amazon destination")
    require('rel="sponsored nofollow noopener"' not in hub_html, "Hub must not include affiliate links")
    require("kişisel veri" in hub_lower, "Hub personal-data statement missing")
    require("json" in hub_lower and ".ics" in hub_lower, "Hub JSON/ICS repeat-test exports missing")
    require("7" in hub_html and "30" in hub_html and "90" in hub_html, "Hub repeat-test intervals missing")
    require("doğrudan affiliate bağlantısı" in hub_lower, "Hub no-direct-affiliate disclosure missing")

    audit = AUDIT.read_text(encoding="utf-8").lower()
    for phrase in ("arama niyeti", "içerik boşluğu", "kullanıcı yolculuğu", "affiliate ürün kategorileri", "tekrar ziyaret nedenleri", "beklenen gelir etkisi"):
        require(phrase in audit, f"Audit section missing: {phrase}")

    print("ALO186 small-business continuity growth v144 contract: PASS")


if __name__ == "__main__":
    main()
