from __future__ import annotations

import json
import re
import sys
import tempfile
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402
from inject_revenue_trust_proof import run as inject_growth  # noqa: E402

ROUTES = {
    "/gelir-ve-bagimsizlik/": ("alo186/gelir-ve-bagimsizlik/index.html", "collection"),
    "/ornek-teslimler/": ("alo186/ornek-teslimler/index.html", "collection"),
    "/hizmetler/elektrik-surekliligi-izleme/": (
        "alo186/hizmetler/elektrik-surekliligi-izleme/index.html",
        "service",
    ),
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def one(html: str, tag: str) -> str:
    matches = re.findall(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    assert len(matches) == 1, (tag, len(matches))
    return clean(matches[0])


def jsonld(html: str) -> list[dict]:
    result: list[dict] = []
    for block in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        payload = json.loads(block)
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            result.extend(item for item in payload["@graph"] if isinstance(item, dict))
        elif isinstance(payload, dict):
            result.append(payload)
    return result


def test_source_pages() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 43
    route_map = {route["canonicalPath"]: route for route in manifest["routes"]}
    titles: set[str] = set()
    h1s: set[str] = set()

    for canonical, (source, route_type) in ROUTES.items():
        route = route_map.get(canonical)
        assert route, canonical
        assert route["source"] == source
        assert route["type"] == route_type
        path = REPO_ROOT / source
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        assert (path.parent / "styles.css").is_file()
        assert '<link rel="stylesheet" href="./styles.css">' in html
        assert f'rel="canonical" href="https://www.alo186.com{canonical}"' in html
        title = one(html, "title")
        h1 = one(html, "h1")
        assert title not in titles and h1 not in h1s
        titles.add(title)
        h1s.add(h1)
        assert "amazon." not in lower and "amzn." not in lower
        assert not re.search(r"\b\d{2,}[.,]?\d*\s*(?:tl|₺|usd|eur|€|\$)\b", lower)
        assert "aggregaterating" not in lower

    trust = (REPO_ROOT / ROUTES["/gelir-ve-bagimsizlik/"][0]).read_text(encoding="utf-8")
    trust_types = {item.get("@type") for item in jsonld(trust)}
    assert {"AboutPage", "FAQPage", "BreadcrumbList"}.issubset(trust_types)
    for term in ["satış ortaklığı", "ücretli teknik hizmet", "sponsorlu içerik", "satın almayın", "EDAŞ"]:
        assert term.casefold() in clean(trust).casefold()
    assert 'rel="sponsored nofollow noopener"' in trust
    assert "/ornek-teslimler/" in trust

    samples = (REPO_ROOT / ROUTES["/ornek-teslimler/"][0]).read_text(encoding="utf-8")
    sample_types = {item.get("@type") for item in jsonld(samples)}
    assert {"CollectionPage", "FAQPage", "BreadcrumbList"}.issubset(sample_types)
    assert clean(samples).casefold().count("kurgusal") >= 8
    assert "gerçek müşteri referansı" in clean(samples).casefold()
    assert "satın alma tavsiyesi" in clean(samples).casefold()
    for filename in ["otel-sureklilik-ornek.json", "teklif-inceleme-ornek.json", "enerji-fizibilite-ornek.json"]:
        sample_path = REPO_ROOT / "alo186/ornek-teslimler" / filename
        assert sample_path.is_file()
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        assert payload["fictional"] is True
        assert payload["customerClaim"] is False
        serialized = json.dumps(payload, ensure_ascii=False).casefold()
        for forbidden in ['"customername"', '"email"', '"phone"', '"address"', '"price"', '"stock"', '"rating"']:
            assert forbidden not in serialized, (filename, forbidden)

    monitor = (REPO_ROOT / ROUTES["/hizmetler/elektrik-surekliligi-izleme/"][0]).read_text(encoding="utf-8")
    monitor_types = {item.get("@type") for item in jsonld(monitor)}
    assert {"Service", "FAQPage", "BreadcrumbList"}.issubset(monitor_types)
    for term in ["otomatik ödeme", "7/24 alarm", "satın almama", "aylık", "üç aylık", "yıllık"]:
        assert term.casefold() in clean(monitor).casefold()
    assert "service=continuity_monitoring" in monitor
    assert "<form" not in monitor.casefold() and "<input" not in monitor.casefold()
    assert "/hesaplama/teknik-takip-listem/" in monitor
    assert "/hesaplama/elektrik-surekliligi-pasaportu/" in monitor


def test_shared_scope_and_pipeline() -> None:
    corporate = (REPO_ROOT / "alo186/kurumsal-on-degerlendirme/index.html").read_text(encoding="utf-8")
    app = (REPO_ROOT / "alo186/kurumsal-on-degerlendirme/app.js").read_text(encoding="utf-8")
    styles = (REPO_ROOT / "alo186/kurumsal-on-degerlendirme/styles.css").read_text(encoding="utf-8")
    pipeline = (REPO_ROOT / "alo186/deployment/inject_shortlist_growth.py").read_text(encoding="utf-8")
    injector = (REPO_ROOT / "alo186/deployment/inject_revenue_trust_proof.py").read_text(encoding="utf-8")

    assert "/hizmetler/elektrik-surekliligi-izleme/" in corporate
    assert "/ornek-teslimler/" in corporate
    assert "/gelir-ve-bagimsizlik/" in corporate
    assert "continuity_monitoring" in app
    assert "serviceProfiles" in app and "source_service" in app
    assert "localStorage" not in app and "sessionStorage" not in app
    assert "repeat(2,minmax(0,1fr))" in styles
    assert pipeline.index("run_commerce_trust(site, base_path)") < pipeline.index("run_revenue_trust_proof(site, base_path)")
    assert "commercialRankingFieldsUsed" in injector
    assert "automaticRenewal" in injector
    assert "directStoreLinksAdded" in injector
    assert "data-alo186-revenue-proof" in injector
    assert "data-alo186-trust-proof-gateway" in injector


def test_injector_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp)
        routes = [
            {"canonicalPath": "/amazon-elektrik-urunleri", "type": "collection"},
            {"canonicalPath": "/hizmetler/test-service/", "type": "service"},
            {"canonicalPath": "/gelir-ve-bagimsizlik/", "type": "collection"},
            {"canonicalPath": "/ornek-teslimler/", "type": "collection"},
            {"canonicalPath": "/hizmetler/elektrik-surekliligi-izleme/", "type": "service"},
        ]
        for route in routes:
            path = site / route["canonicalPath"].strip("/") / "index.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("<!doctype html><html><body><main>Test</main><footer>Alt</footer></body></html>", encoding="utf-8")
        (site / "index.html").write_text("<!doctype html><html><body><main>Ana</main></body></html>", encoding="utf-8")
        (site / "elektrik-portali").mkdir()
        (site / "elektrik-portali/index.html").write_text("<!doctype html><html><body><main>Portal</main></body></html>", encoding="utf-8")
        release = {"routes": [{"canonicalPath": "/chatgpt" + item["canonicalPath"], "type": item["type"]} for item in routes]}
        (site / "alo186-release.json").write_text(json.dumps(release), encoding="utf-8")
        (site / "pages-release.json").write_text(json.dumps({}), encoding="utf-8")
        (site / "checksums.sha256").write_text("old\n", encoding="utf-8")

        result = inject_growth(site, "/chatgpt")
        assert result["trustPanelsInjected"] == 2
        assert result["gatewaySectionsInjected"] == 2
        assert result["automaticRenewal"] is False
        commerce = (site / "amazon-elektrik-urunleri/index.html").read_text(encoding="utf-8")
        service = (site / "hizmetler/test-service/index.html").read_text(encoding="utf-8")
        for html in (commerce, service):
            assert html.index('data-alo186-revenue-proof="true"') < html.index("<footer")
            assert "/chatgpt/gelir-ve-bagimsizlik/" in html
            assert "/chatgpt/ornek-teslimler/" in html
            assert "/chatgpt/hizmetler/elektrik-surekliligi-izleme/" in html
        for relative in ["index.html", "elektrik-portali/index.html"]:
            html = (site / relative).read_text(encoding="utf-8")
            assert 'data-alo186-trust-proof-gateway="true"' in html
            assert "/chatgpt/gelir-ve-bagimsizlik/" in html
        meta = json.loads((site / "pages-release.json").read_text(encoding="utf-8"))["revenueTrustProofGrowth"]
        assert meta["rawPersonalDataCollected"] is False
        assert meta["automaticRenewal"] is False
        assert meta["directStoreLinksAdded"] == 0
        assert len((site / "checksums.sha256").read_text(encoding="utf-8").splitlines()) > 5


def main() -> None:
    test_source_pages()
    test_shared_scope_and_pipeline()
    test_injector_fixture()
    print(json.dumps({
        "ok": True,
        "actions": [
            "revenue-and-independence-center",
            "fictional-sample-deliverables",
            "recurring-continuity-monitoring-service"
        ],
        "routingVersion": load_effective_manifest(REPO_ROOT)["version"],
        "directStoreLinksAdded": 0,
        "automaticRenewal": False,
        "rawPersonalDataCollected": False
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
