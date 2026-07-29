from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = REPO_ROOT / "alo186/deployment"
sys.path.insert(0, str(DEPLOYMENT))

from build_static_site import load_effective_manifest  # noqa: E402

ARTICLES = [
    {
        "slug": "ups-eco-modu-cift-cevrim-transfer-suresi-kritik-yuk",
        "required": [
            "UPS ECO mode",
            "double conversion UPS",
            "UPS transfer time",
            "static bypass",
            "critical load ride-through",
            "generator frequency tolerance",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ups-cikis-kisa-devre-akimi-sigorta-selektivite",
            "/hesaplama/yedek-guc-cozum-secici/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["se.com", "productinfo.se.com", "tripplite.eaton.com"],
    },
    {
        "slug": "jenerator-dusuk-yuk-wet-stacking-load-bank-testi",
        "required": [
            "generator wet stacking",
            "generator underloading",
            "load bank test",
            "exhaust temperature",
            "diesel aftertreatment",
            "generator load factor",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/jenerator-faz-sirasi-ters-motor-ats-kontrolu",
            "/hesaplama/yedek-guc-cozum-secici/",
            "/hesaplama/elektrik-kesintisi-tatbikati/",
            "/hizmetler/otel-elektrik-surekliligi-denetimi/",
        ],
        "source_hosts": ["cat.com", "cummins.com", "generac.com"],
    },
    {
        "slug": "kacak-akim-rolesi-tip-f-tip-b-inverter-vfd-isi-pompasi",
        "required": [
            "RCD type F",
            "RCD type B",
            "smooth DC residual current",
            "single-phase frequency converter",
            "nuisance tripping",
            "protective conductor leakage current",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ev-sarj-acik-pen-korumasi-opdd-nedir",
            "/haberler/ev-sarj-kablosu-kesiti-gerilim-dusumu-isinma",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-teklif-teknik-inceleme/",
        ],
        "source_hosts": ["siemens.com", "empower.abb.com", "assets.sc.hager.com", "hager.com"],
    },
]


def jsonld_graphs(html: str) -> list[dict]:
    graphs: list[dict] = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        payload = json.loads(raw)
        graph = payload.get("@graph") if isinstance(payload, dict) else None
        graphs.extend(graph if isinstance(graph, list) else [payload])
    return graphs


def main() -> None:
    manifest = load_effective_manifest(REPO_ROOT)
    assert manifest["version"] >= 46, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 105, len(article_routes)

    seen_canonical: set[str] = set()
    seen_titles: set[str] = set()
    seen_h1: set[str] = set()
    for article in ARTICLES:
        slug = article["slug"]
        canonical_path = f"/haberler/{slug}"
        route = next((item for item in article_routes if item["canonicalPath"] == canonical_path), None)
        assert route, f"Routing eksik: {canonical_path}"
        assert route["source"] == f"alo186/haberler/{slug}/index.html"

        file_path = REPO_ROOT / route["source"]
        assert file_path.is_file(), file_path
        html = file_path.read_text(encoding="utf-8")
        lower = html.casefold()
        canonical = f"https://www.alo186.com{canonical_path}"

        assert "<!doctype html>" in lower
        assert f'rel="canonical" href="{canonical}"' in html
        assert '<meta name="description"' in html
        assert '<meta name="robots" content="index,follow,max-image-preview:large">' in html
        assert '../alo186-article.css' in html
        assert html.count("<h1>") == 1
        title_match = re.search(r"<title>(.*?)</title>", html, re.S)
        h1_match = re.search(r"<h1>(.*?)</h1>", html, re.S)
        assert title_match and h1_match
        title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
        h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
        assert title not in seen_titles and h1 not in seen_h1
        seen_titles.add(title)
        seen_h1.add(h1)

        assert "Doğrudan cevap" in html
        assert "Kaynaklar ve doğrulama" in html
        assert "Affiliate sınırı" in html or "Ticari sınır" in html
        assert "Bağımsız" in html
        assert "yetkili" in lower or "kullanıcı müdahalesine uygun değildir" in lower
        assert "WebApplication" not in html
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower
        assert not re.search(r"\bfiyat(?:ı)?\s*[:=]?\s*\d|\bstokta\b|\bpuanı\s*\d|\bgaranti\s*[:=]?\s*\d", lower)
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)
        assert not re.search(
            r"kesinlikle güvenlidir|her durumda güvenlidir|kesin çözüm|garantili kazanç|garantili tasarruf",
            lower,
        )

        for required in article["required"]:
            assert required.casefold() in lower, f"Zorunlu ifade eksik ({required}): {slug}"
        for link in article["links"]:
            assert link in html, f"İç bağlantı eksik ({link}): {slug}"
        for host in article["source_hosts"]:
            assert host in lower, f"Birincil kaynak alan adı eksik ({host}): {slug}"

        graphs = jsonld_graphs(html)
        types = {item.get("@type") for item in graphs if isinstance(item, dict)}
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (slug, types)
        assert "Product" not in types and "Offer" not in types
        article_schema = next(item for item in graphs if item.get("@type") == "Article")
        assert article_schema["datePublished"] == "2026-07-29"
        assert article_schema["dateModified"] == "2026-07-29"
        assert article_schema["mainEntityOfPage"] == canonical
        assert len(article_schema.get("about", [])) >= 4
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        assert canonical_path not in seen_canonical
        seen_canonical.add(canonical_path)

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "effectiveSourceArticleCount": len(article_routes),
        "newArticleCount": len(ARTICLES),
        "newCanonicalPaths": sorted(seen_canonical),
        "commercialClaimsAdded": False,
        "formsAdded": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
