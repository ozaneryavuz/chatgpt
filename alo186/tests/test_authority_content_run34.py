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
        "slug": "ups-statik-bypass-senkron-degil-bypass-tolerans-disi",
        "required": [
            "Bypass not in range", "inverter sync to bypass", "faz açısı",
            "bakım bypassı", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ups-bypass-modu-nedir-neden-gecer",
            "/haberler/ups-sebeke-varken-bataryaya-geciyor",
            "/haberler/jenerator-ups-birlikte-calisir-mi",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["iec.ch", "se.com"],
    },
    {
        "slug": "jenerator-paralel-yuk-paylasimi-kw-kvar-droop",
        "required": [
            "kW paylaşımı", "kVAr paylaşımı", "governor", "AVR",
            "dolaşan reaktif akım", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/jenerator-reverse-power-ters-guc-ansi-32",
            "/haberler/jenerator-voltaj-frekans-dalgalanmasi-neden-olur",
            "/haberler/jenerator-dusuk-yuk-wet-stacking-nedir",
            "/hesaplama/jenerator-gucu-secimi/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["iso.org", "deif.com"],
    },
    {
        "slug": "bess-grid-forming-grid-following-black-start-ada-isletmesi",
        "required": [
            "Grid-following", "Grid-forming", "black start", "ada işletmesi",
            "SOC rezervi", "P2800.1 aktif geliştirme projesidir",
            "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/enerji-depolama-round-trip-efficiency-soh-kabul-testi",
            "/haberler/enerji-depolama-bms-soc-kalibrasyon-sapma-drift",
            "/haberler/vpp-toplayicilik-sayac-telemetri-uzaktan-kontrol",
            "/hesaplama/vpp-esnek-yuk-hazirlik/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["energy.gov", "sandia.gov", "ieee.org", "nrel.gov"],
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
    assert manifest["version"] >= 64, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 144, len(article_routes)
    all_paths = {route["canonicalPath"] for route in manifest["routes"]}

    seen_titles: set[str] = set()
    seen_h1: set[str] = set()
    new_paths: set[str] = set()

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
        assert "Ticari sınır" in html
        assert "Satın almama sınırı" in html
        assert "bağımsız" in lower
        assert "yetkili" in lower or "resmî" in lower
        assert "Mevcut içerikten görev ayrımı" in html
        assert "WebApplication" not in html
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower and "amzn." not in lower
        assert '"@type":"product"' not in lower and '"@type":"offer"' not in lower
        assert not re.search(r"\bfiyat(?:ı)?\s*[:=]?\s*\d|\bstokta\b|\bpuanı\s*\d|\bgaranti\s*[:=]?\s*\d", lower)
        assert not re.search(r"<form\b|<input\b|<textarea\b", lower)
        assert not re.search(r"kesinlikle güvenlidir|her durumda güvenlidir|kesin çözüm|garantili kazanç|garantili tasarruf", lower)

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
        assert len(article_schema.get("about", [])) >= 8
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        new_paths.add(canonical_path)

    assert len(new_paths) == 3, new_paths
    assert new_paths.issubset(all_paths)

    ups = (REPO_ROOT / "alo186/haberler/ups-statik-bypass-senkron-degil-bypass-tolerans-disi/index.html").read_text(encoding="utf-8").casefold()
    generator = (REPO_ROOT / "alo186/haberler/jenerator-paralel-yuk-paylasimi-kw-kvar-droop/index.html").read_text(encoding="utf-8").casefold()
    bess = (REPO_ROOT / "alo186/haberler/bess-grid-forming-grid-following-black-start-ada-isletmesi/index.html").read_text(encoding="utf-8").casefold()
    assert "bir dakikalık ups trendinde görünmeyen" in ups and "ups'i değiştirmek gerekli değildir" in ups
    assert "aktif güç paylaşımı" in generator and "negatif kvar" in generator
    assert "yalnız inverter fonksiyonu değildir" in bess and "black-start donanımı zorunlu olmayabilir" in bess

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "effectiveSourceArticleCount": len(article_routes),
        "newArticleCount": len(ARTICLES),
        "newCanonicalPaths": sorted(new_paths),
        "commercialClaimsAdded": False,
        "formsAdded": False,
        "intentSeparationChecked": True,
        "sourceVerificationDate": "2026-07-29",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
