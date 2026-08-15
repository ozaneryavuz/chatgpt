from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RCD_ARTICLE = ROOT / "haberler/kacak-akim-rolesi-test-dugmesi-ne-ise-yarar/index.html"
RCD_LOG = ROOT / "hesaplama/kacak-akim-test-gunlugu/index.html"
GROUNDING = ROOT / "haberler/topraklama-direnci-kac-ohm-olmali/index.html"
HUB = ROOT / "ev-elektrik-guvenlik-kontrol-merkezi/index.html"
ROUTING = ROOT / "deployment/routing-overlays/growth-rcd-grounding-v366.json"


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


def test_rcd_article_is_fail_closed_and_does_not_overclaim():
    html = read(RCD_ARTICLE)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/haberler/kacak-akim-rolesi-test-dugmesi-ne-ise-yarar/">' in html
    for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for marker in (
        "topraklama direncini",
        "profesyonel rcd",
        "tek bir evrensel periyot",
        "pano kapağını açmayın",
        "harici ampul/direnç",
        "tek bir test sonucu yeni ürün satın alma gerekçesi değildir",
        "schneider electric",
        "abb",
    ):
        assert marker in low
    assert "alo186 edaş, kamu kurumu" in low
    assert_no_unverified_commerce(html)


def test_rcd_log_is_private_local_and_user_interval_driven():
    html = read(RCD_LOG)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/kacak-akim-test-gunlugu/">' in html
    for schema in ('"@type":"WebApplication"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for forbidden in ("fetch(", "localstorage.", "sessionstorage.", "navigator.geolocation", "amazon.com.tr"):
        assert forbidden not in low
    for marker in (
        "kendi üretici/kılavuz periyodunuzu girin",
        "alo186 tek bir evrensel periyot",
        "profesyonel kontrol gerekli",
        "yeni rcd satın almayın",
        "yerel csv",
        "ics",
    ):
        assert marker in low
    assert_no_unverified_commerce(html)


def test_grounding_article_removes_magic_number_acceptance():
    html = read(GROUNDING)
    low = html.lower()
    assert '<link rel="canonical" href="https://alo186.com/haberler/topraklama-direnci-kac-ohm-olmali/">' in html
    for schema in ('"@type":"Article"', '"@type":"FAQPage"', '"@type":"BreadcrumbList"'):
        assert schema in html
    for marker in (
        "tek bir sihirli ohm değeri yoktur",
        "ra × iδn ≤ 50 v",
        "teorik formülden tek başına",
        "ölçüm raporunda yalnız ohm değil",
        "affiliate veya merchant bağlantısı yoktur",
        "schneider electric",
    ):
        assert marker in low
    for misleading in ("1.667 Ω", "1.667ω", "yaklaşık 1.667", "yaklaşık 167 Ω"):
        assert misleading.lower() not in low
    assert_no_unverified_commerce(html)


def test_hub_exposes_rcd_and_grounding_paths_without_new_commerce():
    html = read(HUB)
    low = html.lower()
    for route in (
        "/haberler/kacak-akim-rolesi-test-dugmesi-ne-ise-yarar/",
        "/hesaplama/kacak-akim-test-gunlugu/",
        "/haberler/topraklama-direnci-kac-ohm-olmali/",
    ):
        assert route in html
    assert "yeni affiliate kategorisi açılmadı" in low
    assert "topraklama ekipmanı" in low


def test_routing_overlay_v366_owns_only_new_routes():
    text = read(ROUTING)
    assert '"version": 366' in text
    for route in (
        "/haberler/kacak-akim-rolesi-test-dugmesi-ne-ise-yarar/",
        "/hesaplama/kacak-akim-test-gunlugu/",
    ):
        assert route in text
    assert "/haberler/topraklama-direnci-kac-ohm-olmali/" not in text


if __name__ == "__main__":
    test_rcd_article_is_fail_closed_and_does_not_overclaim()
    test_rcd_log_is_private_local_and_user_interval_driven()
    test_grounding_article_removes_magic_number_acceptance()
    test_hub_exposes_rcd_and_grounding_paths_without_new_commerce()
    test_routing_overlay_v366_owns_only_new_routes()
    print({"ok": True, "version": 366, "merchantLinks": 0, "newAffiliateClasses": 0})
