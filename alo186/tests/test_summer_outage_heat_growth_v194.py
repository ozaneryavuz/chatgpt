from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/elektrik-kesintisi-sicak-hava-usb-vantilator-calisma-suresi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/sarjli-vantilator-usb-fan-sicak-hava-secici/index.html",
    "center": ROOT / "sektor-rehberi/yaz-elektrik-kesintisi-sicak-hava-30-90-gun-hazirlik-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/194-summer-outage-heat-growth.json"
AUDIT = ROOT / "audits/summer-outage-heat-growth-v194-2026-08-02.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_exact_three_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 194
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    for route in payload["routes"]:
        source = ROOT.parent / route["source"]
        assert source.exists(), source
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")


def test_canonical_and_structured_data_contract() -> None:
    expected = {
        "calculator": "/hesaplama/elektrik-kesintisi-sicak-hava-usb-vantilator-calisma-suresi/",
        "selector": "/amazon-elektrik-urunleri/sarjli-vantilator-usb-fan-sicak-hava-secici/",
        "center": "/sektor-rehberi/yaz-elektrik-kesintisi-sicak-hava-30-90-gun-hazirlik-merkezi/",
    }
    for key, path in ROUTES.items():
        html = read(path)
        assert f'<link rel="canonical" href="https://alo186.com{expected[key]}">' in html
        assert '"@type":"BreadcrumbList"' in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "AggregateRating" not in html
        assert "resmî kurum" in html
    assert "satıcı değildir" in read(ROUTES["selector"])
    assert "sağlık kuruluşu değildir" in read(ROUTES["center"])


def test_calculator_closes_commerce_for_heat_and_health_risk() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "32.2",
        "Ticari yol kapalı — 112",
        "Fan tek başına yeterli kabul edilmemeli",
        "Mevcut düzen hedefi karşılıyor — yeni ürün almayın",
        "batteryWh",
        "fanW",
        "CPSC",
        "T.C. Sağlık Bakanlığı",
        "mAh değeri tek başına yeterli değildir",
    ):
        assert token in html


def test_selector_has_three_need_classes_and_three_gate_checks() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 3
    for required in (
        "alo186rehber-21",
        "sponsored nofollow noopener",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "Ticari yol kapalı — 112",
        "Fan tek çözüm değil — mağaza yolu kapalı",
        "gevşek 18650",
    ):
        assert required in html
    assert 'href="https://www.amazon.com.tr' not in html


def test_center_is_personal_data_free_and_exports_json_ics() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for required in (
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük prova takvimi",
        "BEGIN:VCALENDAR",
        "Kişisel veri ve kalıcı tarayıcı kaydı kullanılmaz.",
        "Hazırlık testi tamam — yeni ürün almayın",
        "Daha serin yere geçiş planı eksik",
    ):
        assert required in html


def test_no_unverified_commercial_claims_or_pressure_language() -> None:
    joined = "\n".join(read(path) for path in ROUTES.values())
    for phrase in (
        "hemen satın al",
        "stoklar tükenmeden",
        "son fırsat",
        "en ucuz",
        "en iyi fiyat",
        "garanti ediyoruz",
    ):
        assert phrase not in joined.lower()
    assert not re.search(r"\b\d+[.,]?\d*\s*(?:₺|TL)\b", joined)


def test_audit_documents_user_and_revenue_impact() -> None:
    audit = read(AUDIT)
    for heading in (
        "Seçilen üç aksiyon",
        "Beklenen kullanıcı faydası",
        "Beklenen gelir etkisi",
        "Korunan ticari sözleşme",
    ):
        assert heading in audit


if __name__ == "__main__":
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"summer outage heat growth v194: {len(tests)} checks passed")
