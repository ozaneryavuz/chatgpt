from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/mobil-hotspot-yedek-internet-veri-gb-batarya-sure-hesabi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/mobil-hotspot-4g-5g-yedek-internet-secici/index.html",
    "center": ROOT / "sektor-rehberi/mobil-internet-failover-30-90-gun-test-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/199-mobile-hotspot-failover-growth.json"
AUDIT = ROOT / "audits/mobile-hotspot-failover-growth-v199-2026-08-02.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_exact_three_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 199
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    assert {route["type"] for route in payload["routes"]} == {"calculator", "commerce-guide", "guide"}
    for route in payload["routes"]:
        assert (ROOT.parent / route["source"]).exists()
        assert route["canonicalPath"].startswith("/") and route["canonicalPath"].endswith("/")


def test_canonical_schema_and_independence_contract() -> None:
    expected = {
        "calculator": "/hesaplama/mobil-hotspot-yedek-internet-veri-gb-batarya-sure-hesabi/",
        "selector": "/amazon-elektrik-urunleri/mobil-hotspot-4g-5g-yedek-internet-secici/",
        "center": "/sektor-rehberi/mobil-internet-failover-30-90-gun-test-merkezi/",
    }
    for key, path in ROUTES.items():
        html = read(path)
        assert f'<link rel="canonical" href="https://alo186.com{expected[key]}">' in html
        assert '"@type":"BreadcrumbList"' in html
        assert '"@type":"FAQPage"' in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "AggregateRating" not in html
        assert "resmî kurum" in html
        assert "mobil operatör" in html
    assert "satıcı değildir" in read(ROUTES["selector"])


def test_calculator_combines_data_power_coverage_and_no_buy() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "İndirme hızı planı (Mbps)",
        "Yükleme hızı planı (Mbps)",
        "Toplantı dışı veri (GB)",
        "Kullanılabilir mobil veri kotası (GB)",
        "Hotspot/router ortalama gücü (W)",
        "Kullanılabilir harici batarya enerjisi (Wh)",
        "gerçek çalışma konumunda",
        "yeni ürün almayın",
        "Ticari yol kapalı",
        "Google Android",
        "Apple",
        "Microsoft Teams",
        "tarifeli bağlantı",
        "mobile_failover_calculated",
        "mobile_failover_no_buy",
    ):
        assert token.lower() in html.lower(), token
    assert "(indirme Mbps + yükleme Mbps) × 3600 × saat ÷ 8 ÷ 1000" in html
    assert "Wh × verim × (1 − rezerv) ÷ W" in html


def test_selector_has_three_classes_three_gates_and_sponsored_link() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 3
    for token in (
        "alo186rehber-21",
        "Amazon Gelir Ortağı açıklaması",
        "Taşınabilir 4G/5G mobil hotspot/router sınıfı",
        "Çift WAN ve failover router sınıfı",
        "USB-C powerbank sınıfı",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "rel=\"sponsored nofollow noopener\"",
        "affiliate_gate_passed",
        "affiliate_product_clicked",
    ):
        assert token.lower() in html.lower(), token
    assert 'href="https://www.amazon.com.tr' not in html
    assert "operatör politikası" in html.lower()
    assert "gerçek çalışma konumunda" in html.lower()


def test_center_exports_without_personal_or_persistent_storage() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for token in (
        "gerçek çalışma konumunda",
        "güçlü ve benzersiz parola",
        "tarifeli bağlantı",
        "veri kullanımı izlendi",
        "failover",
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük failover provası",
        "BEGIN:VCALENDAR",
        "Failover provası tamam — yeni ürün almayın",
    ):
        assert token.lower() in html.lower(), token


def test_no_unverified_commercial_claims_or_pressure_language() -> None:
    joined = "\n".join(read(path) for path in ROUTES.values())
    for phrase in (
        "hemen satın al",
        "stoklar tükenmeden",
        "son fırsat",
        "en ucuz",
        "en iyi fiyat",
        "sınırlı stok",
    ):
        assert phrase not in joined.lower()
    assert not re.search(r"\b\d+[.,]?\d*\s*(?:₺|TL)\b", joined)
    selector = read(ROUTES["selector"]).lower()
    for claim in ("fiyat, stok", "puan", "garanti"):
        assert claim in selector
    assert "hız veya kesintisiz bağlantı garantisi değildir" in selector


def test_audit_documents_required_growth_dimensions() -> None:
    audit = read(AUDIT)
    for heading in (
        "Arama niyeti ve içerik boşluğu",
        "Seçilen üç aksiyon",
        "Kullanıcı yolculuğu",
        "Affiliate ürün kategorileri",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Korunan ticari sözleşme",
    ):
        assert heading in audit
    assert "PR #647" in audit
    assert "içerik çoğalması" in audit


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"mobile hotspot failover growth v199: {len(tests)} checks passed")
