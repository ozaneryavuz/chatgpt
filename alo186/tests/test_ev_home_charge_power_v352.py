from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / "alo186/hesaplama/ev-sarj-gucu-suresi-elektrik-altyapi-uygunluk"
HTML = (ROUTE / "index.html").read_text(encoding="utf-8")
APP = (ROUTE / "app.js").read_text(encoding="utf-8")
CORE = (ROUTE / "core.js").read_text(encoding="utf-8")
CSS = (ROUTE / "styles.css").read_text(encoding="utf-8")
OVERLAY = json.loads((ROOT / "alo186/deployment/routing-overlays/352-ev-home-charge-power-time.json").read_text(encoding="utf-8"))
POLICY = json.loads((ROOT / "alo186/deployment/affiliate-category-decisions/ev-home-charge-power-v352.json").read_text(encoding="utf-8"))


def require(token: str, text: str, label: str) -> None:
    assert token in text, f"Eksik {label}: {token}"


def main() -> None:
    subprocess.run(["node", str(ROUTE / "test.js")], cwd=ROOT, check=True)

    canonical = "https://alo186.com/hesaplama/ev-sarj-gucu-suresi-elektrik-altyapi-uygunluk/"
    require(f'<link rel="canonical" href="{canonical}">', HTML, "canonical")
    require('"@type":"WebApplication"', HTML, "WebApplication")
    require('"@type":"FAQPage"', HTML, "FAQPage")
    require('"@type":"BreadcrumbList"', HTML, "BreadcrumbList")
    require("IEC 60364-7-722", HTML, "EV tesisat standardı")
    require("IEC 61851-1", HTML, "EVSE standardı")
    require("IEC 62955", HTML, "RDC-DD standardı")
    require("Bu araç kablo veya sigorta boyutlandırmaz", HTML, "boyutlandırma güvenlik metni")
    require("Mevcut güvenli şarj çözümüm zaten hedefi karşılıyor", HTML, "no-buy girişi")
    require("ev-sarj-baslayinca-sigorta-kacak-akim-rolesi-atiyor", HTML, "arıza rehberi iç bağlantısı")

    assert "amazon.com.tr" not in HTML.lower(), "Merchant URL kaynak HTML'de koşulsuz bulunmamalı"
    require("amazon.com.tr/s?k=", APP, "dinamik Amazon Türkiye araması")
    require("alo186rehber-21", APP, "affiliate tag")
    require('rel=\"sponsored nofollow noopener\"', APP, "affiliate rel")
    for gate in ("affNeed", "affSpecs", "affDisclosure"):
        require(gate, HTML, f"affiliate onayı {gate}")
        require(gate, APP, f"runtime affiliate onayı {gate}")

    forbidden_runtime = ("localStorage", "sessionStorage", "geolocation", "navigator.geolocation", "fetch(", "XMLHttpRequest")
    for token in forbidden_runtime:
        assert token not in APP and token not in CORE, f"Kişisel veri/haricî istek sözleşmesi ihlali: {token}"
    forbidden_fields = ("name=\"name\"", "email", "telefon", "phone", "address", "konum", "location")
    lowered = HTML.lower()
    for token in forbidden_fields:
        if token == "location":
            continue
        assert token.lower() not in lowered, f"Kişisel veri alanı şüphesi: {token}"

    for safety in (
        "noRecurringTrips", "damageFree", "directEvseConnection", "dedicatedCircuit", "earthVerified",
        "residualProtectionVerified", "protectionCoordinationVerified", "advancedEnergySystem", "loadManagementRequired"
    ):
        require(safety, HTML, f"güvenlik girişi {safety}")
        require(safety, CORE, f"karar kapısı {safety}")

    for code in ("commercial", "shared", "advanced", "damage", "trips", "extension", "circuit", "earth", "residual", "protection", "load_management"):
        require(f"'{code}'", CORE, f"fail-closed karar kodu {code}")

    require("min(input.vehicleAcMaxKw,input.installationMaxKw)", CORE, "araç+tesisat tavanı")
    require("Math.min(siteVehicleCeilingKw,input.evseMaxKw)", CORE, "etkili güç darboğazı")
    require("gridEnergyKwh/input.targetHours", CORE, "hedef süre gücü")
    require("SQRT3*THREE_V", CORE, "trifaze yaklaşık akım")
    require("Kablo kesiti veya sigorta değerini", CORE, "akım hesabı sınırı")

    assert "@media(max-width:620px)" in CSS
    assert "min-height:48px" in CSS
    assert "prefers-reduced-motion" in CSS
    assert "forced-colors" in CSS
    assert "focus-visible" in CSS
    assert "aria-live=\"polite\"" in HTML

    assert OVERLAY["version"] == 352
    assert OVERLAY["routes"] == [{
        "source": "alo186/hesaplama/ev-sarj-gucu-suresi-elektrik-altyapi-uygunluk/index.html",
        "canonicalPath": "/hesaplama/ev-sarj-gucu-suresi-elektrik-altyapi-uygunluk/",
        "type": "calculator",
    }]
    assert POLICY["defaultDecision"] == "closed"
    assert POLICY["amazonMarketplace"] == "amazon.com.tr"
    assert POLICY["affiliateTag"] == "alo186rehber-21"
    assert len(POLICY["alwaysClosedFor"]) >= 8
    assert "price" in POLICY["claimsForbidden"] and "stock" in POLICY["claimsForbidden"]

    assert not re.search(r"\b(16|32|40|63)\s*A\s*(sigorta|mcb|rcbo)", HTML, re.I), "Sabit koruma cihazı boyutlandırması yayımlanmamalı"
    print("ALO186 EV ev şarj gücü/süre/altyapı v352: PASS")


if __name__ == "__main__":
    main()
