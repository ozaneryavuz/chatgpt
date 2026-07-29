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
        "slug": "ev-sarj-acik-pen-korumasi-opdd-nedir",
        "required": [
            "Open PEN detection device",
            "OPDD",
            "TN-C-S/PME",
            "RDC-DD",
            "Türkiye sınırı",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/hesaplama/ev-sarj-uygunluk/",
            "/haberler/ev-sarj-istasyonu-tip-b-rcd-rdc-dd-secimi",
            "/haberler/notr-kopmasi-nasil-anlasilir",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["theiet.org"],
    },
    {
        "slug": "parafudr-tip-1-tip-2-tip-3-paratoner-secimi",
        "required": [
            "Tip 1 SPD",
            "Tip 2 SPD",
            "Tip 3 SPD",
            "Tip 1+2",
            "10/350 µs",
            "enerji koordinasyonu",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/hesaplama/parafudr-risk-testi/",
            "/haberler/parafudr-uc-up-in-imax-iimp-ne-demek",
            "/haberler/parafudr-yedek-sigorta-scpd-nasil-secilir",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["se.com", "dehn-international.com", "abb.com"],
    },
    {
        "slug": "jenerator-faz-sirasi-ters-motor-ats-kontrolu",
        "required": [
            "faz sırası",
            "ATS",
            "faz rotasyon",
            "VFD",
            "kilitleme-etiketleme",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/hesaplama/jenerator-gucu-secimi/",
            "/haberler/jenerator-ats-amf-farki-nedir",
            "/haberler/faz-dengesizligi-faz-kaybi-motoru-nasil-etkiler",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["se.com", "fluke.com"],
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
    assert manifest["version"] >= 40, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 90, len(article_routes)

    seen_canonical: set[str] = set()
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
        assert "Doğrudan cevap" in html
        assert "Kaynaklar ve doğrulama" in html
        assert "Affiliate sınırı" in html
        assert "Bağımsız" in html
        professional_boundary = (
            "yetkili" in lower
            or "kullanıcı işlemi değildir" in lower
            or "kullanıcı müdahalesine uygun değildir" in lower
        )
        assert professional_boundary, f"Profesyonel müdahale sınırı eksik: {slug}"
        assert "WebApplication" not in html
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower
        assert not re.search(r"\bfiyat(?:ı)?\s*[:=]?\s*\d|\bstokta\b|\bpuanı\s*\d|\bgaranti\s*[:=]?\s*\d", lower)
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)
        assert not re.search(r"kesinlikle güvenlidir|her durumda güvenlidir|garanti gelir|gelir garantisi", lower)

        for required in article["required"]:
            assert required.casefold() in lower, f"Zorunlu ifade eksik ({required}): {slug}"
        for link in article["links"]:
            assert link in html, f"İç bağlantı eksik ({link}): {slug}"
        for host in article["source_hosts"]:
            assert host in lower, f"Birincil kaynak alan adı eksik ({host}): {slug}"

        graphs = jsonld_graphs(html)
        types = {item.get("@type") for item in graphs if isinstance(item, dict)}
        assert {"Article", "FAQPage", "BreadcrumbList"}.issubset(types), (slug, types)
        article_schema = next(item for item in graphs if item.get("@type") == "Article")
        assert article_schema["datePublished"] == "2026-07-29"
        assert article_schema["dateModified"] == "2026-07-29"
        assert article_schema["mainEntityOfPage"] == canonical
        assert len(article_schema.get("about", [])) >= 4
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 3
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
