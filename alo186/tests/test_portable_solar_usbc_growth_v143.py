from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTES = {
    "hesaplama/katlanabilir-gunes-paneli-power-station-uygunluk/index.html": {
        "canonical": "https://alo186.com/hesaplama/katlanabilir-gunes-paneli-power-station-uygunluk/",
        "tokens": ["Voc", "Isc", "Mevcut set yeterli — yeni ürün almayın", "Amazon satış ortaklığı bağlantısı"],
        "affiliate": True,
    },
    "hesaplama/usb-c-hub-goruntu-pd-uygunluk/index.html": {
        "canonical": "https://alo186.com/hesaplama/usb-c-hub-goruntu-pd-uygunluk/",
        "tokens": ["DisplayPort Alt Mode", "PD geçiş", "Mevcut hub yeterli — yeni ürün almayın", "Amazon satış ortaklığı bağlantısı"],
        "affiliate": True,
    },
    "sektor-rehberi/tasinabilir-enerji-ve-dijital-cihaz-uyumluluk-merkezi/index.html": {
        "canonical": "https://alo186.com/sektor-rehberi/tasinabilir-enerji-ve-dijital-cihaz-uyumluluk-merkezi/",
        "tokens": ["Doğrudan affiliate bağlantısı yok", "JSON indir", "ICS tekrar testi", "90 gün"],
        "affiliate": False,
    },
}


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def check_inline_scripts(source: Path) -> None:
    text = source.read_text(encoding="utf-8")
    scripts = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", text, flags=re.S | re.I)
    for script in scripts:
        if '"@context"' in script[:240] and 'schema.org' in script[:320]:
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
            handle.write(script)
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
    assert "resmî kurum" in text or "standart kuruluşu" in text
    assert "fiyat, stok" in text.lower()
    assert '"@type":"Product"' not in text
    assert '"@type":"Offer"' not in text
    assert "aggregateRating" not in text
    assert "availability" not in text
    assert "localStorage." not in text
    assert "sessionStorage." not in text
    assert "navigator.geolocation" not in text
    for token in contract["tokens"]:
        assert token in text, (relative, token)
    if contract["affiliate"]:
        assert "amazon.com.tr" in text.lower()
        assert "tag=alo186rehber-21" in text
        assert 'rel="sponsored nofollow noopener"' in text
        assert all(token in text for token in ('id="need"', 'id="spec"', 'id="ad"'))
    else:
        assert "amazon.com.tr" not in text.lower()
    check_inline_scripts(source)

overlay_path = ROOT / "alo186/deployment/routing-overlays/143-portable-solar-usbc-growth.json"
overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
assert overlay["version"] == 143
assert len(overlay["routes"]) == 3

with tempfile.TemporaryDirectory(prefix="alo186-portable-solar-usbc-v143-") as folder:
    canonical = Path(folder) / "canonical"
    run([sys.executable, "alo186/deployment/build_static_site.py", "--output", str(canonical), "--commit", "portable-solar-usbc-v143-test"])
    for relative in ROUTES:
        assert (canonical / relative).is_file(), relative

    for name, base_path in (("custom", ""), ("project", "/chatgpt")):
        target = Path(folder) / name
        subprocess.run(["cp", "-a", str(canonical), str(target)], check=True)
        run([
            sys.executable,
            "alo186/deployment/prepare_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
            "--repository", "ozaneryavuz/chatgpt",
            "--commit", "portable-solar-usbc-v143-test",
        ])
        run([
            sys.executable,
            "alo186/deployment/smoke_github_pages.py",
            "--site", str(target),
            "--base-path", base_path,
        ])
        for relative in ROUTES:
            assert (target / relative).is_file(), (name, relative)

print(json.dumps({
    "ok": True,
    "version": 143,
    "routes": len(ROUTES),
    "affiliateRoutes": 2,
    "directAmazonLinksAfterConsent": 2,
    "noBuyOutcome": True,
    "personalDataFields": 0,
    "repeatVisitCadence": [7, 30, 90],
    "officialTechnicalSources": ["USB-IF", "VESA", "manufacturer manuals"],
}, ensure_ascii=False))
