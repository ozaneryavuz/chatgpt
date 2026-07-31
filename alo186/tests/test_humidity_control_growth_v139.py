from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "hesaplama/nem-olcer-nem-alma-cihazi-uygunluk/index.html": {
        "canonical": "https://alo186.com/hesaplama/nem-olcer-nem-alma-cihazi-uygunluk/",
        "tokens": ["yeni ürün almayın", "Amazon satış ortaklığı", "Bağıl nem", "Kaynak kontrol tarihi"],
    },
    "hesaplama/nem-alma-cihazi-kwh-drenaj-plani/index.html": {
        "canonical": "https://alo186.com/hesaplama/nem-alma-cihazi-kwh-drenaj-plani/",
        "tokens": ["kWh", "tank", "drenaj", "yeni ürün almayın", "Amazon satış ortaklığı"],
    },
    "sektor-rehberi/ev-rutubet-yogusma-tekrar-test-merkezi/index.html": {
        "canonical": "https://alo186.com/sektor-rehberi/ev-rutubet-yogusma-tekrar-test-merkezi/",
        "tokens": ["7/30/90", "Doğrudan satış yok", "JSON görev planı", ".ics"],
    },
}
AFFILIATE_APPS = (
    "alo186/hesaplama/nem-olcer-nem-alma-cihazi-uygunluk/app.js",
    "alo186/hesaplama/nem-alma-cihazi-kwh-drenaj-plani/app.js",
)


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


for relative, contract in ROUTES.items():
    source = ROOT / "alo186" / relative
    assert source.is_file(), source
    text = source.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{contract["canonical"]}">' in text
    assert "ALO186 bağımsız" in text
    assert "amazon.com.tr" not in text.lower()
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    assert "aggregateRating" not in text
    assert "availability" not in text
    assert "localStorage" not in text
    assert "sessionStorage" not in text
    assert "geolocation" not in text
    for token in contract["tokens"]:
        assert token in text, (relative, token)

for app in (
    *AFFILIATE_APPS,
    "alo186/sektor-rehberi/ev-rutubet-yogusma-tekrar-test-merkezi/app.js",
):
    run(["node", "--check", app])

for app in AFFILIATE_APPS:
    script = (ROOT / app).read_text(encoding="utf-8")
    assert 'rel="sponsored nofollow noopener"' in script, app
    assert "confirmNeed" in script and "confirmSpecs" in script and "confirmAffiliate" in script, app
    assert "amazon.com.tr" not in script.lower(), app
    assert "yeni ürün almayın" in script.lower(), app

hub_script = (ROOT / "alo186/sektor-rehberi/ev-rutubet-yogusma-tekrar-test-merkezi/app.js").read_text(encoding="utf-8")
assert "sponsored nofollow noopener" not in hub_script
assert "amazon.com.tr" not in hub_script.lower()

run(["node", "alo186/hesaplama/nem-olcer-nem-alma-cihazi-uygunluk/test.js"])
run(["node", "alo186/hesaplama/nem-alma-cihazi-kwh-drenaj-plani/test.js"])

overlay = json.loads((ROOT / "alo186/deployment/routing-overlays/139-humidity-control.json").read_text(encoding="utf-8"))
assert overlay["version"] == 139
assert len(overlay["routes"]) == 3

with tempfile.TemporaryDirectory(prefix="alo186-humidity-v139-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "humidity-v139-test"])
    for relative in ROUTES:
        assert (canonical / relative).is_file(), relative

    results = []
    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "humidity-v139-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        for relative in ROUTES:
            assert (target / relative).is_file(), (name, relative)
        results.append({"target": name, "basePath": base_path, "pages": len(list(target.rglob("*.html")))})

print(json.dumps({
    "ok": True,
    "version": 139,
    "routes": len(ROUTES),
    "targets": results,
    "directAmazonLinks": 0,
    "productOfferSchema": False,
    "tripleAffiliateConfirmation": True,
    "affiliateRel": "sponsored nofollow noopener",
    "noBuyOutcome": True,
    "repeatVisitCadence": [7, 30, 90],
    "personalDataFields": 0,
    "unverifiedCommercialFields": [],
}, ensure_ascii=False))
