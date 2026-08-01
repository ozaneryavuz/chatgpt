from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = {
    "/hesaplama/elektrik-kesintisinde-buzdolabi-dondurucu-gida-sicaklik-karari/": ROOT
    / "alo186/hesaplama/elektrik-kesintisinde-buzdolabi-dondurucu-gida-sicaklik-karari/index.html",
    "/hesaplama/prizden-cihaz-elektrik-tuketimi-watt-kwh-maliyet-olcumu/": ROOT
    / "alo186/hesaplama/prizden-cihaz-elektrik-tuketimi-watt-kwh-maliyet-olcumu/index.html",
    "/sektor-rehberi/ev-enerji-soguk-zincir-30-gun-takip-merkezi/": ROOT
    / "alo186/sektor-rehberi/ev-enerji-soguk-zincir-30-gun-takip-merkezi/index.html",
}
OVERLAY = ROOT / "alo186/deployment/routing-overlays/179-cold-chain-energy-growth.json"
AUDIT = ROOT / "alo186/audits/cold-chain-energy-growth-v179-2026-08-01.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_and_unique_routes() -> None:
    data = json.loads(read(OVERLAY))
    assert data["version"] == 179
    routes = data["routes"]
    assert len(routes) == 3
    canonical_paths = [route["canonicalPath"] for route in routes]
    assert len(canonical_paths) == len(set(canonical_paths))
    assert set(canonical_paths) == set(PAGES)
    for route in routes:
        source = ROOT / route["source"]
        assert source.exists()


def test_canonical_schema_and_mobile_contract() -> None:
    for route, path in PAGES.items():
        html = read(path)
        assert f'<link rel="canonical" href="https://alo186.com{route}">' in html
        assert 'name="viewport"' in html
        assert "FAQPage" in html
        assert "BreadcrumbList" in html
        assert "WebApplication" in html
        assert "@media(max-width:" in html
        assert "ALO186" in html
        assert "kamu kurumu" in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "aggregateRating" not in html
        assert "availability" not in html


def test_affiliate_links_are_disclosed_and_safe() -> None:
    affiliate_routes = list(PAGES)[:2]
    total = 0
    for route in affiliate_routes:
        html = read(PAGES[route])
        assert "Reklam / satış ortaklığı açıklaması" in html
        assert "mevcut" in html.lower()
        links = re.findall(
            r'<a[^>]+href="([^"]*amazon\.com\.tr[^"]*)"[^>]+rel="([^"]+)"[^>]*>',
            html,
            flags=re.I,
        )
        assert links, f"no affiliate link in {PAGES[route]}"
        total += len(links)
        for href, rel_value in links:
            assert "alo186rehber-21" in href
            rel = set(rel_value.split())
            assert {"sponsored", "nofollow", "noopener"}.issubset(rel)
        assert html.count("type=\"checkbox\"") >= 3
    assert total >= 5


def test_explicit_no_purchase_and_fail_closed_language() -> None:
    cold = read(PAGES["/hesaplama/elektrik-kesintisinde-buzdolabi-dondurucu-gida-sicaklik-karari/"])
    assert "Gıda güvenliği alışverişten önce gelir" in cold
    assert "Aktif olayda affiliate bağlantısı gösterilmez" in cold
    assert "Şüpheli gıdayı tatmayın" in cold
    assert "4,4 °C" in cold
    assert "Kuru buz bu tüketici affiliate akışına alınmaz" in cold

    energy = read(PAGES["/hesaplama/prizden-cihaz-elektrik-tuketimi-watt-kwh-maliyet-olcumu/"])
    assert "Mevcut ölçer yeterli görünüyor — yeni ürün almayın" in energy
    assert "Sabit bağlı" in energy
    assert "Hasarlı veya ısınan priz" in energy
    assert "Tüketici priz ölçeri uygun yol değil" in energy
    assert "fatura toplamı veya tasarruf garantisi değildir" in energy


def test_repeat_visit_and_exports() -> None:
    tracker = read(PAGES["/sektor-rehberi/ev-enerji-soguk-zincir-30-gun-takip-merkezi/"])
    for token in ["localStorage", "JSON indir", "CSV indir", "7/30/90 gün ICS", "Tüm yerel kayıtları sil"]:
        assert token in tracker
    assert "ALO186 sunucusuna gönderilmez" in tracker
    assert "/iletisim/" in tracker
    assert not re.findall(r'href="[^"]*amazon[^"]*"', tracker, flags=re.I)


def test_no_unverified_commercial_data() -> None:
    currency_pattern = re.compile(r"(?:₺|€|£)|\b\d+[.,]?\d*\s*(?:TL|USD|EUR)\b", re.I)
    for path in PAGES.values():
        html = read(path)
        visible_guard = html.replace("TL/kWh", "").replace(" TL'", "")
        assert not currency_pattern.search(visible_guard), f"currency claim in {path}"
        assert "yıldız" not in html.lower()
        assert "stokta" not in html.lower()
        assert "ücretsiz kargo" not in html.lower()


def test_audit_covers_growth_dimensions() -> None:
    audit = read(AUDIT)
    for heading in [
        "Arama niyeti ve içerik boşluğu",
        "Kullanıcı yolculuğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir / lead etkisi",
        "Doğrulanan kaynaklar",
        "Tamamlanamayan bağımsız kontroller",
    ]:
        assert heading in audit


if __name__ == "__main__":
    tests = [value for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"v179 contract passed: {len(tests)} tests")
