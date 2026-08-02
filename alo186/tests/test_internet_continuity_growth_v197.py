from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/fiber-internet-modem-ont-mini-ups-calisma-suresi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/index.html",
    "center": ROOT / "sektor-rehberi/internet-kesintisi-elektrik-mi-operator-mu-test-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/197-internet-continuity-growth.json"
AUDIT = ROOT / "audits/internet-continuity-growth-v197-2026-08-02.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_exact_three_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 197
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    for route in payload["routes"]:
        assert (ROOT.parent / route["source"]).exists()
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")


def test_canonical_schema_and_independence_contract() -> None:
    expected = {
        "calculator": "/hesaplama/fiber-internet-modem-ont-mini-ups-calisma-suresi/",
        "selector": "/amazon-elektrik-urunleri/modem-ont-mini-ups-yedekleme-secici/",
        "center": "/sektor-rehberi/internet-kesintisi-elektrik-mi-operator-mu-test-merkezi/",
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
        assert "internet servis sağlayıcısı" in html
    assert "satıcı değildir" in read(ROUTES["selector"])


def test_calculator_uses_wh_load_chain_and_fail_closed_rules() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "Ölçülmüş toplam güç",
        "ONT gücü",
        "Modem-router gücü",
        "Yedek enerji kapasitesi (Wh)",
        "Dönüşüm verimi",
        "Güvenlik rezervi",
        "Gerilim, akım, konnektör ve polarite",
        "operatör altyapısı",
        "yeni ürün almayın",
        "Ticari yol kapalı",
        "Openreach",
        "Ofcom",
    ):
        assert token.lower() in html.lower(), token
    assert "tahmini süre = Wh × verim × (1 − rezerv) ÷ toplam W" in html


def test_selector_has_three_classes_three_gates_and_no_static_store_link() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 3
    for token in (
        "alo186rehber-21",
        "sponsored nofollow noopener",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "Ticari yol kapalı",
        "regüle çoklu DC",
        "küçük AC UPS",
        "priz tipi enerji ölçer",
    ):
        assert token.lower() in html.lower(), token
    assert 'href="https://www.amazon.com.tr' not in html


def test_center_classifies_outage_and_exports_without_storage() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for token in (
        "Wi-Fi ağı görünüyor ancak internet",
        "Servis sağlayıcının resmî",
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük prova takvimi",
        "BEGIN:VCALENDAR",
        "Kişisel veri ve kalıcı tarayıcı kaydı kullanılmaz.",
        "Hazırlık testi tamam — yeni ürün almayın",
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
    print(f"internet continuity growth v197: {len(tests)} checks passed")
