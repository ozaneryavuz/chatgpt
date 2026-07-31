from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "bill": ROOT / "alo186/hesaplama/elektrik-faturasi-kwh-gunluk-tuketim-karsilastirma/index.html",
    "meter": ROOT / "alo186/hesaplama/priz-tipi-enerji-olcer-akilli-priz-uygunluk/index.html",
    "center": ROOT / "alo186/sektor-rehberi/ev-enerji-tuketimi-olcum-takip-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/153-home-energy-measurement-growth.json"
AUDIT = ROOT / "alo186/audits/home-energy-measurement-growth-v153-2026-07-31.md"


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

    assert routing["version"] == 153
    expected = {
        "/hesaplama/elektrik-faturasi-kwh-gunluk-tuketim-karsilastirma/",
        "/hesaplama/priz-tipi-enerji-olcer-akilli-priz-uygunluk/",
        "/sektor-rehberi/ev-enerji-tuketimi-olcum-takip-merkezi/",
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

    bill = pages["bill"]
    meter = pages["meter"]
    center = pages["center"]

    for phrase in [
        "Tutarı değil önce tüketimi karşılaştırın",
        "kWh/gün",
        "Priz tipi ölçer resmî sayaç testinin yerine geçmez",
        "30 günlük tüketim senaryosu",
        "EPDK",
    ]:
        assert phrase in bill
    assert "Amazon satış ortaklığı bağlantısı" not in bill

    for phrase in [
        "gereksiz akıllı özellik satın almayın",
        "Mevcut ölçüm aracı yeterli — yeni ürün almayın",
        "Isıtıcı, kettle, ütü",
        "ETSI EN 303 645 V3.1.3",
        "IEC 60884-1:2022",
    ]:
        assert phrase in meter
    assert "Amazon satış ortaklığı bağlantısı" in meter
    assert "sponsored nofollow noopener" in meter
    assert "needConfirm" in meter and "specConfirm" in meter and "adConfirm" in meter
    assert "tag=alo186rehber-21" in meter

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
        "EPDK",
        "IEC 60884-1:2022",
        "ETSI EN 303 645 V3.1.3",
    ]:
        assert phrase in audit

    print("ALO186 home energy measurement growth v153 contract: PASS")


if __name__ == "__main__":
    main()
