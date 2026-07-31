#!/usr/bin/env python3
"""ALO186 home energy measurement growth v145 release contract."""
from __future__ import annotations
import json, re, shutil, subprocess, tempfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CALCULATORS = [
    ROOT / "alo186/hesaplama/priz-tipi-enerji-olcer-akilli-priz-uygunluk/index.html",
    ROOT / "alo186/hesaplama/cihaz-bekleme-tuketimi-yedi-gun-olcum-plani/index.html",
]
HUB = ROOT / "alo186/sektor-rehberi/ev-cihazlari-enerji-olcum-ve-tasarruf-merkezi/index.html"
OVERLAY = ROOT / "alo186/deployment/routing-overlays/145-home-energy-measurement.json"
AUDIT = ROOT / "alo186/audits/home-energy-measurement-growth-v145-2026-07-31.md"
EXPECTED = {
    "/hesaplama/priz-tipi-enerji-olcer-akilli-priz-uygunluk/": CALCULATORS[0],
    "/hesaplama/cihaz-bekleme-tuketimi-yedi-gun-olcum-plani/": CALCULATORS[1],
    "/sektor-rehberi/ev-cihazlari-enerji-olcum-ve-tasarruf-merkezi/": HUB,
}

def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))
def require(condition: bool, message: str) -> None:
    if not condition: raise AssertionError(message)
def scripts(html: str) -> list[str]:
    return [b for a,b in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.I|re.S) if "application/ld+json" not in a.lower() and b.strip()]
def check_js(path: Path, html: str) -> None:
    node=shutil.which("node"); require(node is not None,"Node.js is required")
    for i,script in enumerate(scripts(html),1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as tmp:
            tmp.write(script); name=Path(tmp.name)
        try:
            r=subprocess.run([node,"--check",str(name)],text=True,capture_output=True)
            require(r.returncode==0,f"JS syntax failed {path} #{i}: {r.stderr}")
        finally: name.unlink(missing_ok=True)
def common(path: Path, canonical: str) -> str:
    require(path.is_file(),f"Missing file: {path}")
    html=path.read_text(encoding="utf-8"); lower=fold(html)
    require(f'href="https://alo186.com{canonical}"' in html,f"Canonical mismatch: {path}")
    require("bagımsız" in lower,f"Independent disclosure missing: {path}")
    require("resmi kurum" in lower or "edas" in lower,f"Official guard missing: {path}")
    require(all(x in lower for x in ("fiyat","stok","puan","garanti")),f"Commercial guard missing: {path}")
    require("localstorage" not in lower and "sessionstorage" not in lower,f"Persistent storage found: {path}")
    for token in ('"@type":"product"','"@type":"offer"',"aggregaterating",'"availability"'):
        require(token not in lower,f"Forbidden token {token}: {path}")
    check_js(path,html); return html
def main() -> None:
    overlay=json.loads(OVERLAY.read_text(encoding="utf-8")); require(overlay.get("version")==145,"Overlay version")
    routes={x["canonicalPath"]:x for x in overlay["routes"]}; require(set(routes)==set(EXPECTED),"Route set")
    for canonical,path in EXPECTED.items():
        require(routes[canonical]["source"]==str(path.relative_to(ROOT)),f"Source mismatch {canonical}")
    for canonical,path in list(EXPECTED.items())[:2]:
        html=common(path,canonical); lower=fold(html)
        require("yeni urun almayın" in lower,f"Buy-nothing missing: {path}")
        require("amazon satıs ortaklıgı" in lower,f"Affiliate disclosure missing: {path}")
        require('rel="sponsored nofollow noopener"' in html,f"Affiliate rel missing: {path}")
        require("amazon.com.tr/s?k=" in lower,f"Category search missing: {path}")
        require(all(f'id="{x}"' in html for x in ("need","spec","ad")),f"Confirmations missing: {path}")
        require("hazard" in lower and "scope" in lower,f"Safety inputs missing: {path}")
        require("kritik" in lower and any(x in lower for x in ("ısıtıcı","isıtıcı","ısıtma","ısıtma")),f"High-risk exclusions missing: {path}")
    h=common(HUB,"/sektor-rehberi/ev-cihazlari-enerji-olcum-ve-tasarruf-merkezi/"); lower=fold(h)
    require("amazon.com.tr" not in lower,"Hub Amazon destination")
    require('rel="sponsored nofollow noopener"' not in h,"Hub affiliate rel")
    require("dogrudan affiliate baglantısı yoktur" in lower,"Hub disclosure")
    require("kisisel veri" in lower and "json" in lower and ".ics" in lower,"Hub privacy/exports")
    require(all(x in h for x in ("7","30","90")),"Hub intervals")
    a=fold(AUDIT.read_text(encoding="utf-8"))
    for phrase in ("arama niyeti","icerik boslugu","kullanıcı yolculugu","affiliate urun kategorileri","donusum noktaları","tekrar ziyaret nedenleri","beklenen kullanıcı faydası","beklenen gelir etkisi"):
        require(phrase in a,f"Audit missing {phrase}")
    print("ALO186 home energy measurement growth v145 contract: PASS")
if __name__=="__main__": main()
