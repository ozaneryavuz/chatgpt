from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "alo186/haberler/elektrik-kesilince-havuz-pompasi-calisir-mi/index.html"
TOOL = ROOT / "alo186/hesaplama/havuz-elektrik-kesintisi-yeniden-baslatma-plani/index.html"
SECTOR = ROOT / "alo186/sektor-rehberi/otel-site-havuz-elektrik-kesintisi-surekliligi/index.html"
ROUTING = ROOT / "alo186/deployment/routing-overlays/growth-v295-pool-outage-continuity.json"
DECISION = ROOT / "alo186/deployment/affiliate-category-decisions/pool-outage-continuity-v295.json"
POLICY = ROOT / "alo186/deployment/affiliate_route_risk_policy_v265.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v295_files_exist_and_routes_are_canonical():
    for path in (ARTICLE, TOOL, SECTOR, ROUTING, DECISION, POLICY):
        assert path.exists(), path
    routing = json.loads(read(ROUTING))
    assert routing["version"] == 295
    assert len(routing["routes"]) == 3
    assert {route["type"] for route in routing["routes"]} == {
        "article",
        "tool",
        "professional-only-sector-guide",
    }
    for route in routing["routes"]:
        assert route["canonicalPath"].startswith("/")
        assert route["canonicalPath"].endswith("/")
        assert (ROOT / route["source"]).exists()


def test_visible_independence_safety_privacy_and_no_buy_contract():
    combined = "\n".join(read(path) for path in (ARTICLE, TOOL, SECTOR)).lower()
    for phrase in (
        "bağımsız",
        "kamu kurumu",
        "112",
        "186",
        "yeni ürün almayın",
        "professional-only",
        "resirkülasyon",
        "kimyasal dozaj",
        "su kalitesi",
    ):
        assert phrase in combined, phrase
    for field in (
        'name="name"',
        'name="email"',
        'name="phone"',
        'name="address"',
        'name="serial"',
        'name="facility"',
    ):
        assert field not in combined
    for storage_write in (
        "localstorage.setitem",
        "sessionstorage.setitem",
        "document.cookie=",
    ):
        assert storage_write not in combined


def test_commerce_is_zero_and_professional_boundaries_are_fail_closed():
    combined = "\n".join(read(path) for path in (ARTICLE, TOOL, SECTOR))
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
    assert "amazon veya başka mağaza bağlantısı yoktur" in lower
    assert "havuz kullanıma kapalı kalır" in lower or "havuzu kapalı tutun" in lower
    assert "tekrar resetlemeyi bırakın" in lower


def test_no_unverified_commercial_claims_or_rich_result_abuse():
    combined = "\n".join(read(path) for path in (ARTICLE, TOOL, SECTOR)).lower()
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


def test_restart_flow_dosing_and_reopening_logic_precedes_purchase():
    article = read(ARTICLE).lower()
    tool = read(TOOL).lower()
    sector = read(SECTOR).lower()
    assert "motor sesi veya ekran ışığı yeterli değildir" in sector
    assert "akış yokken klor/asit dozajı çalışmamalıdır" in article
    assert "mevcut sistem yeterli — yeni ürün almayın" in tool
    assert "havuzu hemen kullanıma kapatın" in tool
    assert "misafir baskısı, doluluk veya gelir kaybı güvenlik sırasını değiştirmez" in sector
    assert "ups, jeneratör, ats" in sector.lower()


def test_decision_and_central_policy_match_page_behavior():
    decision = json.loads(read(DECISION))
    conversion = decision["conversionPolicy"]
    assert decision["version"] == 295
    assert decision["decision"] == "professional-lead-only-no-consumer-affiliate"
    assert conversion["merchantLinks"] == 0
    assert conversion["consumerAffiliateClosed"] is True
    assert conversion["professionalOnly"] is True
    assert conversion["noBuyOutcomeRequired"] is True
    assert conversion["activeElectricalOrChemicalHazardCommerceClosed"] is True
    assert conversion["circulationAndDosingVerificationRequired"] is True
    assert conversion["measuredWaterQualityRequiredBeforeReopening"] is True
    assert conversion["noPriceStockRatingWarrantyClaims"] is True
    assert [item["days"] for item in decision["repeatVisitReasons"]] == [7, 30, 365]

    policy = json.loads(read(POLICY))
    professional = set(policy["professionalLeadOnlyRoutePatterns"])
    for pattern in (
        "havuz-pompasi",
        "havuz-filtrasyon",
        "havuz-kimyasal-dozaj",
        "havuz-kontrol-panosu",
        "havuz-isitma",
        "havuz-aydinlatma",
        "havuz-yedek-guc",
    ):
        assert pattern in professional, pattern
    assert not any("havuz" in pattern for pattern in policy["governedAffiliateRoutePatterns"])


def test_source_freshness_and_authoritative_language():
    article = read(ARTICLE)
    lower = article.lower()
    assert "5 Ağustos 2026 kaynak kontrolü" in article
    assert "yabancı kaynaklardaki" in lower
    assert "saglik.gov.tr" in lower
    assert "cdc.gov" in lower
    assert "pentair.com" in lower
    assert "hse.gov.uk" in lower


def test_local_repeat_visit_calendar_without_tracking():
    tool = read(TOOL).lower()
    for day in ('data-days="7"', 'data-days="30"', 'data-days="365"'):
        assert day in tool
    assert "text/calendar" in tool
    assert "fetch(" not in tool
    assert "xmlhttprequest" not in tool


if __name__ == "__main__":
    tests = [
        test_v295_files_exist_and_routes_are_canonical,
        test_visible_independence_safety_privacy_and_no_buy_contract,
        test_commerce_is_zero_and_professional_boundaries_are_fail_closed,
        test_no_unverified_commercial_claims_or_rich_result_abuse,
        test_restart_flow_dosing_and_reopening_logic_precedes_purchase,
        test_decision_and_central_policy_match_page_behavior,
        test_source_freshness_and_authoritative_language,
        test_local_repeat_visit_calendar_without_tracking,
    ]
    for test in tests:
        test()
    print("ok: v295 pool outage continuity trust contract")
