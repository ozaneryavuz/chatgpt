from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "hesaplama/aa-aaa-sarjli-pil-sarj-cihazi-uygunluk/index.html": {
        "canonical": "https://alo186.com/hesaplama/aa-aaa-sarjli-pil-sarj-cihazi-uygunluk/",
        "tokens": ["1,2 V NiMH", "yeni ürün almayın", "Amazon satış ortaklığı", "sponsored nofollow noopener"],
    },
    "hesaplama/sarjli-pil-seti-dongu-planlayici/index.html": {
        "canonical": "https://alo186.com/hesaplama/sarjli-pil-seti-dongu-planlayici/",
        "tokens": ["en küçük döngü", "Mevcut sağlam yedek", "yeni ürün almayın", "Amazon satış ortaklığı"],
    },
    "sektor-rehberi/aa-aaa-pil-sureklilik-test-merkezi/index.html": {
        "canonical": "https://alo186.com/sektor-rehberi/aa-aaa-pil-sureklilik-test-merkezi/",
        "tokens": ["7/30/90", "Doğrudan satış yok", "JSON görev planı", ".ics"],
    },
}


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
    "alo186/hesaplama/aa-aaa-sarjli-pil-sarj-cihazi-uygunluk/app.js",
    "alo186/hesaplama/sarjli-pil-seti-dongu-planlayici/app.js",
    "alo186/sektor-rehberi/aa-aaa-pil-sureklilik-test-merkezi/app.js",
):
    run(["node", "--check", app])

run(["node", "alo186/hesaplama/aa-aaa-sarjli-pil-sarj-cihazi-uygunluk/test.js"])
run(["node", "alo186/hesaplama/sarjli-pil-seti-dongu-planlayici/test.js"])

overlay = json.loads((ROOT / "alo186/deployment/routing-overlays/138-battery-continuity.json").read_text(encoding="utf-8"))
assert overlay["version"] == 138
assert len(overlay["routes"]) == 3

with tempfile.TemporaryDirectory(prefix="alo186-battery-v138-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "battery-v138-test"])
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
            "--commit", "battery-v138-test",
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
    "version": 138,
    "routes": len(ROUTES),
    "targets": results,
    "directAmazonLinks": 0,
    "productOfferSchema": False,
    "tripleAffiliateConfirmation": True,
    "noBuyOutcome": True,
    "repeatVisitCadence": [7, 30, 90],
    "personalDataFields": 0,
}, ensure_ascii=False))
