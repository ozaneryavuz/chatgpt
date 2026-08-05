from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-otomatik-mama-makinesi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/otomatik-mama-makinesi-kesinti-plani/index.html"
SELECTOR = ROOT / "alo186/amazon-elektrik-urunleri/pil-yedekli-otomatik-mama-makinesi-secimi/index.html"
ROUTING = ROOT / "alo186/deployment/routing-overlays/growth-v293-pet-feeder-outage.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/pet-feeder-outage-v293.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v293_files_exist_and_routes_are_canonical():
    for path in (ARTICLE, TOOL, SELECTOR, ROUTING, DECISION):
        assert path.exists(), path
    routing = json.loads(read(ROUTING))
    assert routing["version"] == 293
    assert len(routing["routes"]) == 3
    for route in routing["routes"]:
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")
        assert (ROOT / route["source"]).exists()


def test_visible_independence_privacy_and_no_buy_contract():
    combined = "\n".join(read(p) for p in (ARTICLE, TOOL, SELECTOR)).lower()
    assert "bağımsız" in combined
    assert "kamu kurumu" in combined
    assert "kişisel veri" in combined
    assert "yeni ürün almayın" in combined
    assert "veteriner" in combined
    assert "temiz içme suyu" in combined
    forbidden_inputs = ("name=\"name\"", "name=\"email\"", "name=\"phone\"", "name=\"address\"")
    assert not any(item in combined for item in forbidden_inputs)
    assert "localstorage" not in combined
    assert "sessionstorage" not in combined


def test_affiliate_links_are_disclosed_and_fail_closed():
    selector = read(SELECTOR)
    lower = selector.lower()
    assert "satış ortaklığı bağlantısıdır" in lower
    assert "alo186rehber-21" in selector
    assert "data-href=\"https://www.amazon.com.tr/" in selector
    assert not re.search(r'<a[^>]+href="https://www\.amazon\.com\.tr/', selector, re.I)
    assert "sponsored nofollow noopener" in lower
    assert lower.index("satış ortaklığı açıklaması") < lower.index("data-href=\"https://www.amazon.com.tr/")
    assert lower.count('class="gate"') >= 6


def test_no_unverified_commercial_claims_or_rich_result_abuse():
    combined = "\n".join(read(p) for p in (ARTICLE, TOOL, SELECTOR))
    lower = combined.lower()
    for token in ('"@type":"product"', '"@type":"offer"', 'aggregaterating', 'reviewcount'):
        assert token not in lower
    for phrase in ("stokta", "en ucuz", "garanti süresi", "yıldız puanı", "kargo bedava"):
        assert phrase not in lower
    assert "fiyat, stok, puan" in lower


def test_health_and_scope_gates_precede_commerce():
    tool = read(TOOL).lower()
    selector = read(SELECTOR).lower()
    assert "ürün seçimini durdurun" in tool
    assert "özel diyet" in tool
    assert "yaş mama" in selector
    assert "ilaçlı öğün" in selector
    assert "sorumlu bir kişi" in selector
    assert "aktif sağlık" in selector


def test_decision_governance_matches_page_behavior():
    decision = json.loads(read(DECISION))
    policy = decision["conversionPolicy"]
    assert decision["decision"] == "guarded-low-risk-consumer-affiliate"
    assert policy["merchant"] == "Amazon Türkiye"
    assert policy["linksLockedByDefault"] is True
    assert policy["noBuyOutcomeRequired"] is True
    assert policy["activeAnimalHealthRiskCommerceClosed"] is True
    assert policy["waterAccessRequired"] is True
    assert policy["responsiblePersonCheckRequired"] is True
    assert policy["noPriceStockRatingWarrantyClaims"] is True
    assert len(decision["allowedLowRiskClasses"]) == 3
    assert [x["days"] for x in decision["repeatVisitReasons"]] == [7, 30, 90]
