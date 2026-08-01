from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = [
    ROOT / "alo186/amazon-elektrik-urunleri/kesinti-hazirlik-sepeti-olusturucu/index.html",
    ROOT / "alo186/amazon-elektrik-urunleri/ev-ofis-elektrik-kesintisi-urun-secici/index.html",
    ROOT / "alo186/amazon-elektrik-urunleri/yedek-guc-batarya-tekrar-test-merkezi/index.html",
]
OVERLAY = ROOT / "alo186/deployment/routing-overlays/175-affiliate-gap-planner.json"
AUDIT = ROOT / "alo186/audits/affiliate-gap-planner-v175-2026-08-01.md"

CANONICALS = [
    "https://alo186.com/amazon-elektrik-urunleri/kesinti-hazirlik-sepeti-olusturucu/",
    "https://alo186.com/amazon-elektrik-urunleri/ev-ofis-elektrik-kesintisi-urun-secici/",
    "https://alo186.com/amazon-elektrik-urunleri/yedek-guc-batarya-tekrar-test-merkezi/",
]

FORBIDDEN_SCHEMA = (
    '"@type":"Product"',
    '"@type":"Offer"',
    "priceCurrency",
    "aggregateRating",
    'itemprop="price"',
    'itemprop="availability"',
)


def read(path: Path) -> str:
    assert path.exists(), f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


def inline_scripts(html: str) -> list[str]:
    scripts: list[str] = []
    for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S | re.I):
        if "application/ld+json" in attrs.lower():
            continue
        scripts.append(body)
    return scripts


def validate_js(html: str, page: Path) -> None:
    node = shutil.which("node")
    if not node:
        return
    for index, script in enumerate(inline_scripts(html), start=1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
            handle.write(script)
            temp_path = Path(handle.name)
        try:
            result = subprocess.run(
                [node, "--check", str(temp_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            assert result.returncode == 0, f"JS syntax error in {page} script {index}: {result.stderr}"
        finally:
            temp_path.unlink(missing_ok=True)


def test_pages() -> None:
    combined = ""
    for page, canonical in zip(PAGES, CANONICALS, strict=True):
        html = read(page)
        combined += html
        assert f'<link rel="canonical" href="{canonical}">' in html
        assert '"@type":"WebApplication"' in html
        assert '"@type":"FAQPage"' in html
        assert '"@type":"BreadcrumbList"' in html
        assert "Bağımsız" in html
        assert "resmî kurum değildir" in html or "kamu kurumu değildir" in html
        assert "ALO186" in html and "Amazon" in html and "EDAŞ" in html
        assert 'rel="sponsored nofollow noopener"' in html
        assert "alo186rehber-21" in html
        assert "yeni ürün almayın" in html.lower() or "satın almayın" in html.lower()
        assert "@media(max-width:820px)" in html
        for forbidden in FORBIDDEN_SCHEMA:
            assert forbidden not in html, f"Forbidden commerce schema in {page}: {forbidden}"
        validate_js(html, page)

    # 12 + 8 + 10 context-mapped product categories are encoded as q fields.
    assert combined.count("q:'") >= 30
    assert combined.count("tag=alo186rehber-21") >= 3
    assert combined.count("www.amazon.com.tr/s?k=") >= 3
    assert combined.count("Reklam / satış ortaklığı açıklaması") >= 3


def test_fail_closed_and_repeat_visit_contract() -> None:
    basket, office, retest = [read(path) for path in PAGES]

    assert "phase')==='outage'" in basket
    assert "Aktif kesintide mağaza bağlantısı gösterilmez" in basket
    assert "hazard" in basket and "Alışveriş yolu kapalı" in basket
    assert "Yalnız eksik ürünleri göster" in basket
    assert "miss=[...new Set(miss)]" in basket

    assert "Temkinli enerji ihtiyacı" in office
    assert "total*h/0.8*1.2" in office
    assert "tested')==='pass'" in office
    assert "Mevcut sistem hedefi karşılıyor" in office
    assert "USB-C PD" in office and "W/VA" in office

    assert "localStorage" in retest
    assert "30 günlük" in retest and "90 günlük" in retest
    assert "BEGIN:VCALENDAR" in retest
    assert "JSON indir" in retest and "ICS indir" in retest
    assert "Hasarlı veya geri çağrılan ürün üzerinden affiliate bağlantısı gösterilmez" in retest
    assert "status==='recall'" in retest

    for html in (basket, office, retest):
        assert "kesinti-hazirlik-sepeti-olusturucu" in html
        assert "ev-ofis-elektrik-kesintisi-urun-secici" in html
        assert "yedek-guc-batarya-tekrar-test-merkezi" in html


def test_overlay_and_audit() -> None:
    overlay = json.loads(read(OVERLAY))
    assert overlay["version"] == 175
    assert overlay["generatedAt"] == "2026-08-01"
    assert len(overlay["routes"]) == 3
    assert len({route["canonicalPath"] for route in overlay["routes"]}) == 3
    assert all(route.get("sitemap") is True for route in overlay["routes"])
    assert {route["source"] for route in overlay["routes"]} == {
        str(page.relative_to(ROOT)).replace("\\", "/") for page in PAGES
    }

    audit = read(AUDIT)
    for phrase in (
        "Kesinti hazırlık sepeti",
        "Ev-ofis elektrik kesintisi ürün seçici",
        "Yedek güç ve batarya tekrar test merkezi",
        "Ready.gov",
        "USB-IF",
        "IEC 62040-3:2021",
        "CPSC",
        "Doğrulanmamış fiyat",
        "Product, Offer",
        "Tamamlanamayan bağımsız kontroller",
    ):
        assert phrase in audit


if __name__ == "__main__":
    test_pages()
    test_fail_closed_and_repeat_visit_contract()
    test_overlay_and_audit()
    print("affiliate gap planner v175 contract: OK")
