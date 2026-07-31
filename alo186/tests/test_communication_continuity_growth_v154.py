from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "mini": ROOT / "alo186/hesaplama/modem-ont-router-mini-ups-guc-sure-uygunluk/index.html",
    "powerbank": ROOT / "alo186/hesaplama/telefon-powerbank-acil-sarj-uygunluk/index.html",
    "center": ROOT / "alo186/sektor-rehberi/elektrik-kesintisi-iletisim-sureklilik-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/154-communication-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/communication-continuity-growth-v154-2026-07-31.md"


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
    assert result.returncode == 0, result.stderr


def main() -> None:
    pages = {name: text(path) for name, path in FILES.items()}
    routing = json.loads(text(ROUTING))
    audit = text(AUDIT)

    assert routing["version"] == 154
    expected = {
        "/hesaplama/modem-ont-router-mini-ups-guc-sure-uygunluk/",
        "/hesaplama/telefon-powerbank-acil-sarj-uygunluk/",
        "/sektor-rehberi/elektrik-kesintisi-iletisim-sureklilik-merkezi/",
    }
    assert {r["canonicalPath"] for r in routing["routes"]} == expected

    for name, html in pages.items():
        check_js(html, name)
        assert 'rel="canonical"' in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert "Bağımsız" in html and "resmî kurum" in html
        assert "fiyat" in html.lower() and "stok" in html.lower()
        assert "aggregateRating" not in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "localStorage" not in html and "sessionStorage" not in html

    mini = pages["mini"]
    powerbank = pages["powerbank"]
    center = pages["center"]

    for phrase in [
        "Mevcut mini UPS yeterli — yeni ürün almayın",
        "konektör",
        "polarite",
        "İnternet sürekliliği yalnız evdeki cihazların enerjisine bağlı değildir",
        "IEC 62368-1:2023",
        "IEC 62040-3:2021",
    ]:
        assert phrase in mini
    assert "Amazon satış ortaklığı bağlantısı" in mini
    assert "sponsored nofollow noopener" in mini
    assert "needConfirm" in mini and "specConfirm" in mini and "adConfirm" in mini
    assert "tag=alo186rehber-21" in mini

    for phrase in [
        "Mevcut powerbank yeterli — yeni ürün almayın",
        "mAh değerini doğrudan",
        "USB Power Delivery",
        "geri çağırma",
        "Ready.gov",
        "CPSC",
    ]:
        assert phrase in powerbank
    assert "Amazon satış ortaklığı bağlantısı" in powerbank
    assert "sponsored nofollow noopener" in powerbank
    assert "needConfirm" in powerbank and "specConfirm" in powerbank and "adConfirm" in powerbank
    assert "tag=alo186rehber-21" in powerbank

    assert "doğrudan affiliate bağlantısı içermez" in center
    assert "JSON indir" in center and "Takvime ekle (.ics)" in center
    assert "7 gün" in center and "30 gün" in center and "90 gün" in center
    assert "application/json" in center and "text/calendar" in center

    for phrase in [
        "Arama niyeti",
        "İçerik boşluğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Ready.gov",
        "USB-IF",
        "IEC 62368-1:2023",
        "CPSC",
    ]:
        assert phrase in audit

    print("ALO186 communication continuity growth v154 contract: PASS")


if __name__ == "__main__":
    main()
