from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
CALC = ROOT / "alo186/hesaplama/alarm-paneli-aku-bekleme-suresi/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/index.html"
TEST = ROOT / "alo186/sektor-rehberi/alarm-sistemi-elektrik-kesintisi-30-90-gun-test-merkezi/index.html"
ROUTING = ROOT / "alo186/deployment/routing-overlays/206-alarm-panel-battery-growth.json"

PAGES = {
    CALC: "https://alo186.com/hesaplama/alarm-paneli-aku-bekleme-suresi/",
    SELECTOR: "https://alo186.com/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/",
    TEST: "https://alo186.com/sektor-rehberi/alarm-sistemi-elektrik-kesintisi-30-90-gun-test-merkezi/",
}


def read(path: Path) -> str:
    assert path.exists(), path
    return path.read_text(encoding="utf-8")


def test_common_contract():
    for path, canonical in PAGES.items():
        html = read(path)
        assert f'<link rel="canonical" href="{canonical}">' in html
        assert 'name="viewport"' in html
        assert "FAQPage" in html and "BreadcrumbList" in html
        assert "ALO186" in html
        assert "resmî kurum" in html or "kamu kurumu" in html
        assert '"@type":"Product"' not in html
        assert '"@type":"Offer"' not in html
        assert "AggregateRating" not in html


def test_calculator_fail_closed():
    html = read(CALC)
    for token in ["gerekli Ah", "bekleme", "alarm", "modelVerified", "hazard", "Profesyonel kapsam", "yeni ürün almayın"]:
        assert token in html
    assert "/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/" in html
    assert "/sektor-rehberi/alarm-sistemi-elektrik-kesintisi-30-90-gun-test-merkezi/" in html


def test_selector_commerce_contract():
    html = read(SELECTOR)
    for token in ["alo186rehber-21", "sponsored nofollow noopener", "existingGap", "compatibility", "affiliate", "hazard", "professional", "yeni ürün almayın"]:
        assert token in html
    assert html.index("Amazon satış ortaklığı") < html.index("amazon.com.tr")
    assert '<a href="https://www.amazon.com.tr' not in html
    for claim in ["Fiyat", "stok", "puan", "garanti"]:
        assert claim in html
    assert "affiliate yolu kapalı" in html


def test_test_center_privacy_and_repeat_visit():
    html = read(TEST)
    for token in ["JSON indir", "30 günlük ICS", "90 günlük ICS", "Adres, parola", "personalData:false", "localStorage kullanılmaz", "resmî bakım standardı değildir", "yeni ürün almayın"]:
        assert token in html
    assert "/hesaplama/alarm-paneli-aku-bekleme-suresi/" in html
    assert "/amazon-elektrik-urunleri/alarm-paneli-aku-uygunluk-secici/" in html


def test_routing():
    data = json.loads(read(ROUTING))
    assert data["version"] == 206
    assert len(data["routes"]) == 3
    paths = {route["canonicalPath"] for route in data["routes"]}
    assert paths == {url.removeprefix("https://alo186.com") for url in PAGES.values()}
    assert data["trust"]["affiliateDisclosureBeforeLink"] is True
    assert data["trust"]["professionalLifeSafetyCommerceClosed"] is True
    assert data["trust"]["noBuyWhenAdequate"] is True


if __name__ == "__main__":
    test_common_contract()
    test_calculator_fail_closed()
    test_selector_commerce_contract()
    test_test_center_privacy_and_repeat_visit()
    test_routing()
    print("alarm panel battery growth v206: all checks passed")
