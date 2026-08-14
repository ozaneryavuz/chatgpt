from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "haberler/klima-ne-kadar-elektrik-harcar-kwh-hesaplama/index.html"
CALC = ROOT / "hesaplama/cihaz-elektrik-tuketimi-kwh-hesaplama/index.html"
HUB = ROOT / "fatura-ve-sayac-kontrol-merkezi/index.html"
ROUTES = ROOT / "deployment/routing-overlays/device-energy-growth-v357.json"


def main() -> None:
    article = ARTICLE.read_text(encoding="utf-8")
    calc = CALC.read_text(encoding="utf-8")
    hub = HUB.read_text(encoding="utf-8")
    routes = ROUTES.read_text(encoding="utf-8")

    assert "https://alo186.com/haberler/klima-ne-kadar-elektrik-harcar-kwh-hesaplama/" in article
    assert '"@type":"Article"' in article
    assert '"@type":"FAQPage"' in article
    assert "BTU/h soğutma kapasitesidir; doğrudan elektrik tüketimi değildir" in article
    assert "yeni ürün almayın" in article
    assert "amazon.com.tr" not in article.lower()
    assert '"@type":"Product"' not in article
    assert '"@type":"Offer"' not in article

    assert "https://alo186.com/hesaplama/cihaz-elektrik-tuketimi-kwh-hesaplama/" in calc
    assert '"@type":"WebApplication"' in calc
    assert "ALO186 tarife sağlamaz" in calc
    assert "yeni ürün almayın" in calc
    assert "localStorage" not in calc
    assert "sessionStorage" not in calc
    assert "geolocation" not in calc
    assert "fetch(" not in calc
    assert "amazon.com.tr" not in calc.lower()
    assert '"@type":"Offer"' not in calc

    assert "/hesaplama/cihaz-elektrik-tuketimi-kwh-hesaplama/" in hub
    assert "/haberler/klima-ne-kadar-elektrik-harcar-kwh-hesaplama/" in hub
    assert "Amazon Türkiye satış ortaklığı" in hub
    assert "doğrulanmamış fiyat, stok, puan veya garanti" in hub

    assert '"version": 358' in routes
    assert "klima-ne-kadar-elektrik-harcar-kwh-hesaplama" in routes
    assert "cihaz-elektrik-tuketimi-kwh-hesaplama" in routes
    print({"ok": True, "version": 358, "newMerchantLinks": 0, "newAffiliateClasses": 0})


if __name__ == "__main__":
    main()
