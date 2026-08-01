from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "safety": ROOT / "alo186/hesaplama/elektrik-kesintisi-el-feneri-mum-guvenligi/index.html",
    "suitability": ROOT / "alo186/hesaplama/sarjli-fener-acil-aydinlatma-lumen-wh-sure-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/ev-acil-aydinlatma-batarya-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/163-home-emergency-lighting-growth.json"
AUDIT = ROOT / "alo186/audits/home-emergency-lighting-growth-v163-2026-08-01.md"


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

    assert routing["version"] == 163
    expected = {
        "/hesaplama/elektrik-kesintisi-el-feneri-mum-guvenligi/",
        "/hesaplama/sarjli-fener-acil-aydinlatma-lumen-wh-sure-uygunlugu/",
        "/sektor-rehberi/ev-acil-aydinlatma-batarya-test-merkezi/",
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

    safety = pages["safety"]
    suitability = pages["suitability"]
    center = pages["center"]

    for phrase in [
        "Önce <em>ışık ihtiyacını değil tehlikeyi</em>",
        "Acil güvenlik yolu: uzaklaşın ve 112 eşiğini değerlendirin",
        "Mevcut güvenli feneri kullanın — yeni ürün almayın",
        "Mum yerine çalışan pilli veya şarjlı fener kullanın",
        "15 Ocak 2026",
        "USFA",
        "112",
    ]:
        assert phrase in safety, f"safety phrase missing: {phrase}"
    assert "Amazon satış ortaklığı" not in safety
    assert "tag=alo186rehber-21" not in safety

    for phrase in [
        "En yüksek lümeni değil",
        "Mevcut aydınlatma hedefi karşılıyor — yeni ürün almayın",
        "Temkinli planlama süresi = batarya Wh × 0,75 ÷ kullanılan mod W",
        "Amazon satış ortaklığı bağlantısı",
        "sponsored nofollow noopener",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        "tag=alo186rehber-21",
        "IEC 62133-2:2017+A1:2021",
        "Aktif kesintide alışveriş yolu kapalı",
    ]:
        assert phrase in suitability, f"suitability phrase missing: {phrase}"

    for phrase in [
        "doğrudan affiliate bağlantısı içermez",
        "Kişisel verisiz görev planı",
        "JSON indir",
        "7 günlük olay sonrası ICS",
        "30 günlük şarj ve işlev testi ICS",
        "90 günlük gerçek süre testi ICS",
        "application/json",
        "text/calendar",
        "Tekrar ziyaret nedenleri",
        "26 Ağustos 2025",
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
        "15 Ocak 2026",
        "Mevcut sistem yeterli — yeni ürün almayın",
    ]:
        assert phrase in audit, f"audit phrase missing: {phrase}"

    print("ALO186 home emergency lighting growth v163 contract: PASS")


if __name__ == "__main__":
    main()
