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
    "safety": "/hesaplama/urun-guvenlik-duyurusu-kontrolu/",
    "passport": "/hesaplama/urun-teknik-belge-pasaportu/",
    "kit": "/hesaplama/kesinti-kiti-donemsel-kontrolu/",
}
FILES = {key: REPO_ROOT / "alo186" / route.strip("/") / "index.html" for key, route in ROUTES.items()}
EXPECTED_SOURCES = {key: f"alo186/{route.strip('/')}/index.html" for key, route in ROUTES.items()}


def jsonld_types(text: str) -> set[str]:
    types: set[str] = set()
    for block in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.I | re.S):
        payload = json.loads(block)
        stack = [payload]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                value = item.get("@type")
                if isinstance(value, str):
                    types.add(value)
                elif isinstance(value, list):
                    types.update(str(entry) for entry in value)
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return types


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 66
    effective = {item["canonicalPath"]: item for item in manifest["routes"]}
    for key, route in ROUTES.items():
        assert route in effective, route
        assert effective[route]["source"] == EXPECTED_SOURCES[key]
        assert effective[route]["type"] == "calculator"

    pages = {key: path.read_text(encoding="utf-8") for key, path in FILES.items()}
    for key, html in pages.items():
        lower = html.casefold()
        assert html.count("<h1") == 1, key
        assert f'https://www.alo186.com{ROUTES[key]}' in html, key
        assert {"WebApplication", "FAQPage", "BreadcrumbList"} <= jsonld_types(html), key
        assert "amazon.com" not in lower and "amzn." not in lower, key
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower, key
        assert 'type="email"' not in lower and 'type="tel"' not in lower, key
        assert "fiyat" in lower and "stok" in lower and "garanti" in lower, key
        assert "alo186" in lower and ("resmî" in lower or "resmi" in lower), key

    safety = pages["safety"]
    safety_lower = safety.casefold()
    assert "guvensizurun.ticaret.gov.tr/bildirim/detaysorgu" in safety_lower
    assert "ec.europa.eu/safety-gate-alerts" in safety_lower
    assert "kayıt yokluğu güvenlik onayı değildir" in safety_lower
    assert "affiliate ve yeni ürün yönlendirmesi kapalıdır" in safety_lower
    assert "productSafetyWatch.v1" in safety
    assert "TTL=365*86400000" in safety
    assert "expiresAt:new Date(Date.now()+TTL)" in safety
    assert "marka/model metni yalnız kaydetme kutusu seçilirse" in safety_lower
    assert "30 günlük yeniden kontrol" in safety_lower

    passport = pages["passport"]
    passport_lower = passport.casefold()
    for token in [
        "tam model kodu ve varyant",
        "üretici teknik veri sayfası",
        "desteklenmeyen yük",
        "üretici/ithalatçı kimliği",
        "mevcut ürün güvenli ve ihtiyacı karşılıyor",
        "satın alma yok",
        "affiliate ve kategori yolu kapalıdır",
        "commerceReady:commerce",
        "commercialFieldsUsed:[]",
    ]:
        assert token.casefold() in passport_lower, token
    assert "complete&&safety==='clear'&&need&&disclosure" in passport
    assert "existing==='gap'||existing==='none'" in passport
    assert "localStorage.setItem(K" in passport
    assert "expiresAt:new Date(Date.now()+30*86400000)" in passport
    assert "/hesaplama/akim-korumali-grup-priz-uygunluk/" in passport
    assert "/hesaplama/power-station-kapasite-eps-uygunluk/" in passport

    kit = pages["kit"]
    kit_lower = kit.casefold()
    assert "ilk başarısız testte ürün önerilmez" in kit_lower
    assert "bakım sonrası tekrar test de başarısız" in kit_lower
    assert "bu sonuçta bütün affiliate ve yeni ürün yolları kapalıdır" in kit_lower
    assert "replace=ids.filter(id=>values[id]==='fail2')" in kit
    assert "review=ids.filter(id=>['untested','fail1'].includes(values[id]))" in kit
    assert "affiliateCategories:hazards.length?[]:replace" in kit
    assert "TTL=730*86400000" in kit
    assert "MAX=8" in kit
    assert "90 günlük tekrar" in kit_lower
    assert "satın almama sonucu" in kit_lower

    injector = (DEPLOYMENT / "inject_growth_run18.py").read_text(encoding="utf-8")
    pipeline = (DEPLOYMENT / "inject_shortlist_growth.py").read_text(encoding="utf-8")
    for token in [
        "growthRun18",
        "data-alo186-growth-run18-entry",
        "officialSafetySources",
        "hazardCommerceClosed",
        "firstFailureCommerceClosed",
        "noBuyOutcomePreserved",
        "unverifiedCommercialFieldsUsed",
    ]:
        assert token in injector, token
    assert "from inject_growth_run18 import run as run_growth_run18" in pipeline
    assert "growth_run18 = run_growth_run18(site, base_path)" in pipeline
    assert '"growthRun18": growth_run18' in pipeline
    assert pipeline.index("growth_run18 = run_growth_run18") > pipeline.index("growth_run15 = run_growth_run15")

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "routes": list(ROUTES.values()),
        "directAffiliateLinksAdded": 0,
        "hazardCommerceClosed": True,
        "firstFailureCommerceClosed": True,
        "noBuyOutcomePreserved": True,
        "officialSources": ["GÜBİS", "EU Safety Gate", "manufacturer official source"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
