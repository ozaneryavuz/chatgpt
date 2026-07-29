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
        "slug": "ups-eco-modu-double-conversion-econversion-farki",
        "required": [
            "Double conversion", "geleneksel ECO", "eConversion", "statik bypass",
            "10 ms", "ride-through", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ups-bypass-modu-nedir-neden-gecer",
            "/haberler/ups-online-line-interactive-offline-farki",
            "/haberler/ups-sebeke-varken-bataryaya-geciyor",
            "/haberler/jenerator-ups-birlikte-calisir-mi",
            "/hesaplama/ups-suresi/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["iec.ch", "se.com", "eaton.com"],
    },
    {
        "slug": "harmonik-k-factor-trafo-derating-notr-isinmasi",
        "required": [
            "K-faktörü", "K13", "derating", "triplen", "eddy-current",
            "harmonik azaltıcı trafo", "yüzde 200 nötr", "Satın almama sınırı",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/harmonik-nedir-thd-cihazlari-nasil-etkiler",
            "/haberler/notr-akimi-faz-akimindan-yuksek-neden-olur",
            "/haberler/detuned-reaktor-aktif-harmonik-filtre-farki",
            "/haberler/kompanzasyon-detuned-reaktor-yuzdesi-rezonans-frekansi",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["ieee.org", "se.com", "eaton.com"],
    },
    {
        "slug": "ges-pid-lid-letid-guc-kaybi-teshisi",
        "required": [
            "PID", "LID", "LeTID", "PID-shunting", "PID-polarization",
            "anti-PID", "I-V", "EL/PL", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ges-inverter-dusuk-izolasyon-direnci-riso-alarmi",
            "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
            "/haberler/ges-inverter-sicakta-guc-dusuruyor-temperature-derating",
            "/haberler/gunes-paneli-inverter-clipping-dc-ac-orani",
            "/hesaplama/ges-aylik-uretim-saglik-gunlugu/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["iec.ch", "nrel.gov"],
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
    assert manifest["version"] >= 67, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 150, len(article_routes)
    all_paths = {route["canonicalPath"] for route in manifest["routes"]}

    expected_links = {link for article in ARTICLES for link in article["links"]}
    assert expected_links.issubset(all_paths), expected_links - all_paths

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
        assert "amazon.com" not in lower and "amazon.com.tr" not in lower
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

    ups = (REPO_ROOT / "alo186/haberler/ups-eco-modu-double-conversion-econversion-farki/index.html").read_text(encoding="utf-8").casefold()
    transformer = (REPO_ROOT / "alo186/haberler/harmonik-k-factor-trafo-derating-notr-isinmasi/index.html").read_text(encoding="utf-8").casefold()
    pid = (REPO_ROOT / "alo186/haberler/ges-pid-lid-letid-guc-kaybi-teshisi/index.html").read_text(encoding="utf-8").casefold()
    assert "geleneksel eco uygulamalarında" in ups and "aynı online ups içindeki" in ups
    assert "k-faktörlü trafo kendini korur" in transformer and "sistem harmoniklerini azaltma kararı" in transformer
    assert "düşük izolasyon alarmı görülmesi pid kanıtı değildir" in pid and "iec ts 62804-1 ikinci baskısı" in pid
    assert len(new_paths) == 3, new_paths

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
