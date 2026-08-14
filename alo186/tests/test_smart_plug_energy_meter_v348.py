from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "alo186/hesaplama/akilli-priz-enerji-olcer-uygunluk"
CORE = TOOL / "core.js"
HTML = TOOL / "index.html"
APP = TOOL / "app.js"
CSS = TOOL / "styles.css"
GOV = ROOT / "alo186/deployment/affiliate-category-decisions/smart-plug-energy-meter-v348.json"


def analyze(payload: dict) -> dict:
    js = "const core=require(process.argv[1]);let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>process.stdout.write(JSON.stringify(core.analyze(JSON.parse(s)))));"
    result = subprocess.run(
        ["node", "-e", js, str(CORE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def base(**overrides) -> dict:
    data = {
        "loadType": "electronics",
        "goal": "history",
        "ownership": "candidate",
        "meterType": "smart_plug",
        "loadPowerW": 180,
        "powerFactor": 0.9,
        "startupPowerW": 300,
        "dailyHours": 6,
        "unitPriceTry": 3,
        "standbyPowerW": 3,
        "desiredHistoryDays": 30,
        "candidateCurrentA": 16,
        "candidatePowerW": 3680,
        "candidateContinuousPct": 80,
        "candidateMinMeasureW": 0.1,
        "candidateHistoryDays": 365,
        "energyMonitoring": True,
        "remoteSwitching": True,
        "scheduleSupport": True,
        "labelVerified": True,
        "manufacturerLoadApproved": True,
        "damageFree": True,
        "directWallSocket": True,
        "indoorDry": True,
        "earthContinuity": True,
        "needsEarth": True,
        "unattendedUse": False,
    }
    data.update(overrides)
    return data


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    core = CORE.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    gov = json.loads(GOV.read_text(encoding="utf-8"))

    # Canonical, schema and transparency contract.
    assert '<link rel="canonical" href="https://alo186.com/hesaplama/akilli-priz-enerji-olcer-uygunluk/">' in html
    assert "https://www.alo186.com" not in html
    assert '"@type":"WebApplication"' in html
    assert '"@type":"FAQPage"' in html
    assert '"@type":"Offer"' not in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert html.count('id="affiliateAck') == 3
    assert 'href="#"' in html
    assert "ALO186 canlı tarife kullanmaz" in html
    assert "12 Haziran 2026" in html
    assert "alo186rehber-21" in app
    assert "alo186hazirlik-21" not in app + html
    assert "unitPriceTry" in html + app + core
    assert "candidateContinuousPct" in html + app + core
    assert "monthlyCostTry" in core + app
    assert "continuousLimitKnown" in core

    # Privacy and accessibility.
    joined = (html + app + core).lower()
    for forbidden in ("localstorage", "sessionstorage", "geolocation", "navigator.geolocation", "fetch("):
        assert forbidden not in joined, forbidden
    assert "min-height:48px" in css
    assert "prefers-reduced-motion" in css
    assert "forced-colors" in css
    assert 'aria-live="polite"' in html
    assert 'aria-live="assertive"' in html

    # Main commercial candidate: energy, monthly cost and evidence-based continuous limit.
    r = analyze(base())
    assert r["status"] == "compatible", r
    assert r["commercialAllowed"] is True, r
    assert r["professionalRequired"] is False
    assert r["monthlyKwh"] == 32.4
    assert r["annualKwh"] == 394.2
    assert r["monthlyCostTry"] == 97.2
    assert r["continuousLimitA"] == 12.8
    assert r["continuousLimitW"] == 2944
    assert "akıllı priz" in r["affiliateQuery"]

    # No-buy wins before commerce for an already owned compatible product.
    owned = analyze(base(ownership="owned"))
    assert owned["noPurchaseNeeded"] is True
    assert owned["commercialAllowed"] is False

    # Long-duration use cannot become commercial if the candidate's model-specific rule is missing.
    unknown_continuous = analyze(base(candidateContinuousPct=""))
    assert unknown_continuous["status"] == "conditional"
    assert unknown_continuous["commercialAllowed"] is False
    assert unknown_continuous["continuousLimitKnown"] is False
    assert any("uzun süreli" in item.lower() for item in unknown_continuous["warnings"])

    # The published candidate rule, not a universal hard-coded watt ceiling, drives long-run fit.
    long_ok = analyze(base(loadType="resistive", goal="measure", meterType="plug_meter", loadPowerW=2500, powerFactor=1, startupPowerW=2500, dailyHours=4, desiredHistoryDays="", candidateHistoryDays="", remoteSwitching=False, scheduleSupport=False, needsEarth=True, unattendedUse=False))
    assert long_ok["status"] == "compatible", long_ok
    assert long_ok["commercialAllowed"] is True
    long_over = analyze(base(loadType="resistive", goal="measure", meterType="plug_meter", loadPowerW=3200, powerFactor=1, startupPowerW=3200, dailyHours=4, desiredHistoryDays="", candidateHistoryDays="", remoteSwitching=False, scheduleSupport=False, needsEarth=True, unattendedUse=False))
    assert long_over["status"] == "incompatible"
    assert "continuous_power" in long_over["blockerCodes"]

    # Safety gates.
    for payload, code in [
        (base(loadType="ev"), "ev"),
        (base(loadType="medical"), "medical"),
        (base(loadType="fixed"), "fixed"),
        (base(loadType="multiple"), "multiple"),
        (base(damageFree=False), "damage"),
        (base(directWallSocket=False), "interposed"),
        (base(indoorDry=False), "environment"),
        (base(earthContinuity=False), "earth"),
    ]:
        result = analyze(payload)
        assert result["status"] == "incompatible", (code, result)
        assert code in result["blockerCodes"], (code, result)
        assert result["commercialAllowed"] is False

    motor = analyze(base(loadType="motor", manufacturerLoadApproved=True))
    assert motor["professionalRequired"] is True
    assert motor["commercialAllowed"] is False
    compressor = analyze(base(loadType="compressor", manufacturerLoadApproved=False))
    assert "inductive" in compressor["blockerCodes"]
    assert compressor["commercialAllowed"] is False

    heater_remote = analyze(base(loadType="resistive", goal="schedule", unattendedUse=True))
    assert heater_remote["commercialAllowed"] is False
    assert any("gözetimsiz" in item.lower() for item in heater_remote["warnings"])

    standby = analyze(base(goal="standby", meterType="plug_meter", standbyPowerW=0.05, candidateMinMeasureW=0.1, remoteSwitching=False, scheduleSupport=False, desiredHistoryDays="", candidateHistoryDays=""))
    assert standby["status"] == "conditional"
    assert any("asgari gösterim" in item.lower() for item in standby["warnings"])

    # Governance file mirrors the runtime gates.
    assert gov["version"] == 348
    assert gov["affiliateTag"] == "alo186rehber-21"
    assert len(gov["requiredAffiliateConsents"]) == 3
    assert gov["privacy"]["personalDataRequested"] is False
    assert gov["privacy"]["networkFetch"] is False
    assert "universal 16A compatibility" in gov["commercialClaimsForbidden"]

    print("ALO186 smart plug & energy meter v348: PASS")


if __name__ == "__main__":
    main()
