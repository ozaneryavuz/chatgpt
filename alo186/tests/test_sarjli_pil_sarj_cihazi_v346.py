from pathlib import Path
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"hesaplama"/"sarjli-pil-sarj-cihazi-uygunluk"
HTML=(PAGE/"index.html").read_text(encoding="utf-8")
JS=(PAGE/"app.js").read_text(encoding="utf-8")
CSS=(PAGE/"styles.css").read_text(encoding="utf-8")
OVERLAY=ROOT/"deployment"/"routing-overlays"/"101-sarjli-pil-sarj-cihazi-uygunluk.json"
ROUTE="/hesaplama/sarjli-pil-sarj-cihazi-uygunluk/"

assert HTML.count("<h1>")==1
assert 'rel="canonical" href="https://alo186.com'+ROUTE+'"' in HTML
for schema in ["WebApplication","DefinedTermSet","FAQPage","BreadcrumbList"]:
    assert f'"@type":"{schema}"' in HTML
for token in [
    "Şarj cihazını yalnız", "Alkalin pil şarj edilebilir mi?",
    "IEC 60335-2-29", "IEC 61951-2", "IEC 62133-2",
    "Amazon Türkiye satış ortaklığı açıklaması",
    'rel="sponsored nofollow noopener"',
    "Mevcut pil ve şarj cihazı yeterli; yeni ürün almayın"
]:
    assert token in HTML+JS
for forbidden in [
    '"@type":"Product"','"@type":"Offer"',"aggregateRating","reviewCount",
    "localStorage","sessionStorage","geolocation","navigator.geolocation",
    "fetch(","XMLHttpRequest","telefon numaranız","adresiniz"
]:
    assert forbidden not in HTML+JS
for element_id in [
    "batteryForm","emergency","condition","format","chemistry","rechargeableMark",
    "chargerType","supportedChemistry","modelCode","polarity","capacityMah",
    "chargeCurrentMa","maxChargeCurrentMa","cells","independentChannels",
    "protections","grouping","environment","unattended","recallChecked",
    "certification","ownership","existingStatus","supervisedTest","result",
    "commerce","affiliate","downloadJson","downloadIcs","printResult"
]:
    assert f'id="{element_id}"' in HTML
assert "@media(max-width:560px)" in CSS
assert "prefers-reduced-motion" in CSS
assert ":focus-visible" in CSS
assert "aria-live" in HTML and "skip-link" in HTML
assert "alo186rehber-21" in JS
assert "personalData:false" in JS
assert "18650" in JS and "lithium_primary" in JS
assert "confirmations.every" in JS
assert "reviewDays:120" in JS
assert OVERLAY.exists()
data=json.loads(OVERLAY.read_text(encoding="utf-8"))
assert data["version"]==101
assert data["generatedAt"]=="2026-07-30"
entry=data["routes"][0]
assert entry["canonicalPath"]==ROUTE
assert entry["type"]=="calculator"
assert entry["source"]=="alo186/hesaplama/sarjli-pil-sarj-cihazi-uygunluk/index.html"
subprocess.run(["node","--check",str(PAGE/"app.js")],check=True)
completed=subprocess.run(["node",str(PAGE/"app.test.js")],check=True,capture_output=True,text=True)
payload=json.loads(completed.stdout)
assert payload["ok"] is True
assert payload["scenarios"]>=50
print(json.dumps({
 "ok":True,"route":ROUTE,"decision_scenarios":payload["scenarios"],
 "mobile_breakpoints":[900,560],"personal_data":False,"affiliate_gate":3,
 "no_buy":True,"primary_battery_blocked":True,"loose_lithium_blocked":True
},ensure_ascii=False))
