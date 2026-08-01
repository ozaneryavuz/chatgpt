from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "safety": ROOT / "alo186/hesaplama/akvaryum-elektrik-kesintisi-oksijen-filtre-guvenligi/index.html",
    "power": ROOT / "alo186/hesaplama/akvaryum-hava-motoru-yedek-guc-w-wh-sure-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/akvaryum-elektrik-kesintisi-tekrar-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/167-aquarium-outage-growth.json"
AUDIT = ROOT / "alo186/audits/aquarium-outage-growth-v167-2026-08-01.md"


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
        "safety": "https://alo186.com/hesaplama/akvaryum-elektrik-kesintisi-oksijen-filtre-guvenligi/",
        "power": "https://alo186.com/hesaplama/akvaryum-hava-motoru-yedek-guc-w-wh-sure-uygunlugu/",
        "center": "https://alo186.com/sektor-rehberi/akvaryum-elektrik-kesintisi-tekrar-test-merkezi/",
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
        assert "@media(max-width:820px)" in html
        check_javascript(PAGES[name], html)

    safety = pages["safety"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in safety
    assert "amazon.com.tr" not in safety
    assert "Aktif kesintide ürün teslimatına güvenmeyin" in safety
    assert "Yüzeyde hava yutma" in safety
    assert "112’yi arayın" in safety
    assert "sabit bir “kaç saat dayanır” vaadi güvenli değildir" in safety

    power = pages["power"]
    assert "Mevcut sistem yeterli — yeni ürün almayın" in power
    assert "Batarya Wh = mAh ÷ 1000 × nominal V" in power
    assert "hava motoru W × hedef saat ÷ 0,85 × 1,20" in power
    assert "mevcut Wh × 0,80 ÷ W" in power
    assert "needConfirm" in power and "specConfirm" in power and "adConfirm" in power
    assert 'rel="sponsored nofollow noopener"' in power
    assert "tag=alo186rehber-21" in power
    assert "amazon.com.tr" in power
    assert "Aktif olayda teslimata dayalı çözüm göstermiyoruz" in power
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
    assert routing["version"] == 167
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == {
        "/hesaplama/akvaryum-elektrik-kesintisi-oksijen-filtre-guvenligi/",
        "/hesaplama/akvaryum-hava-motoru-yedek-guc-w-wh-sure-uygunlugu/",
        "/sektor-rehberi/akvaryum-elektrik-kesintisi-tekrar-test-merkezi/",
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

    print("PASS: ALO186 aquarium outage growth v167 contract")


if __name__ == "__main__":
    main()
