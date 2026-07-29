from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTES = {
    "movein": "/hesaplama/yeni-ev-elektrik-guvenligi-devir-kontrolu/",
    "restart": "/hesaplama/kesinti-sonrasi-guvenli-yeniden-baslatma-plani/",
    "baseload": "/hesaplama/gece-baz-yuk-standby-tuketim-deneyi/",
}
PAGES = {key: REPO_ROOT / "alo186" / route.strip("/") / "index.html" for key, route in ROUTES.items()}


def jsonld_types(html: str) -> set[str]:
    found: set[str] = set()
    for block in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S):
        payload = json.loads(block)
        stack = [payload]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                current = value.get("@type")
                if isinstance(current, str):
                    found.add(current)
                elif isinstance(current, list):
                    found.update(str(item) for item in current)
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)
    return found


def script(html: str) -> str:
    blocks = re.findall(r'<script(?![^>]+type=["\']application/ld\+json["\'])[^>]*>(.*?)</script>', html, re.I | re.S)
    assert len(blocks) == 1, len(blocks)
    return blocks[0]


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 67
    routes = {item["canonicalPath"]: item for item in manifest["routes"]}
    for key, route in ROUTES.items():
        assert route in routes, key
        assert routes[route]["source"] == f"alo186/{route.strip('/')}/index.html"
        assert routes[route]["type"] == "calculator"

    pages = {key: path.read_text(encoding="utf-8") for key, path in PAGES.items()}
    for key, html in pages.items():
        lower = html.casefold()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= jsonld_types(html), key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert "fiyat, stok, puan" in lower, key
        assert "resmî" in lower or "resmi" in lower, key
        assert "adres" in lower and ("kişi" in lower or "işletme adı" in lower), key
        assert "localstorage" in lower, key

    movein = script(pages["movein"])
    assert "hazard=$('shock').checked||$('burn').checked||$('heat').checked||$('open').checked" in movein
    assert "fixedIssue=$('panel').value==='issue'||$('rcd').value==='failed'||$('loose').checked||$('majorExtension').checked||$('damagedCord').checked" in movein
    assert "commercial= !hazard&&!fixedIssue&&!fixedUnknown" in movein
    assert "existing==='partial'||existing==='none'" in movein
    assert "Affiliate ve ürün yönlendirmesi bu sonuçta kapalıdır" in movein
    assert "Mevcut ürünlerle devam" in movein
    assert "new Date(Date.now()+TTL)" in movein

    restart = script(pages["restart"])
    assert "hazard=$('smoke').checked||$('shock').checked||$('voltage').checked||$('line').checked" in restart
    assert "repeated=['monthly','weekly'].includes" in restart
    assert "commercial=!hazard&&repeated&&$('existing').value==='gap'" in restart
    assert "Tek olay veya tek yüksek ölçüm" not in restart
    assert "Yeniden başlatmayı durdur" in restart
    assert "Pano, ATS, UPS veya jeneratör işlemini yalnız yetkili prosedüre göre yapın" in restart
    assert "Mevcut plan ve yedek güç yeterliyse yeni ürün satın almayın" in restart

    baseload = script(pages["baseload"])
    assert "x.expiresAt" in baseload
    assert "Date.parse(x.expiresAt)>now" in baseload
    assert "new Date(Date.now()+TTL).toISOString()" in baseload
    assert "x.date<=latest.date" in baseload
    assert "previous.length>=2" in baseload
    assert "recent.avgW>=baseline.avgW*1.2" in baseload
    assert "latest.avgW>=baseline.avgW*1.2" in baseload
    assert "commercial=!hazard&&repeatedHigh&&latest.candidate==='lowrisk'&&latest.meter==='none'" in baseload
    assert "Tek ölçüm yeni ürün kararı değildir" in baseload
    assert "Mevcut enerji ölçer yeterli; yeni ürün satın almayın" in baseload
    assert "items:items.slice(-MAX)" in baseload

    injector = (DEPLOYMENT / "inject_growth_run19.py").read_text(encoding="utf-8")
    shortlist = (DEPLOYMENT / "inject_shortlist_growth.py").read_text(encoding="utf-8")
    for token in ["growthRun19", "fixedWiringCommerceClosed", "singleEventCommerceClosed", "singleHighMeasurementCommerceClosed", "nightBaseloadRecordLimit"]:
        assert token in injector
    assert "from inject_growth_run19 import run as run_growth_run19" in shortlist
    assert "growth_run19 = run_growth_run19(site, base_path)" in shortlist
    assert '"growthRun19": growth_run19' in shortlist

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "routes": list(ROUTES.values()),
        "rawPersonalDataCollected": False,
        "directAffiliateLinksAdded": 0,
        "hazardCommerceClosed": True,
        "fixedWiringCommerceClosed": True,
        "singleEventCommerceClosed": True,
        "singleHighMeasurementCommerceClosed": True,
        "noBuyOutcomePreserved": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
