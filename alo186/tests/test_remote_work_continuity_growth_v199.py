from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/evden-calisma-laptop-monitor-yedek-enerji-sure-hesabi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/evden-calisma-kesinti-yedek-enerji-secici/index.html",
    "center": ROOT / "sektor-rehberi/evden-calisma-kesinti-veri-kaybi-30-90-gun-test-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/199-remote-work-continuity-growth.json"
AUDIT = ROOT / "audits/remote-work-continuity-growth-v199-2026-08-02.md"


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
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")


def test_canonical_schema_and_independence_contract() -> None:
    expected = {
        "calculator": "/hesaplama/evden-calisma-laptop-monitor-yedek-enerji-sure-hesabi/",
        "selector": "/amazon-elektrik-urunleri/evden-calisma-kesinti-yedek-enerji-secici/",
        "center": "/sektor-rehberi/evden-calisma-kesinti-veri-kaybi-30-90-gun-test-merkezi/",
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
    assert "satıcı değildir" in read(ROUTES["selector"])


def test_calculator_prioritizes_minimum_task_and_no_buy() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "Laptop iç bataryasının kullanılabilir enerjisi (Wh)",
        "Harici monitör gücü (W)",
        "Modem + ONT / gerekli ağ yükü (W)",
        "Dış yedek enerji kapasitesi (Wh)",
        "Dönüşüm verimi",
        "Güvenlik rezervi",
        "minimum senaryo",
        "tam senaryo",
        "yeni ürün almayın",
        "Ticari yol kapalı",
        "Microsoft",
        "Eaton",
        "USB-IF",
    ):
        assert token.lower() in html.lower(), token
    assert "dış kaynak süresi = Wh × verim × (1 − rezerv) ÷ dış kaynak yükü" in html
    assert "remote_work_calculated" in html
    assert "remote_work_no_buy" in html


def test_selector_has_three_classes_three_gates_and_fail_closed_exclusions() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 3
    for token in (
        "alo186rehber-21",
        "Amazon Gelir Ortağı açıklaması",
        "USB-C PD laptop yedek batarya sınıfı",
        "Line-interactive masaüstü UPS sınıfı",
        "LiFePO4 taşınabilir güç istasyonu sınıfı",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "Ticari yol kapalı",
        "Lazer yazıcı",
        "prizden prize geri besleme",
        "affiliate_gate_passed",
        "affiliate_product_clicked",
    ):
        assert token.lower() in html.lower(), token
    assert 'href="https://www.amazon.com.tr' not in html


def test_center_exports_without_personal_or_persistent_storage() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for token in (
        "Laptop batarya raporu",
        "çevrimdışı kopyası",
        "geri yükleme denemesi",
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük prova takvimi",
        "BEGIN:VCALENDAR",
        "Kişisel veri ve kalıcı tarayıcı kaydı kullanılmaz.",
        "Hazırlık testi tamam — yeni ürün almayın",
        "NIST SP 1339",
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
    for claim in ("fiyat, stok", "puan", "garanti"):
        assert claim in read(ROUTES["selector"]).lower()


def test_audit_documents_intent_journey_revisit_and_impact() -> None:
    audit = read(AUDIT)
    for heading in (
        "Arama niyeti ve içerik boşluğu",
        "Seçilen üç aksiyon",
        "Kullanıcı yolculuğu",
        "Dönüşüm noktaları",
        "Tekrar ziyaret nedenleri",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Korunan ticari sözleşme",
    ):
        assert heading in audit


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"remote work continuity growth v199: {len(tests)} checks passed")
