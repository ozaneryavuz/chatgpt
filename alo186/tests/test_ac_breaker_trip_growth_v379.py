from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/klima-acinca-sigorta-neden-atar-kacak-akim/index.html"
TOOL = ROOT / "alo186/hesaplama/klima-sigorta-kacak-akim-belirti-ayirici/index.html"
APP = ROOT / "alo186/hesaplama/klima-sigorta-kacak-akim-belirti-ayirici/app.js"
BIZ = ROOT / "alo186/sektor-rehberi/otel-isletme-klima-elektrik-koruma-kabul/index.html"
ROUTES = ROOT / "alo186/deployment/routing-overlays/ac-breaker-trip-growth-v379.json"
COMMERCE = ROOT / "alo186/deployment/affiliate-category-decisions/ac-breaker-trip-growth-v379.json"


def text(path):
    return path.read_text(encoding="utf-8")


def test_v379_files_and_canonicals():
    for path in [GUIDE, TOOL, APP, BIZ, ROUTES, COMMERCE]:
        assert path.is_file(), path
    assert '<link rel="canonical" href="https://alo186.com/haberler/klima-acinca-sigorta-neden-atar-kacak-akim/">' in text(GUIDE)
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/klima-sigorta-kacak-akim-belirti-ayirici/">' in text(TOOL)
    assert '<link rel="canonical" href="https://alo186.com/sektor-rehberi/otel-isletme-klima-elektrik-koruma-kabul/">' in text(BIZ)


def test_no_commerce_and_no_unverified_commercial_claims():
    combined = "\n".join(text(p).lower() for p in [GUIDE, TOOL, APP, BIZ])
    for merchant in ["amazon.com.tr", "amzn.to", "rel=\"sponsored"]:
        assert merchant not in combined
    policy = json.loads(text(COMMERCE))
    assert policy["newAffiliateClasses"] == 0
    assert policy["newMerchantLinks"] == 0
    assert {"unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"}.issubset(set(policy["mustNotClaim"]))


def test_trust_and_no_buy_language():
    guide = text(GUIDE).lower()
    tool = text(TOOL).lower()
    app = text(APP).lower()
    biz = text(BIZ).lower()
    assert "alo186 resmî kurum" in guide
    assert "tekrar tekrar" in guide
    assert "daha büyük sigorta" in guide
    assert "yeni ürün almayın" in tool
    assert "yeni ürün almayın" in app
    assert "consumer affiliate" in biz.lower()
    assert "merchant bağlantısı yoktur" in biz.lower()


def test_privacy_and_safe_scope():
    tool = text(TOOL).lower()
    app = text(APP).lower()
    assert "adres, telefon, abonelik" in tool
    for forbidden in ["fetch(", "localstorage", "sessionstorage", "geolocation"]:
        assert forbidden not in app
    assert "112" in app
    assert "korumayı bypass etmeyin" in app


def test_routing_v379():
    data = json.loads(text(ROUTES))
    assert data["version"] == 379
    paths = {r["canonicalPath"] for r in data["routes"]}
    assert paths == {
        "/haberler/klima-acinca-sigorta-neden-atar-kacak-akim/",
        "/hesaplama/klima-sigorta-kacak-akim-belirti-ayirici/",
        "/sektor-rehberi/otel-isletme-klima-elektrik-koruma-kabul/",
    }


if __name__ == "__main__":
    test_v379_files_and_canonicals()
    test_no_commerce_and_no_unverified_commercial_claims()
    test_trust_and_no_buy_language()
    test_privacy_and_safe_scope()
    test_routing_v379()
    print({"ok": True, "version": 379, "merchantLinks": 0, "affiliateClasses": 0})
