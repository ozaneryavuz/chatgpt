from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/uzatma-kablosu-coklu-priz-kac-watt-guvenli-kullanim/index.html"
TOOL = ROOT / "alo186/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/index.html"
EXISTING_ADVANCED = ROOT / "alo186/hesaplama/akim-korumali-grup-priz-uygunluk/index.html"
ROUTING = ROOT / "alo186/deployment/routing-overlays/extension-power-strip-safety-v340.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/extension-power-strip-safety-v340.json"


def text(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def test_routes_and_canonicals():
    routing = json.loads(text(ROUTING))
    assert routing["version"] == 340
    expected = {
        "/haberler/uzatma-kablosu-coklu-priz-kac-watt-guvenli-kullanim/",
        "/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/",
    }
    assert {r["canonicalPath"] for r in routing["routes"]} == expected
    for path, canonical in [
        (GUIDE, "https://alo186.com/haberler/uzatma-kablosu-coklu-priz-kac-watt-guvenli-kullanim/"),
        (TOOL, "https://alo186.com/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/"),
    ]:
        assert f'rel="canonical" href="{canonical}"' in text(path)


def test_trust_privacy_and_no_buy_contract():
    joined = "\n".join([text(GUIDE), text(TOOL)]).casefold()
    for phrase in [
        "yeni ürün almayın",
        "bağımsız bilgilendirme platformudur",
        "fiyat, stok, puan",
        "zincir",
        "erkek-erkeğe",
        "aşırı yük koruması",
    ]:
        assert phrase in joined, phrase
    assert "akım korumalı" in text(GUIDE).casefold()
    assert "aşırı yük korumasını" in text(GUIDE).casefold()
    tool = text(TOOL).casefold()
    assert "fetch(" not in tool
    assert "xmlhttprequest" not in tool
    assert "localstorage" in tool
    assert "sessionstorage" in tool
    assert "amazon.com.tr" not in text(GUIDE)
    assert "amazon.com.tr" not in text(TOOL)
    assert '"offers"' not in joined
    assert '"aggregaterating"' not in joined


def test_existing_advanced_affiliate_owner_is_reused():
    guide = text(GUIDE)
    tool = text(TOOL)
    existing = text(EXISTING_ADVANCED).casefold()
    route = "/hesaplama/akim-korumali-grup-priz-uygunluk/"
    assert route in guide
    assert route in tool
    assert "satış ortaklığı açıklaması" in existing
    assert "yeni ürün almayın" in existing
    assert "amazon-elektrik-urunleri/coklu-priz-uzatma-kablosu-secimi" not in guide
    assert "amazon-elektrik-urunleri/coklu-priz-uzatma-kablosu-secimi" not in tool


def test_affiliate_decision_reuses_existing_class_without_new_merchant_link():
    decision = json.loads(text(DECISION))
    assert decision["version"] == 340
    assert decision["newAffiliateClasses"] == 0
    assert decision["newMerchantLinks"] == 0
    assert decision["existingDecisionRoute"] == "/hesaplama/akim-korumali-grup-priz-uygunluk/"
    assert "generator-backfeed-or-male-to-male-extension-cord" in decision["blockedClasses"]
    assert "daisy-chained-power-strips-extension-cords-or-adapters" in decision["blockedClasses"]
    assert "below-label-load-alone-proves-safe-use" in decision["mustNotClaim"]
    for item in ["unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"]:
        assert item in decision["mustNotClaim"]


if __name__ == "__main__":
    test_routes_and_canonicals()
    test_trust_privacy_and_no_buy_contract()
    test_existing_advanced_affiliate_owner_is_reused()
    test_affiliate_decision_reuses_existing_class_without_new_merchant_link()
    print({"ok": True, "version": 340, "newAffiliateClasses": 0, "newMerchantLinks": 0, "reusedExistingAffiliateJourney": True})
