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
        "slug": "ups-statik-transfer-salteri-sts-ats-bakim-bypass-farki",
        "required": [
            "STS", "ATS", "bakım bypassı", "çift besleme", "kaynak senkronu",
            "transfer inhibit", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "hosts": ["iec.ch", "vertiv.com"],
    },
    {
        "slug": "enerji-depolama-yardimci-tuketim-hvac-net-rte",
        "required": [
            "yardımcı tüketim", "HVAC", "standby", "net round-trip efficiency",
            "sayaç sınırı", "yardımcı tüketim oranı", "Satın almama sınırı",
            "Ticari sınır", "Son doğrulama: 29 Temmuz 2026",
        ],
        "hosts": ["iec.ch", "energy.gov", "sandia.gov", "nrel.gov"],
    },
    {
        "slug": "topraklama-olcumu-yagmur-yaz-kis-mevsim-farki",
        "required": [
            "yağmur", "kurak", "mevsim", "fall-of-potential", "paralel toprak yolları",
            "prob mesafesi", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "hosts": ["ieee.org", "iec.ch", "fluke.com", "megger.com"],
    },
]


def schema_nodes(html: str) -> list[dict]:
    nodes: list[dict] = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        payload = json.loads(raw)
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        nodes.extend(graph if isinstance(graph, list) else [payload])
    return nodes


def main() -> None:
    manifest = load_effective_manifest(ROOT)
    assert manifest["version"] >= 72, manifest["version"]
    routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(routes) >= 162, len(routes)
    seen_titles: set[str] = set()
    seen_h1: set[str] = set()
    new_paths: set[str] = set()

    for article in ARTICLES:
        slug = article["slug"]
        canonical_path = f"/haberler/{slug}"
        route = next((item for item in routes if item["canonicalPath"] == canonical_path), None)
        assert route, canonical_path
        assert route["source"] == f"alo186/haberler/{slug}/index.html"
        path = ROOT / route["source"]
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        canonical = f"https://www.alo186.com{canonical_path}"

        assert "<!doctype html>" in lower
        assert f'rel="canonical" href="{canonical}"' in html
        assert '<meta name="description"' in html
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html
        assert '../alo186-article.css' in html
        assert html.count("<h1>") == 1
        assert "Doğrudan cevap" in html
        assert "Mevcut içerikten görev ayrımı" in html
        assert "Ticari sınır" in html
        assert "Satın almama sınırı" in html
        assert "bağımsız" in lower
        assert "affiliate" not in lower and "amazon.com" not in lower
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)
        assert not re.search(r"garantili kazanç|garantili tasarruf|kesin çözüm|her durumda güvenlidir", lower)

        for token in article["required"]:
            assert token.casefold() in lower, (slug, token)
        for host in article["hosts"]:
            assert host in lower, (slug, host)

        title_match = re.search(r"<title>(.*?)</title>", html, re.S)
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.S)
        assert title_match and h1_match
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
        assert title not in seen_titles and h1 not in seen_h1
        seen_titles.add(title)
        seen_h1.add(h1)

        nodes = schema_nodes(html)
        types = {node.get("@type") for node in nodes if isinstance(node, dict)}
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (slug, types)
        assert "Product" not in types and "Offer" not in types
        article_node = next(node for node in nodes if node.get("@type") == "Article")
        assert article_node["mainEntityOfPage"] == canonical
        assert article_node["datePublished"] == "2026-07-29"
        assert article_node["dateModified"] == "2026-07-29"
        assert len(article_node.get("about", [])) >= 8
        assert all(item.get("@type") == "DefinedTerm" for item in article_node["about"])
        faq = next(node for node in nodes if node.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        new_paths.add(canonical_path)

    sts = (ROOT / "alo186/haberler/ups-statik-transfer-salteri-sts-ats-bakim-bypass-farki/index.html").read_text(encoding="utf-8").casefold()
    bess = (ROOT / "alo186/haberler/enerji-depolama-yardimci-tuketim-hvac-net-rte/index.html").read_text(encoding="utf-8").casefold()
    ground = (ROOT / "alo186/haberler/topraklama-olcumu-yagmur-yaz-kis-mevsim-farki/index.html").read_text(encoding="utf-8").casefold()
    assert "bu üçü aynı cihaz değildir" in sts
    assert "katalogdaki hücre veya pcs verimi" in bess
    assert "aynı yöntem ve bağlantı durumuyla" in ground
    assert len(new_paths) == 3

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "articleCount": len(routes),
        "newArticles": len(ARTICLES),
        "newCanonicalPaths": sorted(new_paths),
        "sourceVerificationDate": "2026-07-29",
        "commercialClaimsAdded": False,
        "formsAdded": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
