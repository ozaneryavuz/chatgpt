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
        "slug": "elektrik-ark-hatasi-afdd-rcd-sigorta-farki",
        "required": [
            "AFDD", "seri ark", "paralel ark", "kaçak akım rölesi",
            "otomatik sigorta", "IEC 62606", "Satın almama sınırı",
            "Ticari sınır", "Son doğrulama: 30 Temmuz 2026",
        ],
        "hosts": ["iec.ch", "se.com", "abb.com"],
    },
]

CONSOLIDATIONS = {
    "/haberler/ups-aku-string-blok-dengesizligi-ic-direnc":
        "/haberler/ups-aku-string-dengesizligi-zayif-aku-nasil-anlasilir",
    "/haberler/ges-string-sigortasi-gpv-ne-zaman-gerekir":
        "/haberler/ges-pv-string-sigortasi-ters-akim-nasil-secilir",
}


def schema_nodes(html: str) -> list[dict]:
    nodes: list[dict] = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        payload = json.loads(raw)
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        nodes.extend(graph if isinstance(graph, list) else [payload])
    return nodes


def main() -> None:
    manifest = load_effective_manifest(ROOT)
    assert manifest["version"] >= 74, manifest["version"]
    routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(routes) >= 163, len(routes)
    route_paths = {route["canonicalPath"] for route in routes}
    new_paths: set[str] = set()

    for article in ARTICLES:
        slug = article["slug"]
        canonical_path = f"/haberler/{slug}"
        route = next((item for item in routes if item["canonicalPath"] == canonical_path), None)
        assert route, canonical_path
        path = ROOT / route["source"]
        assert path.is_file(), path
        html = path.read_text(encoding="utf-8")
        lower = html.casefold()
        canonical = f"https://www.alo186.com{canonical_path}"

        assert "<!doctype html>" in lower
        assert f'rel="canonical" href="{canonical}"' in html
        assert '<meta name="description"' in html
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html
        assert html.count("<h1>") == 1
        assert "Doğrudan cevap" in html
        assert "Ticari sınır" in html
        assert "Satın almama sınırı" in html
        assert "bağımsız" in lower
        assert "affiliate" not in lower and "amazon.com" not in lower
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)

        for token in article["required"]:
            assert token.casefold() in lower, (slug, token)
        for host in article["hosts"]:
            assert host in lower, (slug, host)

        nodes = schema_nodes(html)
        types = {node.get("@type") for node in nodes if isinstance(node, dict)}
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (slug, types)
        assert "Product" not in types and "Offer" not in types
        new_paths.add(canonical_path)

    htaccess = (ROOT / "alo186/deployment/apache-production.htaccess").read_text(encoding="utf-8")
    for alias, canonical in CONSOLIDATIONS.items():
        assert alias not in route_paths, ("duplicate route remains active", alias)
        assert canonical in route_paths, ("canonical route missing", canonical)
        pattern = rf"RewriteRule \^{re.escape(alias.lstrip('/'))}/\?\$ {re.escape(canonical)} \[R=301,L,NE\]"
        assert re.search(pattern, htaccess), ("301 consolidation missing", alias, canonical)

    assert len(new_paths) == 1
    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "articleCount": len(routes),
        "newCanonicalPaths": sorted(new_paths),
        "consolidatedAliases": CONSOLIDATIONS,
        "sourceVerificationDate": "2026-07-30",
        "commercialClaimsAdded": False,
        "formsAdded": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
