from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "kesinti-hazirlik-atolyesi" / "index.html"
APP = ROOT / "kesinti-hazirlik-atolyesi" / "app.js"
STYLE = ROOT / "kesinti-hazirlik-atolyesi" / "styles.css"
ROUTING = ROOT / "deployment" / "routing-manifest.json"


def test_sales_workshop_route_exists():
    assert PAGE.exists()
    assert APP.exists()
    assert STYLE.exists()
    routing = ROUTING.read_text(encoding="utf-8")
    assert '"canonicalPath": "/kesintiye-hazirlik-atolyesi"' in routing
    assert '"source": "alo186/kesinti-hazirlik-atolyesi/index.html"' in routing


def test_single_canonical_contract():
    html = PAGE.read_text(encoding="utf-8")
    canonical = "https://www.alo186.com/kesintiye-hazirlik-atolyesi"
    assert f'rel="canonical" href="{canonical}"' in html
    assert 'https://www.alo186.com/kesintiye-hazirlik-atolyesi/' not in html


def test_affiliate_disclosure_is_exact_and_visible():
    html = PAGE.read_text(encoding="utf-8")
    assert "Reklam / satış ortaklığı açıklaması" in html
    assert "Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum." in html
    assert "Kullanıcıya ek maliyet yansımaz" in html
    assert "rel=\"sponsored\"" in html
    assert "Fiyat, stok, puan, satıcı, teslimat ve garanti ALO186 üzerinde yayımlanmaz" in html


def test_safety_and_no_buy_gates_block_commerce():
    html = PAGE.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    assert 'id="hazard"' in html
    assert 'value="danger"' in html
    assert "Satın almama geçerli sonuç" in html
    assert "hazard === 'danger'" in app
    assert "existing === 'works'" in app
    assert "Satın alma ve hizmet yönlendirmesi kapatıldı" in app
    assert "yeni ürün almayın" in app
    assert "tel:112" in app and "/edas-bul" in app


def test_sales_segmentation_is_risk_based():
    app = APP.read_text(encoding="utf-8")
    assert "affiliateEligible: true" in app
    assert "affiliateEligible: false" in app
    assert "plan.affiliateEligible && plan.product" in app
    assert "existing === 'unknown' || verified === 'no'" in app
    assert "setting === 'hotel_site'" in app
    assert "priority === 'cold_chain'" in app
    assert "priority === 'long_outage'" in app
    assert "qualified_affiliate_product_center" in app
    assert "paid_b2b" in app
    assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in app
    assert "/hesaplama/home-office-internet-sureklilik-plani/" in app
    assert "amazon.com.tr" not in app.lower()


def test_sales_ctas_and_tracking_are_explicit():
    app = APP.read_text(encoding="utf-8")
    css = STYLE.read_text(encoding="utf-8")
    assert "Satış ortaklığı ürünlerini teknik minimumla karşılaştır" in app
    assert 'commercial: \'affiliate\'' in app
    assert 'commercial: \'paid-service\'' in app
    assert "sales_funnel_rendered" in app
    assert "sales_route_opened" in app
    assert ".button.affiliate" in css
    assert ".button.service" in css


def test_privacy_accessibility_and_schema_contract():
    html = PAGE.read_text(encoding="utf-8")
    assert "Kişisel veri" in html
    assert 'aria-live="polite"' in html
    assert 'href="#workshop"' in html
    assert '"@type":"WebApplication"' in html
    assert '"@type":"FAQPage"' in html
    assert '"@type":"BreadcrumbList"' in html
    for forbidden in (
        'type="email"',
        'type="tel"',
        'name="address"',
        'name="subscription"',
        '"@type":"Product"',
        '"@type":"Offer"',
        "localStorage",
        "sessionStorage",
    ):
        assert forbidden not in html


def main():
    test_sales_workshop_route_exists()
    test_single_canonical_contract()
    test_affiliate_disclosure_is_exact_and_visible()
    test_safety_and_no_buy_gates_block_commerce()
    test_sales_segmentation_is_risk_based()
    test_sales_ctas_and_tracking_are_explicit()
    test_privacy_accessibility_and_schema_contract()
    print("ALO186 satış odaklı kesinti atölyesi kalite sözleşmeleri başarılı.")


if __name__ == "__main__":
    main()
