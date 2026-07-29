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
        "slug": "ges-inverter-dusuk-izolasyon-direnci-riso-alarmi",
        "required": [
            "düşük izolasyon direnci", "Riso", "nem", "string bazlı",
            "alarmı susturmak", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/ges-string-akimi-dusuk-mppt-uretim-farki",
            "/haberler/ges-mc4-konnektor-capraz-eslestirme-krimp-hatasi",
            "/hesaplama/ges-aylik-uretim-saglik-gunlugu/",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/ges-batarya-ev-sarj-fizibilitesi/",
        ],
        "source_hosts": ["huawei.com", "sma.de", "solaredge.com", "iec.ch"],
    },
    {
        "slug": "parafudr-notr-kopmasi-uzun-sureli-asiri-gerilim-tov",
        "required": [
            "nötr kopması", "TOV", "Uc", "Ut", "tek başına yeterli",
            "kA darbe akımı", "Satın almama sınırı", "Ticari sınır",
            "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/parafudr-yedek-sigorta-sccr-kisa-devre-koordinasyonu",
            "/haberler/notr-toprak-gerilimi-yuksek-nedenleri-olcum",
            "/hesaplama/gerilim-olayi-edas-olcum-talebi/",
            "/hesaplama/elektrik-cihaz-hasari-edas-basvuru-paketi/",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["iec.ch", "dehn-international.com", "abb.com"],
    },
    {
        "slug": "toprak-ozgul-direnci-wenner-topraklama-direnci-farki",
        "required": [
            "Toprak özgül direnci", "Ω·m", "Wenner", "2πaR",
            "görünür özdirenç", "evrensel", "Satın almama sınırı",
            "Ticari sınır", "Son doğrulama: 29 Temmuz 2026",
        ],
        "links": [
            "/haberler/notr-toprak-gerilimi-yuksek-nedenleri-olcum",
            "/haberler/jenerator-ats-3-kutup-4-kutup-anahtarlanan-notr",
            "/hesaplama/kacak-akim-rolesi-olay-gunlugu/",
            "/hesaplama/elektrik-kanit-envanteri/",
            "/hesaplama/teknik-devir-kabul-paketi/",
            "/hizmetler/elektrik-surekliligi-izleme/",
        ],
        "source_hosts": ["ieee.org", "fluke.com", "megger.com", "iec.ch"],
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
    assert manifest["version"] >= 63, manifest["version"]
    article_routes = [route for route in manifest["routes"] if route["type"] == "article"]
    assert len(article_routes) >= 141, len(article_routes)
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

    pv = (REPO_ROOT / "alo186/haberler/ges-inverter-dusuk-izolasyon-direnci-riso-alarmi/index.html").read_text(encoding="utf-8").casefold()
    spd = (REPO_ROOT / "alo186/haberler/parafudr-notr-kopmasi-uzun-sureli-asiri-gerilim-tov/index.html").read_text(encoding="utf-8").casefold()
    soil = (REPO_ROOT / "alo186/haberler/toprak-ozgul-direnci-wenner-topraklama-direnci-farki/index.html").read_text(encoding="utf-8").casefold()
    assert "inverter kapalı görünse bile" in pv and "yeni inverter almak" in pv
    assert "regülatör gibi çalışmaz" in spd and "gerilim koruma rölesi parafudrun yerine geçer mi" in spd
    assert "biri zemin verisi" in soil and "pens yöntemi metalik paralel döngüleri" in soil

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
