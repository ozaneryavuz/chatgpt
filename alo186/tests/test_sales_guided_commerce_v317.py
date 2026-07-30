from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "urun-secim-danismani" / "index.html"
ENTRY = ROOT / "kesintiye-hazirlik-atolyesi" / "index.html"


def test_sales_advisor_route_exists():
    assert PAGE.exists()
    assert ENTRY.exists()


def test_affiliate_links_are_transparent_and_tagged():
    html = PAGE.read_text(encoding="utf-8")
    assert "alo186rehber-21" in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert "Satış ortaklığı açıklaması" in html
    assert "kullanıcıya ek maliyet yansımaz" in html


def test_safety_gate_blocks_commerce():
    html = PAGE.read_text(encoding="utf-8")
    assert "Satın alma yönlendirmesi kapatıldı" in html
    assert "state.danger==='yes'" in html
    assert "112" in html and "186" in html


def test_privacy_and_accessibility_contract():
    html = PAGE.read_text(encoding="utf-8")
    assert "Kişisel veri istemez" in html
    assert "localStorage" not in html
    assert "sessionStorage" not in html
    assert 'aria-live="polite"' in html
    assert 'href="#main"' in html


def test_existing_home_revenue_route_now_resolves():
    html = ENTRY.read_text(encoding="utf-8")
    assert "/urun-secim-danismani/" in html
    assert "location.replace" in html
