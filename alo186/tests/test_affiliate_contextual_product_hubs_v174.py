from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
ROUTES = [
    ROOT / "amazon-elektrik-urunleri/elektrik-kesintisi-hazirlik-urunleri/index.html",
    ROOT / "amazon-elektrik-urunleri/ev-elektrik-olcum-koruma-urunleri/index.html",
    ROOT / "amazon-elektrik-urunleri/tasinabilir-enerji-sarj-urunleri/index.html",
]


def test_pages_exist_and_have_enough_contextual_products():
    assert all(path.exists() for path in ROUTES)
    texts = [path.read_text(encoding="utf-8") for path in ROUTES]
    assert sum(text.count('class="card"') for text in texts) >= 30
    assert all('Amazon satış ortaklığı' in text for text in texts)
    assert all('rel="sponsored nofollow noopener"' in text for text in texts)
    assert all('tag=alo186rehber-21' in text for text in texts)


def test_trust_contract():
    for path in ROUTES:
        text = path.read_text(encoding="utf-8")
        assert '<link rel="canonical"' in text
        assert 'CollectionPage' in text
        assert 'BreadcrumbList' in text
        assert 'yeni ürün almayın' in text.lower() or 'yenisini almayın' in text.lower()
        assert 'fiyat' in text.lower() and 'stok' in text.lower() and 'garanti' in text.lower()
        assert '"@type":"Product"' not in text
        assert '"@type":"Offer"' not in text
        assert 'aggregateRating' not in text
        assert 'availability' not in text


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
    print("ALO186 affiliate contextual product hubs v174: PASS")
