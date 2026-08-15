from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "alo186/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/index.html"
TOOL = ROOT / "alo186/hesaplama/kacak-akim-rolesi-test-hatirlatici/index.html"
HUB = ROOT / "alo186/ev-elektrik-guvenlik-kontrol-merkezi/index.html"
ROUTES = ROOT / "alo186/deployment/routing-overlays/rcd-test-repeat-v381.json"
COMMERCE = ROOT / "alo186/deployment/affiliate-category-decisions/rcd-test-repeat-v381.json"


def text(path):
    return path.read_text(encoding="utf-8")


def test_files_canonicals_and_distribution():
    for path in [GUIDE, TOOL, HUB, ROUTES, COMMERCE]:
        assert path.is_file(), path
    assert 'https://alo186.com/haberler/kacak-akim-rolesi-test-butonu-basilinca-atmiyor/' in text(GUIDE)
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/kacak-akim-rolesi-test-hatirlatici/">' in text(TOOL)
    assert '/hesaplama/kacak-akim-rolesi-test-hatirlatici/' in text(GUIDE)
    assert '/hesaplama/kacak-akim-rolesi-test-hatirlatici/' in text(HUB)


def test_no_universal_interval_and_safety_boundaries():
    combined = (text(GUIDE) + "\n" + text(TOOL)).lower()
    assert "evrensel" in combined
    assert "üretici" in combined
    assert "kılavuz" in combined
    assert "açma akımı" in combined
    assert "açma süresi" in combined
    assert "pano kapağ" in combined
    assert "yeni ürün almayın" in combined
    policy = json.loads(text(COMMERCE))
    assert "one-universal-rcd-test-interval-applies-to-all-devices" in policy["mustNotClaim"]
    assert "test-button-pass-proves-the-whole-installation-is-safe" in policy["mustNotClaim"]


def test_privacy_local_ics_and_no_commerce():
    tool = text(TOOL).lower()
    assert "begin:vcalendar" in tool
    assert "createobjecturl" in tool
    assert "type=\"date\"" in tool
    # No actual data-network or persistent browser storage calls.
    for forbidden in ["window.fetch(", "navigator.geolocation", ".setitem(", ".getitem("]:
        assert forbidden not in tool
    combined = "\n".join(text(p).lower() for p in [GUIDE, TOOL, HUB])
    for merchant in ["amazon.com.tr", "amzn.to", 'rel="sponsored']:
        assert merchant not in combined
    policy = json.loads(text(COMMERCE))
    assert policy["newAffiliateClasses"] == 0
    assert policy["newMerchantLinks"] == 0
    assert {"unverified-price", "unverified-stock", "unverified-rating", "unverified-warranty"}.issubset(set(policy["mustNotClaim"]))


def test_routing_v381():
    data = json.loads(text(ROUTES))
    assert data["version"] == 381
    paths = {r["canonicalPath"] for r in data["routes"]}
    assert paths == {"/hesaplama/kacak-akim-rolesi-test-hatirlatici/"}


if __name__ == "__main__":
    test_files_canonicals_and_distribution()
    test_no_universal_interval_and_safety_boundaries()
    test_privacy_local_ics_and_no_commerce()
    test_routing_v381()
    print({"ok": True, "version": 381, "merchantLinks": 0, "affiliateClasses": 0})
