from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALO186_ROOT = HERE.parent
DEPLOYMENT = ALO186_ROOT / "deployment"
sys.path.insert(0, str(DEPLOYMENT))

INJECTOR_PATH = DEPLOYMENT / "inject_affiliate_aeo_v250.py"
VALIDATOR_PATH = DEPLOYMENT / "validate_affiliate_aeo_v250.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


aeo = load("inject_affiliate_aeo_v250", INJECTOR_PATH)
validator = load("validate_affiliate_aeo_v250", VALIDATOR_PATH)


def seed(site: Path, *, collision: bool = False) -> None:
    affiliate = (
        '<a href="https://www.amazon.com.tr/s?k=ups&tag=alo186rehber-21">Amazon seçenekleri</a>'
    )
    for index, target in enumerate(aeo.TARGETS):
        path = site / target.file
        path.parent.mkdir(parents=True, exist_ok=True)
        duplicate = f'<div id="{target.scenario_id}"></div>' if collision and index == 0 else ""
        path.write_text(
            f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>{target.heading}</title><link rel="canonical" href="https://www.alo186.com{target.canonical_path}"></head><body><main><h1>{target.heading}</h1><p>{target.lead}</p>{duplicate}{affiliate if index == 0 else ''}</main></body></html>''',
            encoding="utf-8",
        )
    (site / "pages-release.json").write_text(json.dumps({"version": 1}), encoding="utf-8")
    (site / "checksums.sha256").write_text("placeholder\n", encoding="utf-8")


def test_offer_gate() -> None:
    today = date.today()
    assert aeo.verified_offer(None, today=today) is None
    assert aeo.verified_offer({"price": "999"}, today=today) is None
    stale = {
        "merchantUrl": "https://www.amazon.com.tr/dp/TEST?tag=alo186rehber-21",
        "price": "999.90",
        "priceCurrency": "TRY",
        "availability": "https://schema.org/InStock",
        "priceValidUntil": (today + timedelta(days=1)).isoformat(),
        "verifiedAt": (today - timedelta(days=2)).isoformat(),
    }
    assert aeo.verified_offer(stale, today=today) is None
    fresh = dict(stale)
    fresh["verifiedAt"] = today.isoformat()
    offer = aeo.verified_offer(fresh, today=today)
    assert offer is not None
    assert offer["@type"] == "Offer"
    assert offer["priceCurrency"] == "TRY"
    assert offer["availability"] == "https://schema.org/InStock"
    assert offer["seller"]["name"] == "Amazon.com.tr"


def run_case(base_path: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        first = aeo.inject(site, base_path)
        assert first["ok"] is True
        assert first["version"] == 250
        assert first["targetCount"] == len(aeo.TARGETS)
        assert len(first["injectedTargets"]) == len(aeo.TARGETS)
        assert first["ssrRecommendationCardCount"] == sum(len(t.recommendations) for t in aeo.TARGETS)
        assert first["comparisonMatrixCount"] == 1
        assert first["emittedOfferCount"] == 0
        assert first["fakePriceOrStockPublished"] is False
        assert first["affiliateLinks"]["affiliateLinkCount"] == 1
        assert first["affiliateLinks"]["normalizedLinkCount"] == 1

        report = validator.validate(site, base_path)
        assert report["ok"] is True, report["errors"]
        assert report["schemaOrgLocalValidation"]["status"] == "PASS"
        assert report["googleRichResultsReadiness"]["status"] == "PASS_WITH_CONDITIONAL_PRODUCT_OFFER"
        assert report["googleRichResultsReadiness"]["merchantOfferPublished"] is False
        assert report["robots"]["status"] == "PASS"
        assert report["llms"]["status"] == "PASS"

        for target in aeo.TARGETS:
            html = (site / target.file).read_text(encoding="utf-8")
            assert html.count(aeo.MARKER) == 1
            assert html.count(aeo.SCHEMA_MARKER) == 1
            assert html.count(aeo.STYLE_MARKER) == 1
            assert target.scenario_id in html
            for recommendation in target.recommendations:
                assert f'id="{recommendation.deep_id}"' in html
            expected_asset = aeo.public_url(base_path, "/assets/affiliate-aeo-v250.css")
            assert expected_asset in html
        first_page = (site / aeo.TARGETS[0].file).read_text(encoding="utf-8")
        assert 'rel="nofollow noopener sponsored"' in first_page or 'rel="sponsored nofollow noopener"' in first_page

        release = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))
        receipt = release["affiliateAeoV250"]
        assert receipt["version"] == 250
        assert receipt["offerPolicy"] == "conditional_verified_merchant_payload_only"
        assert receipt["emittedOfferCount"] == 0
        assert receipt["rootFiles"]["crawlerCount"] == len(aeo.AI_CRAWLERS)

        checksums = (site / "checksums.sha256").read_text(encoding="utf-8")
        assert "llms.txt" in checksums
        assert "robots.txt" in checksums
        assert "assets/affiliate-aeo-v250.css" in checksums

        second = aeo.inject(site, base_path)
        assert second["injectedTargets"] == []
        assert second["emittedOfferCount"] == 0
        second_report = validator.validate(site, base_path)
        assert second_report["ok"] is True, second_report["errors"]
        for target in aeo.TARGETS:
            html = (site / target.file).read_text(encoding="utf-8")
            assert html.count(aeo.MARKER) == 1
            assert html.count(aeo.SCHEMA_MARKER) == 1
            assert html.count(aeo.STYLE_MARKER) == 1


def test_collision_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site, collision=True)
        try:
            aeo.inject(site, "")
        except RuntimeError as exc:
            assert "deep-link id çakışması" in str(exc)
            return
        raise AssertionError("Deep-link id çakışması fail-closed durmadı")


def test_missing_target_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        seed(site)
        (site / aeo.TARGETS[-1].file).unlink()
        try:
            aeo.inject(site, "")
        except FileNotFoundError:
            return
        raise AssertionError("Eksik hedef fail-closed durmadı")


if __name__ == "__main__":
    test_offer_gate()
    run_case("")
    run_case("/chatgpt")
    run_case("/preview/alo186")
    test_collision_fails_closed()
    test_missing_target_fails_closed()
    print("ALO186 affiliate AEO v250: PASS")
