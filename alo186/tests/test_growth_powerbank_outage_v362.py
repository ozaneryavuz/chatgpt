from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTICLE = ROOT / "haberler/powerbank-ucaga-alinir-mi-2026-mah-wh/index.html"
POWER = ROOT / "hesaplama/powerbank-mah-wh-hesaplama/index.html"
OUTAGE = ROOT / "hesaplama/elektrik-kesintisi-sure-gunlugu/index.html"
ROUTING = ROOT / "deployment/routing-overlays/growth-powerbank-outage-v362.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def assert_no_unverified_commerce(html: str) -> None:
    low = html.lower()
    assert "pricecurrency" not in low
    assert '"@type":"offer"' not in low
    assert "aggregaterating" not in low
    assert "amazon.com.tr" not in low
    for phrase in ("fiyat", "stok", "puan", "garanti"):
        assert phrase in low, f"missing explicit commercial-boundary phrase: {phrase}"


def test_powerbank_article_has_current_rules_and_no_direct_merchant_link():
    html = read(ARTICLE)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/haberler/powerbank-ucaga-alinir-mi-2026-mah-wh/">' in html
    for marker in ("24 Nisan 2026", "27 Mart 2026", "UOD-2026-01", "100 Wh", "160 Wh"):
        assert marker in html
    for source in ("web.shgm.gov.tr", "icao.int", "iata.org", "faa.gov"):
        assert source in low
    for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    assert "ALO186 havayolu, SHGM veya resmî kurum değildir" in html
    assert "yeni ürün almayın" in low
    assert_no_unverified_commerce(html)


def test_powerbank_calculator_is_local_no_default_efficiency_and_fail_closed():
    html = read(POWER)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/powerbank-mah-wh-hesaplama/">' in html
    for schema in ('"@type":"WebApplication"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for forbidden in ("fetch(", "localstorage.", "sessionstorage.", "navigator.geolocation"):
        assert forbidden not in low
    assert "varsayılan verim yüzdesi uydurmaz" in low
    assert "yeni ürün almayın" in low
    assert "/amazon-elektrik-urunleri/telefon-powerbank-kablo-secimi/" in html
    assert "affiliate açıklaması" in low
    assert_no_unverified_commerce(html)


def test_outage_journal_is_private_non_commercial_and_not_an_official_claim_system():
    html = read(OUTAGE)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/elektrik-kesintisi-sure-gunlugu/">' in html
    for schema in ('"@type":"WebApplication"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for forbidden in ("fetch(", "localstorage.", "sessionstorage.", "navigator.geolocation", "amazon.com.tr"):
        assert forbidden not in low
    for marker in ("arıza ihbarı almaz", "dağıtım şirketine veri göndermez", "CSV", "112", "186"):
        assert marker.lower() in low
    assert "affiliate bağlantısı içermez" in low
    assert "şebeke kalitesi ihlali" in low
    assert "açık adres" in low and "abonelik numarası" in low


def test_routing_overlay_v362_owns_three_new_routes():
    text = read(ROUTING)
    assert '"version": 362' in text
    for route in (
        "/haberler/powerbank-ucaga-alinir-mi-2026-mah-wh/",
        "/hesaplama/powerbank-mah-wh-hesaplama/",
        "/hesaplama/elektrik-kesintisi-sure-gunlugu/",
    ):
        assert route in text


if __name__ == "__main__":
    test_powerbank_article_has_current_rules_and_no_direct_merchant_link()
    test_powerbank_calculator_is_local_no_default_efficiency_and_fail_closed()
    test_outage_journal_is_private_non_commercial_and_not_an_official_claim_system()
    test_routing_overlay_v362_owns_three_new_routes()
    print({"ok": True, "version": 362, "merchantLinks": 0, "newAffiliateClasses": 0})
