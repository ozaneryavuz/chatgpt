from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "safety": ROOT / "alo186/hesaplama/elektrik-kesintisi-buzdolabi-dondurucu-gida-guvenligi/index.html",
    "power": ROOT / "alo186/hesaplama/buzdolabi-dondurucu-yedek-guc-w-wh-kalkis-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/buzdolabi-dondurucu-kesinti-gida-sicaklik-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/166-refrigerator-cold-chain-growth.json"
AUDIT = ROOT / "alo186/audits/refrigerator-cold-chain-growth-v166-2026-08-01.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def check_javascript(path: Path, html: str) -> None:
    scripts = re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", html, flags=re.I | re.S)
    assert scripts, f"no executable script found in {path}"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write("\n".join(scripts))
        script_path = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(script_path)], check=True, capture_output=True, text=True)
    finally:
        script_path.unlink(missing_ok=True)


def main() -> None:
    pages = {name: read(path) for name, path in PAGES.items()}
    expected = {
        "safety": "https://alo186.com/hesaplama/elektrik-kesintisi-buzdolabi-dondurucu-gida-guvenligi/",
        "power": "https://alo186.com/hesaplama/buzdolabi-dondurucu-yedek-guc-w-wh-kalkis-uygunlugu/",
        "center": "https://alo186.com/sektor-rehberi/buzdolabi-dondurucu-kesinti-gida-sicaklik-test-merkezi/",
    }

    for name, page in pages.items():
        assert f'<link rel="canonical" href="{expected[name]}">' in page
        assert "Bağımsız" in page
        assert "FAQPage" in page and "BreadcrumbList" in page
        assert '"@type":"Product"' not in page
        assert '"@type":"Offer"' not in page
        assert '"availability"' not in page
        assert '"aggregateRating"' not in page
        assert ".setItem(" not in page and ".getItem(" not in page
        assert "@media(max-width:820px)" in page
        check_javascript(PAGES[name], page)

    safety = pages["safety"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in safety
    assert "amazon.com.tr" not in safety
    assert "yaklaşık <strong>4 saat</strong>" in safety
    assert "yaklaşık <strong>48 saat</strong>" in safety
    assert "yaklaşık <strong>24 saat</strong>" in safety
    assert "Gıdanın güvenliğini tat" in safety
    assert "112’yi arayın" in safety

    power = pages["power"]
    assert "Mevcut sistem yeterli — yeni ürün almayın" in power
    assert "cihaz W × 1,25" in power
    assert "kalkış W × 1,15" in power
    assert "cihaz W × saat ÷ verim × 1,20" in power
    assert "needConfirm" in power and "specConfirm" in power and "adConfirm" in power
    assert 'rel="sponsored nofollow noopener"' in power
    assert "tag=alo186rehber-21" in power
    assert "amazon.com.tr" in power
    assert "Aktif olayda teslimata dayalı çözüm göstermiyoruz" in power
    assert "Prizden prize" in power
    assert "fiyat, stok, puan" in power.lower()

    center = pages["center"]
    assert "Bu merkez doğrudan affiliate bağlantısı içermez" in center
    assert "amazon.com.tr" not in center
    assert "JSON görev planı" in center
    assert "7 günlük olay kontrolü" in center
    assert "30 günlük işlev testi" in center
    assert "90 günlük süre testi" in center
    assert "application/json" in center and "text/calendar" in center

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 166
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == {
        "/hesaplama/elektrik-kesintisi-buzdolabi-dondurucu-gida-guvenligi/",
        "/hesaplama/buzdolabi-dondurucu-yedek-guc-w-wh-kalkis-uygunlugu/",
        "/sektor-rehberi/buzdolabi-dondurucu-kesinti-gida-sicaklik-test-merkezi/",
    }
    for route in routing["routes"]:
        assert (ROOT / route["source"]).exists()

    audit = read(AUDIT)
    for phrase in (
        "Arama niyetleri",
        "İçerik boşluğu",
        "Kullanıcı yolculuğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Doğrulanmamış fiyat, stok, puan",
        "Mevcut sistem yeterli — yeni ürün almayın",
    ):
        assert phrase in audit

    print("PASS: ALO186 refrigerator cold-chain growth v166 contract")


if __name__ == "__main__":
    main()
