from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "safety": ROOT / "alo186/hesaplama/elektrik-kesintisi-hidrofor-su-yok-guvenlik-teshis/index.html",
    "sizing": ROOT / "alo186/hesaplama/hidrofor-jenerator-ups-kalkis-w-kva-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/apartman-otel-hidrofor-elektrik-surekliligi-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/169-hydrofor-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/hydrofor-continuity-growth-v169-2026-08-01.md"


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
        "safety": "https://alo186.com/hesaplama/elektrik-kesintisi-hidrofor-su-yok-guvenlik-teshis/",
        "sizing": "https://alo186.com/hesaplama/hidrofor-jenerator-ups-kalkis-w-kva-uygunlugu/",
        "center": "https://alo186.com/sektor-rehberi/apartman-otel-hidrofor-elektrik-surekliligi-test-merkezi/",
    }

    for name, html in pages.items():
        assert f'<link rel="canonical" href="{expected[name]}">' in html
        assert "Bağımsız" in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert '"availability"' not in html
        assert '"aggregateRating"' not in html
        assert "amazon.com.tr" not in html.lower()
        assert 'rel="sponsored' not in html
        assert ".setItem(" not in html and ".getItem(" not in html
        assert "@media(max-width:820px)" in html
        check_javascript(PAGES[name], html)

    safety = pages["safety"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in safety
    assert "Koruma köprülemeyin, panoyu açmayın" in safety
    assert "Yangın pompası bu aracın dışındadır" in safety
    assert "Su kaynağı doğrulanmadan pompa çalıştırılmaz" in safety
    assert "Yeni ürün almayın" in safety

    sizing = pages["sizing"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in sizing
    assert "Evrensel kalkış çarpanı kullanılmaz" in sizing
    assert "Çalışma kVA = çalışma kW ÷ güç faktörü" in sizing
    assert "Mevcut sistem gerçek testi geçti — yeni ürün almayın" in sizing
    assert "Doğrulanmış kalkış kanıtı olmadan sonuç üretilmez" in sizing
    assert "/iletisim/" in sizing

    center = pages["center"]
    assert "Bu merkez doğrudan affiliate bağlantısı içermez" in center
    assert "Affiliate yerine neden teknik lead?" in center
    assert "JSON görev planı" in center
    assert "7 günlük olay kontrolü" in center
    assert "30 günlük işlev testi" in center
    assert "90 günlük kabul testi" in center
    assert "application/json" in center and "text/calendar" in center
    assert "/iletisim/" in center

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 169
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == {
        "/hesaplama/elektrik-kesintisi-hidrofor-su-yok-guvenlik-teshis/",
        "/hesaplama/hidrofor-jenerator-ups-kalkis-w-kva-uygunlugu/",
        "/sektor-rehberi/apartman-otel-hidrofor-elektrik-surekliligi-test-merkezi/",
    }
    for route in routing["routes"]:
        assert (ROOT / route["source"]).exists()

    for canonical in expected.values():
        count = 0
        for path in (ROOT / "alo186").rglob("*.html"):
            count += read(path).count(f'<link rel="canonical" href="{canonical}">')
        assert count == 1, f"canonical collision: {canonical} count={count}"

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
        "sitemap",
    ):
        assert phrase in audit

    print("PASS: ALO186 hydrofor continuity growth v169 contract")


if __name__ == "__main__":
    main()
