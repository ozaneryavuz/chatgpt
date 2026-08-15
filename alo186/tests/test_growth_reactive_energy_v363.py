from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARTICLE = ROOT / "haberler/elektrik-faturasinda-reaktif-enduktif-kapasitif-bedel-nedir/index.html"
CALC = ROOT / "hesaplama/reaktif-enerji-oran-hesaplama/index.html"
GUIDE = ROOT / "sektor-rehberi/isletme-reaktif-enerji-kompanzasyon-kontrolu/index.html"
ROUTING = ROOT / "deployment/routing-overlays/growth-reactive-energy-v363.json"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def assert_no_unverified_commerce(html: str) -> None:
    low = html.lower()
    assert "amazon.com.tr" not in low
    assert '"@type":"offer"' not in low
    assert "pricecurrency" not in low
    assert "aggregaterating" not in low
    for phrase in ("fiyat", "stok", "puan", "garanti"):
        assert phrase in low, f"missing explicit commercial boundary: {phrase}"


def test_article_has_current_epdk_boundaries_and_independence():
    html = read(ARTICLE)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/haberler/elektrik-faturasinda-reaktif-enduktif-kapasitif-bedel-nedir/">' in html
    for marker in ("15 kW", "50 kVA", "%33", "%20", "%15", "ilk ihlal"):
        assert marker in html
    assert "epdk.gov.tr" in low
    for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    assert "ALO186 EPDK, EDAŞ, tedarikçi veya OSB değildir" in html
    assert "doğrudan kondansatör" in low
    assert_no_unverified_commerce(html)


def test_calculator_is_private_no_money_and_fail_closed():
    html = read(CALC)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/reaktif-enerji-oran-hesaplama/">' in html
    for schema in ('"@type":"WebApplication"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for forbidden in ("fetch(", "localstorage.", "sessionstorage.", "navigator.geolocation", "amazon.com.tr"):
        assert forbidden not in low
    for marker in ("33", "20", "15", "para tutarı", "tek oran aşımı ürün seçimi değildir", "epdk.gov.tr"):
        assert marker.lower() in low
    assert "ad, adres, abonelik no" in low
    assert_no_unverified_commerce(html)


def test_business_guide_is_professional_only_and_repeat_visit_driven():
    html = read(GUIDE)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/sektor-rehberi/isletme-reaktif-enerji-kompanzasyon-kontrolu/">' in html
    for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for marker in ("professional-only", "30 gün", "90 gün", "365 gün", "tek bir reaktif ihlal yeni ekipman satın alma gerekçesi değildir"):
        assert marker.lower() in low
    for component in ("kondansatör", "kontaktör", "reaktif güç kontrol rölesi", "harmonik filtre", "akım trafosu"):
        assert component in low
    assert "merchant bağlantısı yoktur" in low
    assert_no_unverified_commerce(html)


def test_routing_overlay_v363_owns_three_routes():
    text = read(ROUTING)
    assert '"version": 363' in text
    for route in (
        "/haberler/elektrik-faturasinda-reaktif-enduktif-kapasitif-bedel-nedir/",
        "/hesaplama/reaktif-enerji-oran-hesaplama/",
        "/sektor-rehberi/isletme-reaktif-enerji-kompanzasyon-kontrolu/",
    ):
        assert route in text


if __name__ == "__main__":
    test_article_has_current_epdk_boundaries_and_independence()
    test_calculator_is_private_no_money_and_fail_closed()
    test_business_guide_is_professional_only_and_repeat_visit_driven()
    test_routing_overlay_v363_owns_three_routes()
    print({"ok": True, "version": 363, "merchantLinks": 0, "newAffiliateClasses": 0})
