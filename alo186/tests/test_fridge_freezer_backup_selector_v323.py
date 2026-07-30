from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/"
SOURCE = "alo186/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 84
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == ROUTE]
    assert routes == [{"source": SOURCE, "canonicalPath": ROUTE, "type": "calculator"}]

    for name in ("index.html", "styles.css", "app.js", "app.test.js"):
        assert (MODULE / name).is_file(), name

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    common = (REPO_ROOT / "alo186/hesaplama/common.js").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/buzdolabi-dondurucu-yedek-guc-uygunluk/"' in html
    for token in ("WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"):
        assert token in html
    assert html.count("<h1>") == 1
    assert 'id="fridgeForm"' in html
    assert 'aria-live="polite"' in html
    assert "Kapıyı kapalı tutmak ilk müdahaledir" in html
    assert "yaklaşık 4 saat" in html
    assert "yaklaşık 48 saat" in html
    assert "yaklaşık 24 saat" in html
    assert "4 °C" in html
    assert "Satış ortaklığı açıklaması" in html
    assert "doğrudan mağaza bağlantısı açmaz" in html
    assert "Mevcut kaynak yeterliyse satın alma önerilmez" in html
    assert "ürün satıcısı, EDAŞ, kamu kurumu veya yetkili servis değildir" in html
    assert "amazon.com" not in html.casefold()

    for token in (
        "@media(max-width:820px)",
        "@media(max-width:560px)",
        "prefers-reduced-motion",
        "min-inline-size:0",
        ":focus-visible",
        ".food-safety",
    ):
        assert token in css

    for forbidden in (
        "localStorage",
        "sessionStorage",
        "fetch(",
        "XMLHttpRequest",
        "navigator.geolocation",
    ):
        assert forbidden not in app
    for personal in (
        'type="email"',
        'type="tel"',
        'name="email"',
        'name="phone"',
        'name="address"',
        'name="location"',
    ):
        assert personal not in html

    for token in (
        "START_MULTIPLIER={fridge:3,fridge_freezer:3.5,upright_freezer:3.5,chest_freezer:3}",
        "DUTY_CYCLE_DEFAULT={fridge:45,fridge_freezer:50,upright_freezer:50,chest_freezer:40}",
        "PF_DEFAULT=0.85",
        "RESERVE=1.25",
        "SURGE_RESERVE=1.15",
        "BATTERY_EFF=0.85",
        "USABLE=0.8",
        "Math.sqrt(3)",
        "refrigeratorHours",
        "freezerHours",
        "capacityIssues",
        "requiredContinuousW",
        "requiredSurgeW",
        "requiredWh",
        "conditional_purchase",
        "active_event",
        "no_buy",
        "actualNeed",
        "technicalCheck",
        "affiliateCheck",
        "power_station",
        "generator",
        "inverter",
        "Saf sinüs çıkış doğrulanmadı",
        "230 V / 50 Hz",
        "Kontrollü kompresör başlatma testi",
        "Buzdolabı bölümü için yaklaşık",
        "foodSafetyWindow",
        "foodSafetyIssues",
        "chooseCategory(input,metrics)",
    ):
        assert token in app, token
    evidence_index = app.index("const evidence=[]")
    assert app.index("if(input.emergency)") < evidence_index
    assert app.index("if(input.medicalStorage)") < evidence_index
    active_index = app.index("if(input.scenario==='active')")
    category_index = app.index("const category=chooseCategory")
    assert active_index < category_index
    assert "amazon." not in app.casefold()
    assert "../../akilli-urun-secimi?kategori=" in app

    assert ROUTE in common
    assert "data-alo186-fridge-freezer-backup-card" in common
    count_matches = re.findall(r"(\d+) çekirdek araç", common)
    assert count_matches, "Hesaplama Merkezi araç sayısı etiketi bulunamadı"
    tool_count = max(map(int, count_matches))
    assert tool_count >= 38

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["scenarios"] == 29
    assert payload["route"] == ROUTE
    assert payload["affiliateGateChecks"] == 3
    assert payload["personalDataFields"] == 0
    assert payload["directStoreLinks"] == 0
    assert payload["foodSafetyWindows"] == [4, 24, 48]
    assert payload["reviewFindingsFixed"] == 3

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": payload["scenarios"],
        "foodSafetyWindows": payload["foodSafetyWindows"],
        "reviewFindingsFixed": payload["reviewFindingsFixed"],
        "personalDataFields": 0,
        "directStoreLinks": 0,
        "affiliateGateChecks": 3,
        "toolCountLabel": tool_count,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
