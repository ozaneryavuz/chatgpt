from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT = ROOT / "deployment"
if str(DEPLOYMENT) not in sys.path:
    sys.path.insert(0, str(DEPLOYMENT))

from guard_commerce_routes_v3 import scan_affiliate_anchors  # noqa: E402


def scan(html: str) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="alo186-commerce-v3-") as folder:
        site = Path(folder)
        path = site / "index.html"
        path.write_text(html, encoding="utf-8")
        return scan_affiliate_anchors(path, site)


def test_adjacent_safety_text_does_not_poison_low_risk_card() -> None:
    html = """
    <html><body>
      <p>Reklam / satış ortaklığı: nitelikli satın alımlardan komisyon kazanılabilir.</p>
      <section class="technical-warning"><h2>Topraklama güvenliği</h2><p>Sabit tesisata müdahale etmeyin.</p></section>
      <article class="product-card low-risk">
        <h2>USB-C şarj cihazı</h2>
        <p>Port, watt ve kabloyu doğrulayın.</p>
        <a href="https://www.amazon.com.tr/dp/B000000001?tag=alo186rehber-21"
           rel="sponsored nofollow noopener">Amazon ürün sayfasını aç</a>
      </article>
    </body></html>
    """
    assert scan(html) == []


def test_high_risk_product_inside_same_card_is_rejected() -> None:
    html = """
    <html><body>
      <p>Satış ortaklığı bağlantılarından komisyon kazanılabilir.</p>
      <article class="product-card">
        <h2>Wallbox ve sabit tesisat ekipmanı</h2>
        <a href="https://www.amazon.com.tr/dp/B000000002?tag=alo186rehber-21"
           rel="sponsored nofollow noopener">Mağazayı aç</a>
      </article>
    </body></html>
    """
    errors = scan(html)
    assert len(errors) == 1
    assert "yüksek riskli" in errors[0]
    assert "wallbox" in errors[0].casefold()


def test_rel_and_disclosure_contract_remains_fail_closed() -> None:
    html = """
    <html><body>
      <article class="product-card">
        <h2>USB-C kablo</h2>
        <a href="https://www.amazon.com.tr/dp/B000000003?tag=alo186rehber-21" rel="noopener">Aç</a>
      </article>
    </body></html>
    """
    errors = scan(html)
    assert any("eksik rel" in item for item in errors)
    assert any("açıklaması yok" in item for item in errors)


def test_nearest_card_wins_over_broad_page_context() -> None:
    html = """
    <html><body>
      <p>Bir Amazon Gelir Ortağı olarak nitelikli satın alımlardan komisyon kazanılabilir.</p>
      <main>
        <section><h2>Elektrik güvenliği</h2><p>Parafudr, RCD ve topraklama profesyonel doğrulama ister.</p></section>
        <div class="calculator-result">
          <div class="recommendation-card">
            <h3>Düşük riskli HDMI kablosu</h3>
            <a href="https://www.amazon.com.tr/dp/B000000004?tag=alo186rehber-21"
               rel="sponsored nofollow noopener">Amazon ürün sayfasını aç</a>
          </div>
        </div>
      </main>
    </body></html>
    """
    assert scan(html) == []


if __name__ == "__main__":
    test_adjacent_safety_text_does_not_poison_low_risk_card()
    test_high_risk_product_inside_same_card_is_rejected()
    test_rel_and_disclosure_contract_remains_fail_closed()
    test_nearest_card_wins_over_broad_page_context()
    print("ALO186 commerce governance v3 DOM context: PASS")
