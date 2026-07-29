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
        "slug": "ups-cikis-kisa-devre-akimi-sigorta-selektivite",
        "required": [
            "inverter current limitation",
            "static bypass",
            "selective coordination",
            "time-current curve",
            "minimum/maksimum kısa devre",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ups-bypass-modu-nedir-neden-gecer",
            "/haberler/ups-cikisinda-kacak-akim-rolesi-notr-toprak",
            "/haberler/jenerator-ups-birlikte-calisir-mi",
            "/haberler/jenerator-ats-3-kutuplu-4-kutuplu-notr-anahtarlama",
            "/hesaplama/teknik-teklif-kapsam-karsilastirma/",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["se.com", "productinfo.se.com"],
    },
    {
        "slug": "ges-zero-export-ct-yonu-faz-eslesmesi",
        "required": [
            "zero export",
            "current transformer direction",
            "phase mapping",
            "point of interconnection",
            "fail-safe",
            "negatif güç",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/vpp-toplayicilik-sayac-telemetri-uzaktan-kontrol",
            "/hesaplama/inverter-uygunluk/",
            "/hesaplama/teknik-teklif-kapsam-karsilastirma/",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["fronius.com", "manuals.sma.de"],
    },
    {
        "slug": "detuned-reaktor-yuzde-7-yuzde-14-nasil-secilir",
        "required": [
            "detuning factor",
            "189 Hz",
            "134 Hz",
            "3. harmonik",
            "5. harmonik",
            "empedans",
            "kapasitör gerilimi",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/detuned-reaktor-aktif-harmonik-filtre-farki",
            "/haberler/kompanzasyon-panosu-reaktif-guc-neden-bozulur",
            "/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler",
            "/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur",
            "/hesaplama/teknik-teklif-kapsam-karsilastirma/",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["tdk-electronics.tdk.com", "circutor.com", "se.com"],
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
    assert manifest["version"] >= 44, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 99, len(article_routes)

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
