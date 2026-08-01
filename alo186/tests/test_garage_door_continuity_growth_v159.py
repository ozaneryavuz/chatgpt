from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "manual": ROOT / "alo186/hesaplama/garaj-kapisi-elektrik-kesintisi-manuel-acma-guvenligi/index.html",
    "power": ROOT / "alo186/hesaplama/garaj-kapisi-motoru-ups-batarya-w-wh-uygunluk/index.html",
    "center": ROOT / "alo186/sektor-rehberi/garaj-kapisi-elektrik-kesintisi-guvenlik-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/159-garage-door-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/garage-door-continuity-growth-v159-2026-08-01.md"


def text(path: Path) -> str:
    assert path.exists(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def executable_scripts(html: str) -> list[str]:
    return re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", html, re.S)


def check_js(html: str, label: str) -> None:
    scripts = executable_scripts(html)
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

    assert routing["version"] == 159
    expected = {
        "/hesaplama/garaj-kapisi-elektrik-kesintisi-manuel-acma-guvenligi/",
        "/hesaplama/garaj-kapisi-motoru-ups-batarya-w-wh-uygunluk/",
        "/sektor-rehberi/garaj-kapisi-elektrik-kesintisi-guvenlik-test-merkezi/",
    }
    assert {route["canonicalPath"] for route in routing["routes"]} == expected

    for name, html in pages.items():
        check_js(html, name)
        scripts = "\n".join(executable_scripts(html))
        assert 'rel="canonical"' in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert "Bağımsız" in html and "değildir" in html
        assert "fiyat" in html.lower() and "stok" in html.lower()
        assert "aggregateRating" not in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "localStorage" not in scripts and "sessionStorage" not in scripts
        assert "@media(max-width:760px)" in html

    manual = pages["manual"]
    power = pages["power"]
    center = pages["center"]

    for phrase in [
        "Acil ayırma kolu kapıyı kaldırmaz",
        "Kısmen açık kapıda acil ayırma yapmayın",
        "Bu sonuç yeni ürün almanızı gerektirmez",
        "Chamberlain Group",
        "CPSC",
        "IEC 60335-2-95:2023",
    ]:
        assert phrase in manual, f"manual phrase missing: {phrase}"
    assert "Amazon satış ortaklığı" not in manual
    assert "tag=alo186rehber-21" not in manual

    for phrase in [
        "VA değerini süre sanmayın",
        "Planlama sürekli güç",
        "Planlama tepe güç",
        "Planlama enerjisi",
        "Mevcut sistem hedef çevrimi gerçek testte karşılıyor — yeni ürün almayın",
        "Amazon satış ortaklığı bağlantısı",
        "sponsored nofollow noopener",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        "tag=alo186rehber-21",
        "IEC 60335-2-95:2023",
    ]:
        assert phrase in power, f"power phrase missing: {phrase}"

    for phrase in [
        "doğrudan affiliate bağlantısı içermez",
        "Kişisel verisiz görev planı",
        "JSON indir",
        "7 günlük olay sonrası ICS",
        "30 günlük güvenlik testi ICS",
        "90 günlük yedekleme testi ICS",
        "application/json",
        "text/calendar",
        "Tekrar ziyaret nedenleri",
    ]:
        assert phrase in center, f"center phrase missing: {phrase}"
    assert "tag=alo186rehber-21" not in center

    for phrase in [
        "Arama niyeti",
        "İçerik boşluğu",
        "Kullanıcı yolculuğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "IEC 60335-2-95:2023",
        "Mevcut sistem yeterli — yeni ürün almayın",
    ]:
        assert phrase in audit, f"audit phrase missing: {phrase}"

    print("ALO186 garage door continuity growth v159 contract: PASS")


if __name__ == "__main__":
    main()
