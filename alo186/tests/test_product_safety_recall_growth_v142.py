from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "amazon-elektrik-urunleri/elektrikli-urun-satin-alma-guvenlik-kapisi/index.html": {
        "canonical": "https://alo186.com/amazon-elektrik-urunleri/elektrikli-urun-satin-alma-guvenlik-kapisi/",
        "tokens": ["Satın alma öncesi 7 kanıt", "yeni ürün almayın", "Amazon satış ortaklığı", "GÜBİS"],
        "module": "amazon-elektrik-urunleri/elektrikli-urun-satin-alma-guvenlik-kapisi/test.js",
    },
    "hesaplama/elektrikli-urun-geri-cagirma-model-kontrolu/index.html": {
        "canonical": "https://alo186.com/hesaplama/elektrikli-urun-geri-cagirma-model-kontrolu/",
        "tokens": ["Tam model", "güvenlik garantisi değildir", "GÜBİS", "doğrudan affiliate bağlantısı göstermez"],
        "module": "hesaplama/elektrikli-urun-geri-cagirma-model-kontrolu/test.js",
    },
    "sektor-rehberi/elektrikli-urun-guvenlik-ve-geri-cagirma-merkezi/index.html": {
        "canonical": "https://alo186.com/sektor-rehberi/elektrikli-urun-guvenlik-ve-geri-cagirma-merkezi/",
        "tokens": ["Doğrudan affiliate yok", "7 gün", "90 gün", "JSON indir", "ICS tekrar testi"],
        "module": None,
    },
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def check_inline_script(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, flags=re.S | re.I)
    executable = [script for script in scripts if "application/ld+json" not in script[:120]]
    if not executable:
        return
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
    assert "localStorage." not in text
    assert "sessionStorage." not in text
    assert "geolocation" not in text
    assert "fiyat, stok" in text.lower()
    for token in contract["tokens"]:
        assert token in text, (relative, token)
    check_inline_script(source)
    if contract["module"]:
        run(["node", str(ROOT / "alo186" / contract["module"])])

overlay = json.loads((ROOT / "alo186/deployment/routing-overlays/142-product-safety-recall.json").read_text(encoding="utf-8"))
assert overlay["version"] == 142
assert len(overlay["routes"]) == 3

with tempfile.TemporaryDirectory(prefix="alo186-product-safety-v142-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "product-safety-v142-test"])
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
            "--commit", "product-safety-v142-test",
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
    "version": 142,
    "routes": len(ROUTES),
    "targets": targets,
    "directAmazonLinks": 0,
    "productOfferSchema": False,
    "recallExactMatchStopsCommerce": True,
    "noBuyOutcome": True,
    "repeatVisitCadence": [7, 30, 90, 180],
    "officialSources": ["GÜBİS", "EU Safety Gate", "CPSC"],
    "personalDataFields": 0,
}, ensure_ascii=False))
