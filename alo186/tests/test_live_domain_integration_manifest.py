from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
manifest_path = ROOT / "alo186/deployment/live-domain-integration.json"
workflow_path = ROOT / ".github/workflows/alo186-live-domain-acceptance.yml"
guard_path = ROOT / "alo186/tests/live_release_identity_guard.py"
pages_workflow_path = ROOT / ".github/workflows/alo186-github-pages.yml"
hardening_path = ROOT / "alo186/deployment/inject_live_quality_hardening.py"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
workflow = workflow_path.read_text(encoding="utf-8")
guard = guard_path.read_text(encoding="utf-8")
pages_workflow = pages_workflow_path.read_text(encoding="utf-8")
hardening = hardening_path.read_text(encoding="utf-8")

assert manifest["version"] >= 3
assert manifest["productionOrigin"] == "https://alo186.com"
assert manifest["canonicalOrigin"] == "https://alo186.com"
assert manifest["apexOrigin"] == "https://alo186.com"
assert manifest["wwwOrigin"] == "https://www.alo186.com"
assert manifest["productionOrigin"] == manifest["canonicalOrigin"]
assert manifest["minimumReleaseRouteCount"] >= 275
assert manifest["identityGuard"] == "alo186/tests/live_release_identity_guard.py"
assert "pages-release.json" in manifest["knownBlockingCondition"]
assert "fail-closed" in manifest["knownBlockingCondition"].casefold()
assert len(manifest["requiredRoutes"]) >= 16
assert "canonicalHost=https://alo186.com" in manifest["requiredReleaseSignals"]
assert "liveTechnicalQuality.minimumTouchTargetCssPx=44" in manifest["requiredReleaseSignals"]

for route in [
    "/pages-release.json",
    "/elektrik-durum-merkezi/",
    "/elektrik-portali/",
    "/edas-bul/",
    "/hesaplama/",
    "/hesaplama/aydinlatma-ihtiyac-ve-ampul-uygunluk/",
    "/hesaplama/kesinti-hazirlik-envanteri/",
    "/hesaplama/home-office-internet-sureklilik-plani/",
    "/akilli-urun-secimi/",
    "/amazon-elektrik-urunleri/",
    "/urun-bilgi-grafigi/",
    "/haberler/ups-eco-modu-online-cift-cevrim-farki",
    "/sitemap.xml",
    "/robots.txt",
]:
    assert route in manifest["requiredRoutes"], route

for token in [
    "actions/checkout@v4",
    "live_release_identity_guard.py",
    "pages-release.json",
    "device_damage_deadline_guard.py",
]:
    assert token in workflow, token

for token in [
    "serving_origin != canonical_origin",
    "minimumReleaseRouteCount",
    "routeCount",
    "deviceDamageDeadline",
    "rootDeviceDamageDeadline",
    "30\\s*",
    "10 iş günü",
    "sitemap.xml",
    "robots.txt",
]:
    assert token in guard, token

for token in [
    "custom-domain alo186.com",
    "inject_live_quality_hardening_v2.py",
    "upload-pages-artifact@v4",
    "deploy-pages@v4",
]:
    assert token in pages_workflow, token

for token in [
    'CANONICAL_ORIGIN = "https://alo186.com"',
    "minimumTouchTargetCssPx",
    "personalDataCollectionAdded",
    "officialInstitutionClaimed",
]:
    assert token in hardening, token

print(json.dumps({
    "ok": True,
    "version": manifest["version"],
    "routes": len(manifest["requiredRoutes"]),
    "productionOrigin": manifest["productionOrigin"],
    "canonicalOrigin": manifest["canonicalOrigin"],
    "minimumReleaseRouteCount": manifest["minimumReleaseRouteCount"],
    "singleOriginFailClosed": True,
}, ensure_ascii=False, indent=2))
