from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "food": ROOT / "alo186/hesaplama/elektrik-kesintisi-buzdolabi-dondurucu-gida-guvenligi/index.html",
    "power": ROOT / "alo186/hesaplama/buzdolabi-dondurucu-guc-istasyonu-w-wh-kalkis-uygunluk/index.html",
    "center": ROOT / "alo186/sektor-rehberi/buzdolabi-dondurucu-soguk-zincir-kesinti-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/155-cold-chain-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/cold-chain-continuity-growth-v155-2026-07-31.md"


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

    assert routing["version"] == 155
    expected = {
        "/hesaplama/elektrik-kesintisi-buzdolabi-dondurucu-gida-guvenligi/",
        "/hesaplama/buzdolabi-dondurucu-guc-istasyonu-w-wh-kalkis-uygunluk/",
        "/sektor-rehberi/buzdolabi-dondurucu-soguk-zincir-kesinti-merkezi/",
    }
    assert {r["canonicalPath"] for r in routing["routes"]} == expected

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

    food = pages["food"]
    power = pages["power"]
    center = pages["center"]

    for phrase in [
        "4 saat",
        "48 saat",
        "24 saat",
        "4 °C",
        "tadına bak",
        "Mevcut termometreyi kullanın — yeni ürün almayın",
        "CDC",
        "USDA",
        "IEC 60335-2-24:2025",
    ]:
        assert phrase in food
    assert "Amazon satış ortaklığı bağlantısı" in food
    assert "sponsored nofollow noopener" in food
    assert "needConfirm" in food and "specConfirm" in food and "adConfirm" in food
    assert "tag=alo186rehber-21" in food
    assert "Kesinti sürerken yeni ürün teslimatı çözüm değildir" in food

    for phrase in [
        "Mevcut güç istasyonu yeterli — yeni ürün almayın",
        "kalkış/tepe",
        "Temkinli enerji",
        "Prizden prize",
        "IEC 62040-3:2021",
        "IEC 60335-2-24:2025",
    ]:
        assert phrase in power
    assert "Amazon satış ortaklığı bağlantısı" in power
    assert "sponsored nofollow noopener" in power
    assert "needConfirm" in power and "specConfirm" in power and "adConfirm" in power
    assert "tag=alo186rehber-21" in power
    assert "Kesinti sürerken yeni ürün teslimatı çözüm değildir" in power

    assert "doğrudan affiliate bağlantısı içermez" in center
    assert "JSON indir" in center and "Takvime ekle (.ics)" in center
    assert "7 / 30 / 90" in center
    assert "application/json" in center and "text/calendar" in center
    assert "İlaç / tıbbi ürün" in center

    for phrase in [
        "Arama niyeti",
        "İçerik boşluğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "CDC",
        "USDA",
        "IEC 60335-2-24:2025",
        "IEC 62040-3:2021",
    ]:
        assert phrase in audit

    print("ALO186 cold chain continuity growth v155 contract: PASS")


if __name__ == "__main__":
    main()
