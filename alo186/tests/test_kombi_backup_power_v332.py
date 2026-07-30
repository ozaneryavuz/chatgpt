from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/kombi-kazan-yedek-guc-uygunluk/"
SOURCE = "alo186/hesaplama/kombi-kazan-yedek-guc-uygunluk/index.html"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 93
    matches = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(matches) == 1
    assert matches[0]["source"] == SOURCE
    assert matches[0]["type"] == "calculator"

    root = REPO_ROOT / "alo186/hesaplama/kombi-kazan-yedek-guc-uygunluk"
    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")
    css = (root / "styles.css").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/kombi-kazan-yedek-guc-uygunluk/"' in html
    for token in [
        "WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList",
        'aria-live="polite"', "Amazon Türkiye satış ortaklığı bağlantısı",
        "JSON teknik fişi", "90 günlük test takvimi", "Doğal Gaz Acil 187",
        "Gaz acilinde affiliate yok", "24 kW", "yeni ürün almayın",
        "gaz dağıtım şirketi, sağlık hizmeti sağlayıcısı, yetkili servis, ürün satıcısı, EDAŞ veya kamu kurumu değildir",
    ]:
        assert token in html, token
    for input_id in [
        "gasEmergency", "electricalEmergency", "applianceCondition", "applianceType",
        "criticalHeating", "connectionType", "generatorTransfer", "activeOutage",
        "annualService", "flueVentilation", "coAlarm", "manufacturerCompatibility",
        "phaseNeutralVerified", "recallChecked", "boilerModel", "boilerMaxW",
        "boilerStartW", "otherW", "dutyPercent", "targetHours", "existingSource",
        "sourceContinuousW", "sourceSurgeW", "sourceWh", "pureSine",
        "output230V50Hz", "transferTest", "actualHeatingTest",
    ]:
        assert f'id="{input_id}"' in html, input_id

    for token in [
        "alo186rehber-21", "sponsored nofollow noopener", "commercialAllowed",
        "gasEmergency", "phaseNeutralVerified", "no_buy", "active_outage",
        "evidence_required", "professional", "emergency", "stop_use",
        "AC_EFFICIENCY", "USABLE_FRACTION", "OUTPUT_HEADROOM", "SURGE_HEADROOM",
    ]:
        assert token in js, token
    for forbidden in ["localStorage", "sessionStorage", "geolocation", "fetch("]:
        assert forbidden not in js
    assert '"@type":"Product"' not in html
    assert '"@type":"Offer"' not in html
    assert all(term not in html.casefold() for term in ["aggregaterating", '"availability"', '"review"'])
    assert "@media(max-width:560px)" in css
    assert "focus-visible" in css
    assert "prefers-reduced-motion" in css

    completed = subprocess.run(
        ["node", str(root / "app.test.js")], cwd=REPO_ROOT,
        check=True, capture_output=True, text=True,
    )
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["scenarios"] == 19
    assert result["requiredContinuousW"] == 150
    assert result["requiredSurgeW"] == 280
    assert result["requiredNominalWh"] == 920
    assert result["noBuy"] == "no_buy"

    print(json.dumps({
        "ok": True,
        "route": ROUTE,
        "routingVersion": manifest["version"],
        "scenarios": 19,
        "states": ["emergency", "stop_use", "professional", "active_outage", "evidence_required", "no_buy", "conditional_purchase"],
        "gasEmergencyAffiliateBlocked": True,
        "affiliateTripleGate": True,
        "personalData": False,
        "storage": False,
        "revisitDays": 90,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
