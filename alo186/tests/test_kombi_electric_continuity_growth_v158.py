from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "restart": ROOT / "alo186/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-yeniden-baslatma/index.html",
    "ups": ROOT / "alo186/hesaplama/kombi-ups-w-va-wh-saf-sinus-uygunluk/index.html",
    "center": ROOT / "alo186/sektor-rehberi/kombi-elektrik-surekliligi-donma-koruma-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/158-kombi-electric-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/kombi-electric-continuity-growth-v158-2026-08-01.md"


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

    assert routing["version"] == 158
    expected = {
        "/hesaplama/kombi-elektrik-kesintisi-sonrasi-guvenli-yeniden-baslatma/",
        "/hesaplama/kombi-ups-w-va-wh-saf-sinus-uygunluk/",
        "/sektor-rehberi/kombi-elektrik-surekliligi-donma-koruma-merkezi/",
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

    restart = pages["restart"]
    ups = pages["ups"]
    center = pages["center"]

    for phrase in [
        "Gaz kokusu varsa elektrik düğmesine, fişe veya kombiye dokunmayın",
        "güvenli bir yerden 187",
        "Art arda resetlemeyi bırakın",
        "Donmuş sistemi çalıştırmaya zorlamayın",
        "Bu sonuç yeni ürün almanızı gerektirmez",
        "EPDK",
        "Aksa Doğalgaz",
        "Bosch Home Comfort",
    ]:
        assert phrase in restart, f"restart phrase missing: {phrase}"
    assert "Amazon satış ortaklığı" not in restart
    assert "tag=alo186rehber-21" not in restart

    for phrase in [
        "VA süre değildir",
        "Planlama sürekli W",
        "Planlama VA",
        "Hedef enerji",
        "Mevcut UPS yeterli — yeni ürün almayın",
        "Prizden prize ve kullanıcı yapımı sabit geri besleme yapılmaz",
        "Kombi model onayı doğrulanmadan UPS önerilmez",
        "Amazon satış ortaklığı bağlantısı",
        "sponsored nofollow noopener",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        "tag=alo186rehber-21",
        "IEC 62040-3:2021",
        "IEC 62040-1",
    ]:
        assert phrase in ups, f"ups phrase missing: {phrase}"

    for phrase in [
        "doğrudan affiliate bağlantısı içermez",
        "Kişisel verisiz görev planı",
        "JSON indir",
        "7 günlük olay sonrası ICS",
        "30 günlük yeni kurulum ICS",
        "90 günlük rutin ICS",
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
        "EPDK",
        "IEC 62040-3:2021",
        "Mevcut UPS yeterli — yeni ürün almayın",
    ]:
        assert phrase in audit, f"audit phrase missing: {phrase}"

    print("ALO186 kombi electric continuity growth v158 contract: PASS")


if __name__ == "__main__":
    main()
