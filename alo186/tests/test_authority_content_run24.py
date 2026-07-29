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
        "slug": "jenerator-calisiyor-ama-ats-yuku-transfer-etmiyor",
        "required": [
            "automatic transfer switch",
            "source acceptable",
            "transfer inhibit",
            "generator main circuit breaker",
            "phase sequence",
            "loaded exercise",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/jenerator-calisiyor-elektrik-uretmiyor-ne-yapilmali",
            "/haberler/jenerator-transfer-salteri-neden-gerekir",
            "/hesaplama/elektrik-kesintisi-tatbikati/",
            "/hesaplama/teknik-devir-kabul-paketi/",
        ],
        "source_hosts": ["se.com", "support.generac.com", "cummins.com"],
    },
    {
        "slug": "ges-string-akimi-dusuk-mppt-uretim-farki",
        "required": [
            "PV string current",
            "MPPT mismatch",
            "I-V curve",
            "short-circuit current",
            "open-circuit voltage",
            "reverse polarity",
            "current limiting",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ges-inverter-riso-dusuk-izolasyon-direnci-arizasi",
            "/haberler/ges-panel-hotspot-bypass-diyot-termal-kamera",
            "/hesaplama/inverter-uygunluk/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["info.support.huawei.com", "manuals.sma.de", "fronius.com"],
    },
    {
        "slug": "elektrik-guc-artirimi-basvurusu-edas-sozlesme-gucu",
        "required": [
            "bağlantı gücü",
            "sözleşme gücü",
            "güç artırımı",
            "bağlantı görüşü",
            "onaylı elektrik projesi",
            "tesis tadili",
            "dağıtım şirketi",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/edas-bul",
            "/haberler/elektrik-arizasinda-edas-mi-tedarikci-mi-aranir",
            "/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi",
            "/hesaplama/teknik-sartname-talep-paketi/",
        ],
        "source_hosts": ["epdk.gov.tr", "tedas.gov.tr"],
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
    assert manifest["version"] >= 51, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 114, len(article_routes)
    active_paths = {route["canonicalPath"] for route in article_routes}

    nearby_existing = {
        "/haberler/jenerator-calisiyor-elektrik-uretmiyor-ne-yapilmali",
        "/haberler/jenerator-transfer-salteri-neden-gerekir",
        "/haberler/ges-panel-hotspot-bypass-diyot-termal-kamera",
        "/haberler/gunes-paneli-inverter-clipping-dc-ac-orani",
        "/haberler/elektrik-gerilimi-dusuk-yuksek-edas-olcum-talebi",
        "/haberler/elektrik-arizasinda-edas-mi-tedarikci-mi-aranir",
    }
    assert nearby_existing.issubset(active_paths), nearby_existing - active_paths

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
        assert "yetkili" in lower or "resmî" in lower or "kullanıcı müdahalesine uygun değildir" in lower
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
        assert len(article_schema.get("about", [])) >= 7
        assert all(item.get("@type") == "DefinedTerm" for item in article_schema["about"])
        faq = next(item for item in graphs if item.get("@type") == "FAQPage")
        assert len(faq.get("mainEntity", [])) >= 4
        assert all(item.get("@type") == "Question" for item in faq["mainEntity"])
        assert len(re.findall(r'<a href="https://', html)) >= 4
        assert canonical_path not in seen_canonical
        seen_canonical.add(canonical_path)

    generator = (REPO_ROOT / "alo186/haberler/jenerator-calisiyor-ama-ats-yuku-transfer-etmiyor/index.html").read_text(encoding="utf-8").casefold()
    pv = (REPO_ROOT / "alo186/haberler/ges-string-akimi-dusuk-mppt-uretim-farki/index.html").read_text(encoding="utf-8").casefold()
    power = (REPO_ROOT / "alo186/haberler/elektrik-guc-artirimi-basvurusu-edas-sozlesme-gucu/index.html").read_text(encoding="utf-8").casefold()
    assert "motorun çalışması" in generator and "yük transferi" in generator
    assert "aynı ışınım" in pv and "string akımı sıfır" in pv
    assert "yalnız ana sigortayı büyütmeyin" in power and "bağlantı görüşü" in power

    print(json.dumps({
        "ok": True,
        "routingVersion": manifest["version"],
        "effectiveSourceArticleCount": len(article_routes),
        "newArticleCount": len(ARTICLES),
        "newCanonicalPaths": sorted(seen_canonical),
        "commercialClaimsAdded": False,
        "formsAdded": False,
        "intentSeparationChecked": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
