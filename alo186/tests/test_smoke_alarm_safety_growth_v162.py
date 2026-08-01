from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "event": ROOT / "alo186/hesaplama/duman-alarmi-otuyor-dusuk-pil-yanlis-alarm-acil-durum/index.html",
    "suitability": ROOT / "alo186/hesaplama/duman-alarmi-ihtiyac-yerlesim-batarya-baglanti-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/duman-alarmi-yangin-kacis-plani-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/162-smoke-alarm-safety-growth.json"
AUDIT = ROOT / "alo186/audits/smoke-alarm-safety-growth-v162-2026-08-01.md"


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

    assert routing["version"] == 162
    expected = {
        "/hesaplama/duman-alarmi-otuyor-dusuk-pil-yanlis-alarm-acil-durum/",
        "/hesaplama/duman-alarmi-ihtiyac-yerlesim-batarya-baglanti-uygunlugu/",
        "/sektor-rehberi/duman-alarmi-yangin-kacis-plani-test-merkezi/",
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

    event = pages["event"]
    suitability = pages["suitability"]
    center = pages["center"]

    for phrase in [
        "Önce <em>gerçek yangın riskini</em>",
        "Acil durum yolu: tahliye ve 112",
        "Alarm şu anda testte çalışıyor — yeni ürün almayın",
        "pili çıkarmayın",
        "Sürekli alarm",
        "aralıklı bip",
        "112",
    ]:
        assert phrase in event, f"event phrase missing: {phrase}"
    assert "Amazon satış ortaklığı" not in event
    assert "tag=alo186rehber-21" not in event

    for phrase in [
        "Mevcut duman alarmı kapsamı yeterli — yeni ürün almayın",
        "Her yatak odasında alarm",
        "Şebeke bağlantılı sistem: yetkili elektrikçi/yangın sistemi yolu",
        "Amazon satış ortaklığı bağlantısı",
        "sponsored nofollow noopener",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        "tag=alo186rehber-21",
        "USFA’nın 1 Mayıs 2026",
        "CPSC’nin 23 Ocak 2026",
    ]:
        assert phrase in suitability, f"suitability phrase missing: {phrase}"

    for phrase in [
        "doğrudan affiliate bağlantısı içermez",
        "Kişisel verisiz görev planı",
        "JSON indir",
        "7 günlük olay sonrası ICS",
        "30 günlük aylık alarm testi ICS",
        "90 günlük kaçış planı testi ICS",
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
        "1 Mayıs 2026",
        "Mevcut sistem yeterli — yeni ürün almayın",
    ]:
        assert phrase in audit, f"audit phrase missing: {phrase}"

    print("ALO186 smoke alarm safety growth v162 contract: PASS")


if __name__ == "__main__":
    main()
