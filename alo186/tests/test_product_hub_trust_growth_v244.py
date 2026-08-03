from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "amazon-elektrik-urunleri" / "commercial.js"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_product_hub_direct_store_links_are_gated_before_navigation() -> None:
    text = script_text()

    assert "function gateHubDirectStoreLinks()" in text
    assert 'a[href*="amazon.com.tr"]' in text
    assert "data.originalAffiliateUrl" not in text
    assert "link.dataset.originalAffiliateUrl = storeUrl" in text
    assert "link.href = technicalRoute" in text
    assert "Önce teknik ihtiyacı doğrula" in text
    assert "hub_direct_store_links_gated" in text


def test_catalog_size_vanity_counts_are_not_primary_user_copy() -> None:
    text = script_text()

    assert "function deEmphasizeCatalogCounts()" in text
    assert "güncel teknik seçim yolları" in text
    assert "güncel doğrulanmış ürün kimlikleri" in text
    assert "catalog_vanity_counts_deemphasized" in text


def test_repeat_visit_planner_is_local_and_purchase_neutral() -> None:
    text = script_text()

    assert "function injectReturnVisitPlanner()" in text
    assert "function downloadReturnVisitReminder(days)" in text
    assert "30 günlük kontrolü takvime ekle" in text
    assert "90 günlük kontrolü takvime ekle" in text
    assert "Mevcut sistem güvenli ve yeterliyse satın alma yapmayın" in text
    assert "text/calendar;charset=utf-8" in text
    assert "localStorage" not in text
    assert "sessionStorage" not in text
    assert "fetch(" not in text


def test_existing_affiliate_gate_and_no_buy_contract_remain_intact() -> None:
    text = script_text()

    assert 'data-affiliate-confirm="need"' in text
    assert 'data-affiliate-confirm="fit"' in text
    assert 'data-affiliate-confirm="disclosure"' in text
    assert "Mevcut ürünüm yeterli — satın alma yapmayacağım" in text
    assert "sponsored nofollow noopener" in text
    assert "Fiyat, stok, satıcı, teslimat, puan ve garanti yalnız Amazon’un güncel sayfasında doğrulanır." in text
