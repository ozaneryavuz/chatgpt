#!/usr/bin/env python3
"""ALO186 security camera continuity growth v150 release contract."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOURNEY = ROOT / "alo186/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-kayit-erisimi/index.html"
POWER = ROOT / "alo186/hesaplama/poe-kamera-nvr-ups-guc-sure-uygunluk/index.html"
HUB = ROOT / "alo186/sektor-rehberi/guvenlik-kamerasi-kayit-sureklilik-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/150-security-camera-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/security-camera-continuity-growth-v150-2026-07-31.md"
EXPECTED = {
    "/hesaplama/guvenlik-kamerasi-elektrik-kesintisi-kayit-erisimi/": JOURNEY,
    "/hesaplama/poe-kamera-nvr-ups-guc-sure-uygunluk/": POWER,
    "/sektor-rehberi/guvenlik-kamerasi-kayit-sureklilik-merkezi/": HUB,
}


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def executable_scripts(html: str) -> list[str]:
    return [body for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", html, re.I | re.S)
            if "application/ld+json" not in attrs.lower() and body.strip()]


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
    require("resmi kurum" in lower or "edas" in lower or "112" in lower, f"Role boundary missing {path}")
    for token in ("fiyat", "stok", "puan", "garanti"):
        require(token in lower, f"Commercial guard missing {token}: {path}")
    require("localstorage" not in lower and "sessionstorage" not in lower, f"Persistent storage found {path}")
    for forbidden in ('"@type":"product"', '"@type":"offer"', "aggregaterating", '"availability"'):
        require(forbidden not in lower, f"Forbidden schema {forbidden}: {path}")
    check_js(path, html)
    return html


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    require(overlay.get("version") == 150, "Overlay version must be 150")
    require(overlay.get("generatedAt") == "2026-07-31", "Overlay date mismatch")
    routes = {item["canonicalPath"]: item for item in overlay.get("routes", [])}
    require(set(routes) == set(EXPECTED), f"Unexpected routes {set(routes)}")
    for canonical, path in EXPECTED.items():
        require(routes[canonical]["source"] == str(path.relative_to(ROOT)), f"Source mismatch {canonical}")

    journey = check_common(JOURNEY, list(EXPECTED)[0])
    journey_lower = fold(journey)
    for phrase in ("kayıt, uzaktan erisim", "mevcut kayıt surekliligi yeterli", "yeni urun almayın", "aktif olayda urun aramayın"):
        require(phrase in journey_lower, f"Journey phrase missing: {phrase}")
    require("amazon.com.tr" not in journey_lower, "Journey page must not contain Amazon")
    require(all(token in journey for token in ("cameraPower", "recorder", "poe", "network", "playback")), "Journey gates missing")
    require("standards.ieee.org" in journey_lower and "axis.com" in journey_lower, "Primary technical sources missing")

    power = check_common(POWER, list(EXPECTED)[1])
    power_lower = fold(power)
    require("poe butcesi yetersiz" in power_lower, "PoE budget fail-closed result missing")
    require("mevcut sistem yeterli" in power_lower and "yeni urun almayın" in power_lower, "Buy-nothing result missing")
    require("amazon satıs ortaklıgı" in power_lower, "Affiliate disclosure missing")
    require('rel="sponsored nofollow noopener"' in power, "Affiliate rel missing")
    require("amazon.com.tr/s?k=" in power_lower, "Category search destination missing")
    require(all(f'id="{item}"' in power for item in ("need", "spec", "ad")), "Three confirmations missing")
    require(all(token in power for token in ("cameraMaxW", "poeBudgetW", "upsW", "upsWh", "upsVA", "runtimeTest", "playback")), "Power gates missing")
    require("aktif kesintide" in power_lower and "ticari yol kapalı" in power_lower, "Active outage commerce block missing")

    hub = check_common(HUB, list(EXPECTED)[2])
    hub_lower = fold(hub)
    require("amazon.com.tr" not in hub_lower, "Hub must not include Amazon")
    require('rel="sponsored nofollow noopener"' not in hub, "Hub must not include affiliate rel")
    require("dogrudan affiliate baglantısı yoktur" in hub_lower, "No-direct-affiliate disclosure missing")
    require("kisisel veri" in hub_lower and "json" in hub_lower and "ics" in hub_lower, "Privacy/export controls missing")
    require(all(token in hub for token in (">7 gün", ">30 gün", ">90 gün")), "Repeat intervals missing")

    audit = fold(AUDIT.read_text(encoding="utf-8"))
    for phrase in ("arama niyeti", "icerik boslugu", "kullanıcı yolculugu", "affiliate urun kategorileri", "donusum noktaları", "tekrar ziyaret nedenleri", "beklenen kullanıcı faydası", "beklenen gelir etkisi"):
        require(phrase in audit, f"Audit section missing {phrase}")

    print("ALO186 security camera continuity growth v150 contract: PASS")


if __name__ == "__main__":
    main()
