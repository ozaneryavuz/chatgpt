from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "safety": ROOT / "alo186/hesaplama/guvenlik-kamerasi-elektrik-internet-kesintisi-kayit-guvenligi/index.html",
    "suitability": ROOT / "alo186/hesaplama/guvenlik-kamerasi-nvr-poe-router-ups-w-va-wh-sure-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/ev-guvenlik-kamerasi-elektrik-internet-kesintisi-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/165-security-camera-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/security-camera-continuity-growth-v165-2026-08-01.md"


def read(path: Path) -> str:
    assert path.is_file(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def check_js(path: Path, html: str) -> None:
    scripts = re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", html, flags=re.I | re.S)
    assert scripts, f"no executable JS: {path}"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write("\n".join(scripts))
        temp = Path(handle.name)
    try:
        result = subprocess.run(["node", "--check", str(temp)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    finally:
        temp.unlink(missing_ok=True)


def main() -> None:
    pages = {name: read(path) for name, path in PAGES.items()}
    expected = {
        "safety": "https://alo186.com/hesaplama/guvenlik-kamerasi-elektrik-internet-kesintisi-kayit-guvenligi/",
        "suitability": "https://alo186.com/hesaplama/guvenlik-kamerasi-nvr-poe-router-ups-w-va-wh-sure-uygunlugu/",
        "center": "https://alo186.com/sektor-rehberi/ev-guvenlik-kamerasi-elektrik-internet-kesintisi-test-merkezi/",
    }

    for name, html in pages.items():
        assert f'<link rel="canonical" href="{expected[name]}">' in html
        assert "Bağımsız" in html and "değildir" in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert '"availability"' not in html
        assert '"aggregateRating"' not in html
        scripts = "\n".join(re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", html, flags=re.I | re.S))
        assert "localStorage" not in scripts and "sessionStorage" not in scripts
        assert "@media(max-width:760px)" in html
        check_js(PAGES[name], html)

    safety = pages["safety"]
    assert "Bu sayfada affiliate bağlantısı yoktur" in safety
    assert "amazon.com.tr" not in safety
    for phrase in (
        "Kamera çevrimdışı",
        "Yerel kayıt internet olmadan doğrulandı",
        "Yalnız bulut kaydı internet bağımlıdır",
        "Mahremiyet sınırı tamamlanmadan sistemi büyütmeyin",
        "27 Temmuz 2026",
        "NIST SP 1800",
    ):
        assert phrase in safety, phrase

    suitability = pages["suitability"]
    for phrase in (
        "Mevcut sistem hedefi karşılıyor — yeni ürün almayın",
        "Planlama sürekli W = toplam W × 1,25",
        "Planlama VA = toplam W ÷ güç faktörü × 1,25",
        "Gerekli enerji Wh = toplam W × hedef saat ÷ 0,80 × 1,20",
        "Reklam / satış ortaklığı açıklaması",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        'rel="sponsored nofollow noopener"',
        "tag=alo186rehber-21",
        "IEC 62040",
    ):
        assert phrase in suitability, phrase
    assert "amazon.com.tr" in suitability
    assert "fiyat, stok, puan" in suitability.lower()

    center = pages["center"]
    for phrase in (
        "doğrudan affiliate bağlantısı içermez",
        "Kişisel verisiz görev planı",
        "JSON görev planı indir",
        "7 günlük olay kontrolü",
        "30 günlük işlev testi",
        "90 günlük tam kesinti testi",
        "application/json",
        "text/calendar",
        "Tekrar ziyaret nedenleri",
        "27 Temmuz 2026",
    ):
        assert phrase in center, phrase
    assert "amazon.com.tr" not in center

    routing = json.loads(read(ROUTING))
    assert routing["version"] == 165
    assert routing["generatedAt"] == "2026-08-01"
    assert len(routing["routes"]) == 3
    assert {route["canonicalPath"] for route in routing["routes"]} == {
        "/hesaplama/guvenlik-kamerasi-elektrik-internet-kesintisi-kayit-guvenligi/",
        "/hesaplama/guvenlik-kamerasi-nvr-poe-router-ups-w-va-wh-sure-uygunlugu/",
        "/sektor-rehberi/ev-guvenlik-kamerasi-elektrik-internet-kesintisi-test-merkezi/",
    }
    for route in routing["routes"]:
        assert (ROOT / route["source"]).exists()

    audit = read(AUDIT)
    for phrase in (
        "Arama niyetleri",
        "İçerik boşluğu",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Affiliate kategorileri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Doğrulanmamış fiyat, stok, puan",
        "Mevcut sistem hedefi karşılıyor — yeni ürün almayın",
    ):
        assert phrase in audit, phrase

    print("PASS: ALO186 security camera continuity growth v165 contract")


if __name__ == "__main__":
    main()
