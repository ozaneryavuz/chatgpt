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

ROUTE = "/hesaplama/klima-yedek-guc-kalkis-uygunluk/"
SOURCE = "alo186/hesaplama/klima-yedek-guc-kalkis-uygunluk/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/klima-yedek-guc-kalkis-uygunluk"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 83
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == ROUTE]
    assert routes == [{"source": SOURCE, "canonicalPath": ROUTE, "type": "calculator"}]

    for name in ("index.html", "styles.css", "app.js", "app.test.js"):
        assert (MODULE / name).is_file(), name

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    common = (REPO_ROOT / "alo186/hesaplama/common.js").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/klima-yedek-guc-kalkis-uygunluk/"' in html
    for token in ("WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"):
        assert token in html
    assert html.count("<h1>") == 1
    assert 'id="acForm"' in html
    assert 'aria-live="polite"' in html
    assert "BTU elektrik gücü değildir" in html
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
        "START_MULTIPLIER={inverter_split:1.5,fixed_split:4.5,portable:4,window:4}",
        "PF_DEFAULT=0.9",
        "RESERVE=1.25",
        "SURGE_RESERVE=1.15",
        "BATTERY_EFF=0.85",
        "USABLE=0.8",
        "requiredContinuousW",
        "requiredSurgeW",
        "requiredWh",
        "approximateVA",
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
        "controlled" if False else "Kontrollü başlatma testi",
    ):
        assert token in app, token
    assert app.index("if(input.emergency)") < app.index("const evidence=[]")
    assert app.index("if(input.medicalCooling)") < app.index("const evidence=[]")
    assert "amazon." not in app.casefold()
    assert "../../akilli-urun-secimi?kategori=" in app

    assert ROUTE in common
    assert "data-alo186-air-conditioner-backup-card" in common
    count_match = re.search(r"(\d+) çekirdek araç", common)
    assert count_match, "Hesaplama Merkezi araç sayısı etiketi bulunamadı"
    tool_count = int(count_match.group(1))
    assert tool_count >= 37

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["scenarios"] == 20
    assert payload["route"] == ROUTE
    assert payload["affiliateGateChecks"] == 3
    assert payload["personalDataFields"] == 0
    assert payload["directStoreLinks"] == 0

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": payload["scenarios"],
        "personalDataFields": 0,
        "directStoreLinks": 0,
        "affiliateGateChecks": 3,
        "toolCountLabel": tool_count,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
