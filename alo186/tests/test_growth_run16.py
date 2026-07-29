from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    "mode2": ROOT / "hesaplama" / "tasinabilir-ev-sarj-cihazi-priz-uygunluk",
    "mini": ROOT / "hesaplama" / "modem-ont-mini-ups-sure-saglik-gunlugu",
    "voltage": ROOT / "hesaplama" / "priz-tipi-gerilim-monitoru-uygunluk",
}


def require(text: str, *needles: str) -> None:
    for needle in needles:
        assert needle in text, needle


for directory in ROUTES.values():
    html = (directory / "index.html").read_text(encoding="utf-8")
    js = (directory / "app.js").read_text(encoding="utf-8")
    require(html, "application/ld+json", "FAQPage", "BreadcrumbList", "Bağımsız elektrik bilgi ağı")
    assert "amazon.com.tr" not in html.lower() and "amzn." not in html.lower()
    require(js, "rawPersonalDataCollected:false", "retentionMode:'per-record'", "commercial=false", "localStorage")

mode2_html = (ROUTES["mode2"] / "index.html").read_text(encoding="utf-8")
mode2_js = (ROUTES["mode2"] / "app.js").read_text(encoding="utf-8")
require(mode2_html, "IEC 62752:2024", "Reklam / satış ortaklığı açıklaması", "Günlük veya düzenli ev şarjı", "Uzatma, çoklayıcı ve üçüncü taraf adaptör kullanılmıyor")
require(mode2_js, "r.useCase==='daily'", "r.heat||r.wet", "fullGate", "r.purpose==='purchase'", "commercial=true", "officialRecord:false")
assert mode2_js.index("if(danger)") < mode2_js.index("commercial=true")

mini_html = (ROUTES["mini"] / "index.html").read_text(encoding="utf-8")
mini_js = (ROUTES["mini"] / "app.js").read_text(encoding="utf-8")
require(mini_html, "gerçek kesinti süresini", "Tam şarj", "APC Back‑UPS Connect", "satın almama")
require(mini_js, "r.stage==='first'", "r.stage==='retest'", "r.hazard", "ratio>=1", "commercial=true", "officialRecord:false")
assert mini_js.index("if(r.hazard)") < mini_js.index("commercial=true")

voltage_html = (ROUTES["voltage"] / "index.html").read_text(encoding="utf-8")
voltage_js = (ROUTES["voltage"] / "app.js").read_text(encoding="utf-8")
require(voltage_html, "IEC 61000‑4‑30:2025", "EPDK", "resmî teknik kalite", "7 günlük", "Basit cihaz hiçbir zaman otomatik resmî ölçüm değildir")
require(voltage_js, "officialScope", "r.scope==='building'", "r.goal==='harmonics'", "r.hazard", "commercial=true", "officialMeasurement:false")
assert voltage_js.index("if(r.hazard)") < voltage_js.index("commercial=true")

overlay = json.loads((ROOT / "deployment" / "routing-overlays" / "growth-trust-revenue-run16.json").read_text(encoding="utf-8"))
assert overlay["version"] >= 63
assert len(overlay["routes"]) == 3
trust = overlay["trust"]
assert trust["rawPersonalDataCollected"] is False
assert trust["directAffiliateLinksAdded"] == 0
assert trust["unverifiedCommercialFieldsUsed"] == []
assert trust["noBuyOutcomePreserved"] is True
assert trust["affiliateDisclosureRequired"] is True
assert trust["officialApprovalClaimed"] is False
assert trust["emergencyCommerceClosed"] is True
assert trust["buildingWideCommerceClosed"] is True
assert trust["mode2JournalTtlDays"] == 540
assert trust["miniUpsJournalTtlDays"] == 730
assert trust["voltageMonitorJournalTtlDays"] == 365

injector = (ROOT / "deployment" / "inject_growth_run16.py").read_text(encoding="utf-8")
require(injector, "id:'ev_mobile_charger'", "id:'voltage_monitor'", "directAffiliateLinksAdded", "buildingWideCommerceClosed", "data-alo186-growth-run16-tools")
print("ALO186 growth run16 trust, no-buy, affiliate and official-measurement gates passed.")
