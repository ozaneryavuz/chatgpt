#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "accessible": ROOT / "alo186/hesaplama/elektrik-kesintisi-erisilebilir-ev-cikis-aydinlatma-plani/index.html",
    "lock": ROOT / "alo186/hesaplama/akilli-kilit-pil-acil-guc-mekanik-anahtar-uygunlugu/index.html",
    "access": ROOT / "alo186/sektor-rehberi/garaj-kapi-panjur-kepenk-elektrik-kesintisi-test-merkezi/index.html",
}
CANONICALS = {
    "accessible": "https://alo186.com/hesaplama/elektrik-kesintisi-erisilebilir-ev-cikis-aydinlatma-plani/",
    "lock": "https://alo186.com/hesaplama/akilli-kilit-pil-acil-guc-mekanik-anahtar-uygunlugu/",
    "access": "https://alo186.com/sektor-rehberi/garaj-kapi-panjur-kepenk-elektrik-kesintisi-test-merkezi/",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/181-access-continuity-growth.json"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def check_js(name: str, html: str) -> None:
    scripts = []
    for match in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", html, flags=re.I | re.S):
        if "application/ld+json" in match.group("attrs").lower():
            continue
        scripts.append(match.group("body"))
    assert scripts, f"{name}: executable script missing"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write("\n".join(scripts))
        temp_path = Path(handle.name)
    try:
        result = subprocess.run(["node", "--check", str(temp_path)], capture_output=True, text=True)
        assert result.returncode == 0, f"{name}: javascript syntax error\n{result.stderr}"
    finally:
        temp_path.unlink(missing_ok=True)


def check_common(name: str, html: str) -> None:
    compact = re.sub(r"\s+", "", html)
    assert f'<linkrel="canonical"href="{CANONICALS[name]}">' in compact
    assert '"@type":"WebApplication"' in compact
    assert '"@type":"FAQPage"' in compact
    assert '"@type":"BreadcrumbList"' in compact
    for forbidden in ('"@type":"Offer"', '"@type":"Product"', '"availability"', '"aggregateRating"', '"priceCurrency"'):
        assert forbidden not in compact, f"{name}: forbidden commerce schema {forbidden}"
    assert not re.search(r'href=["\']https://www\.amazon\.com\.tr', html, flags=re.I), f"{name}: static Amazon href"
    assert "resmî kurum" in html or "resmi kurum" in html
    check_js(name, html)


def main() -> None:
    content = {name: read(path) for name, path in PAGES.items()}
    for name, html in content.items():
        check_common(name, html)

    for name in ("accessible", "lock"):
        html = content[name]
        for marker in ("needConfirm", "specConfirm", "adConfirm", "alo186rehber-21", "sponsored nofollow noopener"):
            assert marker in html, f"{name}: missing affiliate gate marker {marker}"
        assert "yeni ürün almayın" in html.lower(), f"{name}: no-buy outcome missing"
        assert "fiyat, stok, puan" in html.lower()
        assert "Ticari yol kapalı" in html

    accessible = content["accessible"]
    for marker in ("Ready.gov", "ADA.gov", "U.S. Fire Administration", "aktif kesintinin çözümü değildir"):
        assert marker.lower() in accessible.lower()
    assert accessible.count("shopCard(") >= 5

    lock = content["lock"]
    for marker in ("9 V acil güç", "Tam model", "mekanik anahtar", "Yale YDM3168", "Profesyonel erişim sistemi"):
        assert marker in lock
    assert "belgelenmemiş" in lock
    assert lock.count("card(") >= 5

    access = content["access"]
    assert "alo186rehber-21" not in access
    assert "amazon.com.tr" not in access.lower()
    for marker in ("Doğrudan affiliate bağlantısı yoktur", "JSON planını indir", "7 günlük kontrol ICS", "30 günlük işlev testi ICS", "90 günlük kabul testi ICS", "Yangın güvenliği sistemi"):
        assert marker in access
    assert "LiftMaster" in access

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 181
    routes = overlay["routes"]
    assert len(routes) == 3
    paths = [route["canonicalPath"] for route in routes]
    assert len(paths) == len(set(paths))
    assert {"https://alo186.com" + path for path in paths} == set(CANONICALS.values())
    for route in routes:
        assert (ROOT / route["source"]).exists(), route["source"]

    audit = read(ROOT / "alo186/audits/access-continuity-growth-v181-2026-08-01.md")
    for marker in ("Seçilen 3 aksiyon", "Arama niyeti", "Affiliate ürün kategorileri", "Tekrar ziyaret nedenleri", "Beklenen gelir / lead etkisi", "Gerçek gelir artışı henüz ölçülmemiştir"):
        assert marker in audit

    print("access continuity growth v181 contract: OK")


if __name__ == "__main__":
    main()
