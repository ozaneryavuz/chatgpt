from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "safety": ROOT / "alo186/hesaplama/elektrik-kesintisinde-gunes-paneli-neden-calismiyor-guvenlik/index.html",
    "sizing": ROOT / "alo186/hesaplama/ev-ges-eps-backup-kritik-yuk-w-wh-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/ev-ges-batarya-yedek-guc-kabul-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/171-solar-backup-readiness-growth.json"
AUDIT = ROOT / "alo186/audits/solar-backup-readiness-growth-v171-2026-08-01.md"


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
        "safety": "https://alo186.com/hesaplama/elektrik-kesintisinde-gunes-paneli-neden-calismiyor-guvenlik/",
        "sizing": "https://alo186.com/hesaplama/ev-ges-eps-backup-kritik-yuk-w-wh-uygunlugu/",
        "center": "https://alo186.com/sektor-rehberi/ev-ges-batarya-yedek-guc-kabul-test-merkezi/",
    }

    for name, html in pages.items():
        assert f'<link rel="canonical" href="{expected[name]}">' in html
        assert "ALO186" in html and "Bağımsız" in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert '"availability"' not in html
        assert '"aggregateRating"' not in html
        assert ".setItem(" not in html and ".getItem(" not in html
        assert "@media(max-width:820px)" in html
        check_javascript(PAGES[name], html)

    safety = pages["safety"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in safety
    assert "anti-islanding" in safety.lower()
    assert "koruma" in safety.lower() and "köprülemeyin" in safety.lower()
    assert "Mevcut sistem gerçek kabul testini geçti — yeni ürün almayın" in safety
    assert "amazon.com.tr" not in safety.lower()
    assert 'rel="sponsored' not in safety

    sizing = pages["sizing"]
    assert "Bu araç ürün seçmez ve affiliate bağlantısı içermez" in sizing
    assert "Temkinli enerji ihtiyacı" in sizing
    assert "Mevcut sistem hedefi karşılıyor — yeni ürün almayın" in sizing
    assert "Affiliate ürün kategorileri neden kapalı?" in sizing
    assert "/iletisim/" in sizing
    assert "amazon.com.tr" not in sizing.lower()
    assert 'rel="sponsored' not in sizing
    for forbidden in ("₺", " TL", "stokta", "yıldız", "garanti süresi"):
        assert forbidden.lower() not in sizing.lower()

    center = pages["center"]
    assert "Bu merkez doğrudan affiliate bağlantısı içermez" in center
    assert "Affiliate yerine neden tekrar test ve teknik lead?" in center
    assert "JSON görev planı indir" in center
    assert "7 günlük olay kontrolü" in center
    assert "30 günlük işlev testi" in center
    assert "90 günlük kabul testi" in center
    assert "application/json" in center and "text/calendar" in center
    assert "/iletisim/" in center
    assert "amazon.com.tr" not in center.lower()
    assert 'rel="sponsored' not in center

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 171
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == {
        "/hesaplama/elektrik-kesintisinde-gunes-paneli-neden-calismiyor-guvenlik/",
        "/hesaplama/ev-ges-eps-backup-kritik-yuk-w-wh-uygunlugu/",
        "/sektor-rehberi/ev-ges-batarya-yedek-guc-kabul-test-merkezi/",
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
        "Tamamlanamayan bağımsız kontroller",
    ):
        assert phrase in audit

    print("PASS: ALO186 solar backup readiness growth v171 contract")


if __name__ == "__main__":
    main()
