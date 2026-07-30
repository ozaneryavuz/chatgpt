from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/cpap-bipap-yedek-guc-sure-uygunluk/"
SOURCE = "alo186/hesaplama/cpap-bipap-yedek-guc-sure-uygunluk/index.html"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 92
    matches = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(matches) == 1
    assert matches[0]["source"] == SOURCE
    assert matches[0]["type"] == "calculator"

    root = REPO_ROOT / "alo186/hesaplama/cpap-bipap-yedek-guc-sure-uygunluk"
    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")
    css = (root / "styles.css").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/cpap-bipap-yedek-guc-sure-uygunluk/"' in html
    for token in [
        "WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList",
        'aria-live="polite"', "Amazon Türkiye satış ortaklığı bağlantısı",
        "JSON teknik fişi", "90 günlük test takvimi", "Yaşam destekte affiliate yok",
        "Sağlık hizmeti sağlayıcısı, tıbbi cihaz üreticisi, EDAŞ veya kamu kurumu değildir",
    ]:
        assert token in html, token
    for input_id in [
        "emergency", "lifeSustaining", "deviceType", "wetOrDamaged", "activeOutage",
        "clinicalPlan", "recallChecked", "deviceModel", "manufacturerCompatibility",
        "configurationW", "targetHours", "configurationVerified", "outputCompatibility",
        "fixedInstallation", "generatorTransfer", "existingSource", "sourceContinuousW",
        "sourceWh", "transferTest", "actualNightTest",
    ]:
        assert f'id="{input_id}"' in html, input_id

    for token in [
        "alo186rehber-21", "sponsored nofollow noopener", "commercialAllowed",
        "lifeSustaining", "ventilator", "oxygen_concentrator", "no_buy",
        "active_outage", "evidence_required", "professional", "emergency",
        "AC_EFFICIENCY", "USABLE_FRACTION", "OUTPUT_HEADROOM",
    ]:
        assert token in js, token
    for forbidden in ["localStorage", "sessionStorage", "geolocation", "fetch("]:
        assert forbidden not in js
    assert '"@type":"Product"' not in html
    assert '"@type":"Offer"' not in html
    assert all(term not in html.casefold() for term in ["aggregateRating".casefold(), '"availability"', '"review"'])
    assert "@media(max-width:560px)" in css
    assert "focus-visible" in css
    assert "prefers-reduced-motion" in css

    completed = subprocess.run(
        ["node", str(root / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["scenarios"] == 16
    assert result["requiredContinuousW"] == 90
    assert result["requiredNominalWh"] == 770
    assert result["noBuy"] == "no_buy"

    print(json.dumps({
        "ok": True,
        "route": ROUTE,
        "routingVersion": manifest["version"],
        "scenarios": 16,
        "states": ["emergency", "professional", "stop_use", "active_outage", "evidence_required", "gap_found", "no_buy", "conditional_purchase"],
        "affiliateTripleGate": True,
        "medicalLifeSupportAffiliateBlocked": True,
        "personalData": False,
        "storage": False,
        "revisitDays": 90,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
