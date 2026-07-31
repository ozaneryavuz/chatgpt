from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "hesaplama/seyahat-priz-adaptoru-voltaj-donusturucu-uygunluk/index.html": {
        "canonical": "https://alo186.com/hesaplama/seyahat-priz-adaptoru-voltaj-donusturucu-uygunluk/",
        "tokens": ["Seyahat adaptörü voltaj veya frekans dönüştürmez", "Topraklama", "yeni ürün almayın", "Amazon satış ortaklığı"],
        "affiliate": True,
        "module": "hesaplama/seyahat-priz-adaptoru-voltaj-donusturucu-uygunluk/test.js",
    },
    "hesaplama/sac-kurutma-kettle-seyahat-gerilim-uygunluk/index.html": {
        "canonical": "https://alo186.com/hesaplama/sac-kurutma-kettle-seyahat-gerilim-uygunluk/",
        "tokens": ["Dönüştürücü satışı yok", "tıraş prizleri", "yeni ürün almayın", "Amazon satış ortaklığı"],
        "affiliate": True,
        "module": "hesaplama/sac-kurutma-kettle-seyahat-gerilim-uygunluk/test.js",
    },
    "sektor-rehberi/yurt-disi-seyahat-priz-sarj-tekrar-test-merkezi/index.html": {
        "canonical": "https://alo186.com/sektor-rehberi/yurt-disi-seyahat-priz-sarj-tekrar-test-merkezi/",
        "tokens": ["7/30/90", "Doğrudan affiliate yok", "JSON görev planı", "ICS tekrar testi"],
        "affiliate": False,
        "module": None,
    },
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def check_inline_script(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, flags=re.S | re.I)
    executable = [script for script in scripts if "application/ld+json" not in script[:120]]
    assert executable, source
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(executable[-1])
        temp = Path(handle.name)
    try:
        subprocess.run(["node", "--check", str(temp)], check=True)
    finally:
        temp.unlink(missing_ok=True)


for relative, contract in ROUTES.items():
    source = ROOT / "alo186" / relative
    assert source.is_file(), source
    text = source.read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{contract["canonical"]}">' in text
    assert "ALO186 bağımsız" in text
    assert "resmî kurum" in text or "resmî otorite" in text
    assert "amazon.com.tr" not in text.lower()
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    assert "aggregateRating" not in text
    assert "availability" not in text
    assert "localStorage" not in text
    assert "sessionStorage" not in text
    assert "geolocation" not in text
    assert "fiyat, stok" in text.lower()
    for token in contract["tokens"]:
        assert token in text, (relative, token)
    if contract["affiliate"]:
        assert 'rel="sponsored nofollow noopener"' in text
        assert "confirmNeed" in text and "confirmAffiliate" in text
    else:
        assert 'rel="sponsored nofollow noopener"' not in text
    check_inline_script(source)
    if contract["module"]:
        run(["node", str(ROOT / "alo186" / contract["module"])])

overlay = json.loads((ROOT / "alo186/deployment/routing-overlays/141-travel-adapter-voltage.json").read_text(encoding="utf-8"))
assert overlay["version"] == 141
assert len(overlay["routes"]) == 3

with tempfile.TemporaryDirectory(prefix="alo186-travel-adapter-v141-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "travel-adapter-v141-test"])
    for relative in ROUTES:
        assert (canonical / relative).is_file(), relative

    targets = []
    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "travel-adapter-v141-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        for relative in ROUTES:
            assert (target / relative).is_file(), (name, relative)
        targets.append({"target": name, "basePath": base_path})

print(json.dumps({
    "ok": True,
    "version": 141,
    "routes": len(ROUTES),
    "targets": targets,
    "directAmazonLinks": 0,
    "productOfferSchema": False,
    "tripleAffiliateConfirmation": True,
    "affiliateRel": "sponsored nofollow noopener",
    "voltageConverterAffiliate": False,
    "noBuyOutcome": True,
    "repeatVisitCadence": [7, 30, 90],
    "personalDataFields": 0,
}, ensure_ascii=False))
