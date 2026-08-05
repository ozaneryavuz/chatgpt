from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-kombi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/kombi-elektrik-kesintisi-ups-uygunluk-kontrolu/index.html"
DECISION_PAGE = ROOT / "alo186/amazon-elektrik-urunleri/kombi-ups-yedek-guc-secimi/index.html"
ROUTING = ROOT / "alo186/deployment/routing-overlays/growth-v294-boiler-outage-trust.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/boiler-outage-backup-v294.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v294_files_exist_and_routes_are_canonical():
    for path in (ARTICLE, TOOL, DECISION_PAGE, ROUTING, DECISION, POLICY):
        assert path.exists(), path
    routing = json.loads(read(ROUTING))
    assert routing["version"] == 294
    assert len(routing["routes"]) == 3
    assert {route["type"] for route in routing["routes"]} == {
        "article",
        "tool",
        "professional-only-decision-guide",
    }
    for route in routing["routes"]:
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")
        assert (ROOT / route["source"]).exists()


def test_visible_independence_safety_privacy_and_no_buy_contract():
    combined = "\n".join(read(path) for path in (ARTICLE, TOOL, DECISION_PAGE)).lower()
    for phrase in (
        "bağımsız",
        "kamu kurumu",
        "187",
        "112",
        "yeni ürün almayın",
        "professional-only",
        "yetkili servis",
        "reset",
        "donma",
        "w/va",
    ):
        assert phrase in combined, phrase
    for field in (
        'name="name"',
        'name="email"',
        'name="phone"',
        'name="address"',
        'name="serial"',
    ):
        assert field not in combined
    assert "localstorage" not in combined
    assert "sessionstorage" not in combined


def test_commerce_is_zero_and_route_is_fail_closed():
    combined = "\n".join(read(path) for path in (ARTICLE, TOOL, DECISION_PAGE))
    lower = combined.lower()
    for token in (
        "amazon.com.tr",
        "amzn.to",
        "alo186rehber-21",
        "data-href=",
        "salesrank",
    ):
        assert token not in lower, token
    assert not re.search(r'<a[^>]+rel="[^"]*sponsored', combined, re.I)
    assert "affiliate bağlantısı yok" in lower or "affiliate veya mağaza bağlantısı gösterilmez" in lower
    assert "mağaza bağlantısı yok" in lower


def test_no_unverified_commercial_claims_or_rich_result_abuse():
    combined = "\n".join(read(path) for path in (ARTICLE, TOOL, DECISION_PAGE)).lower()
    for schema_token in (
        '"@type":"product"',
        '"@type":"offer"',
        "aggregaterating",
        "reviewcount",
    ):
        assert schema_token not in combined, schema_token
    for claim in (
        "stokta",
        "en ucuz",
        "yıldız puanı",
        "kargo bedava",
        "garanti süresi",
    ):
        assert claim not in combined, claim
    assert "fiyat, stok" in combined


def test_restart_and_professional_boundaries_precede_any_purchase_intent():
    article = read(ARTICLE).lower()
    tool = read(TOOL).lower()
    decision_page = read(DECISION_PAGE).lower()
    assert "iki defayı geçmemesini" in article
    assert "ap" in article
    assert "gaz kokusunda" in article
    assert "ürün ve reset işlemini durdurun" in tool
    assert "resetlemeyi bırakın" in tool
    assert "mevcut sistem yeterli — yeni ürün almayın" in tool
    assert "consumer affiliate kapsamına kapatılmıştır" in decision_page
    assert "merkezi/kaskad" in decision_page
    assert "nötr-toprak" in decision_page


def test_decision_and_central_policy_match_page_behavior():
    decision = json.loads(read(DECISION))
    conversion = decision["conversionPolicy"]
    assert decision["version"] == 294
    assert decision["decision"] == "professional-lead-only-no-consumer-affiliate"
    assert conversion["merchantLinks"] == 0
    assert conversion["consumerAffiliateClosed"] is True
    assert conversion["noBuyOutcomeRequired"] is True
    assert conversion["activeGasOrElectricalHazardCommerceClosed"] is True
    assert conversion["repeatedResetRequiresAuthorizedService"] is True
    assert conversion["manufacturerOrAuthorizedServiceApprovalRequired"] is True
    assert conversion["noPriceStockRatingWarrantyClaims"] is True
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [30, 90, 365]

    policy = json.loads(read(POLICY))
    professional = set(policy["professionalLeadOnlyRoutePatterns"])
    for pattern in (
        "kombi",
        "dogalgazli-kombi",
        "kombi-ups",
        "isitma-kazani",
        "kazan-dairesi",
        "sirkulasyon-pompasi",
    ):
        assert pattern in professional, pattern
    assert "kombi-ups-yedek-guc" not in policy["governedAffiliateRoutePatterns"]


def test_source_freshness_and_model_specific_language():
    article = read(ARTICLE)
    lower = article.lower()
    assert "5 Ağustos 2026 kaynak kontrolü" in article
    assert "başka marka veya modellere genellenmemelidir" in lower
    assert "tam model kılavuzu" in lower
    assert "bosch-homecomfort.com" in lower
    assert "eca.com.tr" in lower
    assert "gazbir.org.tr" in lower
    assert "eaton.com" in lower


if __name__ == "__main__":
    tests = [
        test_v294_files_exist_and_routes_are_canonical,
        test_visible_independence_safety_privacy_and_no_buy_contract,
        test_commerce_is_zero_and_route_is_fail_closed,
        test_no_unverified_commercial_claims_or_rich_result_abuse,
        test_restart_and_professional_boundaries_precede_any_purchase_intent,
        test_decision_and_central_policy_match_page_behavior,
        test_source_freshness_and_model_specific_language,
    ]
    for test in tests:
        test()
    print("ok: v294 boiler outage and backup trust contract")
