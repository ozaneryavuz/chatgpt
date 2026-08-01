from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ROUTES = [
    ROOT / "amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/index.html",
    ROOT / "amazon-elektrik-urunleri/ev-elektrik-olcum-koruma-urunleri/index.html",
    ROOT / "amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/index.html",
]
PORTABLE = ROUTES[-1]


def test_pages_exist_and_have_enough_contextual_products():
    assert all(path.exists() for path in ROUTES)
    texts = [path.read_text(encoding="utf-8") for path in ROUTES]
    # İlk iki merkez statik ürün sınıflarını korur. Taşınabilir merkez v175 ile
    # mağaza URL'sini ancak üçlü kullanıcı onayından sonra JavaScript ile üretir.
    assert sum(text.count('class="card"') for text in texts[:2]) >= 20
    assert all('satış ortaklığı' in text.lower() for text in texts)
    assert all('Bir Amazon Gelir Ortağı olarak' in text or 'Amazon satış ortaklığı' in text for text in texts)
    portable = texts[-1]
    assert 'id="exactProducts"' in portable
    assert 'id="productClasses"' in portable
    assert 'id="gateExisting"' in portable
    assert 'id="gateTechnical"' in portable
    assert 'id="gateAffiliate"' in portable
    assert './exact-products-v175.js' in portable
    assert './app-v175.js' in portable


def test_trust_contract():
    no_buy_phrases = (
        'almayın',
        'yeni ürün almay',
        'yenisini almay',
        'mevcut ürün yeterliyse',
        'mevcut güvenli ürün',
        'satın almama',
        'satın alma yok',
    )
    for path in ROUTES:
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        assert '<link rel="canonical"' in text
        assert 'CollectionPage' in text
        assert 'BreadcrumbList' in text
        assert any(phrase in lower for phrase in no_buy_phrases), path
        assert 'fiyat' in lower and 'stok' in lower and 'garanti' in lower
        assert '"@type":"Product"' not in text
        assert '"@type":"Offer"' not in text
        assert 'aggregateRating' not in text
        assert 'availability' not in text

    portable = PORTABLE.read_text(encoding="utf-8")
    assert 'amazon.com.tr/dp/' not in portable
    assert 'amazon.com.tr/s?' not in portable
    assert 'Mağaza bağlantıları kapalı' in portable


def test_routing_overlay():
    overlay = ROOT / "deployment/routing-overlays/174-affiliate-contextual-product-hubs.json"
    data = json.loads(overlay.read_text(encoding="utf-8"))
    assert data["version"] == 174
    assert len(data["routes"]) == 3
    assert len({route["canonicalPath"] for route in data["routes"]}) == 3
    for route in data["routes"]:
        assert (ROOT.parent / route["source"]).exists()


if __name__ == "__main__":
    test_pages_exist_and_have_enough_contextual_products()
    test_trust_contract()
    test_routing_overlay()
    print("ALO186 affiliate contextual product hubs v174/v175: PASS")
