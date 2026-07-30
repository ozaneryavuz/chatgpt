from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/kesinti-hazirlik-plani/"
SOURCE = "alo186/hesaplama/kesinti-hazirlik-plani/index.html"


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    matches = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(matches) == 1
    assert matches[0]["source"] == SOURCE

    root = REPO_ROOT / "alo186/hesaplama/kesinti-hazirlik-plani"
    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "app.js").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com/hesaplama/kesinti-hazirlik-plani/"' in html
    for token in [
        "WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList",
        "Mevcut hazırlık yeterli; yeni ürün aramayın", "Doğrudan affiliate yok",
        "JSON teknik planı", "Kontrol takvimi (.ics)", "180 gün sonra",
        "EDAŞ, kamu kurumu, sağlık hizmeti sağlayıcısı veya ürün satıcısı değildir",
        "CPAP / APAP / BiPAP", "Modem / fiber ONT", "Kombi / ısıtma elektroniği",
        "Akvaryum hava", "Kamera, NVR/DVR, PoE switch",
    ]:
        assert token in html, token

    for route in [
        "cpap-bipap-yedek-guc-sure-uygunluk", "modem-internet-yedekleme",
        "kombi-elektrik-kesintisi-yedek-guc-uygunluk", "akvaryum-kesinti-yedek-guc-uygunluk",
        "kamera-nvr-poe-yedek-guc-uygunluk", "evden-calisma-laptop-modem-yedek-guc-seti",
        "buzdolabi-dondurucu-kesinti-guvenligi",
    ]:
        assert route in js, route

    for token in [
        "active_outage", "commercialAllowed:false", "affiliateLinks:0",
        "alo186_outage_plan_v3", "STORAGE_DAYS=180", "expiresAt",
        "Fiyat veya kampanya kontrolü değildir",
    ]:
        assert token in js, token

    assert "amazon.com.tr" not in html.casefold()
    assert "amazon.com.tr" not in js.casefold()
    assert '"@type":"Product"' not in html
    assert '"@type":"Offer"' not in html
    for forbidden in ["aggregateRating", '"availability"', '"review"']:
        assert forbidden.casefold() not in html.casefold()
    for personal in ["email", "telefon numarası", "abonelik numarası", "adres alanı"]:
        assert f'id="{personal}"' not in html

    completed = subprocess.run(
        ["node", str(root / "app.test.js")],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["scenarios"] == 6
    assert result["readyStatus"] == "ready"
    assert result["readyScore"] == 100
    assert result["affiliateLinks"] == 0
    assert result["storageDays"] == 180

    print(json.dumps({
        "ok": True,
        "route": ROUTE,
        "scenarios": 6,
        "directAffiliateLinks": 0,
        "noBuyState": True,
        "activeOutageSalesBlocked": True,
        "criticalIntentRoutes": 7,
        "storageExpiryDays": 180,
        "jsonExport": True,
        "icsExport": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
