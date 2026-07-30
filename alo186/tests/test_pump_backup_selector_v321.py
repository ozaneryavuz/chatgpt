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

ROUTE = "/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/"
SOURCE = "alo186/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/index.html"
MODULE = REPO_ROOT / "alo186/hesaplama/hidrofor-pompa-yedek-guc-uygunluk"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 82
    routes = [route for route in manifest["routes"] if route["canonicalPath"] == ROUTE]
    assert routes == [{"source": SOURCE, "canonicalPath": ROUTE, "type": "calculator"}]

    for name in ("index.html", "styles.css", "app.js", "app.test.js"):
        assert (MODULE / name).is_file(), name

    html = (MODULE / "index.html").read_text(encoding="utf-8")
    css = (MODULE / "styles.css").read_text(encoding="utf-8")
    app = (MODULE / "app.js").read_text(encoding="utf-8")
    common = (REPO_ROOT / "alo186/hesaplama/common.js").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/hidrofor-pompa-yedek-guc-uygunluk/"' in html
    for token in ("WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"):
        assert token in html
    assert html.count("<h1>") == 1
    assert 'id="pumpForm"' in html
    assert 'aria-live="polite"' in html
    assert "Satış ortaklığı açıklaması" in html
    assert "doğrudan mağaza bağlantısı açmaz" in html
    assert "ürün satıcısı veya resmî kurum değildir" in html
    assert "Mevcut kaynak yeterliyse satın alma önerilmez" in html
    assert "amazon.com" not in html.casefold()

    for token in (
        "@media(max-width:820px)",
        "@media(max-width:560px)",
        "prefers-reduced-motion",
        "min-inline-size:0",
        ".record",
    ):
        assert token in css

    for forbidden in (
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
    ):
        assert personal not in html

    for token in (
        "START_MULTIPLIER={direct:6,soft:3,vfd:1.5}",
        "PF_DEFAULT=0.8",
        "RESERVE=1.25",
        "BATTERY_EFF=0.85",
        "USABLE=0.8",
        "SQRT3",
        "requiredContinuousW",
        "requiredSurgeW",
        "requiredWh",
        "conditional_purchase",
        "no_buy",
        "actualNeed",
        "technicalCheck",
        "affiliateCheck",
        "generator",
        "power_station",
        "inverter",
        "Mevcut kaynağın sınıfını doğrulayın",
        "String(value??'').trim()",
        "STORAGE_KEY='alo186-pump-backup-records-v1'",
        "MAX_RECORDS=8",
        "TTL_DAYS=365",
        "REVIEW_DAYS=90",
        "normalizeRecord",
        "purgeRecords",
        "loadStoredRecords",
        "exportPayload",
        "text/calendar",
        "elektrikci-is-emri-ozeti",
    ):
        assert token in app, token
    assert app.index("input.environment==='wet'") < app.index("const fixed=input.connection==='fixed'")
    assert "amazon." not in app.casefold()
    assert "../../akilli-urun-secimi?kategori=" in app

    for token in (
        'id="saveResult"',
        'id="calendarResult"',
        'id="exportResults"',
        'id="clearRecords"',
        'id="recordList"',
        "90 günlük kontrol",
        "365 gün",
        "En fazla 8 kayıt",
    ):
        assert token in html

    assert ROUTE in common
    assert "data-alo186-pump-backup-card" in common
    count_match = re.search(r"(\d+) çekirdek araç", common)
    assert count_match, "Hesaplama Merkezi araç sayısı etiketi bulunamadı"
    tool_count = int(count_match.group(1))
    assert tool_count >= 36

    result = subprocess.run(
        ["node", str(MODULE / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["scenarios"] == 25
    assert payload["route"] == ROUTE
    assert payload["records"] == 8
    assert payload["reviewDays"] == 90

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": payload["scenarios"],
        "personalDataFields": 0,
        "directStoreLinks": 0,
        "affiliateGateChecks": 3,
        "recordLimit": payload["records"],
        "recordTtlDays": 365,
        "reviewDays": payload["reviewDays"],
        "toolCountLabel": tool_count,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
