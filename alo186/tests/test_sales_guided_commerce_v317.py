from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "kesintiye-hazirlik-atolyesi" / "index.html"
ALIAS = ROOT / "urun-secim-danismani" / "index.html"
OVERLAY = ROOT / "deployment" / "routing-overlays" / "sales-guided-commerce-v317.json"


def test_sales_advisor_route_exists():
    assert PAGE.exists()
    assert ALIAS.exists()
    assert OVERLAY.exists()


def test_single_canonical_and_alias_contract():
    html = PAGE.read_text(encoding="utf-8")
    alias = ALIAS.read_text(encoding="utf-8")
    overlay = OVERLAY.read_text(encoding="utf-8")
    canonical = "https://www.alo186.com/kesintiye-hazirlik-atolyesi/"
    assert f'rel="canonical" href="{canonical}"' in html
    assert 'name="robots" content="noindex,follow"' in alias
    assert f'rel="canonical" href="{canonical}"' in alias
    assert "/kesintiye-hazirlik-atolyesi/" in alias
    assert '"canonicalPath": "/kesintiye-hazirlik-atolyesi/"' in overlay
    assert '"source": "alo186/kesintiye-hazirlik-atolyesi/index.html"' in overlay
    assert "/urun-secim-danismani/" not in overlay


def test_affiliate_links_are_transparent_and_tagged():
    html = PAGE.read_text(encoding="utf-8")
    assert "alo186rehber-21" in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert "Reklam / satış ortaklığı açıklaması" in html
    assert "Bir Amazon Gelir Ortağı olarak nitelikli satın alımlar üzerinden kazanç elde ediyorum." in html
    assert "Kullanıcıya ek maliyet yansımaz" in html
    assert "Satış ortaklığı bağlantısı · Amazon’da uygun sınıfı ara" in html


def test_safety_and_no_buy_gates_block_commerce():
    html = PAGE.read_text(encoding="utf-8")
    assert "Satın alma yönlendirmesi kapatıldı" in html
    assert "state.danger==='yes'" in html
    assert "state.existing==='sufficient'" in html
    assert "Yeni ürün gerekmiyor" in html
    assert "Mevcut çözümünüz güvenli ve hedef süre için yeterliyse satın alma yapmayın" in html
    assert "112" in html and "186" in html


def test_high_risk_and_uncertain_paths_are_not_direct_affiliate():
    html = PAGE.read_text(encoding="utf-8")
    assert "internet:{" in html and "direct:false" in html
    assert "electronics:{" in html and "service:true" in html
    assert "m.direct&&!uncertain" in html
    assert "state.existing==='untested'" in html
    assert "state.verified==='no'" in html
    assert "state.duration==='long'" in html
    assert "/hesaplama/home-office-internet-sureklilik-plani/" in html
    assert "/hesaplama/inverter-uygunluk/" in html
    assert "/kurumsal-elektrik-surekliligi-on-degerlendirme" in html


def test_privacy_accessibility_and_schema_contract():
    html = PAGE.read_text(encoding="utf-8")
    assert "Kişisel veri istemez" in html
    assert "localStorage" not in html
    assert "sessionStorage" not in html
    assert 'aria-live="polite"' in html
    assert 'href="#main"' in html
    assert '"@type":"WebApplication"' in html
    assert '"@type":"FAQPage"' in html
    assert '"@type":"BreadcrumbList"' in html
    for forbidden in ('type="email"', 'type="tel"', 'name="address"', 'name="subscription"', '"@type":"Product"', '"@type":"Offer"'):
        assert forbidden not in html
