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
    "/hesaplama/elektrik-bakim-takvimi/": ("alo186/hesaplama/elektrik-bakim-takvimi/index.html", "calculator"),
    "/hizmet-secici/": ("alo186/hizmet-secici/index.html", "tool"),
    "/hesaplama/urun-sonrasi-guvenlik-kontrolu/": ("alo186/hesaplama/urun-sonrasi-guvenlik-kontrolu/index.html", "calculator"),
}


def jsonld_types(html: str) -> set[str]:
    result: set[str] = set()
    for raw in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        payload = json.loads(raw)
        items = payload.get("@graph", [payload]) if isinstance(payload, dict) else []
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("@type"), str):
                result.add(item["@type"])
    return result


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 45
    route_map = {item["canonicalPath"]: item for item in manifest["routes"]}

    for route, (source, route_type) in ROUTES.items():
        item = route_map.get(route)
        assert item, route
        assert item["source"] == source
        assert item["type"] == route_type
        html = (REPO_ROOT / source).read_text(encoding="utf-8")
        lower = html.casefold()
        assert f'rel="canonical" href="https://www.alo186.com{route}"' in html
        assert len(re.findall(r"<h1\b", html, re.I)) == 1
        assert {"WebApplication", "FAQPage", "BreadcrumbList"}.issubset(jsonld_types(html))
        assert "amazon.com" not in lower and "amzn." not in lower
        assert not re.search(r"\b\d{2,}[.,]?\d*\s*(?:tl|₺|usd|eur|€|\$)\b", lower)
        assert 'type="email"' not in lower and 'type="tel"' not in lower and 'type="file"' not in lower
        assert "açık adres" not in lower or "istenmez" in lower or "almadan" in lower
        assert "bağımsız" in lower and ("edaş" in lower or "resmî" in lower or "ürün satmaz" in lower)

    maintenance = (REPO_ROOT / ROUTES["/hesaplama/elektrik-bakim-takvimi/"][0]).read_text(encoding="utf-8")
    assert "alo186.maintenance.v1" in maintenance
    assert "370*DAY" in maintenance
    assert "localStorage.removeItem" in maintenance
    assert "text/calendar" in maintenance and "application/json" in maintenance
    assert "satın almama" in maintenance.casefold() or "satın almayın" in maintenance.casefold()
    assert all(term in maintenance for term in ["RCD", "SPD", "UPS", "Jeneratör", "Topraklama", "GES", "EV", "Harmonik"])

    selector = (REPO_ROOT / ROUTES["/hizmet-secici/"][0]).read_text(encoding="utf-8")
    assert "localStorage" not in selector and "sessionStorage" not in selector
    assert "Ücretli hizmet gerekmez" in selector or "ücretli hizmet gerektirmez" in selector
    assert "risk==='danger'" in selector
    for path in [
        "/edas-bul",
        "/hizmetler/otel-elektrik-surekliligi-denetimi/",
        "/hizmetler/elektrik-teklif-teknik-inceleme/",
        "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        "/hizmetler/elektrik-surekliligi-izleme/",
        "/amazon-elektrik-urunleri",
    ]:
        assert path in selector

    aftercare = (REPO_ROOT / ROUTES["/hesaplama/urun-sonrasi-guvenlik-kontrolu/"][0]).read_text(encoding="utf-8")
    assert "alo186.aftercare.v1" in aftercare
    assert "365*DAY" in aftercare
    assert "doğrudan amazon veya mağaza bağlantısı yoktur" in aftercare.casefold()
    assert "satış ortaklığı" in aftercare.casefold()
    assert "kullanımı ve şarjı durdurun" in aftercare.casefold()
    assert "mevcut ürünle devam edin" in aftercare.casefold()
    assert "text/calendar" in aftercare

    injector = (REPO_ROOT / "alo186/deployment/inject_retention_growth.py").read_text(encoding="utf-8")
    pipeline = (REPO_ROOT / "alo186/deployment/inject_shortlist_growth.py").read_text(encoding="utf-8")
    for marker in [
        "data-alo186-retention-tools",
        "data-alo186-retention-growth",
        "data-alo186-aftercare-entry",
        "data-alo186-service-fit-entry",
    ]:
        assert marker in injector
    assert "directAffiliateLinksAdded" in injector and "rawPersonalDataCollected" in injector
    assert "noPaidServiceResultSupported" in injector
    assert "run_retention_growth" in pipeline
    assert pipeline.index("run_revenue_trust_proof(site, base_path)") < pipeline.index("run_retention_growth(site, base_path)")

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "actions": ["maintenance_calendar", "service_fit_selector", "product_aftercare"],
        "directAffiliateLinksAdded": 0,
        "rawPersonalDataCollected": False,
        "noPaidServiceResultSupported": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
