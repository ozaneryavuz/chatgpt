from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTE = "/hesaplama/kacak-akim-rolesi-tip-hassasiyet-testi/"
SOURCE = "alo186/hesaplama/kacak-akim-rolesi-tip-hassasiyet-testi/index.html"


def jsonld(html: str) -> list[dict]:
    blocks = re.findall(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.I | re.S)
    return [json.loads(block) for block in blocks]


def types(payloads: list[dict]) -> set[str]:
    found: set[str] = set()
    for payload in payloads:
        nodes = payload.get("@graph", [payload]) if isinstance(payload, dict) else []
        for node in nodes:
            value = node.get("@type") if isinstance(node, dict) else None
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(str(item) for item in value)
    return found


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 76
    routes = [item for item in manifest["routes"] if item["canonicalPath"] == ROUTE]
    assert len(routes) == 1
    assert routes[0]["source"] == SOURCE
    assert routes[0]["type"] == "tool"

    page = (REPO_ROOT / SOURCE).read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/hesaplama/kacak-akim-rolesi-tip-hassasiyet-testi/app.js").read_text(encoding="utf-8")
    styles = (REPO_ROOT / "alo186/hesaplama/kacak-akim-rolesi-tip-hassasiyet-testi/styles.css").read_text(encoding="utf-8")
    hub = (REPO_ROOT / "alo186/hesaplama/index.html").read_text(encoding="utf-8")

    assert page.count("<h1") == 1
    assert f'<link rel="canonical" href="https://www.alo186.com{ROUTE}">' in page
    assert {"WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"} <= types(jsonld(page))
    assert page.count("<details>") >= 4
    assert "IEC 62423" in page and "IEC 62955" in page
    assert "empower.abb.com" in page and "se.com" in page and "webstore.iec.ch" in page
    assert "30 Temmuz 2026" in page
    assert "Sabit pano cihazında doğrudan affiliate yönlendirmesi kapalıdır" in page
    assert "Amazon veya mağaza bağlantısı yoktur" in page
    assert "amazon.com" not in page.casefold() and "amzn." not in page.casefold()
    assert 'type="email"' not in page.casefold() and 'type="tel"' not in page.casefold()
    assert "ad, adres" not in page.casefold()
    assert "112" in page and "yetkili elektrikçi" in page

    assert "localStorage" not in app and "sessionStorage" not in app
    assert "directAffiliateLinks:false" in app
    assert "noBuyOutcomePreserved:true" in app
    assert "A_F_RDC_OR_B" in app and "F_REVIEW" in app and "B_REVIEW" in app
    assert "30 mA ek korumanın yerine otomatik olarak geçmez" in app
    assert "Ürün veya tip seçimi durduruldu" in app
    assert "textContent" in app
    assert "innerHTML" not in app
    assert len(styles) > 1800

    assert ROUTE in hub
    assert "32 çekirdek araç" in hub
    assert "Kaçak Akım Rölesi Tip ve Hassasiyet Testi" in hub

    completed = subprocess.run(
        ["node", "alo186/hesaplama/kacak-akim-rolesi-tip-hassasiyet-testi/app.test.js"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["directAffiliateLinks"] is False
    assert result["noBuyOutcomePreserved"] is True

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "mobileResponsive": "@media(max-width:700px)" in styles,
        "personalDataCollected": False,
        "directAffiliateLinks": 0,
        "professionalServiceConversion": True,
        "emergencyCommerceClosed": True,
        "sourceVerificationDate": "2026-07-30",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
