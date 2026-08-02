from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/guvenlik-kamerasi-nvr-poe-ups-calisma-suresi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/guvenlik-kamerasi-nvr-poe-ups-secici/index.html",
    "center": ROOT / "sektor-rehberi/guvenlik-kamerasi-kesinti-30-90-gun-test-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/200-security-camera-nvr-ups-growth.json"
AUDIT = ROOT / "audits/security-camera-nvr-ups-growth-v200-2026-08-02.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_exact_three_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 200
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    assert {route["type"] for route in payload["routes"]} == {"calculator", "commerce-guide", "guide"}
    for route in payload["routes"]:
        assert (ROOT.parent / route["source"]).exists()
        assert route["canonicalPath"].startswith("/") and route["canonicalPath"].endswith("/")


def test_canonical_schema_and_independence_contract() -> None:
    expected = {
        "calculator": "/hesaplama/guvenlik-kamerasi-nvr-poe-ups-calisma-suresi/",
        "selector": "/amazon-elektrik-urunleri/guvenlik-kamerasi-nvr-poe-ups-secici/",
        "center": "/sektor-rehberi/guvenlik-kamerasi-kesinti-30-90-gun-test-merkezi/",
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
        assert "güvenlik şirketi" in html
    assert "satıcı değildir" in read(ROUTES["selector"])


def test_calculator_covers_full_chain_and_no_buy() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "PoE/IP kamera sayısı",
        "Kamera başına belgeli/ölçülmüş güç (W)",
        "Gece IR / ısıtıcı / hareket rezervi",
        "PoE switch veya PoE NVR taban gücü",
        "NVR / kayıt cihazı ve disk gücü",
        "Router + ONT toplam gücü",
        "UPS'in kullanılabilir batarya enerjisi (Wh)",
        "UPS sürekli çıkış gücü (W)",
        "yeni ürün almayın",
        "Ticari yol kapalı",
        "Cisco",
        "Axis",
        "APC",
        "camera_ups_calculated",
        "camera_ups_no_buy",
    ):
        assert token.lower() in html.lower(), token
    assert "adet × kamera W × (1 + gece rezervi)" in html
    assert "Wh × verim × (1 − batarya rezervi) ÷ toplam W" in html


def test_selector_has_three_classes_three_gates_and_dynamic_sponsored_links() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 3
    for token in (
        "alo186rehber-21",
        "Amazon Gelir Ortağı açıklaması",
        "Model uyumlu AC UPS sınıfı",
        "Belgeli PoE switch sınıfı",
        "Priz tipi enerji ölçer sınıfı",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "sponsored nofollow noopener",
        "affiliate_gate_passed",
        "affiliate_product_clicked",
        "affiliate_no_buy_selected",
    ):
        assert token.lower() in html.lower(), token
    assert 'href="https://www.amazon.com.tr' not in html
    assert "toplam güç bütçesi" in html.lower()
    assert "hukuka aykırı" in html.lower()


def test_center_exports_without_personal_or_persistent_storage() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for token in (
        "mahremiyet",
        "PoE port standardı ve toplam güç bütçesi",
        "Gece modu",
        "örnek kayıt",
        "İnternet olmadan yerel kayıt",
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük tam kesinti provası",
        "BEGIN:VCALENDAR",
        "Kesinti provası tamam — yeni ürün almayın",
    ):
        assert token.lower() in html.lower(), token
    for private_field in ("kamera görüntüsü", "adres", "kullanıcı adı", "parola", "IP adresi", "seri numarası", "konum"):
        assert private_field.lower() in html.lower()


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
    assert "kesintisiz kayıt garantisi" in read(ROUTES["calculator"]).lower()


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
    assert "gelir veya sipariş garantisi vermez" in audit
    assert "mevcut sistem yeterliyse yeni ürün alınmaz" in audit.lower()


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"security camera NVR UPS growth v200: {len(tests)} checks passed")
