from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "urun-eslestirme" / "catalog.js"

PRODUCT_RE = re.compile(
    r"\{id:'(?P<id>[^']+)',category:'(?P<category>[^']+)',asin:'(?P<asin>[A-Z0-9]{10})'"
    r".*?status:'verified_listing'.*?url:amazonProductUrl\('(?P<url_asin>[A-Z0-9]{10})'\)\},?",
    re.MULTILINE,
)

NEW_PRODUCT_IDS = {
    "samsung-ep-ta800-25w",
    "spigen-arcstation-45w-ach02589",
    "spigen-ee201-20w-ach09217",
    "ugreen-dp14-2m",
    "ugreen-hdmi21-3m",
    "daytona-hc01-usbc-hdmi-18m",
}


def source() -> str:
    return CATALOG.read_text(encoding="utf-8")


def products() -> list[dict[str, str]]:
    return [match.groupdict() for match in PRODUCT_RE.finditer(source())]


def runtime_snapshot() -> dict[str, object]:
    script = r"""
const catalog = require(process.argv[1]);
const now = new Date('2026-07-30T12:00:00Z');
const health = catalog.catalogHealth({now});
const graph = catalog.knowledgeGraph({now})['@graph'];
const all = graph.find(node => node['@id'] === 'https://www.alo186.com/akilli-urun-secimi#verified-products');
const direct = graph.find(node => node['@id'] === 'https://www.alo186.com/akilli-urun-secimi#direct-affiliate-products');
const gated = graph.find(node => node['@id'] === 'https://www.alo186.com/akilli-urun-secimi#tool-gated-products');
console.log(JSON.stringify({
  health,
  allItems: all.numberOfItems,
  directItems: direct.numberOfItems,
  gatedItems: gated.numberOfItems,
  tagged: catalog.products.every(product => product.url.includes('tag=alo186rehber-21')),
  newProductsDirect: %s.every(id => {
    const product = catalog.products.find(item => item.id === id);
    return Boolean(product && catalog.publicAffiliateEligible(product, {now}));
  })
}));
""" % json.dumps(sorted(NEW_PRODUCT_IDS))
    result = subprocess.run(
        ["node", "-e", script, str(CATALOG)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_catalog_has_at_least_24_verified_products() -> None:
    items = products()
    assert len(items) >= 24
    assert len({item["id"] for item in items}) == len(items)
    assert len({item["asin"] for item in items}) == len(items)
    assert all(item["asin"] == item["url_asin"] for item in items)


def test_six_new_low_risk_products_are_present() -> None:
    items = {item["id"]: item for item in products()}
    assert NEW_PRODUCT_IDS.issubset(items)
    assert {items[item_id]["category"] for item_id in NEW_PRODUCT_IDS} == {
        "usb_c_charger",
        "display_cable",
    }
    text = source()
    for item_id in NEW_PRODUCT_IDS:
        line = next(line for line in text.splitlines() if f"id:'{item_id}'" in line)
        assert "verifiedAt:'2026-07-30'" in line
        assert "status:'verified_listing'" in line


def test_runtime_health_and_knowledge_graph_counts_match() -> None:
    snapshot = runtime_snapshot()
    health = snapshot["health"]
    assert health["totalVerified"] >= 24
    assert health["publicDirect"] >= 17
    assert snapshot["allItems"] == health["totalVerified"]
    assert snapshot["directItems"] == health["publicDirect"]
    assert snapshot["gatedItems"] == health["gatedVerified"]
    assert snapshot["tagged"] is True
    assert snapshot["newProductsDirect"] is True


def test_catalog_keeps_commercial_claims_conservative() -> None:
    text = source()
    assert "USB-C, DisplayPort ve HDMI görüntü kablosu" in text
    assert "affiliateTag='alo186rehber-21'" in text
    assert "verificationMaxAgeDays=45" in text
    for forbidden in (
        "price:",
        "stock:",
        "rating:",
        "warranty:",
        "affiliateCommission:",
    ):
        assert forbidden not in text
