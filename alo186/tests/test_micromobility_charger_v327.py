from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "alo186/deployment"))
from build_static_site import load_effective_manifest

ROUTE = "/hesaplama/elektrikli-bisiklet-scooter-sarj-cihazi-uygunluk/"
SOURCE = "alo186/hesaplama/elektrikli-bisiklet-scooter-sarj-cihazi-uygunluk/index.html"


def main() -> None:
    manifest = load_effective_manifest(ROOT)
    matches = [r for r in manifest["routes"] if r["canonicalPath"] == ROUTE]
    assert len(matches) == 1
    assert matches[0]["source"] == SOURCE
    assert manifest["version"] >= 90

    directory = ROOT / SOURCE.rsplit("/", 1)[0]
    page = (directory / "index.html").read_text(encoding="utf-8")
    app = (directory / "app.js").read_text(encoding="utf-8")
    css = (directory / "styles.css").read_text(encoding="utf-8")

    assert 'rel="canonical" href="https://alo186.com' + ROUTE + '"' in page
    for token in ["WebApplication", "DefinedTermSet", "FAQPage", "BreadcrumbList"]:
        assert token in page
    for token in ["CPSC", "Universal şarj cihazı", "satış ortaklığı", "alo186rehber-21"]:
        assert token in page or token in app
    for forbidden in ["localStorage", "sessionStorage", "geolocation", "fetch("]:
        assert forbidden not in page + app
    for personal in ["Telefon", "E-posta", "Adres", "Konum", "T.C."]:
        assert personal not in page
    assert "sponsored nofollow noopener" in app
    assert "price" not in app and "stock" not in app and "aggregateRating" not in page
    assert "@media(max-width:820px)" in css
    assert "@media(max-width:560px)" in css
    assert "prefers-reduced-motion" in css
    assert "aria-live=\"polite\"" in page

    completed = subprocess.run(
        ["node", str(directory / "app.test.js")], cwd=ROOT, check=True, capture_output=True, text=True
    )
    payload = json.loads(completed.stdout)
    assert payload["scenarios"] >= 18
    assert payload["noBuyPreserved"] is True

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "route": ROUTE,
        "decisionScenarios": payload["scenarios"],
        "personalDataRequested": False,
        "directAffiliateGate": "three-confirmation",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
