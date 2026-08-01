from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "access": ROOT / "alo186/hesaplama/akilli-kilit-elektrik-kesintisi-pil-bitti-erisim-guvenligi/index.html",
    "suitability": ROOT / "alo186/hesaplama/akilli-kilit-pil-yedek-guc-siber-guvenlik-uygunlugu/index.html",
    "center": ROOT / "alo186/sektor-rehberi/akilli-kilit-erisim-surekliligi-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/161-smart-lock-continuity-growth.json"
AUDIT = ROOT / "alo186/audits/smart-lock-continuity-growth-v161-2026-08-01.md"


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

    assert routing["version"] == 161
    expected = {
        "/hesaplama/akilli-kilit-elektrik-kesintisi-pil-bitti-erisim-guvenligi/",
        "/hesaplama/akilli-kilit-pil-yedek-guc-siber-guvenlik-uygunlugu/",
        "/sektor-rehberi/akilli-kilit-erisim-surekliligi-test-merkezi/",
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

    access = pages["access"]
    suitability = pages["suitability"]
    center = pages["center"]

    for phrase in [
        "Elektrik kesintisini, <em>pil bitmesini ve internet kopmasını</em>",
        "Kapıyı veya kilidi zorlamayın",
        "Yerel kilit çalışıyor — yeni ürün almayın",
        "Yalnız üreticinin acil güç yöntemini kullanın",
        "9 V pil",
        "112",
    ]:
        assert phrase in access, f"access phrase missing: {phrase}"
    assert "Amazon satış ortaklığı" not in access
    assert "tag=alo186rehber-21" not in access

    for phrase in [
        "Pil boyutu tek başına uyumluluk kanıtı değildir",
        "Mevcut pil seti ve erişim planı yeterli — yeni ürün almayın",
        "ETSI EN 303 645",
        "NISTIR 8259 Rev.1",
        "Amazon satış ortaklığı bağlantısı",
        "sponsored nofollow noopener",
        "needConfirm",
        "specConfirm",
        "adConfirm",
        "tag=alo186rehber-21",
        "AA alkalin",
        "CR123A lityum",
    ]:
        assert phrase in suitability, f"suitability phrase missing: {phrase}"

    for phrase in [
        "doğrudan affiliate bağlantısı içermez",
        "Kişisel verisiz görev planı",
        "JSON indir",
        "7 günlük olay sonrası ICS",
        "30 günlük yeni kurulum ICS",
        "90 günlük rutin test ICS",
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
        "ETSI EN 303 645 V3.1.3",
        "Mevcut sistem yeterli — yeni ürün almayın",
    ]:
        assert phrase in audit, f"audit phrase missing: {phrase}"

    print("ALO186 smart lock continuity growth v161 contract: PASS")


if __name__ == "__main__":
    main()
