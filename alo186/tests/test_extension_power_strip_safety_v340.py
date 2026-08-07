from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/uzatma-kablosu-coklu-priz-kac-watt-guvenli-kullanim/index.html"
TOOL = ROOT / "alo186/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/coklu-priz-uzatma-kablosu-secimi/index.html"
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
        "/amazon-elektrik-urunleri/coklu-priz-uzatma-kablosu-secimi/",
    }
    assert {r["canonicalPath"] for r in routing["routes"]} == expected
    for path, canonical in [
        (GUIDE, "https://alo186.com/haberler/uzatma-kablosu-coklu-priz-kac-watt-guvenli-kullanim/"),
        (TOOL, "https://alo186.com/hesaplama/coklu-priz-uzatma-kablosu-yuk-kontrolu/"),
        (SELECTOR, "https://alo186.com/amazon-elektrik-urunleri/coklu-priz-uzatma-kablosu-secimi/"),
    ]:
        assert f'rel="canonical" href="{canonical}"' in text(path)


def test_trust_and_no_buy_contract():
    joined = "\n".join([text(GUIDE), text(TOOL), text(SELECTOR)]).casefold()
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
    assert "fetch(" not in text(TOOL)
    assert "xmlhttprequest" not in text(TOOL).casefold()
    assert "localstorage" in text(TOOL).casefold()
    assert "sessionstorage" in text(TOOL).casefold()


def test_affiliate_is_disclosed_and_locked_by_default():
    guide = text(GUIDE)
    tool = text(TOOL)
    selector = text(SELECTOR)
    assert "amazon.com.tr" not in guide
    assert "amazon.com.tr" not in tool
    assert selector.count("amazon.com.tr") == 1
    assert "data-merchant-url=" in selector
    assert 'href="https://www.amazon.com.tr' not in selector
    assert selector.count('rel="sponsored noopener"') == 1
    assert selector.count('class="gate"') == 8
    disclosure_pos = selector.find("satış ortaklığı açıklaması")
    merchant_pos = selector.find("data-merchant-url=")
    assert 0 <= disclosure_pos < merchant_pos


def test_affiliate_decision_is_bounded():
    decision = json.loads(text(DECISION))
    assert decision["version"] == 340
    assert decision["newAffiliateClasses"] == 1
    assert decision["newMerchantLinks"] == 1
    assert "generator-backfeed-or-male-to-male-extension-cord" in decision["blockedClasses"]
    assert "daisy-chained-power-strips-extension-cords-or-adapters" in decision["blockedClasses"]
    assert "below-label-load-alone-proves-safe-use" in decision["mustNotClaim"]
    assert "unverified-price" in decision["mustNotClaim"]
    assert "unverified-stock" in decision["mustNotClaim"]
    assert "unverified-rating" in decision["mustNotClaim"]
    assert "unverified-warranty" in decision["mustNotClaim"]


if __name__ == "__main__":
    test_routes_and_canonicals()
    test_trust_and_no_buy_contract()
    test_affiliate_is_disclosed_and_locked_by_default()
    test_affiliate_decision_is_bounded()
    print({"ok": True, "version": 340, "newAffiliateClasses": 1, "newMerchantLinks": 1, "merchantTrustGated": True})
