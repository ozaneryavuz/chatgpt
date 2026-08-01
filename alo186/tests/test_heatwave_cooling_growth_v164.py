from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "safety": ROOT / "alo186/hesaplama/elektrik-kesintisi-asiri-sicak-isi-stresi-guvenligi/index.html",
    "suitability": ROOT / "alo186/hesaplama/sarjli-vantilator-usb-fan-wh-sure-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/sicak-hava-elektrik-kesintisi-serinleme-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/164-heatwave-cooling-growth.json"
AUDIT = ROOT / "alo186/audits/heatwave-cooling-growth-v164-2026-08-01.md"


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
        "safety": "https://alo186.com/hesaplama/elektrik-kesintisi-asiri-sicak-isi-stresi-guvenligi/",
        "suitability": "https://alo186.com/hesaplama/sarjli-vantilator-usb-fan-wh-sure-uygunlugu/",
        "center": "https://alo186.com/sektor-rehberi/sicak-hava-elektrik-kesintisi-serinleme-test-merkezi/",
    }

    for name, html in pages.items():
        assert f'<link rel="canonical" href="{expected[name]}">' in html
        assert "Bağımsız" in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert '"availability"' not in html
        assert '"aggregateRating"' not in html
        assert ".setItem(" not in html and ".getItem(" not in html
        assert "fiyat, stok, puan" in html.lower() or name == "center"
        check_javascript(PAGES[name], html)

    safety = pages["safety"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in safety
    assert "amazon.com.tr" not in safety
    assert "40 °C" in safety
    assert "112’yi arayın" in safety
    assert "Fanı ana koruma olarak kullanmayın" in safety

    suitability = pages["suitability"]
    assert "Mevcut fan yeterli — yeni ürün almayın" in suitability
    assert "Wh × 0,75 ÷ kullanılan kademe W" in suitability
    assert "mAh ÷ 1000 × nominal V" in suitability
    assert "needConfirm" in suitability and "specConfirm" in suitability and "adConfirm" in suitability
    assert 'rel="sponsored nofollow noopener"' in suitability
    assert "tag=alo186rehber-21" in suitability
    assert "amazon.com.tr" in suitability
    assert "Aktif olayda teslimata dayalı çözüm göstermiyoruz" in suitability
    assert "Giyilebilir fanı varsayılan çözüm olarak önermiyoruz" in suitability

    center = pages["center"]
    assert "Bu merkez doğrudan affiliate bağlantısı içermez" in center
    assert "amazon.com.tr" not in center
    assert "JSON görev planı" in center
    assert "7 günlük olay kontrolü" in center
    assert "30 günlük işlev testi" in center
    assert "90 günlük süre testi" in center
    assert "application/json" in center and "text/calendar" in center

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 164
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == {
        "/hesaplama/elektrik-kesintisi-asiri-sicak-isi-stresi-guvenligi/",
        "/hesaplama/sarjli-vantilator-usb-fan-wh-sure-uygunlugu/",
        "/sektor-rehberi/sicak-hava-elektrik-kesintisi-serinleme-test-merkezi/",
    }
    for route in routing["routes"]:
        assert (ROOT / route["source"]).exists()

    audit = read(AUDIT)
    for phrase in (
        "Arama niyetleri",
        "İçerik boşluğu",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Doğrulanmamış fiyat, stok, puan",
        "Mevcut fan yeterli — yeni ürün almayın",
    ):
        assert phrase in audit

    print("PASS: ALO186 heatwave cooling growth v164 contract")


if __name__ == "__main__":
    main()
