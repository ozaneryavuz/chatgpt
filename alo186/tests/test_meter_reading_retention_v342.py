from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/elektrik-sayaci-nasil-okunur-t0-t1-t2-t3-endeks/index.html"
TOOL = ROOT / "alo186/hesaplama/elektrik-sayaci-endeks-kwh-gun-takibi/index.html"
HUB = ROOT / "alo186/fatura-ve-sayac-kontrol-merkezi/index.html"
EXISTING_SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/priz-tipi-enerji-olcer-secimi/index.html"
ROUTING = ROOT / "alo186/deployment/routing-overlays/meter-reading-retention-v342.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/meter-reading-retention-v342.json"


def text(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def test_routes_and_canonicals():
    routing = json.loads(text(ROUTING))
    assert routing["version"] == 342
    expected = {
        "/haberler/elektrik-sayaci-nasil-okunur-t0-t1-t2-t3-endeks/",
        "/hesaplama/elektrik-sayaci-endeks-kwh-gun-takibi/",
        "/fatura-ve-sayac-kontrol-merkezi/",
    }
    assert {r["canonicalPath"] for r in routing["routes"]} == expected
    for path, canonical in [
        (GUIDE, "https://alo186.com/haberler/elektrik-sayaci-nasil-okunur-t0-t1-t2-t3-endeks/"),
        (TOOL, "https://alo186.com/hesaplama/elektrik-sayaci-endeks-kwh-gun-takibi/"),
        (HUB, "https://alo186.com/fatura-ve-sayac-kontrol-merkezi/"),
    ]:
        assert f'rel="canonical" href="{canonical}"' in text(path)


def test_trust_privacy_and_no_buy_contract():
    joined = "\n".join([text(GUIDE), text(TOOL), text(HUB)]).casefold()
    for phrase in [
        "yeni ürün almayın",
        "bağımsız bilgilendirme platformu",
        "fiyat, stok, puan",
        "sayaç mühr",
        "kwh/gün",
        "resmî",
    ]:
        assert phrase in joined, phrase
    tool = text(TOOL).casefold()
    assert "fetch(" not in tool
    assert "xmlhttprequest" not in tool
    assert "localstorage" not in tool
    assert "sessionstorage" not in tool
    assert "amazon.com.tr" not in joined
    assert '"@type":"product"' not in joined
    assert '"@type":"offer"' not in joined
    assert '"aggregaterating"' not in joined


def test_tariff_times_are_not_hardcoded_as_universal_truth():
    guide = text(GUIDE)
    for stale_fixed_window in ["06:00-17:00", "17:00-22:00", "22:00-06:00"]:
        assert stale_fixed_window not in guide
    assert "saat aralıklarını sabitlemez" in guide
    assert "tedarikçi" in guide.casefold()
    assert "EPDK" in guide


def test_existing_affiliate_owner_is_reused_without_new_merchant_surface():
    hub = text(HUB)
    selector = text(EXISTING_SELECTOR).casefold()
    route = "/amazon-elektrik-urunleri/priz-tipi-enerji-olcer-secimi/"
    assert route in hub
    assert "affiliate açıklaması" in hub.casefold()
    assert "satış ortaklığı" in hub.casefold()
    assert "yeni ürün almayın" in hub.casefold()
    assert "amazon.com.tr" in selector
    decision = json.loads(text(DECISION))
    assert decision["version"] == 342
    assert decision["newAffiliateClasses"] == 0
    assert decision["newMerchantLinks"] == 0
    assert decision["existingDecisionRoute"] == route
    assert "sealed-meter-or-meter-terminal-work" in decision["blockedClasses"]
    assert "fixed-t1-t2-t3-time-window-without-current-tariff-verification" in decision["mustNotClaim"]
    for item in ["unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"]:
        assert item in decision["mustNotClaim"]


def test_repeat_visit_and_official_routing():
    tool = text(TOOL)
    hub = text(HUB)
    assert "30 gün sonra tekrar kontrol et" in tool
    assert "text/calendar" in tool
    assert "/haberler/elektrik-sayaci-arizali-mi-fatura-itirazi/" in tool
    assert "/haberler/elektrik-faturasi-neden-yuksek-kwh-gun-tuketim-artisi/" in hub
    assert "EDAŞ" in hub and "EPDK" in hub


if __name__ == "__main__":
    test_routes_and_canonicals()
    test_trust_privacy_and_no_buy_contract()
    test_tariff_times_are_not_hardcoded_as_universal_truth()
    test_existing_affiliate_owner_is_reused_without_new_merchant_surface()
    test_repeat_visit_and_official_routing()
    print({"ok": True, "version": 342, "newAffiliateClasses": 0, "newMerchantLinks": 0, "repeatVisit": "monthly-meter-baseline"})
