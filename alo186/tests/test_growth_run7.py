from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ROUTES = {
    "/hesaplama/7-gunluk-cihaz-tuketim-deneyi/": (
        "alo186/hesaplama/7-gunluk-cihaz-tuketim-deneyi/index.html",
        "calculator",
    ),
    "/hesaplama/elektrikci-is-emri-ozeti/": (
        "alo186/hesaplama/elektrikci-is-emri-ozeti/index.html",
        "business-tool",
    ),
}


def plain(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def one(html: str, tag: str) -> str:
    found = re.findall(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    assert len(found) == 1, (tag, len(found))
    return plain(found[0])


def schemas(html: str) -> list[dict]:
    result: list[dict] = []
    for raw in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        payload = json.loads(raw)
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            result.extend(item for item in payload["@graph"] if isinstance(item, dict))
        elif isinstance(payload, dict):
            result.append(payload)
    return result


def visible_markup(html: str) -> str:
    return re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.I | re.S)


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 48
    route_map = {item["canonicalPath"]: item for item in manifest["routes"]}
    titles: set[str] = set()
    h1s: set[str] = set()

    for route, (source, route_type) in ROUTES.items():
        assert route in route_map
        assert route_map[route]["source"] == source
        assert route_map[route]["type"] == route_type
        html = (REPO_ROOT / source).read_text(encoding="utf-8")
        lower = html.casefold()
        visible_lower = visible_markup(html).casefold()
        title = one(html, "title")
        h1 = one(html, "h1")
        assert title not in titles and h1 not in h1s
        titles.add(title)
        h1s.add(h1)
        assert f'https://www.alo186.com{route}' in html
        types = {item.get("@type") for item in schemas(html)}
        assert {"WebApplication", "FAQPage", "BreadcrumbList"}.issubset(types)
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower and "amzn." not in lower
        assert not re.search(r"\b\d{2,}[.,]?\d*\s*(?:tl|₺|usd|eur|€|\$)\b", lower)
        for forbidden in ["aggregaterating", '"price"', '"pricecurrency"', '"offers"']:
            assert forbidden not in lower
        assert "satın almama" in lower or "mevcut cihaz ihtiyacı" in lower or "gereksiz parça" in lower
        assert not re.search(r'<input\b[^>]*\btype=["\']text["\']', visible_lower)
        assert not re.search(r"<textarea\b", visible_lower)

    experiment = (REPO_ROOT / ROUTES["/hesaplama/7-gunluk-cihaz-tuketim-deneyi/"][0]).read_text(encoding="utf-8")
    assert "alo186.deviceConsumptionExperiment.v1" in experiment
    assert "safePlug" in experiment and "affiliateEligible" in experiment
    assert "/amazon-elektrik-urunleri/akilli-priz-enerji-olcer-secimi" in experiment
    assert "Reklam / satış ortaklığı açıklaması" in experiment
    assert "Sabit bağlı, yüksek güçlü" in experiment
    assert "text/calendar" in experiment and "application/json" in experiment

    workorder = (REPO_ROOT / ROUTES["/hesaplama/elektrikci-is-emri-ozeti/"][0]).read_text(encoding="utf-8")
    assert "alo186.electricianWorkOrder.v1" in workorder
    assert "Ticari yönlendirme kapatıldı" in workorder
    assert 'href="tel:112"' in workorder and 'href="tel:186"' in workorder
    assert "paid ranking" not in workorder.casefold()
    assert "ödeme sıralamayı satın almamalıdır" in workorder
    assert "localStorage" not in workorder and "sessionStorage" not in workorder
    assert "/hesaplama/teknik-teklif-kapsam-karsilastirma/" in workorder

    injector = (DEPLOYMENT / "inject_growth_run7.py").read_text(encoding="utf-8")
    pipeline = (DEPLOYMENT / "inject_shortlist_growth.py").read_text(encoding="utf-8")
    for marker in [
        "data-alo186-growth-run7-tools",
        "data-alo186-growth-run7-journey",
        "data-alo186-growth-run7-measurement",
        "data-alo186-growth-run7-journal",
    ]:
        assert marker in injector
    assert "alo186.monthlyKwhJournal.v1" in injector
    assert "400*86400000" in injector
    assert "billAmountCollected" in injector
    assert "monthlyKwhLocalOnly" in injector
    assert "directAffiliateLinksAdded" in injector
    assert "paidReferralDisclosureRequired" in injector
    assert "run_growth_run7" in pipeline
    assert pipeline.index("run_growth_run7(site, base_path)") > pipeline.index("run_growth_run6(site, base_path)")

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "routes": sorted(ROUTES),
        "monthlyKwhLocalOnly": True,
        "directAffiliateLinksAdded": 0,
        "providerRanking": False,
        "personalDataFields": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
