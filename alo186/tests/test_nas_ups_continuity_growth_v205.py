from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "calculator": ROOT / "hesaplama/nas-ups-guvenli-kapatma-calisma-suresi/index.html",
    "selector": ROOT / "amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/index.html",
    "center": ROOT / "sektor-rehberi/nas-elektrik-kesintisi-30-90-gun-test-merkezi/index.html",
}
OVERLAY = ROOT / "deployment/routing-overlays/205-nas-ups-continuity-growth.json"
AUDIT = ROOT / "audits/nas-ups-continuity-growth-v205-2026-08-02.md"


def read(path: Path) -> str:
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def test_overlay_registers_exact_three_routes() -> None:
    payload = json.loads(read(OVERLAY))
    assert payload["version"] == 205
    assert payload["generatedAt"] == "2026-08-02"
    assert len(payload["routes"]) == 3
    assert {route["type"] for route in payload["routes"]} == {"calculator", "commerce-guide", "guide"}
    for route in payload["routes"]:
        assert (ROOT.parent / route["source"]).exists()
        assert route["canonicalPath"].startswith("/") and route["canonicalPath"].endswith("/")


def test_canonical_schema_and_independence_contract() -> None:
    expected = {
        "calculator": "/hesaplama/nas-ups-guvenli-kapatma-calisma-suresi/",
        "selector": "/amazon-elektrik-urunleri/nas-ups-usb-snmp-uygunluk-secici/",
        "center": "/sektor-rehberi/nas-elektrik-kesintisi-30-90-gun-test-merkezi/",
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
        assert "EDAŞ" in html
    assert "satıcı değildir" in read(ROUTES["selector"])


def test_calculator_prioritizes_safe_shutdown_over_runtime() -> None:
    html = read(ROUTES["calculator"])
    for token in (
        "NAS ve disklerin gerçek/belgeli gücü",
        "Kesintiden sonra kapanma komutu süresi",
        "Kapanma işlemi ve ağ bildirimi rezervi",
        "USB, SNMP veya ağ UPS yöntemi",
        "tahmini süre = Wh × verim",
        "Mevcut düzen hedefi karşılıyor — yeni ürün almayın",
        "Ticari yol kapalıdır",
        "Synology — DSM UPS desteği",
        "QNAP — Ani kapanmayı önleme",
        "APC — UPS seçimi",
        "nas_runtime_calculated",
    ):
        assert token.lower() in html.lower(), token
    assert "veri kaybını" in html.lower()
    assert "garanti etmez" in html.lower()


def test_selector_has_three_classes_three_gates_and_dynamic_links() -> None:
    html = read(ROUTES["selector"])
    assert len(re.findall(r'name="need" value="', html)) == 3
    assert len(re.findall(r'class="gatebox"', html)) == 4
    for token in (
        "Reklam · Amazon satış ortaklığı",
        "USB iletişimli UPS sınıfı",
        "SNMP veya ağ UPS yönetimi sınıfı",
        "priz tipi enerji ölçer sınıfı",
        "Mevcut düzen yeterli — yeni ürün almayın",
        "alo186rehber-21",
        "sponsored nofollow noopener",
        "affiliate_gate_viewed",
        "affiliate_gate_passed",
        "affiliate_product_clicked",
        "affiliate_no_buy_selected",
        "Profesyonel/kritik sistem için affiliate yol kapalı",
    ):
        assert token.lower() in html.lower(), token
    assert 'href="https://www.amazon.com.tr' not in html
    assert "tam model doğrulanmadan mağaza yolu açılmaz" in html.lower()


def test_center_exports_without_personal_or_persistent_storage() -> None:
    html = read(ROUTES["center"])
    for forbidden in ("localStorage", "sessionStorage", "XMLHttpRequest", "fetch("):
        assert forbidden not in html
    for token in (
        "Tam cihaz modeli ve güncel belge",
        "Yedek ve geri yükleme kanıtı",
        "Kesinti bildirimi",
        "Güvenli kapatma",
        "Depolama sağlığı",
        "JSON indir",
        "30 günlük kontrol takvimi",
        "90 günlük tam prova takvimi",
        "BEGIN:VCALENDAR",
        "Hazırlık provası tamam — yeni ürün almayın",
        "Veriler sunucuya gönderilmez",
        "containsPersonalData:false",
        "containsCredentials:false",
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
    assert "ürünler komisyon oranına göre sıralanmaz" in selector


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
        "Doğrulanan kaynaklar",
        "Korunan ticari sözleşme",
    ):
        assert heading in audit
    assert "gelir veya sipariş garantisi vermez" in audit
    assert "mevcut sistem yeterliyse yeni ürün alınmaz" in audit.lower()


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print(f"nas ups continuity growth v205: {len(tests)} checks passed")
