from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/elektrik-kesintisi-insulin-ilac-soguk-zincir-karar-destegi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/insulin-ilac-soguk-zincir-hazirlik-secici/index.html",
    "center": ROOT / "sektor-rehberi/insulin-ilac-soguk-zincir-30-90-gun-test-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/196-insulin-medicine-cold-chain-growth.json"
AUDIT = ROOT / "audits/insulin-medicine-cold-chain-growth-v196-2026-08-02.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_exact_three_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 196
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    for route in payload["routes"]:
        assert (ROOT.parent / route["source"]).exists()
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")


def test_canonical_and_schema_contract() -> None:
    expected = {
        "calculator": "/hesaplama/elektrik-kesintisi-insulin-ilac-soguk-zincir-karar-destegi/",
        "selector": "/amazon-elektrik-urunleri/insulin-ilac-soguk-zincir-hazirlik-secici/",
        "center": "/sektor-rehberi/insulin-ilac-soguk-zincir-30-90-gun-test-merkezi/",
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
    assert "sağlık kuruluşu" in read(ROUTES["calculator"])


def test_calculator_is_label_first_and_closes_commerce_on_risk() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "tam ürün etiketi",
        "min–max sıcaklık",
        "2–8°C",
        "15–30°C",
        "28 güne kadar",
        "İnsülin dışındaki ilaçlara insülin aralığı uygulanmaz",
        "Ticari yol kapalı",
        "dozu değiştirmeyin",
        "yeni ürün almayın",
        "CDC",
        "FDA",
    ):
        assert token.lower() in html.lower()
    assert "kullanılabilirliğine, dozuna veya başka ürüne geçişe bu araç karar vermez" in html


def test_selector_has_three_classes_three_gates_and_no_static_store_link() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 3
    for token in (
        "alo186rehber-21",
        "sponsored nofollow noopener",
        "Mevcut hazırlık düzeni yeterli — yeni ürün almayın",
        "Ticari yol kapalı",
        "doğrudan temas",
        "reçeteli ürün",
    ):
        assert token in html
    assert 'href="https://www.amazon.com.tr' not in html


def test_center_exports_json_and_ics_without_personal_storage() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for token in (
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük prova takvimi",
        "BEGIN:VCALENDAR",
        "Kişisel veri ve kalıcı tarayıcı kaydı kullanılmaz.",
        "gerçek ilaç yerine su şişesi",
        "Hazırlık testi tamam — yeni ürün almayın",
    ):
        assert token.lower() in html.lower()


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
    print(f"insulin medicine cold-chain growth v196: {len(tests)} checks passed")
