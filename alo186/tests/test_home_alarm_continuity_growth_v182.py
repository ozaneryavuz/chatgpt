#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "decision": ROOT / "alo186/hesaplama/duman-karbonmonoksit-alarmi-pil-omur-test-karari/index.html",
    "selector": ROOT / "alo186/amazon-elektrik-urunleri/ev-alarm-pil-test-urun-secici/index.html",
    "center": ROOT / "alo186/sektor-rehberi/ev-alarm-30-180-gun-test-merkezi/index.html",
}
CANONICALS = {
    "decision": "https://alo186.com/hesaplama/duman-karbonmonoksit-alarmi-pil-omur-test-karari/",
    "selector": "https://alo186.com/amazon-elektrik-urunleri/ev-alarm-pil-test-urun-secici/",
    "center": "https://alo186.com/sektor-rehberi/ev-alarm-30-180-gun-test-merkezi/",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/182-home-alarm-continuity-growth.json"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def check_js(name: str, html: str) -> None:
    scripts: list[str] = []
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
    assert not re.search(r'<a\b[^>]*\bhref=["\']https://www\.amazon\.com\.tr', html, flags=re.I | re.S), f"{name}: static Amazon href"
    assert "resmî kurum" in html or "resmi kurum" in html
    check_js(name, html)


def main() -> None:
    content = {name: read(path) for name, path in PAGES.items()}
    for name, html in content.items():
        check_common(name, html)

    for name in ("decision", "selector"):
        html = content[name]
        for marker in ("needConfirm", "specConfirm", "adConfirm", "alo186rehber-21", "sponsored nofollow noopener"):
            assert marker in html, f"{name}: missing affiliate gate marker {marker}"
        assert "yeni ürün almayın" in html.lower(), f"{name}: no-buy outcome missing"
        assert "Ticari yol kapalı" in html
        assert "fiyat, stok, puan" in html.lower()

    decision = content["decision"]
    for marker in ("U.S. Fire Administration", "USFA", "CPSC", "9 Temmuz 2026", "geri çağırma", "test düğmesi"):
        assert marker.lower() in decision.lower(), marker
    assert "alarmı susturmak" in decision.lower()
    assert "new Date().getFullYear()-year<10" in decision

    selector = content["selector"]
    for marker in ("aa:{", "aaa:{", "'9v':{", "tester:{", "smoke:{", "co:{", "combo:{", "access:{"):
        assert marker in selector, f"selector catalog missing {marker}"
    for marker in ("25 Haziran", "9 Temmuz 2026", "ilan başlığı tek başına", "pil test cihazı alarm testinin yerini"):
        assert marker.lower() in selector.lower(), marker
    assert "productCard" in selector

    center = content["center"]
    assert "alo186rehber-21" not in center
    assert "amazon.com.tr" not in center.lower()
    for marker in (
        "Doğrudan affiliate bağlantısı yoktur",
        "JSON planını indir",
        "30 günlük test ICS",
        "180 günlük yerleşim ve erişilebilirlik ICS",
        "Üretici değiştirme tarihi ICS",
        "localStorage",
        "yeni ürün almayın",
    ):
        assert marker in center, marker
    assert "ad, adres, telefon" in center.lower()

    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 182
    routes = overlay["routes"]
    assert len(routes) == 3
    paths = [route["canonicalPath"] for route in routes]
    assert len(paths) == len(set(paths))
    assert {"https://alo186.com" + path for path in paths} == set(CANONICALS.values())
    for route in routes:
        assert (ROOT / route["source"]).exists(), route["source"]

    audit = read(ROOT / "alo186/audits/home-alarm-continuity-growth-v182-2026-08-01.md")
    for marker in (
        "Seçilen 3 aksiyon",
        "Arama niyeti",
        "Kullanıcı yolculuğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir / lead etkisi",
        "Gerçek gelir artışı henüz ölçülmemiştir",
    ):
        assert marker in audit

    print("home alarm continuity growth v182 contract: OK")


if __name__ == "__main__":
    main()
