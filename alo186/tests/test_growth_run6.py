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
    "/konu-takip-merkezi/": ("alo186/konu-takip-merkezi/index.html", "tool"),
    "/hesaplama/elektrik-kanit-envanteri/": ("alo186/hesaplama/elektrik-kanit-envanteri/index.html", "calculator"),
    "/hesaplama/teknik-sartname-talep-paketi/": ("alo186/hesaplama/teknik-sartname-talep-paketi/index.html", "business-tool"),
}


def text(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def one(html: str, tag: str) -> str:
    found = re.findall(fr"<{tag}\b[^>]*>(.*?)</{tag}>", html, re.I | re.S)
    assert len(found) == 1, (tag, len(found))
    return text(found[0])


def schemas(html: str) -> list[dict]:
    result = []
    for raw in re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', html, re.I | re.S):
        payload = json.loads(raw)
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            result.extend(item for item in payload["@graph"] if isinstance(item, dict))
        elif isinstance(payload, dict):
            result.append(payload)
    return result


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 46
    route_map = {item["canonicalPath"]: item for item in manifest["routes"]}
    titles: set[str] = set()
    h1s: set[str] = set()

    for route, (source, route_type) in ROUTES.items():
        assert route in route_map
        assert route_map[route]["source"] == source
        assert route_map[route]["type"] == route_type
        html = (REPO_ROOT / source).read_text(encoding="utf-8")
        lower = html.casefold()
        title = one(html, "title")
        h1 = one(html, "h1")
        assert title not in titles and h1 not in h1s
        titles.add(title)
        h1s.add(h1)
        assert f'https://www.alo186.com{route}' in html
        types = {item.get("@type") for item in schemas(html)}
        assert "WebApplication" in types and "FAQPage" in types and "BreadcrumbList" in types
        assert "amazon." not in lower and "amzn." not in lower
        assert not re.search(r"\b\d{2,}[.,]?\d*\s*(?:tl|₺|usd|eur|€|\$)\b", lower)
        for forbidden in ["aggregaterating", '"price"', '"pricecurrency"', '"offers"']:
            assert forbidden not in lower
        assert any(boundary in lower for boundary in ["edaş veya kamu kurumu", "edaş veya resmî", "edaş işlemi", "resmî proje"])
        assert "satın almama" in lower or "mevcut ekipman yeterliyse" in lower or "mevcut sistem yeterliyse" in lower

    topic = (REPO_ROOT / ROUTES["/konu-takip-merkezi/"][0]).read_text(encoding="utf-8")
    assert "alo186.topicTracker.v1" in topic
    assert "400*86400000" in topic
    assert "../arama/search-index.json" in topic
    assert "oldPaths" in topic and "canonicalPath" in topic
    assert "e-posta, telefon veya push" in topic.casefold()
    assert "commercialRanking:false" in topic
    assert "localStorage" in topic and "sessionStorage" not in topic

    evidence = (REPO_ROOT / ROUTES["/hesaplama/elektrik-kanit-envanteri/"][0]).read_text(encoding="utf-8")
    assert "alo186.evidenceInventory.v1" in evidence
    assert "730*86400000" in evidence
    assert 'accept="application/json"' in evidence
    assert "personalData:false" in evidence
    assert '<input id="date" type="date"' in evidence
    assert 'type="text"' not in evidence and "textarea" not in evidence
    assert "files[0]" in evidence and "JSON.parse" in evidence

    spec = (REPO_ROOT / ROUTES["/hesaplama/teknik-sartname-talep-paketi/"][0]).read_text(encoding="utf-8")
    assert "alo186.specRequest.v1" in spec
    assert "Marka bağımsız teknik talep paketi" in spec
    assert "commercialRanking:false" in spec
    assert "localStorage" not in spec and "sessionStorage" not in spec
    assert "/hesaplama/teknik-teklif-kapsam-karsilastirma/" in spec
    assert "/hizmetler/elektrik-teklif-teknik-inceleme/" in spec
    for system in ["ups", "generator", "solar", "storage", "ev", "protection", "quality"]:
        assert f'value="{system}"' in spec

    injector = (DEPLOYMENT / "inject_growth_run6.py").read_text(encoding="utf-8")
    pipeline = (DEPLOYMENT / "inject_shortlist_growth.py").read_text(encoding="utf-8")
    for marker in [
        "data-alo186-growth-run6-tools",
        "data-alo186-growth-run6-retention",
        "data-alo186-growth-run6-gateway",
        "data-alo186-growth-run6-spec",
    ]:
        assert marker in injector
    assert "rawPersonalDataCollected" in injector
    assert "directAffiliateLinksAdded" in injector
    assert "noBuyOutcomePreserved" in injector
    assert "run_growth_run6" in pipeline
    assert pipeline.index("run_growth_run6(site, base_path)") > pipeline.index("run_retention_growth(site, base_path)")

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "routes": sorted(ROUTES),
        "topicComparisonLocalOnly": True,
        "evidenceFilesUploaded": False,
        "vendorNeutralSpecification": True,
        "directAffiliateLinksAdded": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
