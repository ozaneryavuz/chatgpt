from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))
from build_static_site import load_effective_manifest  # noqa: E402

ARTICLES = [
    {
        "slug": "ev-sarj-22kw-neden-11kw-74kw-onboard-charger",
        "required": ["on-board charger", "22 kW", "11 kW", "7,4 kW", "Satın almama sınırı", "Son doğrulama: 29 Temmuz 2026"],
        "hosts": ["afdc.energy.gov", "iec.ch", "epdk.gov.tr"],
    },
    {
        "slug": "elektrik-guc-artisi-edas-baglanti-gorusu-proje",
        "required": ["sözleşme gücü", "bağlantı görüşü", "proje", "trafo kapasitesi", "Satın almama sınırı", "Son doğrulama: 29 Temmuz 2026"],
        "hosts": ["epdk.gov.tr"],
    },
    {
        "slug": "vpp-telemetri-kontrol-protokol-toplayici-hazirlik",
        "required": ["telemetri", "opt-out", "OpenADR", "IEEE 2030.5", "Toplayıcı", "Gelir sınırı", "Son doğrulama: 29 Temmuz 2026"],
        "hosts": ["teias.gov.tr", "openadr.org", "ieee.org", "energy.gov"],
    },
]


def schema_nodes(html: str) -> list[dict]:
    out: list[dict] = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        payload = json.loads(raw)
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        out.extend(graph if isinstance(graph, list) else [payload])
    return out


def main() -> None:
    manifest = load_effective_manifest(ROOT)
    assert manifest["version"] >= 69, manifest["version"]
    routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(routes) >= 156, len(routes)
    seen_titles: set[str] = set()
    seen_h1: set[str] = set()
    for article in ARTICLES:
        slug = article["slug"]
        canonical_path = f"/haberler/{slug}"
        route = next((item for item in routes if item["canonicalPath"] == canonical_path), None)
        assert route, canonical_path
        path = ROOT / route["source"]
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        canonical = f"https://www.alo186.com{canonical_path}"
        assert f'rel="canonical" href="{canonical}"' in html
        assert html.count("<h1>") == 1
        assert "Doğrudan cevap" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Ticari sınır" in html
        assert "affiliate" not in lower and "amazon.com" not in lower
        assert not re.search(r"\bfiyat(?:ı)?\s*[:=]?\s*\d|\bstokta\b|\bpuanı\s*\d", lower)
        for token in article["required"]:
            assert token.casefold() in lower, (slug, token)
        for host in article["hosts"]:
            assert host in lower, (slug, host)
        title = re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip()
        h1 = re.sub(r"<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", html, re.S).group(1)).strip()
        assert title not in seen_titles and h1 not in seen_h1
        seen_titles.add(title); seen_h1.add(h1)
        nodes = schema_nodes(html)
        types = {node.get("@type") for node in nodes if isinstance(node, dict)}
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types)
        article_node = next(node for node in nodes if node.get("@type") == "Article")
        assert article_node["mainEntityOfPage"] == canonical
        assert article_node["datePublished"] == "2026-07-29"
        assert len(article_node.get("about", [])) >= 8
        faq = next(node for node in nodes if node.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
    print(json.dumps({"ok": True, "routingVersion": manifest["version"], "articleCount": len(routes), "newArticles": len(ARTICLES)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
