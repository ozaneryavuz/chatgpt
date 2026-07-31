from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "placement": ROOT / "alo186/hesaplama/jenerator-karbonmonoksit-konum-guvenligi/index.html",
    "alarm": ROOT / "alo186/hesaplama/karbonmonoksit-alarmi-ihtiyac-yerlesim-test/index.html",
    "center": ROOT / "alo186/sektor-rehberi/jenerator-karbonmonoksit-guvenlik-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/156-generator-co-safety-growth.json"
AUDIT = ROOT / "alo186/audits/generator-co-safety-growth-v156-2026-07-31.md"


def text(path: Path) -> str:
    assert path.exists(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def check_js(html: str, label: str) -> None:
    scripts = re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", html, re.S)
    assert scripts, f"no executable JS in {label}"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as fh:
        fh.write("\n".join(scripts))
        name = fh.name
    result = subprocess.run(["node", "--check", name], capture_output=True, text=True)
    assert result.returncode == 0, f"{label}: {result.stderr}"


def main() -> None:
    pages = {name: text(path) for name, path in FILES.items()}
    routing = json.loads(text(ROUTING))
    audit = text(AUDIT)

    assert routing["version"] == 156
    expected = {
        "/hesaplama/jenerator-karbonmonoksit-konum-guvenligi/",
        "/hesaplama/karbonmonoksit-alarmi-ihtiyac-yerlesim-test/",
        "/sektor-rehberi/jenerator-karbonmonoksit-guvenlik-test-merkezi/",
    }
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    for name, html in pages.items():
        check_js(html, name)
        assert 'rel="canonical"' in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert "Bağımsız" in html and "resmî" in html
        assert "fiyat" in html.lower() and "stok" in html.lower()
        assert "aggregateRating" not in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "localStorage" not in html and "sessionStorage" not in html

    placement = pages["placement"]
    alarm = pages["alarm"]
    center = pages["center"]

    for phrase in [
        "yaklaşık 6,1 m",
        "tamamen açık dış alan",
        "Egzoz yönü",
        "temiz havaya çıkın ve 112’yi arayın",
        "ev prizine",
        "CPSC",
        "CDC",
    ]:
        assert phrase in placement
    assert "Amazon satış ortaklığı" not in placement
    assert "tag=alo186rehber-21" not in placement

    for phrase in [
        "her katında ve uyuma alanlarının dışında",
        "Bataryalı veya batarya yedekli",
        "Mevcut CO alarmı hazırlığı yeterli görünüyor — yeni ürün almayın",
        "Yalnız duman alarmı",
        "Amazon satış ortaklığı bağlantısı",
        "sponsored nofollow noopener",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        "tag=alo186rehber-21",
    ]:
        assert phrase in alarm
    assert "Aktif CO alarmı veya zehirlenme belirtisinde alışveriş yapılmaz" in alarm

    for phrase in [
        "doğrudan affiliate bağlantısı içermez",
        "JSON indir",
        "7 günlük olay sonrası ICS",
        "30 günlük yeni kurulum ICS",
        "90 günlük rutin ICS",
        "application/json",
        "text/calendar",
        "Kişisel verisiz görev planı",
    ]:
        assert phrase in center

    for phrase in [
        "Arama niyeti",
        "İçerik boşluğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "CPSC",
        "CDC",
        "20 feet",
    ]:
        assert phrase in audit

    print("ALO186 generator CO safety growth v156 contract: PASS")


if __name__ == "__main__":
    main()
