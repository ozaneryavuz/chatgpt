from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = {
    "load": ROOT / "alo186/hesaplama/priz-uzatma-kablosu-yuk-guvenlik/index.html",
    "chain": ROOT / "alo186/hesaplama/akim-korumali-priz-spd-koruma-zinciri/index.html",
    "center": ROOT / "alo186/sektor-rehberi/priz-uzatma-kablosu-koruma-test-merkezi/index.html",
}
ROUTING = ROOT / "alo186/deployment/routing-overlays/152-portable-power-safety-growth.json"
AUDIT = ROOT / "alo186/audits/portable-power-safety-growth-v152-2026-07-31.md"


def text(path: Path) -> str:
    assert path.exists(), f"missing: {path}"
    return path.read_text(encoding="utf-8")


def check_js(html: str, label: str) -> None:
    scripts = re.findall(r"<script(?![^>]*application/ld\+json)[^>]*>(.*?)</script>", html, re.S)
    assert scripts, f"no executable JS in {label}"
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as fh:
        fh.write("\n".join(scripts))
        name = fh.name
    result = subprocess.run(["node", "--check", name], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def main() -> None:
    pages = {name: text(path) for name, path in FILES.items()}
    routing = json.loads(text(ROUTING))
    audit = text(AUDIT)

    assert routing["version"] == 152
    expected = {
        "/hesaplama/priz-uzatma-kablosu-yuk-guvenlik/",
        "/hesaplama/akim-korumali-priz-spd-koruma-zinciri/",
        "/sektor-rehberi/priz-uzatma-kablosu-koruma-test-merkezi/",
    }
    assert {r["canonicalPath"] for r in routing["routes"]} == expected

    for name, html in pages.items():
        check_js(html, name)
        assert 'rel="canonical"' in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert "Bağımsız" in html and "resmî kurum" in html
        assert "fiyat" in html.lower() and "stok" in html.lower()
        assert "aggregateRating" not in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "localStorage" not in html and "sessionStorage" not in html
        assert "e-posta" not in html.lower() or "istenmez" in html.lower()

    load = pages["load"]
    chain = pages["chain"]
    center = pages["center"]

    for phrase in [
        "Zincirleme çoklayıcı kullanmayın",
        "Makarayı tamamen açmadan yük bağlamayın",
        "Mevcut bağlantı bu görev için yeterli görünüyor — yeni ürün almayın",
        "yüksek güçlü yük",
        "230 V için yaklaşık akım",
    ]:
        assert phrase in load

    for phrase in [
        "kaçak akım",
        "Uzun süreli gerilim sapması ayrı koruma görevidir",
        "Mevcut koruma zinciri yeterli — yeni ürün almayın",
        "Pano tipi SPD",
        "IEC 61643-11:2025",
    ]:
        assert phrase in chain

    for page in (load, chain):
        assert "Amazon satış ortaklığı bağlantısı" in page
        assert 'rel="sponsored nofollow noopener"' in page
        assert "need" in page and "spec" in page and "ad" in page
        assert "tag=alo186rehber-21" in page

    assert "doğrudan affiliate bağlantısı içermez" in center
    assert "JSON indir" in center and "Takvime ekle (.ics)" in center
    assert "7 gün" in center and "30 gün" in center and "90 gün" in center
    assert "application/json" in center and "text/calendar" in center

    for phrase in [
        "Arama niyeti",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "IEC 60884-1:2022",
        "IEC 61643-11:2025",
    ]:
        assert phrase in audit

    print("ALO186 portable power safety growth v152 contract: PASS")


if __name__ == "__main__":
    main()
