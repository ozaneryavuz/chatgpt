from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/elektrik-borcu-odendi-ne-zaman-acilir/index.html"
TOOL = ROOT / "alo186/hesaplama/borctan-kesilen-elektrik-yeniden-baglama-takibi/index.html"
HUB = ROOT / "alo186/abonelik-ve-guvence-bedeli-kontrol-merkezi/index.html"
REPEAT = ROOT / "alo186/tekrar-kullanilan-araclar/index.html"
ROUTES = ROOT / "alo186/deployment/routing-overlays/debt-reconnection-growth-v380.json"
COMMERCE = ROOT / "alo186/deployment/affiliate-category-decisions/debt-reconnection-growth-v380.json"


def text(path):
    return path.read_text(encoding="utf-8")


def test_v380_files_canonicals_and_internal_distribution():
    for path in [GUIDE, TOOL, HUB, REPEAT, ROUTES, COMMERCE]:
        assert path.is_file(), path
    assert '<link rel="canonical" href="https://alo186.com/haberler/elektrik-borcu-odendi-ne-zaman-acilir/">' in text(GUIDE)
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/borctan-kesilen-elektrik-yeniden-baglama-takibi/">' in text(TOOL)
    assert '/haberler/elektrik-borcu-odendi-ne-zaman-acilir/' in text(HUB)
    assert '/hesaplama/borctan-kesilen-elektrik-yeniden-baglama-takibi/' in text(HUB)
    assert '/hesaplama/borctan-kesilen-elektrik-yeniden-baglama-takibi/' in text(REPEAT)
    assert 'Borç ödendi / açma kaydı bekleniyor' in text(REPEAT)


def test_epdk_timing_is_not_misrepresented():
    combined = (text(GUIDE) + "\n" + text(TOOL)).lower()
    assert "imar yerleşim alanında iki gün" in combined
    assert "imar yerleşim alanı dışında üç gün" in combined
    assert "iş günü" in combined
    assert "bildirim" in combined
    assert "ödeme saatinden" in combined or "ödeme anı" in combined
    assert "mühür" in combined
    policy = json.loads(text(COMMERCE))
    must_not = set(policy["mustNotClaim"])
    assert "payment-time-is-always-the-start-of-the-two-or-three-day-period" in must_not
    assert "the-two-or-three-day-period-is-a-business-day-period" in must_not


def test_privacy_and_life_support_safety():
    tool = text(TOOL).lower()
    for forbidden in ["fetch(", "localstorage", "sessionstorage", "geolocation"]:
        assert forbidden not in tool
    assert "t.c." in tool
    assert "abonelik/tesisat no" in tool
    assert "yaşam destek" in tool
    assert "112" in tool
    assert "hayati risk" in tool


def test_no_commerce_and_no_unverified_commercial_claims():
    combined = "\n".join(text(p).lower() for p in [GUIDE, TOOL, HUB, REPEAT])
    for merchant in ["amazon.com.tr", "amzn.to", "rel=\"sponsored"]:
        assert merchant not in combined
    policy = json.loads(text(COMMERCE))
    assert policy["newAffiliateClasses"] == 0
    assert policy["newMerchantLinks"] == 0
    assert {"unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"}.issubset(set(policy["mustNotClaim"]))
    assert "ürün satın alma problemi değildir" in text(GUIDE).lower()
    assert "ürün satın alarak çözülmez" in text(HUB).lower()
    assert "mevcut çözüm yeterliyse yeni ürün almayın" in text(REPEAT).lower()


def test_routing_v380():
    data = json.loads(text(ROUTES))
    assert data["version"] == 380
    paths = {r["canonicalPath"] for r in data["routes"]}
    assert paths == {
        "/haberler/elektrik-borcu-odendi-ne-zaman-acilir/",
        "/hesaplama/borctan-kesilen-elektrik-yeniden-baglama-takibi/",
    }


if __name__ == "__main__":
    test_v380_files_canonicals_and_internal_distribution()
    test_epdk_timing_is_not_misrepresented()
    test_privacy_and_life_support_safety()
    test_no_commerce_and_no_unverified_commercial_claims()
    test_routing_v380()
    print({"ok": True, "version": 380, "merchantLinks": 0, "affiliateClasses": 0})
